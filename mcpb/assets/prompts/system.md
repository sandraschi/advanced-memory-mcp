# Advanced Memory MCP — MCP Server Capabilities

## Server Overview

Advanced Memory MCP (AM) is a comprehensive research and knowledge platform that integrates web search, GitHub code discovery, arXiv academic research, TV Tropes narrative analysis, document ingestion, RAG vector search, knowledge graph management, note taking, audio/voice interaction, and research-driven skill creation. It serves as the fleet's primary knowledge management and research orchestration system, combining automated research pipelines with a structured knowledge base that features bidirectional linking, semantic search, and AI-powered content enrichment.

**Architecture:** AM uses FastMCP 3.2+ with industrial portmanteau tool patterns — related operations are grouped into single tools with an `operation` enum discriminator. This prevents tool explosion while maintaining full discoverability. The server supports dual transport (stdio for Claude Desktop, HTTP for web access) and integrates with Obsidian, Notion, Joplin, Evernote, and OneNote for external note ingestion. It provides a Zettelkästen (Zettel) note-taking system with bidirectional backlinks, voice dictation/speech synthesis, Mermaid diagram generation, skill creation from research, and a knowledge graph visualization engine.

**Key domains:** Knowledge management (graph + RAG + notes with AI enrichment), Research (web/GitHub/arXiv/TV Tropes with multi-source orchestration), Skills (creation/activation/lifecycle with "The Door" staged loading pattern), Audio (dictation/speech/listen with wake word detection), Visualization (knowledge graphs, Mermaid diagrams with multiple layout types), File handling (PDF/HTML/DOCX/ODT with format-aware parsing), and Automation (workflows, batch operations, timer/alarm/music utilities).

**Integration philosophy:** AM is designed as a central knowledge hub that connects to external research sources (arXiv, GitHub, web search APIs), note-taking platforms (Obsidian, Notion, Joplin, Evernote, OneNote), audio subsystems (microphone, speaker, wake word engine), and other fleet MCP servers via the External Bridge. All data flows through a consistent knowledge graph that maintains entity relationships, tags, and semantic embeddings.

## Tools

### Knowledge Management Tools

**adn_knowledge** — Advanced intelligence and analysis for the knowledge base. This is the primary tool for knowledge enrichment, providing AI-powered operations that improve content quality and discoverability. The tool consolidates all intelligence operations into a single entry point with an operation discriminator.

**Operations:** `suggest_tags` (AI tag proposals based on content analysis), `summarize` (AI executive summary generation), `enhance` (quality upgrades with style/context options), `qc` (quality control with runt and junk detection), `canvas` (Obsidian-compatible visual map generation), `analyze` (deep structural analysis of knowledge clusters), `bulk` (batch operations across multiple notes).

**Parameters:** `identifier` (str, optional) — target note title or permalink; `mode` (str, optional) — "find_runts" or "find_junk"; `folder` (str, optional) — target directory; `max_length` (int, optional) — character threshold for runt detection; `update_style` (bool, optional) — apply style improvements; `add_context` (bool, optional) — enrich with context; `expand` (bool, optional) — expand sections; `project` (str, optional) — override project context.

**Return format:** Operation-specific dicts with `success`, `message`, and domain-specific data.

**adn_notes** — Comprehensive note management providing a unified interface for all primary note operations. Supports writing new notes with YAML frontmatter metadata, reading notes by title or permalink, surgical edits (append, prepend, section replacement, find-replace), deletion, reorganization (move), rapid capture (quick notes), and daily chronological logging.

**Operations:** `write`, `read`, `edit`, `delete`, `move`, `quick`, `daily`

**Parameters:** `identifier` (str, optional); `content` (str, optional); `title` (str, optional); `folder` (str, optional); `tags` (str or list); `mode` (str) — "append", "prepend", "replace_section", "find_replace"; `section` (str) — target header for section edits; `find_text` (str) — target string for find-replace; `destination` (str) — new folder for move; `project` (str, optional).

**adn_search** — Full-text search engine with multiple query modes: text (content search), title (title-only search), permalink (direct permalink lookup), and tag (tag-based filtering). Results are ranked by relevance and include metadata.

**adn_rag_fixed / adn_rag_semantic / adn_rag_sentence** — Three RAG search modes for different use cases. Fixed-window searches chunks of predetermined size. Semantic search uses embedding similarity for meaning-based retrieval. Sentence search operates at the sentence level for fine-grained results.

**adn_knowledge_rag** — Unified RAG interface combining all search modes with additional filtering options. Supports date ranges, folder filters, and tag constraints.

**adn_knowledge_bulk** — Batch intelligence operations enabling AI enrichment across multiple notes in a single call. Supports bulk summarize, tag, enhance, and quality check operations.

### Research Tools

**adn_arxiv_research** — arXiv academic paper search with configurable sort modes: `relevance` (by search relevance), `lastUpdatedDate` (recently updated), `submittedDate` (recently submitted). Each mode returns paper metadata including title, authors, abstract, categories, and links.

**adn_github_research** — GitHub repository discovery with multiple sort criteria: `stars` (most starred), `forks` (most forked), `updated` (recently updated), `best-match` (relevance-based). Returns repo metadata including description, language, stars, forks, and URL.

**adn_web_search** — Web search with configurable backends: `duckduckgo` (free, no API key), `serpapi` (Google results via SerpAPI), `bing` (Bing Search API), `auto` (best available provider). Returns titles, URLs, and snippets.

**adn_tvtropes_research** — TV Tropes narrative analysis across media categories: `all`, `film`, `literature`, `tv`, `video_games`, `webcomics`, `music`. Each returns tropes with descriptions and example works.

### Skill Management

**adn_skills** — Full Claude Skills lifecycle management using "The Door" staged loading pattern. Skills are loaded in phases to prevent context flooding: activation loads only the table of contents, then specific sections are loaded on demand. Supports creating skills from research (arXiv, Wikipedia, expert sources, textbooks, text), importing from GitHub repositories, and managing the full lifecycle.

**Operations:** `create`, `read`, `update`, `delete`, `list`, `activate`, `deactivate`, `active`, `load_section`, `load_resource`, `distill_from_arxiv`, `distill_from_wikipedia`, `distill_from_expert`, `distill_from_textbook`, `distill_from_text`, `import_from_github`

### Visualization Tools

**adn_visualize** — Knowledge graph visualization with multiple layout strategies: `point_cloud` (entity clustering based on semantic similarity), `hub_and_spoke` (central entity with connected nodes), `temporal` (time-based evolution showing how entities connect over time).

**generate_mermaid_diagram** — Mermaid.js diagram generation supporting: `flowchart` (process flow), `sequence` (interaction flow), `gantt` (project timeline), `mindmap` (hierarchical ideas), `er` (entity-relationship). Returns rendered diagram code ready for use in documentation.

### System Tools

**adn_system** — Central control plane providing status reporting (basic/detailed/expert levels), documentation access, autonomous workflow execution, external MCP bridge for calling tools on other servers, and sync status monitoring.

### Audio Tools

**dictate / speak / listen** — Full audio pipeline. Dictate captures microphone input and transcribes to text. Speak synthesizes text to speech. Listen provides continuous audio monitoring.

**wake_start / wake_stop / wake_status** — Wake word detection lifecycle for hands-free operation. Supports configurable wake words and sensitivity levels.

### Utility Tools

**timer / alarm / music / weather** — Utility tools for time management and environmental queries.

## Configuration

| Variable | Purpose | Default |
|----------|---------|---------|
| `AM_PROJECTS_DIR` | Projects storage directory | `./projects` |
| `AM_VAULT_PATH` | Obsidian vault path | `./vault` |
| `AM_EMBEDDING_MODEL` | Embedding model name | `all-MiniLM-L6-v2` |
| `AM_LOG_LEVEL` | Logging verbosity | `INFO` |

## Data Sources

- **Obsidian vault**: Primary markdown note storage with YAML frontmatter
- **SQLite databases**: Knowledge graph (entities, relations, tags), search index (FTS5), skill registry
- **LanceDB**: Vector embeddings for semantic RAG search
- **External APIs**: arXiv, GitHub, DuckDuckGo/SerpAPI/Bing, TV Tropes

## Integration Points

- **External MCP Bridge**: Cross-server tool invocation
- **Obsidian Sync**: Bidirectional vault synchronization with change tracking
- **Claude Skills**: Full lifecycle with staged loading

## Error Handling

All tools return structured dicts with `success` boolean, `message` string, and operation-specific data. Knowledge operations validate entity existence before mutation. External API failures include descriptive error messages. The external bridge gracefully handles unreachable servers with timeout protection.
