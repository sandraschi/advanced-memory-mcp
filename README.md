[![FastMCP Version](https://img.shields.io/badge/FastMCP-3.2.0-blue?style=flat-square&logo=python&logoColor=white)](https://github.com/sandraschi/fastmcp) [![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff) [![Linted with Biome](https://img.shields.io/badge/Linted_with-Biome-60a5fa?style=flat-square&logo=biome&logoColor=white)](https://biomejs.dev/) [![Built with Just](https://img.shields.io/badge/Built_with-Just-000000?style=flat-square&logo=gnu-bash&logoColor=white)](https://github.com/casey/just)

![Advanced Memory Hub](docs/assets/header.png)

# Advanced Memory (Memops)

[![Docs: compliance](https://img.shields.io/badge/Docs-compliance-gold.svg)](docs/COMPLIANCE_AND_STANDARDS.md)
[![Package: v1.7.0](https://img.shields.io/badge/Package-v1.7.0-blue.svg)](pyproject.toml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

- **Why** — Give an MCP-capable assistant a **durable place** for notes, research, and retrieval: search and RAG over *your* content instead of losing context every session.
- **What** — A **FastMCP** server (Python 3.12+) with tools for web/GitHub/arXiv research, document ingestion, vector search (LanceDB), exports (HTML, PDF, Pandoc, and more), skills workflows, and hooks into common note stacks (e.g. Obsidian, Joplin, Notion-oriented flows where implemented).
- **How** — **Connect** the MCP server from your client ([installation](docs/INSTALLATION.md), then [usage](docs/USAGE.md)). Optionally run the **[webapp](webapp/README.md)** for a browser UI on top of the same backend.

---

## Documentation

- [Installation](docs/INSTALLATION.md) — Python `uv`, optional OCR/Pandoc
- [Usage](docs/USAGE.md) — MCP clients, webapp, advanced topics
- [AI features](docs/AI-FEATURES.md) — RAG, agentic mode, sampling
- [FastMCP 3.2.0+](docs/FastMCP 3.2.0md) — portmanteaus, prefabs, CodeMode, transports
- [Architecture](docs/ARCHITECTURE.md)
- [Fleet / multi-node](docs/FLEET.md)
- [Compliance & standards](docs/COMPLIANCE_AND_STANDARDS.md)
- [Development](docs/DEVELOPMENT.md) — `just` recipes (lint, test, pack)

---

**Author:** Sandra Schipal · Vienna, Austria


## 🛡️ Industrial Quality Stack

This project adheres to **SOTA 14.1** industrial standards for high-fidelity agentic orchestration:

- **Python (Core)**: [Ruff](https://astral.sh/ruff) for linting and formatting. Zero-tolerance for `print` statements in core handlers (`T201`).
- **Webapp (UI)**: [Biome](https://biomejs.dev/) for sub-millisecond linting. Strict `noConsoleLog` enforcement.
- **Protocol Compliance**: Hardened `stdout/stderr` isolation to ensure crash-resistant JSON-RPC communication.
- **Automation**: [Justfile](./justfile) recipes for all fleet operations (`just lint`, `just fix`, `just dev`).
- **Security**: Automated audits via `bandit` and `safety`.
