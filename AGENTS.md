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
2. Stdio clients (Claude Desktop, opencode, Cursor) probe `http://127.0.0.1:10732/mcp` on startup
3. If the daemon is alive, the stdio instance becomes a lightweight proxy via `create_proxy()` — zero DB initialization
4. If unreachable, starts normally as a standalone server

**Env var** to override the probe URL: `ADVANCED_MEMORY_HTTP_PROXY` (default: `http://127.0.0.1:10732/mcp`)
**Reference implementation:** `src/advanced_memory/cli/commands/mcp.py`

Install docs: follow mcp-central-docs/standards/AGENT_INSTALL_REFERENCE.md
