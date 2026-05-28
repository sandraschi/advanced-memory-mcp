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
