# AI features (RAG, agentic mode, sampling)

Short reference for how this repo uses retrieval, automation-oriented tool shapes, and MCP sampling. For **FastMCP 3.2+** specifics (portmanteaus, prefabs, `--agentic`, transports), see [FASTMCP.md](FASTMCP.md). For setup, see [Installation](INSTALLATION.md) and [Usage](USAGE.md).

---

## Semantic search and embeddings (main app)

Most day‑to‑day “find related notes” behavior uses:

- **SQLite + FTS5** for keyword / structured search (`SearchService` / search index).
- **LanceDB** with **fastembed** embeddings in **`VectorRepository`** for semantic (vector) search over indexed content.

That path is what backs typical vault search and the webapp’s semantic search API. Content has to be **indexed** (ingestion / normal entity indexing) before vectors are meaningful—empty vaults do not magically retrieve well.

### Where LanceDB is stored

The running code opens LanceDB at:

**`{parent directory of the app SQLite DB}/vectors`**

`AdvancedMemoryConfig.app_database_path` defaults to **`%USERPROFILE%\.advanced-memory\memory.db`** (unless `ADVANCED_MEMORY_HOME` moves the `.advanced-memory` layout). So the usual vector directory is **`%USERPROFILE%\.advanced-memory\vectors`** — alongside `memory.db`, **not** inside your `advanced-memory-mcp` git clone.

- **One store per install:** all vault **projects** share this LanceDB directory; rows carry **`metadata.project_id`** (and optional **global extra-root** rows from **`rag_extra_roots`**).
- **`rag_persist_dir` / `RAG_PERSIST_DIR`:** present in config for historical / env reasons; **`VectorRepository` does not use this field for its path** (the implementation hard-wires the `vectors` sibling path — see `src/advanced_memory/deps.py`).

### Extra RAG folders (`rag_extra_roots`)

From **1.8.1**, global config may list additional **absolute** directories on the machine running the API. Their `.md` / `.mdx` / `.txt` files are chunked into LanceDB when you run a **full Rebuild search index** (webapp **Vault sync** or `POST .../search/reindex`). Use the management API **`/api/v1/management/rag-extra-roots`** to read or replace the list.

**Other documentation products** (for example a separate **mcp-central-docs** checkout with its own RAG stack) keep **their own** LanceDB path by default (`src/docs_mcp/data/lancedb` in that repo). Advanced Memory does **not** automatically share or merge with those stores.

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
