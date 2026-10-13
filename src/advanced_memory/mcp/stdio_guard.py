"""Single-writer enforcement for stdio launches (SPEC_SINGLE_WRITER, BUG-048).

There are TWO stdio entrypoints (cli/commands/mcp.py and mcp/server.py
__main__), and possibly more in the wild (IDE sidecars). All of them must go
through enforce_single_writer_stdio() before running a local server:

- daemon reachable -> run as PROXY (never touch the vault directly),
- daemon unreachable + read-write + not STANDALONE -> exit(2), loud,
- read-only -> local reader (cannot corrupt),
- ADVANCED_MEMORY_STANDALONE=1 -> explicit local writer (maintenance).

The DB-layer writer lock (db.claim_writer_lock) remains the backstop for
anything that bypasses even this module: violations die there instead of
contending silently.
"""

import os
import sys

DEFAULT_HTTP_PROXY_URL = "http://127.0.0.1:10732/mcp"


def _die(message: str, code: int = 2):
    """Fail loud: a clean startup error beats silent vault corruption."""
    try:
        from loguru import logger

        logger.error(message)
    except Exception:
        print(message, file=sys.stderr)
    raise SystemExit(code)


def _own_git_sha() -> str | None:
    """Own commit SHA, or None when undeterminable (fail-open, warn)."""
    try:
        import subprocess
        from pathlib import Path

        repo = Path(__file__).resolve().parents[3]  # src/advanced_memory/mcp/ -> repo root
        if not (repo / ".git").exists():
            return None
        proc = subprocess.run(
            ["git", "-C", str(repo), "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        return proc.stdout.strip() or None
    except Exception:
        return None


def _daemon_git_sha(proxy_url: str) -> str | None:
    """Daemon commit SHA via /health, or None when unreachable."""
    try:
        import httpx

        base = proxy_url[:-4] if proxy_url.endswith("/mcp") else proxy_url
        health_url = os.getenv("ADVANCED_MEMORY_HEALTH_URL", base + "/health")
        resp = httpx.get(health_url, timeout=5.0)
        return resp.json().get("git_sha")
    except Exception:
        return None


def _version_gate_or_exit(proxy_url: str) -> None:
    """Refuse to serve stale code against a newer daemon (rule 3)."""
    if os.getenv("ADVANCED_MEMORY_SKIP_VERSION_GATE", "0").strip() == "1":
        return
    own = _own_git_sha()
    daemon = _daemon_git_sha(proxy_url)
    # Daemon reports the short SHA, git gives the full one - prefix-compare.
    match = bool(own and daemon and (own.startswith(daemon) or daemon.startswith(own)))
    if own and daemon and not match:
        _die(
            f"advanced-memory version mismatch: stdio {own[:8]} vs daemon {daemon[:8]} - "
            "update code and restart the daemon (SPEC_SINGLE_WRITER rule 3)",
            code=3,
        )


def _probe_ok(proxy_url: str) -> bool:
    try:
        import httpx

        probe = httpx.post(
            proxy_url,
            json={
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {
                    "protocolVersion": "2025-11-25",
                    "capabilities": {},
                    "clientInfo": {"name": "probe", "version": "1"},
                },
            },
            headers={"Accept": "application/json, text/event-stream"},
            timeout=5.0,
        )
        return probe.status_code == 200
    except Exception:
        return False


def enforce_single_writer_stdio(mcp_server) -> bool:
    """Guard for every stdio launch path. Returns True when PROXIED.

    When True, the caller must NOT run a local server (the proxy call blocks
    until the client disconnects; the caller should then exit). When False,
    the caller proceeds as a local instance (reader, or explicit standalone).
    A read-write stdio launch with an unreachable daemon and no STANDALONE
    opt-in exits the process instead of becoming a silent second writer.
    """
    from advanced_memory.readonly import IS_READONLY

    proxy_url = os.getenv("ADVANCED_MEMORY_HTTP_PROXY", DEFAULT_HTTP_PROXY_URL)
    standalone = os.getenv("ADVANCED_MEMORY_STANDALONE", "0").strip() == "1"

    if _probe_ok(proxy_url):
        if not IS_READONLY:
            _version_gate_or_exit(proxy_url)
        try:
            from advanced_memory.utils.stdio import restore_stdout

            restore_stdout()
            sys.stdout.flush()
        except Exception as e:  # stderr only - stdout is JSON-RPC
            print(f"stdio_guard: restore_stdout failed: {e}", file=sys.stderr)
        from fastmcp import Client
        from fastmcp.server import create_proxy

        # BUG-062: timeout-less forwarding Client wedges the session on one
        # stalled daemon call. 55s lands inside the host 60s tool timeout.
        proxied = create_proxy(Client(proxy_url, timeout=55), name="Advanced Memory MCP")
        proxied.run(transport="stdio")
        return True

    if not IS_READONLY and not standalone:
        _die(
            f"advanced-memory daemon unreachable at {proxy_url} and "
            "ADVANCED_MEMORY_STANDALONE is not set - refusing to start a second "
            "local writer (would corrupt the vault; see SPEC_SINGLE_WRITER). "
            "Start it: nssm start advanced-memory-mcp-daemon",
            code=2,
        )
    return False
