# Advanced Memory MCP — Product Requirements Document

**Version:** 1.8.0
**Status:** Stable — FastMCP 3.2 GA Managed Namespaces
**Last Updated:** 2026-04-21
**Supersedes:** [docs/archive/PRD-1.0.0.md](archive/PRD-1.0.0.md)

---

## 1. Executive Summary

Advanced Memory (Memops) is a **local-first MCP memory substrate** for AI assistants. It gives an MCP-capable client a durable place for notes, research results, and retrieval over the user's own content, instead of losing context each session.

Release **1.8.0** decomposes the old portmanteau tool surface into **12 FastMCP 3.2 GA Managed Namespaces** (`audio`, `inbox`, `skills`, `zettel`, `nav`, `notes`, `search`, `knowledge`, `project`, `system`, `mcp`, `typora`), exposing **79 first-class tools**. This is a pure interface-quality change — storage, RAG, import / export, and the webapp are unchanged — aimed squarely at improving model tool-selection accuracy and satisfying strict static scanners (toolbench.arcade.dev) without shadow tools.

---

## 2. Mission & Vision

**Mission.** Provide a reliable, portable knowledge substrate that lets AI assistants maintain long-term, contextually rich memory through semantic retrieval and universal I/O, with the user's data staying on the user's machine.

**Vision.** Be the default "memory back end" for personal and small-team knowledge bases used with Cursor, Claude Desktop, Antigravity IDE, and similar MCP clients — fully portable, fully local-first, inspectable via a webapp when that's useful.

---

## 3. Scope & Non-Goals

### In scope (1.8.0)

- MCP server over stdio, streamable-http, and SSE.
- Zettelkasten-style note CRUD, observations, relations, wikilinks.
- Hybrid retrieval: FTS5 keyword + LanceDB vector (FastEmbed `BAAI/bge-small-en-v1.5`).
- Ingestion of PDF / EPUB / Markdown and round-trip with Obsidian, Joplin, Evernote (ENEX), Notion-style exports.
- Pandoc export (PDF, DOCX, HTML, LaTeX, EPUB, …).
- Local skills workflows (discovery, synthesis, validation).
- Optional webapp (Vite + FastAPI bridge) for browser-based inspection.

### Out of scope (1.8.0)

- Cloud synchronization, server-hosted multi-tenant deployments.
- Realtime multi-user collaboration.
- Mobile applications.
- Opinionated telemetry or account systems.

### Explicitly deferred

- Cross-device sync (beyond user-managed file sync such as Syncthing / OneDrive).
- Managed / enterprise SaaS offering.

---

## 4. Success Metrics

### Primary KPIs

| KPI | Target |
| :--- | :--- |
| IDE cold start (stdio) | ≤ 1.5 s to `tools/list` response |
| Simple tool round-trip (e.g. `notes_read`) | p95 < 200 ms on a 3 k-entity vault |
| Sync — path-only moves | 3 k files in ≤ 5 min (achieved in 1.7.1) |
| Tool-selection accuracy (internal evals) | ≥ 90 % on namespaced names vs. prior portmanteau baseline |
| Data loss incidents in production | 0 |

### Quality metrics

- **Test coverage.** ≥ 90 % lines in core modules; 100 % of registered MCP tool names have at least one regression test.
- **Static-scanner cleanliness.** `toolbench.arcade.dev` green without shadow unrolling.
- **Docs freshness.** `README.md`, `docs/README.md`, `docs/FASTMCP.md`, `CHANGELOG.md`, this `PRD.md` all agree on version + tool count.
- **Security.** `bandit` + `safety` clean in CI.

---

## 5. Core Features (1.8.0 snapshot)

### 5.1 MCP tool surface — 12 Managed Namespaces, 79 tools

Each namespace is a mounted `FastMCP` sub-app under `src/advanced_memory/mcp/tools/<name>.py`; on the wire, tools are named `<namespace>_<operation>`.

| Namespace | Representative tools |
| :--- | :--- |
| `audio` | `audio_dictate` (task-tool), `audio_tts`, `audio_transcribe` |
| `inbox` | `inbox_capture`, `inbox_triage`, `inbox_route` |
| `skills` | `skills_discover`, `skills_synthesize`, `skills_validate` |
| `zettel` | `zettel_scaffold`, `zettel_customize`, `zettel_generate` |
| `nav` | `nav_list_directory`, `nav_recent_activity`, `nav_goto` |
| `notes` | `notes_write`, `notes_read`, `notes_edit`, `notes_delete` |
| `search` | `search_notes`, `search_rag`, `search_title`, `search_permalink` |
| `knowledge` | `knowledge_observations`, `knowledge_relations`, `knowledge_graph` |
| `project` | `project_list`, `project_switch`, `project_current`, `project_create` |
| `system` | `system_help`, `system_health`, `system_env` |
| `mcp` | `mcp_prompts`, `mcp_resources`, `mcp_introspect` |
| `typora` | `typora_open`, `typora_focus`, `typora_roundtrip` |

The legacy `adn_*` / `portmanteau_*` functions remain importable as **logic providers** for Python callers; they are no longer registered as MCP tools.

### 5.2 Semantic memory (RAG)

- LanceDB vector store (local).
- FastEmbed embeddings (`BAAI/bge-small-en-v1.5`).
- Hybrid retrieval combining FTS5 keyword + vector similarity.
- Ingestion pipeline for PDF, EPUB, Markdown with chunk-aware segmentation.

### 5.3 Knowledge graph

- Entities, observations, bidirectional relations.
- Wikilink-aware parsing with hardened safety limits (≤ 5 000 links, ≤ 500 chars / link, ≤ 10 MB / file).
- SQLite + Alembic with deterministic migrations.

### 5.4 Portability

- Obsidian vault import / export (canvas round-trip).
- Joplin, Evernote (ENEX), Notion-style HTML/Markdown.
- Pandoc export engine (PDF, DOCX, HTML, LaTeX, EPUB).
- Claude Skills bidirectional sync with IDE skills folders.

### 5.5 Webapp (optional)

- React + Tailwind frontend (port 10704), FastAPI bridge (port 10705).
- Note viewer, search explorer, knowledge-graph (Mermaid), skill studio.
- Not required to use the MCP server.

### 5.6 Prefab UI responses

Tools that support it return `fastmcp.tools.ToolResult` with attached prefab apps (`NoteViewer`, `KnowledgeGraph`, `SearchExplorer`, `ZettelCollector`). Clients that don't render prefabs see the text content cleanly.

---

## 6. Architecture

```
          ┌─────────────────────┐
          │  MCP Client (LLM)   │
          │  Cursor / Claude /  │
          │  Antigravity / etc. │
          └──────────┬──────────┘
                     │ JSON-RPC (stdio | http | sse)
          ┌──────────▼──────────┐
          │  FastMCP 3.2 root   │  advanced_memory.mcp.mcp_instance
          │  + app_lifespan     │  (file watcher, project session, resources)
          └──────────┬──────────┘
                     │ mcp.mount(namespace="...")
  ┌────────┬─────────┼─────────┬────────┬─────────┐
  │ audio  │ inbox   │ skills  │ zettel │ nav     │   ... 12 sub-apps ...
  │ notes  │ search  │knowledge│project │ system  │
  │ mcp    │ typora  │         │        │         │
  └────────┴─────────┴─────────┴────────┴─────────┘
                     │
          ┌──────────▼──────────┐
          │   Core services     │  SearchService, SyncService,
          │                     │  EntityRepository, ProjectSession
          └──────────┬──────────┘
                     │
       ┌─────────────┼──────────────┐
       ▼             ▼              ▼
   ┌───────┐   ┌───────────┐   ┌──────────────┐
   │SQLite │   │  LanceDB  │   │  Markdown FS │
   │+ FTS5 │   │  (vector) │   │  (vault)     │
   └───────┘   └───────────┘   └──────────────┘
```

### Technology stack

- **Backend.** Python 3.12+, FastMCP 3.2 GA (`fastmcp[code-mode]`), FastAPI, SQLAlchemy 2.x.
- **Vector.** LanceDB.
- **Embeddings.** FastEmbed `BAAI/bge-small-en-v1.5`.
- **Database.** SQLite + Alembic.
- **Frontend (webapp).** React, Tailwind, Vite, Biome.
- **Build & quality.** `uv`, `ruff`, `pyright`, `bandit`, `safety`, `just`.
- **CI/CD.** GitHub Actions with Windows + Linux matrix.

---

## 7. Functional requirements

### FR-1 — Knowledge graph & semantic ops

- **FR-1.1.** CRUD on entities, observations, relations.
- **FR-1.2.** Category + context on observations.
- **FR-1.3.** Hybrid search (FTS5 + vector) with tag / type / date filters.
- **FR-1.4.** Boolean query parser (`AND`, `OR`, `NOT`, grouping, `"exact phrases"`, `tag:x`).
- **FR-1.5.** Context expansion across relations for a given entity.

### FR-2 — Projects

- **FR-2.1.** Multiple projects with isolated roots.
- **FR-2.2.** Runtime `project_switch` without server restart.
- **FR-2.3.** `projects="ALL" | "ALL_EXCEPT:x,y" | "p1,p2"` targeting in search.
- **FR-2.4.** `project_create` bootstraps directory + initial config.

### FR-3 — Import / export

- **FR-3.1.** Obsidian vault round-trip (incl. canvas).
- **FR-3.2.** Pandoc export to 40+ formats.
- **FR-3.3.** Data-integrity guarantees during import (atomic writes, rollback).
- **FR-3.4.** Scale target: 10 000+ notes per project.

### FR-4 — MCP integration & compatibility

- **FR-4.1.** MCP protocol compliance for stdio, streamable-http, SSE.
- **FR-4.2.** Cross-platform (Windows, macOS, Linux).
- **FR-4.3.** Works with Claude Desktop, Cursor, Antigravity IDE, generic MCP hosts.
- **FR-4.4.** Reliable under strict JSON-RPC hosts (LF-only line endings on Windows; no stdout pollution in stdio mode).

### FR-5 — Tool-surface quality (new in 1.8.0)

- **FR-5.1.** Each MCP tool is first-class (its own name, docstring, schema).
- **FR-5.2.** No `operation: Literal[...]` dispatcher as the only way to call a capability.
- **FR-5.3.** Long-running tools use FastMCP 3.2 `tool(task=True)` where applicable (cancellation + progress).
- **FR-5.4.** Tool set is discoverable in a single `tools/list` call without env-var toggles.

---

## 8. Non-functional requirements

### NFR-1 — Performance

- **NFR-1.1.** Cold stdio start → `tools/list` response: ≤ 1.5 s.
- **NFR-1.2.** Simple ops p95 < 200 ms on a 3 k-entity vault.
- **NFR-1.3.** Resident memory < 500 MB for typical vaults.
- **NFR-1.4.** 50 000+ entities supported per project.

### NFR-2 — Reliability

- **NFR-2.1.** No data-loss incidents.
- **NFR-2.2.** Sync robust to malformed markdown, bad UTF-8, oversized files (10 MB cap).
- **NFR-2.3.** Graceful cancellation of the file watcher on shutdown (≤ 5 s).
- **NFR-2.4.** Single-instance lock on Windows stdio mode (overridable with `ADVANCED_MEMORY_STDIN_SINGLE_INSTANCE=0`).

### NFR-3 — Security & privacy

- **NFR-3.1.** Zero network calls by default beyond explicit research / export tools.
- **NFR-3.2.** Input validation & sanitization on all write tools.
- **NFR-3.3.** `bandit` + `safety` clean in CI.
- **NFR-3.4.** Optional encryption at rest via OS-level mechanisms (BitLocker, LUKS, FileVault) — not re-implemented by the app.

### NFR-4 — Usability

- **NFR-4.1.** Tool descriptions are self-sufficient for an LLM to pick the right call without extra prompting.
- **NFR-4.2.** Error responses are actionable (suggest next call, list valid enum values).
- **NFR-4.3.** One-command install (`uv tool install` or `pip install`).

---

## 9. Migration notes (from 1.7.x)

- **Tool names changed on the wire.** `adn_<domain>(operation="x", ...)` is now `<domain>_x(...)`. Example: `adn_audio(operation="dictate", ...)` → `audio_dictate(...)`. Run `scripts/test_stdio_handshake.py` for the authoritative list.
- **Env-var toggles removed.**
  - `ADVANCED_MEMORY_FULL_TOOLS_MODE` — no longer needed; the full surface is default.
  - `ADVANCED_MEMORY_ARCADE_COMPLIANCE` — no longer needed; namespaced names are first-class.
- **`mcp.ToolResult` replaced.** Use `from fastmcp.tools import ToolResult`. Internal call sites have already been fixed.
- **Python callers unaffected.** The old `adn_*` / `portmanteau_*` functions still exist and still work; only the MCP registration changed.

---

## 10. Testing strategy

1. **Unit tests.** Per-module logic providers (`pytest`).
2. **Integration tests.** MCP protocol + DB, including ProjectManager and PrefabManager rehydration.
3. **E2E handshake.** `scripts/test_stdio_handshake.py` for IDE-style launches.
4. **Performance tests.** Sync passes and search queries against seeded 3 k / 10 k vaults.
5. **Static scans.** `ruff`, `pyright`, `bandit`, `safety`, toolbench.arcade.dev.

### Coverage goals

- ≥ 90 % line coverage in core.
- 100 % of MCP tool names round-tripped by at least one regression test.

---

## 11. Distribution & deployment

### Installation

- `uv tool install schip-mcp-advanced-memory`
- `pip install schip-mcp-advanced-memory`
- `git clone` for development; `uv run advanced-memory mcp --transport stdio`.

### Transports

- **stdio** — default for Cursor / Claude Desktop / Antigravity IDE.
- **streamable-http** / **sse** — `--transport streamable-http --host ... --port ...` for remote / webapp use.

### Versioning

- SemVer. `1.8.0` is a minor bump because the Python API is backward-compatible; MCP tool names changed but no client was contractually guaranteed the old names.
- `CHANGELOG.md` follows Keep a Changelog.

---

## 12. Roadmap signals (post-1.8.0)

- **Per-tool eval harness** against a benchmark prompt set to keep namespace tool-selection above the target KPI.
- **`task=True` coverage.** Extend task-tool usage beyond `audio_dictate` to long ingestion / sync jobs so clients can show progress + cancel.
- **Prefab polish.** Tighten `KnowledgeGraph` and `SearchExplorer` for client-side filtering.
- **Fleet / multi-node.** Smooth the multi-instance experience (see [FLEET.md](FLEET.md)).

Explicitly **not** promised:

- A cloud-hosted tier.
- Realtime collaborative editing.
- Mobile clients.

---

## 13. Documentation map

| Topic | Doc |
| :--- | :--- |
| FastMCP 3.2 GA + Managed Namespaces architecture | [FASTMCP.md](FASTMCP.md) |
| Install | [INSTALLATION.md](INSTALLATION.md) |
| Daily usage (MCP clients, webapp) | [USAGE.md](USAGE.md) |
| RAG, sampling, agentic mode | [AI-FEATURES.md](AI-FEATURES.md) |
| Full architectural deep-dive | [ARCHITECTURE.md](ARCHITECTURE.md), [ARCHITECTURE_DEEP_DIVE.md](ARCHITECTURE_DEEP_DIVE.md) |
| Fleet / multi-node | [FLEET.md](FLEET.md) |
| Compliance & standards | [COMPLIANCE_AND_STANDARDS.md](COMPLIANCE_AND_STANDARDS.md) |
| Contributing / dev loop | [DEVELOPMENT.md](DEVELOPMENT.md), [DEVELOPER_GUIDE.md](DEVELOPER_GUIDE.md) |
| Tool reference | [TOOLS_REFERENCE.md](TOOLS_REFERENCE.md) |
| Release history | [../CHANGELOG.md](../CHANGELOG.md) |

---

**Document owner:** Advanced Memory maintainers
**Status:** Production stable (1.8.0)
