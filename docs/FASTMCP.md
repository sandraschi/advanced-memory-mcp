# FastMCP 3.2+ in Advanced Memory

This server is built on **[FastMCP](https://github.com/jlowin/fastmcp)** with the **`code-mode`** extra (`fastmcp[code-mode]>=3.2.0` in `pyproject.toml`). That extra pulls in **CodeMode**, which the CLI uses when you pass **`--agentic`** (see below).

---

## What the stack does here

- **One `FastMCP` instance** (`advanced_memory.mcp.mcp_instance` / `server`) owns tool registration, lifespan, and `run()` for **stdio**, **streamable-http**, or **sse**.
- Tools are mostly plain **`@mcp.tool`** functions. Several large surfaces use a **portmanteau** pattern: one function with an `operation` parameter (or similar) so many behaviors share one tool name.
- The Typer command **`advanced-memory mcp`** is the supported entry for local and HTTP transports (see [Usage](USAGE.md)).

---

## Transports

| Mode | Typical use |
| :--- | :--- |
| **stdio** | Cursor, Claude Desktop, other local MCP hosts |
| **streamable-http** / **sse** | Network or custom clients; `--host`, `--port`, `--path` on the CLI |

Stdio mode suppresses stdout logging so JSON-RPC is not corrupted; that is why you should not expect banner text on stdout in IDE use.

---

## Portmanteau tools vs full tool list

**Default:** A **small set of portmanteau tools** is registered (knowledge, research, skills, system, external, import/export, plus `help`). This keeps the tool count manageable in clients with limits.

**Full surface:** Set the environment variable **`ADVANCED_MEMORY_FULL_TOOLS_MODE=true`** before starting the server to import and register the **individual** tools (per `advanced_memory/mcp/tools/__init__.py`). Use when you need every atomic tool name exposed.

---

## `CodeMode` and `--agentic`

Starting the MCP with **`--agentic`** applies FastMCP’s **CodeMode** transform so the server exposes a **reduced meta-tool surface** (suited to automated pipelines that expect fewer entry points).

For normal interactive use, start **without** `--agentic` so portmanteau tools stay available as usual.

---

## Rich results: `ToolResult` and **prefabs**

FastMCP lets a tool return structured UI for clients that support it. This repo uses the **`prefab-ui`** package and helpers in **`advanced_memory/mcp/prefabs.py`**:

| Prefab helper | Role |
| :--- | :--- |
| **`NoteViewer`** | Card layout for a note body plus metadata (Markdown + sidebar). |
| **`KnowledgeGraph`** | Mermaid graph from nodes/edges. |
| **`SearchExplorer`** | Grid of search hit cards with actions (used by RAG bridge). |
| **`ZettelCollector`** | Simple capture / zettel UI. |

These return a **`PrefabApp`** built from layout primitives (`Page`, `Grid`, `Card`, `Markdown`, `Mermaid`, `Button`, etc.).

**Example:** `adn_knowledge_rag` (registered from `adn_knowledge_rag.register_rag_bridge`) returns **`mcp.ToolResult`** with both **textual context** (markdown chunks for the model) and **`app=SearchExplorer(...)`** so a capable client can show the explorer prefab alongside the text.

Tools such as **zettelmaker** may attach **`ZettelCollector`**; visualization code paths may use **`KnowledgeGraph`**. Not every MCP client renders prefab apps; fall back to text content where unsupported.

---

## RAG bridge tool

**`register_adn_knowledge_rag(mcp)`** (called from `server.py`) adds **`adn_knowledge_rag`**, which runs **LanceDB-backed** retrieval via `SearchService.knowledge_rag` and can attach **`SearchExplorer`** as above. This is separate from the optional Chroma-based **`adn_rag`** tool described in [AI-FEATURES.md](AI-FEATURES.md).

---

## Optional “Arcade compliance” flattening

If **`ADVANCED_MEMORY_ARCADE_COMPLIANCE=true`**, `tool_registry.register_portmanteau_tool` **duplicates** portmanteau tools into **per-operation shadow tools** (e.g. `adn_knowledge_write`) so strict static scanners see distinct names. Default is off.

---

## Sampling and `Context`

Tools that need the **host LLM** take a FastMCP **`Context`** (often `ctx`) and use **sampling** patterns (e.g. `ctx.sample` with tool lists where supported). See [AI-FEATURES.md](AI-FEATURES.md) for what that means in practice and client requirements.

---

## Prompts and resources

Prompts and MCP resources are registered during server initialization with references kept alive (see `_initialize_prompts_and_resources` in `mcp_instance.py`) so they are not garbage-collected after import.

---

## Upstream documentation

For API details beyond this repo, use the **FastMCP** and **Model Context Protocol** docs for your installed version (3.2+).

---

[Usage](USAGE.md) · [AI features](AI-FEATURES.md) · [README](../README.md)
