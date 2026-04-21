"""Simulate the Cursor stdio launch: init + tools/list; fail fast on errors.

Uses a reader thread + queue so recv() actually honors the timeout.
"""

import json
import os
import queue
import subprocess
import sys
import threading
import time


def main() -> int:
    cmd = [
        "D:/Dev/repos/uv-install/uv.exe",
        "--directory",
        "D:/Dev/repos/advanced-memory-mcp",
        "run",
        "python",
        "-m",
        "advanced_memory.cli.main",
        "mcp",
        "--transport",
        "stdio",
    ]
    env = os.environ.copy()
    env["PYTHONUNBUFFERED"] = "1"
    env["ADVANCED_MEMORY_HOME"] = "C:/Users/sandr"
    env["ADVANCED_MEMORY_READONLY"] = "1"
    env["ADVANCED_MEMORY_STDIN_SINGLE_INSTANCE"] = "0"

    print(f"[harness] spawning: {' '.join(cmd)}", file=sys.stderr)
    proc = subprocess.Popen(
        cmd,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=env,
        bufsize=0,
    )
    assert proc.stdin is not None and proc.stdout is not None and proc.stderr is not None

    stdout_q: queue.Queue[str] = queue.Queue()
    stderr_q: queue.Queue[str] = queue.Queue()

    def pump(src, q, tag):
        try:
            for raw in iter(src.readline, b""):
                line = raw.decode("utf-8", "replace").rstrip("\r\n")
                if line:
                    q.put(line)
                    if tag == "err":
                        print(f"[server.err] {line}", file=sys.stderr)
        except Exception as e:
            print(f"[pump.{tag}] {e}", file=sys.stderr)

    t_out = threading.Thread(target=pump, args=(proc.stdout, stdout_q, "out"), daemon=True)
    t_err = threading.Thread(target=pump, args=(proc.stderr, stderr_q, "err"), daemon=True)
    t_out.start()
    t_err.start()

    def send(msg: dict) -> None:
        data = (json.dumps(msg) + "\n").encode("utf-8")
        proc.stdin.write(data)
        proc.stdin.flush()

    def recv_json(timeout: float) -> dict | None:
        deadline = time.time() + timeout
        while time.time() < deadline:
            try:
                line = stdout_q.get(timeout=0.5)
            except queue.Empty:
                if proc.poll() is not None:
                    return None
                continue
            try:
                return json.loads(line)
            except json.JSONDecodeError:
                print(f"[harness] non-json stdout: {line!r}", file=sys.stderr)
        return None

    try:
        # Give server a moment to boot before we write
        time.sleep(2.0)

        send({
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2025-06-18",
                "capabilities": {},
                "clientInfo": {"name": "handshake-test", "version": "0.0.1"},
            },
        })
        init_resp = recv_json(60.0)
        if init_resp is None:
            print("[harness] FAIL: no initialize response within 60s", file=sys.stderr)
            return 2
        print(
            f"[harness] initialize OK: server={init_resp.get('result', {}).get('serverInfo')}",
            file=sys.stderr,
        )

        send({"jsonrpc": "2.0", "method": "notifications/initialized", "params": {}})

        send({"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}})
        tools_resp = recv_json(30.0)
        if tools_resp is None:
            print("[harness] FAIL: no tools/list response within 30s", file=sys.stderr)
            return 3
        tools = tools_resp.get("result", {}).get("tools", [])
        print(f"[harness] tools/list OK: {len(tools)} tools", file=sys.stderr)

        namespaces: dict[str, int] = {}
        for t in tools:
            name = t.get("name", "")
            ns = name.split("_", 1)[0] if "_" in name else "(none)"
            namespaces[ns] = namespaces.get(ns, 0) + 1
        for ns, count in sorted(namespaces.items()):
            print(f"  {ns}: {count}", file=sys.stderr)

        return 0
    finally:
        try:
            proc.stdin.close()
        except Exception:
            pass
        try:
            proc.terminate()
            proc.wait(timeout=3)
        except Exception:
            proc.kill()


if __name__ == "__main__":
    sys.exit(main())
