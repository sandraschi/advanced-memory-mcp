![Advanced Memory Hub](docs/assets/header.png)

# Advanced Memory (Memops)

[![Docs: compliance](https://img.shields.io/badge/Docs-compliance-gold.svg)](docs/COMPLIANCE_AND_STANDARDS.md)
[![Package: v1.7.0](https://img.shields.io/badge/Package-v1.7.0-blue.svg)](pyproject.toml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

MCP server for **research and personal knowledge**: web search, GitHub and arXiv helpers, optional TV Tropes narrative lookups, document ingestion, vector search (RAG), research-oriented skill creation, exports (HTML, PDF, Pandoc, and more), and integrations with notes apps (e.g. Obsidian, Joplin, Notion workflows where supported). Built with **FastMCP** on Python 3.12+.

---

## Documentation

- [Installation](docs/INSTALLATION.md) — Python `uv`, optional OCR/Pandoc
- [Architecture](docs/ARCHITECTURE.md)
- [Usage](docs/USAGE.md)
- [Fleet / multi-node notes](docs/FLEET.md) — if you run more than one instance
- [Compliance & standards](docs/COMPLIANCE_AND_STANDARDS.md)

---

## Repo commands (`just`)

This project uses a [Just](https://github.com/casey/just) file for common tasks. From the repo root:

```bash
just
```

Typical recipes:

| Command   | Purpose        |
| :-------- | :------------- |
| `just lint` | Ruff lint      |
| `just fix`  | Ruff fix + format |
| `just test` | Tests          |
| `just pack` | Build `.mcpb` package |

See the `Justfile` for the full list.

---

**Author:** Sandra Schipal · Vienna, Austria
