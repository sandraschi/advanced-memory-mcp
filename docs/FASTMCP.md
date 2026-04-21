# FastMCP 3.2 GA in Advanced Memory

This server is built on **[FastMCP](https://github.com/jlowin/fastmcp)** 3.2 GA with the **`code-mode`** extra (`fastmcp[code-mode]>=3.2.0` in `pyproject.toml`). CodeMode is used when the CLI is started with **`--agentic`** (see below).

Since **1.8.0** the tool surface is decomposed into **12 Managed Namespaces** — one mounted `FastMCP` sub-app per domain — instead of a small set of multi-operation portmanteau tools. This page is the architectural reference for that surface.

---

## What the stack does here

- A single root **`FastMCP`** instance (`advanced_memory.mcp.mcp_instance.mcp`) owns the lifespan, transport, and `run()` for **stdio**, **streamable-http**, and **sse**.
- Each domain is its own small `FastMCP(...)` sub-app in `src/advanced_memory/mcp/tools/<domain>.py`, registered via `mcp.mount(<app>, namespace="<domain>")` in `server.py`.
- The lifespan handler (`app_lifespan`) is attached directly to the root instance (`mcp.lifespan = app_lifespan`) and runs the file watcher, project session bootstrap, and MCP resource initialization.
- The Typer command **`advanced-memory mcp`** is the supported entry point for both local (stdio) and HTTP transports — see [USAGE.md](USAGE.md).

---

## Managed Namespaces (the current surface)

| Namespace | Source file | Scope |
| :--- | :--- | :--- |
| `audio` | `tools/audio.py` | Dictation (`task=True`), TTS, transcription, voice memo capture |
| `inbox` | `tools/inbox.py` | Inbox triage, capture, routing |
| `skills` | `tools/skills.py` | Skill discovery, synthesis, validation, uptake |
| `zettel` | `tools/zettel.py` | Zettelkasten scaffolding, customize, generation |
| `nav` | `tools/nav.py` | Directory / permalink navigation, recent activity |
| `notes` | `tools/notes.py` | Note CRUD, write / read / delete / edit |
| `search` | `tools/search.py` | Text / title / permalink / tag search + RAG bridge |
| `knowledge` | `tools/knowledge.py` | Knowledge graph ops, observations, relations |
| `project` | `tools/project.py` | Project list / switch / current / create |
| `system` | `tools/system.py` | Help, health, observability, environment |
| `mcp` | `tools/mcp.py` | MCP-level introspection, prompts / resources |
| `typora` | `tools/typora.py` | Typora editor control and round-trip |

On the wire a tool name looks like `<namespace>_<operation>` — e.g. `audio_dictate`, `notes_write`, `search_rag`, `zettel_customize`. Clients that list tools see **79 first-class tools** with their own descriptions and schemas rather than a handful of `operation=` dispatchers.

### Why namespaces (vs. portmanteaus)

- **Model tool-selection.** Verb-level names and per-tool required-parameter schemas give the LLM much sharper signal than a single `operation: Literal[...]` argument on a mega-tool.
- **Scanner compatibility.** Strict static scanners (e.g. toolbench.arcade.dev) see distinct tool names natively — the old `ADVANCED_MEMORY_ARCADE_COMPLIANCE` shadow-unrolling is no longer needed and has been removed.
- **Task tools.** Long-running operations (like dictation) can use FastMCP 3.2's `tool(task=True)` for cancellation + progress, which is only available per-tool.
- **Incremental evolution.** A namespace can be extended (new tool) or reshaped (splitting one tool into two) without touching any other namespace.

The old `adn_*` / `portmanteau_*` functions still exist in their original files with their `@mcp.tool` decorators removed. They are **logic providers** now: the namespaced tool calls delegate into them for the actual implementation, so internal Python callers keep working during the transition.

---

## Transports

| Mode | Typical use |
| :--- | :--- |
| **stdio** | Cursor, Claude Desktop, Antigravity IDE, other local MCP hosts |
| **streamable-http** / **sse** | Network or remote clients; `--host`, `--port`, `--path` on the CLI |

Stdio mode suppresses stdout logging so JSON-RPC is not corrupted; do not expect banner text on stdout in IDE use. The server also normalizes line endings to LF on Windows so Antigravity IDE's strict `"invalid trailing data"` check passes.

Verification harness: `scripts/test_stdio_handshake.py` spawns the server exactly the way an IDE does (`uv run python -m advanced_memory.cli.main mcp --transport stdio`), performs `initialize` + `tools/list`, and prints the per-namespace tool count. Typical cold boot is ~1.2 s.

---

## `CodeMode` and `--agentic`

Starting the MCP with **`--agentic`** applies FastMCP's **CodeMode** transform, which exposes a reduced meta-tool surface suited to automated pipelines that expect fewer entry points. For interactive use, leave `--agentic` **off** so all 79 namespaced tools stay visible.

---

## Rich results: `ToolResult` and **prefabs**

FastMCP lets a tool return structured UI for clients that support it. This repo pins **`prefab-ui` ≥ 0.19** (see `pyproject.toml`) and the helpers in **`advanced_memory/mcp/prefabs.py`**:

**Where it renders.** Prefabs ship as **structured tool result content** plus the Prefab renderer resource (`ui://prefab/...`). The chat surface must **implement that renderer** to show grids, Mermaid, and buttons—not just print JSON. **Google Antigravity** is one IDE that advertises this path. **Cursor** (as of early 2026) generally surfaces MCP tool output as **text/markdown** in the agent transcript; if your build does not show interactive Prefab panels, use **`fastmcp dev apps`** from the FastMCP CLI to preview app tools in a browser while developing.

| Prefab helper | Role |
| :--- | :--- |
| **`NoteViewer`** | Card layout for a note body plus metadata (Markdown + sidebar). |
| **`KnowledgeGraph`** | Mermaid graph from nodes / edges. |
| **`SearchExplorer`** | Grid of search-hit cards with actions (used by the RAG bridge). |
| **`ZettelCollector`** | Simple capture / zettel UI. |

These return a **`PrefabApp`** built from layout primitives (`Page`, `Grid`, `Card`, `Markdown`, `Mermaid`, `Button`, …).

**Example:** `search_rag` (the namespaced wrapper over `adn_knowledge_rag`) returns **`fastmcp.tools.ToolResult`** with both textual context (markdown chunks for the model) and `app=SearchExplorer(...)` so a capable client can render the explorer prefab alongside the text.

`zettel_*` paths may attach **`ZettelCollector`**; beta visualization routes use **`KnowledgeGraph`**. Clients that do not render prefab apps fall back to the text content cleanly.

> **Note.** The symbol is `from fastmcp.tools import ToolResult`. The legacy spelling `mcp.ToolResult` does not exist on FastMCP 3.2 and has been purged from this repo.

---

## RAG bridge tool

`search_rag` (namespaced) and `adn_knowledge_rag` (legacy name, logic-provider only) run LanceDB-backed retrieval via `SearchService.knowledge_rag` and may attach `SearchExplorer`. This is separate from the optional Chroma-based `adn_rag` tool described in [AI-FEATURES.md](AI-FEATURES.md).

---

## Sampling and `Context`

Tools that need the **host LLM** accept a FastMCP **`Context`** (usually `ctx`) and use sampling patterns (e.g. `ctx.sample` with tool lists, where supported). See [AI-FEATURES.md](AI-FEATURES.md) for client requirements and the agentic workflows this enables.

---

## Prompts and resources

Prompts and MCP resources are registered during lifespan startup by `initialize_mcp_resources()` (in `mcp_instance.py`, called from `app_lifespan`). Keeping them strongly referenced on the instance prevents them from being garbage-collected after import.

---

## Removed / deprecated (1.8.0)

| Removed | Reason |
| :--- | :--- |
| `src/advanced_memory/mcp/tool_registry.py` | Portmanteau + shadow-unrolling registration is obsolete; namespaces replace it. |
| `ADVANCED_MEMORY_FULL_TOOLS_MODE` env var | The full tool surface is always on; there is no "compact vs. full" mode. |
| `ADVANCED_MEMORY_ARCADE_COMPLIANCE` env var | Namespaced tool names are first-class; no shadow tools needed. |
| `mcp.ToolResult` symbol usage | Not real on FastMCP 3.2; use `from fastmcp.tools import ToolResult`. |

---

## Upstream documentation

For API details beyond this repo, use the FastMCP and Model Context Protocol docs for your installed version (3.2+).

---

[Usage](USAGE.md) · [AI features](AI-FEATURES.md) · [PRD](PRD.md) · [README](../README.md)
