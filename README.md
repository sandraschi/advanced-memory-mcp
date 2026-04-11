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
- [Architecture](docs/ARCHITECTURE.md)
- [Fleet / multi-node](docs/FLEET.md)
- [Compliance & standards](docs/COMPLIANCE_AND_STANDARDS.md)
- [Development](docs/DEVELOPMENT.md) — `just` recipes (lint, test, pack)

---

**Author:** Sandra Schipal · Vienna, Austria
