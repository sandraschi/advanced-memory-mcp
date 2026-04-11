# AI features (RAG, agentic mode, sampling)

Short reference for how this repo uses retrieval, automation-oriented tool shapes, and MCP sampling. For setup, see [Installation](INSTALLATION.md) and [Usage](USAGE.md).

---

## Semantic search and embeddings (main app)

Most day‑to‑day “find related notes” behavior uses:

- **SQLite + FTS5** for keyword / structured search (`SearchService` / search index).
- **LanceDB** with **fastembed** embeddings in **`VectorRepository`** for semantic (vector) search over indexed content.

That path is what backs typical vault search and the webapp’s semantic search API. Content has to be **indexed** (ingestion / normal entity indexing) before vectors are meaningful—empty vaults do not magically retrieve well.

---

## The `adn_rag` tool vs the core vector store

The MCP tool **`adn_rag`** drives a **separate optional stack** in `advanced_memory.rag.system`: **ChromaDB** + **sentence-transformers**, only if those optional dependencies are installed (`get_rag_system()` returns `None` otherwise). It is aimed at ingest/query of documents into that optional store (chunking, `query_knowledge`, etc.).

So in practice you have:

| Area | Role |
| :--- | :--- |
| LanceDB / fastembed | Primary semantic layer for normal Advanced Memory entities and web search |
| Chroma-based `adn_rag` | Optional MCP tool path for document-centric RAG when extras are installed |

Do not assume both layers share the same index unless you have wired workflows that way.

---

## “Agentic” in two different senses

**1. CLI flag `--agentic` on `advanced-memory mcp`**

FastMCP **CodeMode** is applied: many tools are collapsed into a small **meta‑tool** surface so automated agents see fewer entry points. For interactive daily use, run **without** `--agentic` so the full portmanteau tools stay visible.

**2. Tools named like “agentic … workflow”**

Some tools orchestrate multi‑step work inside the server (for example workflows in `inter_server_tools_new.py` that are built around **sampling** and optional tool lists). They are optional power features, not required for basic note taking or search.

---

## MCP sampling (host LLM inside server tools)

**Sampling** (see MCP / FastMCP docs) means: a tool running **inside the MCP server** can ask the **connected client** to run a **language model** call (e.g. via FastMCP **`Context`** and patterns like **`ctx.sample(...)`**), instead of bundling a model inside the server.

- **Requires** a client (or host) that implements **sampling**; not all MCP clients do.
- **Use case:** multi‑step flows where the server should steer prompts or validate steps using the same model the user already has in the IDE.

Older helper code in `advanced_memory.mcp.sampling` is a **stub**; current guidance in-tree points at **`Context` on tools** and the inter‑server / skill tooling rather than a separate global sampling client.

---

## Practical tips

- **Better retrieval:** clear titles, consistent tags, and ingest or index material before expecting strong semantic hits.
- **RAG overload:** If you only need “search my vault,” use normal search / semantic search tools; add **`adn_rag`**-style Chroma workflows only when you need that document store.
- **Sampling:** If a tool returns errors about sampling not being available, check whether your MCP client supports sampling and whether you are on a recent FastMCP stack.

---

[Usage](USAGE.md) · [Architecture](ARCHITECTURE.md) · [README](../README.md)
