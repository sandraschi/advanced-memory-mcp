# Advanced Memory MCP — MCP Server Capabilities

## Server Overview

Advanced Memory MCP (AM) is a comprehensive research and knowledge platform that integrates web search, GitHub code discovery, arXiv academic research, TV Tropes narrative analysis, document ingestion, RAG vector search, knowledge graph management, note taking, audio/voice interaction, and research-driven skill creation. It serves as the fleet's primary knowledge management and research orchestration system, combining automated research pipelines with a structured knowledge base that features bidirectional linking, semantic search, and AI-powered content enrichment.

**Architecture:** AM uses FastMCP 3.2+ with industrial portmanteau tool patterns — related operations are grouped into single tools with an `operation` enum discriminator. This prevents tool explosion while maintaining full discoverability. The server supports dual transport (stdio for Claude Desktop, HTTP for web access) and integrates with Obsidian, Notion, Joplin, Evernote, and OneNote for external note ingestion. It provides a Zettelkästen (Zettel) note-taking system with bidirectional backlinks, voice dictation/speech synthesis, Mermaid diagram generation, skill creation from research, and a knowledge graph visualization engine.

**Key domains:** Knowledge management (graph + RAG + notes with AI enrichment), Research (web/GitHub/arXiv/TV Tropes with multi-source orchestration), Skills (creation/activation/lifecycle with "The Door" staged loading pattern), Audio (dictation/speech/listen with wake word detection), Visualization (knowledge graphs, Mermaid diagrams with multiple layout types), File handling (PDF/HTML/DOCX/ODT with format-aware parsing), and Automation (workflows, batch operations, timer/alarm/music utilities).

**Integration philosophy:** AM is designed as a central knowledge hub that connects to external research sources (arXiv, GitHub, web search APIs), note-taking platforms (Obsidian, Notion, Joplin, Evernote, OneNote), audio subsystems (microphone, speaker, wake word engine), and other fleet MCP servers via the External Bridge. All data flows through a consistent knowledge graph that maintains entity relationships, tags, and semantic embeddings.

## Tool Catalog (portmanteau reference)

Every tool below is one MCP function with an `operation` parameter. Pass the operation
first, then the operation-specific arguments. All tools return structured dicts with
`success` (bool), `message` (str), and operation-specific payload fields.

### Knowledge Management Tools

**adn_knowledge** — Advanced intelligence and analysis for the knowledge base. This is the primary tool for knowledge enrichment, providing AI-powered operations that improve content quality and discoverability. The tool consolidates all intelligence operations into a single entry point with an operation discriminator.

**Operations:** `suggest_tags` (AI tag proposals based on content analysis), `summarize` (AI executive summary generation), `enhance` (quality upgrades with style/context options), `qc` (quality control with runt and junk detection), `canvas` (Obsidian-compatible visual map generation), `analyze` (deep structural analysis of knowledge clusters), `bulk` (batch operations across multiple notes).

**Parameters:** `identifier` (str, optional) — target note title or permalink; `mode` (str, optional) — "find_runts" or "find_junk"; `folder` (str, optional) — target directory; `max_length` (int, optional) — character threshold for runt detection; `update_style` (bool, optional) — apply style improvements; `add_context` (bool, optional) — enrich with context; `expand` (bool, optional) — expand sections; `project` (str, optional) — override project context.

**Analyze sub-types** (`operation="analyze"`, `analysis_type`): `analyze_quality` (grade note quality), `suggest_relationships` (propose links between notes), `find_gaps` (topics the vault covers thinly), `cluster_content` (group related notes), `extract_insights` (distill claims across notes). Pair with `filters` (e.g. `{"topics": [...]}`) and `limit`.

**Bulk sub-operations** (`operation="bulk"`, `bulk_operation`): `tag_analytics` (tag frequency/coverage report), `consolidate_tags` (merge duplicate tags), `tag_maintenance` (rename/prune tags), `bulk_update` (apply one edit across many notes), `validate_content` (frontmatter/link hygiene), `project_stats` (per-project counts), `find_duplicates` (near-duplicate detection), `bulk_move` (relocate notes), `bulk_delete` (remove notes). Use `dry_run=True` first for destructive bulk ops.

**Canvas generation** (`operation="canvas"`): pass `nodes` (file/text/link/group objects), `edges` (connections), `title`, and `folder`. Produces an Obsidian-compatible `.canvas` file for visual maps of note relations.

**Return format:** Operation-specific dicts with `success`, `message`, and domain-specific data.

**adn_notes** — Comprehensive note management providing a unified interface for all primary note operations. Supports writing new notes with YAML frontmatter metadata, reading notes by title or permalink, surgical edits (append, prepend, section replacement, find-replace), deletion, reorganization (move), rapid capture (quick notes), and daily chronological logging.

**Operations:** `write`, `read`, `edit`, `delete`, `move`, `quick`, `daily`

**Parameters:** `identifier` (str, optional); `content` (str, optional); `title` (str, optional); `folder` (str, optional); `tags` (str or list); `mode` (str) — "append", "prepend", "replace_section", "find_replace"; `section` (str) — target header for section edits; `find_text` (str) — target string for find-replace; `destination` (str) — new folder for move; `project` (str, optional).

**Edit-mode guide:** `append`/`prepend` add to the note ends (daily logs, running lists). `replace_section` swaps everything under a `## Header` (status blocks, summaries). `find_replace` swaps one exact string (renames, corrections). Prefer exact titles or permalinks as `identifier`; fuzzy matching is not supported — search first with `adn_search` if unsure.

**adn_search** — Full-text search engine with multiple query modes: text (content search), title (title-only search), permalink (direct permalink lookup), and tag (tag-based filtering). Results are ranked by relevance and include metadata.

**Operations:** `query` (Boolean full-text: AND/OR/NOT, `search_type` text/title/permalink/tag), `rag` (semantic vector retrieval with `prompt` and `limit`), `external` (search across Obsidian/Notion/Joplin/Evernote vaults by `source` + `path`), `reindex` (rebuild indexes, `mode` full/incremental).

**adn_rag_fixed / adn_rag_semantic / adn_rag_sentence** — Three RAG search modes for different use cases. Fixed-window searches chunks of predetermined size. Semantic search uses embedding similarity for meaning-based retrieval. Sentence search operates at the sentence level for fine-grained results.

**adn_knowledge_rag** — Unified RAG interface combining all search modes with additional filtering options. Supports date ranges, folder filters, and tag constraints.

**adn_knowledge_bulk** — Batch intelligence operations enabling AI enrichment across multiple notes in a single call. Supports bulk summarize, tag, enhance, and quality check operations.

### Navigation and Projects

**adn_nav** — Semantic graph traversal and relational discovery. `ls` lists files/folders by `path`. `recent` returns a chronological activity feed (`timeframe` like "7d", `page`/`page_size`). `backlinks` finds every note linking TO an `identifier`. `build_context` walks relations from a `url` (`memory://project/permalink`) to `depth` 1-3 with `max_related` per level — the core "surround this note with context" call. `status` reports graph density; `sync` reports background indexing progress.

**adn_project** — Project lifecycle and active context. `ls` lists registered projects with health. `create` links a `name` to a filesystem `path` (optionally `set_default`). `switch` activates a different project for all subsequent calls. `rm` removes the registration (files on disk are preserved). `status` shows statistics and sync health. `detect` auto-selects the most relevant project. All note/search/knowledge calls accept a `project` override, but switching sets the ambient context.

**Memory-context tools** (secondary surface): `build_context` (assemble identifiers into one context block), `recent` (recent activity), `ls` (list), `backlinks`, `sync` (sync status). Prefer `adn_nav` equivalents for new work.

### Zettelkasten

**adn_zettel** — Atomic slip-box management. `generate` synthesizes a note from `topic` + `category` at `quality` quick/standard/comprehensive/expert (optionally `ai_generate` to bridge template gaps). `suggest` proposes next topics for a category (`count`). `expand` grows a `note_identifier` horizontally to `depth` 1-5. `analyze` scores vault maturity/connectivity (optionally per `category`). `connect` auto-discovers and links semantic relations (optionally anchored at a note). `collect` is low-friction rapid capture. `customize` tunes the generation pipeline (`category`, `topic`, `depth`).

### Research Tools

**adn_arxiv_research** — arXiv academic paper search with configurable sort modes: `relevance` (by search relevance), `lastUpdatedDate` (recently updated), `submittedDate` (recently submitted). Each mode returns paper metadata including title, authors, abstract, categories, and links.

**adn_github_research** — GitHub repository discovery with multiple sort criteria: `stars` (most starred), `forks` (most forked), `updated` (recently updated), `best-match` (relevance-based). Returns repo metadata including description, language, stars, forks, and URL.

**adn_web_search** — Web search with configurable backends: `duckduckgo` (free, no API key), `serpapi` (Google results via SerpAPI), `bing` (Bing Search API), `auto` (best available provider). Returns titles, URLs, and snippets.

**adn_tvtropes_research** — TV Tropes narrative analysis across media categories: `all`, `film`, `literature`, `tv`, `video_games`, `webcomics`, `music`. Each returns tropes with descriptions and example works.

**adn_research** — Orchestrated multi-source research. `web_search` / `arxiv` / `github` run single-source queries. `document_ingest` pulls a file at `path` into the pipeline. `rag_query` grounds a question in the vault. `llm_config` + `llm_generate` (`provider`, `model`, `content`) run model passes over gathered material. `research_orchestrate` runs the full chain (gather → ground → generate) from one `query`. `tvtropes` covers narrative analysis. Use orchestrate for "research X and brief me"; use single-source ops when you need one corpus only.

### Skill Management

**adn_skills** — Full Claude Skills lifecycle management using "The Door" staged loading pattern. Skills are loaded in phases to prevent context flooding: activation loads only the table of contents, then specific sections are loaded on demand. Supports creating skills from research (arXiv, Wikipedia, expert sources, textbooks, text), importing from GitHub repositories, and managing the full lifecycle.

**Operations:** `create`, `read`, `update`, `delete`, `list`, `activate`, `deactivate`, `active`, `load_section`, `load_resource`, `distill_from_arxiv`, `distill_from_wikipedia`, `distill_from_expert`, `distill_from_textbook`, `distill_from_text`, `import_from_github`

**The Door pattern (mandatory for skill use):** 1. `activate` (TOC only — cheap). 2. `load_section` for the one section the task needs. 3. `load_resource` for a bundled script/reference only when executing. Never read whole skills into context. `scope` controls lifespan: message/session/persistent.

**Distillation ops** take `topic` (+ `query`/`category` for arXiv, `expert_name`/`focus_area` for experts, `pdf_path`/`chapters` for textbooks, `text_path` for text, `repository`+`branch` for GitHub) and scaffold a skill directory with references.

### Visualization Tools

**adn_visualize** — Knowledge graph visualization with multiple layout strategies: `point_cloud` (entity clustering based on semantic similarity), `hub_and_spoke` (central entity with connected nodes), `temporal` (time-based evolution showing how entities connect over time).

**generate_mermaid_diagram** — Mermaid.js diagram generation supporting: `flowchart` (process flow), `sequence` (interaction flow), `gantt` (project timeline), `mindmap` (hierarchical ideas), `er` (entity-relationship). Returns rendered diagram code ready for use in documentation.

### System Tools

**adn_system** — Central control plane. `status` (`level` basic/detailed/expert, optional `focus` db/audio/memory) reports environment health. `help` (`topic`, `level`) reads the documentation library. `workflow` runs an autonomous multi-step `goal` (optionally `project`-scoped). `external_bridge` calls a tool on another MCP server (`server`, `tool`, `args`) — the fleet cross-connect path. `sync` reports file-sync engine state. `reindex` (`focus` rag/db/all, `project`) rebuilds indexes.

### Audio Tools

**adn_audio** — Voice and audio management. `dictate` transcribes a live recording (`record_duration` seconds) or a file (`audio_path`) into a note with `tags`. `speak` renders `identifier` (note title or raw text) via Kokoro voices (`voice`, `speed` 0.5-2.0, `volume` 1-10, `save_audio` for WAV output). `listen` records a short window and executes the interpreted voice command. `wake_start`/`wake_stop`/`wake_status` manage the hands-free listener (`wake_word`, `record_duration`). `weather` reports for a `location`. `timer` counts down a `duration` ("5 minutes"). `alarm` fires at `time_str` ("7:00 AM"). `music` controls Plex/Windows Media Player (`command` play/pause/next/previous, `query` artist/song/album; Plex needs PLEX_SERVER_URL + PLEX_TOKEN).

**dictate / speak / listen** — Full audio pipeline. Dictate captures microphone input and transcribes to text. Speak synthesizes text to speech. Listen provides continuous audio monitoring.

**wake_start / wake_stop / wake_status** — Wake word detection lifecycle for hands-free operation. Supports configurable wake words and sensitivity levels.

### Ingestion, Automation, Editor, LLM

**adn_inbox** — Document ingestion pipeline. `status` shows pending files by format (md/docx/html/pdf/txt). `process` converts (Pandoc) and ingests everything pending, or one `file_name`, into the active project. `info` reports Pandoc/pypdf health and inbox paths. `watch` toggles background monitoring.

**adn_automation** — Batch intelligence and autonomous workflows. `batch` applies one `goal` prompt across `items` (note identifiers/URLs). `workflow` executes a high-level `goal` for up to `iterations` steps with an allowed `tools` subset. `status` checks the sampling engine.

**adn_typora** — Bidirectional Typora co-editing. `open` a file by `file_path`. `save`, `get_content`, `set_content` for whole-document ops. `insert` injects `text` at an anchor (`position`, e.g. "current cursor"). `cursor` reports position/selection telemetry. `analyze` reports headings/links/health. `export` renders to `format` pdf/html/docx/odt at `path`.

**adn_llm** — LLM lifecycle across providers (ollama/lmstudio/openai). `list_providers`, `list_models` (`provider`, `base_url`), `select_model` (persist default), `load_model`/`unload_model` (VRAM management for local providers), `status` (active model + health), `health` (all providers). Prefer local providers for bulk enrichment; hosted for quality passes.

### Utility Tools

**timer / alarm / music / weather** — Utility tools for time management and environmental queries.

## Response Envelope and Errors

All tools return structured dicts with `success` boolean, `message` string, and operation-specific data. Knowledge operations validate entity existence before mutation. External API failures include descriptive error messages. The external bridge gracefully handles unreachable servers with timeout protection.

Conventions: `success: false` always pairs with an actionable `message` (what failed + what to try). List operations paginate (`page`/`page_size` or `limit`). Mutations echo the affected identifiers. Destructive bulk operations support `dry_run`. Timeouts are operation-scoped (a slow embedding pass fails that call, not the session).

## Deployment and Transports

**Dual transport.** stdio (Claude Desktop, Cursor, opencode) and streamable HTTP can run side by side. The persistent-state pattern: one HTTP daemon owns the SQLite database and LanceDB index; stdio instances probe the daemon URL and become lightweight proxies when it is alive, standalone servers when it is not. Never run two daemons against one database.

**Bundle entry.** This `.mcpb` runs `run_server.py` via `uv run --directory ${PWD}` with `PYTHONPATH=${PWD}/src`. Data (vault, DB, indexes) lives outside the bundle in the user's projects directory, so reinstalls never touch notes.

**Environment.** `ADVANCED_MEMORY_HTTP_PROXY` overrides the daemon probe URL (default `http://127.0.0.1:10732/mcp`). `AM_VAULT_PATH` / `AM_PROJECTS_DIR` set storage roots. `AM_LOG_LEVEL` controls verbosity. On Windows services, pin `USERPROFILE` (and `ADVANCED_MEMORY_HOME`) on the service account — an unpinned LocalSystem service silently serves a phantom vault that looks empty.

## Configuration

| Variable | Purpose | Default |
|----------|---------|---------|
| `AM_PROJECTS_DIR` | Projects storage directory | `./projects` |
| `AM_VAULT_PATH` | Obsidian vault path | `./vault` |
| `AM_EMBEDDING_MODEL` | Embedding model name | `all-MiniLM-L6-v2` |
| `AM_LOG_LEVEL` | Logging verbosity | `INFO` |
| `ADVANCED_MEMORY_HTTP_PROXY` | Daemon probe URL for stdio clients | `http://127.0.0.1:10732/mcp` |

## Data Sources

- **Obsidian vault**: Primary markdown note storage with YAML frontmatter
- **SQLite databases**: Knowledge graph (entities, relations, tags), search index (FTS5), skill registry
- **LanceDB**: Vector embeddings for semantic RAG search
- **External APIs**: arXiv, GitHub, DuckDuckGo/SerpAPI/Bing, TV Tropes

## Integration Points

- **External MCP Bridge**: Cross-server tool invocation
- **Obsidian Sync**: Bidirectional vault synchronization with change tracking
- **Claude Skills**: Full lifecycle with staged loading

## Troubleshooting (operator level)

**Empty vault / phantom data.** The service account lacks pinned `USERPROFILE`/`ADVANCED_MEMORY_HOME` and is serving a different home directory. Pin both, restart the service, verify the vault path in project status.

**Search finds nothing but notes exist.** The FTS/vector index is stale or partially built (interrupted scan or reindex). Run a full reindex and wait for idle; compare entity totals with a wildcard search before trusting counts. Recent-activity feeds read the index, not the entity table, so they under-report first.

**Two processes, one log file.** API and daemon must never share a rotating log sink on Windows (rename collides). This bundle uses per-process log files; if `PermissionError WinError 32` appears on rotation, two processes are sharing a sink path.

**External provider failures.** Web/arxiv/github calls fail with descriptive messages (rate limits, missing API keys for serpapi/bing, network). `duckduckgo` needs no key and is the default fallback. Reduce `max_results`/frequency on 429s.

## Error Handling

All tools return structured dicts with `success` boolean, `message` string, and operation-specific data. Knowledge operations validate entity existence before mutation. External API failures include descriptive error messages. The external bridge gracefully handles unreachable servers with timeout protection.

## Worked Request/Response Examples

**Write then enrich a note.**
Request `adn_notes(operation="write", title="Vector DBs", content="# Vector DBs\n\nLanceDB stores embeddings.", folder="research", tags=["rag", "vectors"])` returns `{"success": true, "message": "Note created", "identifier": "Vector DBs", "permalink": "research/vector-dbs"}`. Follow with `adn_knowledge(operation="suggest_tags", identifier="research/vector-dbs")` which returns `{"success": true, "tags": ["rag", "vectors", "lancedb", "embeddings"]}`. Apply with `adn_notes(operation="edit", identifier="research/vector-dbs", mode="append", content="\nTags: rag, vectors, lancedb")`.

**Grounded question answering.**
Request `adn_research(operation="rag_query", query="How do I rebuild a stale index?", limit=5)` returns ranked chunks with permalinks. Feed the top chunks into `adn_research(operation="llm_generate", provider="ollama", model="llama3:8b", content="Question: ... Context: ...")` for a grounded answer with citations back to vault notes.

**Multi-hop context assembly.**
`adn_nav(operation="backlinks", identifier="Transformers")` returns every note linking to it. `adn_nav(operation="build_context", url="memory://main/transformers", depth=2, max_related=10)` returns the assembled context block (note bodies plus relation edges), ready to paste into a prompt or hand to `llm_generate`.

**Batch with safety.**
`adn_knowledge(operation="bulk", bulk_operation="consolidate_tags", dry_run=True)` returns the merge plan (which tags fold into which, affected note counts). Re-run with `dry_run=False` to execute. The same pattern applies to `bulk_move`, `bulk_delete`, and `bulk_update`: plan first, execute second, verify with `project_stats`.

**Skill from research to activation.**
`adn_skills(operation="distill_from_arxiv", topic="Sparse attention", query="sparse attention", max_papers=5, category="research")` scaffolds `skills/sparse-attention/SKILL.md` plus references. `adn_skills(operation="activate", identifier="sparse-attention", scope="session")` loads only the table of contents. `adn_skills(operation="load_section", identifier="sparse-attention", section="When to use")` pulls one section. `adn_skills(operation="deactivate", identifier="sparse-attention")` unloads.

## Project Configuration Reference

Projects bind a short `name` to an absolute vault `path` plus sync flags. `adn_project(operation="create", name="phd", path="D:/vaults/phd")` registers; `switch` changes ambient context for all subsequent calls; per-call `project=` overrides without switching. `status` reports entity/observation/relation counts, index health, and watcher state per project. `detect` picks the project whose path best matches the current working context. `rm` unregisters (disk files untouched). Keep one project per vault; never point two projects at the same folder (index collisions).

## Watch Service Semantics

The watcher follows disk changes into the database: created files import, modified files re-index, deleted files mark entities stale (configurable purge). `adn_system(operation="sync")` and `adn_nav(operation="sync")` report queue depth and last-cycle stats. Large initial imports run as background scans with progress; do not restart the daemon mid-scan. If disk and index disagree, a full reindex (not a restart) is the repair. The watcher ignores hidden directories, temp files, and editor swap files by pattern.

## Checkpoint and Snapshot Model

Snapshots freeze entity/observation/relation state with a label and timestamp. Rollback restores a snapshot after taking an automatic pre-rollback backup, so no restore is destructive. Use snapshots before bulk operations, reindex runs on production vaults, and distillation passes that rewrite many notes. Verify rollback by reading a known note before and after; keep snapshot labels descriptive (`pre-tag-consolidation-2026-09` beats `snap1`).

## Sampling and Autonomous Operation

Several tools (`adn_automation workflow`, skill research chains, `adn_system workflow`) reason over multiple steps using the host's sampling capability: the server asks the client model for the next action, executes tool calls, and loops until the goal is met or `iterations` exhaust. Keep goals narrow ("summarize notes tagged X and file under Y") rather than open-ended. Constrain `tools` to the minimum set the workflow needs — a research goal does not need delete operations. `status` on the automation tool reports engine health before launching long runs. Batch operations are not autonomous: `batch` applies one fixed instruction per item with no branching, which makes it predictable and safe for large lists. When a workflow stalls, inspect intermediate notes it wrote (workflows log progress to the vault) rather than re-running blindly; re-runs duplicate partial work.

## Versioning and Compatibility

The bundle manifest pins a version matching the source package. Tool names are stable across minor versions; new operations appear as additional enum values, never as renamed tools, so saved prompts keep working. Deprecated operations answer with a migration message pointing at the replacement. The response envelope (`success`/`message`/payload) is versioned separately from tools and changes only on major versions. When upgrading the bundle, reindex once: schema migrations for the search index ship with the package and apply on first run.
