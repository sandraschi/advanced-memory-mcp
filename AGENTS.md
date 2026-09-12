# advanced-memory-mcp — Agent Guide

## Overview
Comprehensive research and knowledge platform with web search, GitHub trawling, arXiv academic research, TV Tropes narrative analysis, document ingestion, RAG vector search, and research-driven skill creation

## Entry Points

- `uv run advanced-memory` → `advanced_memory.cli.main:app`
- `uv run am` → `advanced_memory.cli.main:app`
- `uv run release` → `scripts.release:main`
- `uv run am-skill-creator` → `advanced_memory.services.skill_creator.cli:main`

## Standards
- FastMCP 3.2+ portmanteau tool pattern — tools use `operation` enum param
- Responses: structured dicts with `success`, `message`, domain-specific fields
- Dual transport: stdio (Claude Desktop) + HTTP (`MCP_TRANSPORT=http`)
- See [mcp-central-docs](https://github.com/sandraschi/mcp-central-docs) for fleet-wide coding standards

## Key Files
- `README.md` — full documentation
- `pyproject.toml` — build config and entry points
- `CLAUDE.md` — Claude Code context (if present)

## HTTP Daemon + Stdio Proxy

This server owns persistent state (SQLite database, LanceDB vector index). To prevent database contention when multiple stdio clients connect concurrently, use the HTTP Daemon + Stdio Proxy pattern:

1. Start the HTTP daemon (owns DB): `python -m advanced_memory.cli.main mcp --transport streamable-http --host 127.0.0.1 --port 10732`

   **As of 2026-08-13 this daemon runs as the Windows service `advanced-memory-mcp-daemon`**
   (NSSM, Automatic start, LocalSystem with pinned `ADVANCED_MEMORY_HOME` + `USERPROFILE=C:\Users\sandr`).
   Check it with `Get-Service advanced-memory-mcp-daemon` before spawning a manual daemon —
   if the service is down, start it (`nssm start advanced-memory-mcp-daemon`) instead of
   running a second daemon. Logs: `logs/daemon-service-*.log`.
2. Stdio clients (Claude Desktop, opencode, Cursor) probe `http://127.0.0.1:10732/mcp` on startup
3. If the daemon is alive, the stdio instance becomes a lightweight proxy via `create_proxy()` — zero DB initialization

**Windows NSSM trap:** if the NSSM service runs as LocalSystem without pinned `USERPROFILE`, MCP writes can succeed while the webapp shows nothing — see [docs/troubleshooting/BUG_REPORT_NSSM_SPLIT_BRAIN.md](docs/troubleshooting/BUG_REPORT_NSSM_SPLIT_BRAIN.md).
4. If unreachable, starts normally as a standalone server

**Env var** to override the probe URL: `ADVANCED_MEMORY_HTTP_PROXY` (default: `http://127.0.0.1:10732/mcp`)
**Reference implementation:** `src/advanced_memory/cli/commands/mcp.py`

### Reload daemon after code changes

The NSSM service `advanced-memory-mcp-daemon` keeps Python loaded until SCM restart. After `git pull` or local commits:

1. **Elevated** PowerShell (UAC): `Restart-Service advanced-memory-mcp-daemon -Force`
2. Confirm `http://127.0.0.1:10732/health` shows the expected `git_sha`
3. Reload Cursor MCP (or restart Cursor)

Non-elevated `Restart-Service` from an agent shell may not reload code (useless retry loop). Fleet: mcp-central-docs `standards/TRAPS_AND_PITFALLS.md` section 32.

### Note edits (`adn_notes` `operation=edit`)

Use exact **title or permalink** from `adn_search` (no fuzzy match). Modes: `append`, `prepend`, `find_replace`, `replace_section`. If edits fail with `EntityResponse` / `input_value=None`, upgrade to **1.10.1+** and restart the HTTP daemon as above. Details: `docs/TROUBLESHOOTING_GUIDE.md` section 2a.

Install docs: follow mcp-central-docs/standards/AGENT_INSTALL_REFERENCE.md
