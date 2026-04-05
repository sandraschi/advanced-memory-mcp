# Features Overview

Advanced Memory (Memops) provides a reliable memory substrate for AI assistants, focusing on local-first note management, semantic search (RAG), and universal data portability.

## Memory Management

### Zettelkasten Note System
Atomic note-based knowledge management system:

- **Note Linking**: Bidirectional relationships between concepts.
- **Metadata Management**: Frontmatter-based note classification.
- **Project Isolation**: Multi-project support with data separation.
- **Search Capabilities**: Full-text search with filtering and pagination.

### Data Portability (I/O)
Universal connectivity with existing knowledge tools:

- **Imports**: Native support for Obsidian, Joplin, and Notion (via Markdown/CSV).
- **Exports**: Professional-grade conversion to PDF, DOCX, and EPUB via Pandoc.
- **Claude Skills Sync**: Bidirectional synchronization with IDE skills folders.

## Semantic Intelligence (RAG)

### RAG Engine
High-performance local vector search for large-scale knowledge retrieval:

- **Vector Storage**: LanceDB for efficient, local-first vector management.
- **Embedding Generation**: FastEmbed (BAAI/bge-small-en-v1.5) for local processing.
- **Hybrid Retrieval**: Combined FTS5 keyword and semantic similarity search.
- **Document Processing**: PDF, EPUB, and Markdown ingestion with automated indexing.

## [BETA] Research & Visualization

### Research Tools (BETA)
Experimental multi-source gathering from external providers:

- **Web Search**: Integration with DuckDuckGo and Google (SerpApi).
- **Academic Papers**: Retrieval from the arXiv preprint database.
- **GitHub Analysis**: Repository scanning and implementation pattern discovery.

### Skill Synthesis (BETA)
Automated expert skill generation from research data:

- **FastMCP Sampling**: Direct LLM interrogation for structured knowledge synthesis.
- **Citation Tracking**: Automated source attribution for generated skills.

### Visualization (BETA)
Graphical representations of knowledge structures:

- **Point Cloud Engine**: Particle-based 3D graph view for relationship mapping.
- **Mermaid Mapping**: Dynamic generation of flowcharts and entity diagrams.

## Platform Infrastructure

### MCP Implementation
Optimized Model Context Protocol server:

- **FastMCP 3.1+**: Support for Prefab UI and latest protocol standards.
- **Portmanteau Tools**: Consolidated toolset for improved LLM efficiency.
- **Monitoring**: Real-time resource tracking and operation auditing.

### Web Interface
Standalone React application for managing knowledge without an MCP client.
- **Dark Theme**: Professional high-fidelity UI with glassmorphism.
- **Responsive Design**: Optimized for desktop and tablet usage.
