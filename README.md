[![FastMCP Version](https://img.shields.io/badge/FastMCP-3.2%20GA%20(namespaces)-blue?style=flat-square&logo=python&logoColor=white)](https://github.com/jlowin/fastmcp) [![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff) [![Linted with Biome](https://img.shields.io/badge/Linted_with-Biome-60a5fa?style=flat-square&logo=biome&logoColor=white)](https://biomejs.dev/) [![Built with Just](https://img.shields.io/badge/Built_with-Just-000000?style=flat-square&logo=gnu-bash&logoColor=white)](https://github.com/casey/just)

![Advanced Memory Hub](docs/assets/header.png)

# Advanced Memory (Memops)

<p align="center">
  <a href="https://github.com/casey/just"><img src="https://img.shields.io/badge/just-ready_to_go-7c5cfc?style=flat-square&logo=just&logoColor=white" alt="Just"></a>
  <a href="https://github.com/astral-sh/ruff"><img src="https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json" alt="Ruff"></a>
  <a href="https://python.org"><img src="https://img.shields.io/badge/Python-3.13+-3776AB?style=flat-square&logo=python&logoColor=white" alt="Python"></a>
  <a href="https://biomejs.dev"><img src="https://img.shields.io/badge/Linted_with-Biome-60a5fa?style=flat-square&logo=biome&logoColor=white" alt="Biome"></a>
  <a href="https://github.com/PrefectHQ/fastmcp"><img src="https://img.shields.io/badge/FastMCP-3.2-7c5cfc?style=flat-square" alt="FastMCP"></a>
</p>

- **Why** — Give an MCP-capable assistant a **durable place** for notes, research, and retrieval: search and RAG over *your* content instead of losing context every session.
- **What** — A **FastMCP 3.2 GA** server (Python 3.12+) exposing **79 tools across 12 Industrial Portmanteaus** (`audio`, `inbox`, `skills`, `zettel`, `nav`, `notes`, `search`, `knowledge`, `project`, `system`, `mcp`, `typora`). Optimized with **2026 Industrial Docstrings** (Rationale-First) and **Discriminated Unions** for high-fidelity tool selection in Antigravity/Cursor.
- **How** — **Connect** the MCP server from your client ([installation](docs/INSTALLATION.md), then [usage](docs/USAGE.md)). Optionally run the **[webapp](webapp/README.md)** for a browser UI on top of the same backend.

---

## Quick Start

```powershell
git clone https://github.com/sandraschi/advanced-memory-mcp
cd advanced-memory-mcp
just
```

This opens an interactive dashboard showing all available commands. Run `just bootstrap` to install dependencies, then `just serve` or `just dev` to start.

### Manual Setup

If you don't have `just` installed:

## Documentation

- [Installation](docs/INSTALLATION.md) — Python `uv`, optional OCR/Pandoc
- [Usage](docs/USAGE.md) — MCP clients, webapp, advanced topics
- [AI features](docs/AI-FEATURES.md) — RAG, agentic mode, sampling
- [FastMCP 3.2](docs/FASTMCP.md) — Managed Namespaces, prefabs, CodeMode, transports
- [Product requirements (PRD)](docs/PRD.md) — current mission, scope, KPIs (1.8.x)
- [Architecture](docs/ARCHITECTURE.md)
- [Fleet / multi-node](docs/FLEET.md)
- [Compliance & standards](docs/COMPLIANCE_AND_STANDARDS.md)
- [Development](docs/DEVELOPMENT.md) — `just` recipes (lint, test, pack)
- [Changelog](CHANGELOG.md)
- [Release checklist (MCPB + Git tag)](docs/operations/RELEASE_CHECKLIST.md)

---

**Author:** Sandra Schipal · Vienna, Austria


## 🛡️ Industrial Quality Stack

This project adheres to **SOTA 14.1** industrial standards for high-fidelity agentic orchestration:

- **Python (Core)**: [Ruff](https://astral.sh/ruff) for linting and formatting. Zero-tolerance for `print` statements in core handlers (`T201`).
- **Webapp (UI)**: [Biome](https://biomejs.dev/) for sub-millisecond linting. Strict `noConsoleLog` enforcement.
- **Protocol Compliance**: Hardened `stdout/stderr` isolation to ensure crash-resistant JSON-RPC communication.
- **Automation**: [Justfile](./justfile) recipes for all fleet operations (`just lint`, `just fix`, `just dev`).
- **Security**: Automated audits via `bandit` and `safety`.
