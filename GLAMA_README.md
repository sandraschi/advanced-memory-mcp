# Advanced Memory MCP - Research-Driven Knowledge Platform

**Transform any AI assistant into a research powerhouse** with multi-source intelligence gathering, academic literature access, code analysis, and intelligent skill creation.

[![License: AGPL v3](https://img.shields.io/badge/License-AGPL_v3-blue.svg)](https://www.gnu.org/licenses/agpl-3.0)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Tests](https://img.shields.io/badge/tests-1244%20passing-brightgreen)](https://github.com/sandraschi/advanced-memory-mcp/actions)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
![MCP Server](https://badge.mcpx.dev?type=server 'MCP Server')

## 🎯 Overview

Advanced Memory MCP provides unified research and knowledge management via MCP, enabling AI assistants to perform comprehensive multi-source intelligence gathering and intelligent skill creation.

### Key Features

* **Multi-Source Research**: Web search, academic papers (arXiv), code repositories (GitHub), narrative patterns (TV Tropes)
* **Document Processing**: PDF/EPUB ingestion with RAG vector search for large document analysis
* **Skill Creation**: Research-driven expert skill generation using FastMCP 2.14.3 sampling
* **Knowledge Management**: Zettelkasten-based note system with Claude Skills export/import
* **Cross-Platform**: Compatible with Claude Desktop, Cursor IDE, Windsurf, and other MCP clients
* **Portmanteau Tools**: Clean 10-tool interface for Cursor IDE compatibility

## 📚 Documentation

* [**Research Guide**](docs/RESEARCH_DRIVEN_SKILLS.md) - Complete research ecosystem usage
* [**API Reference**](docs/PORTMANTEAU_TOOLS_REFERENCE.md) - All MCP tools and parameters
* [**Architecture Deep Dive**](docs/ARCHITECTURE_DEEP_DIVE.md) - System design and data flow
* [**Claude Skills Integration**](docs/user-guide/claude-skills.md) - Skills export/import guide
* [**Installation Guide**](INSTALLATION.md) - Setup for all MCP clients
* [**Troubleshooting**](docs/TROUBLESHOOTING_GUIDE.md) - Common issues and solutions

## 🔍 Research Capabilities

### Web Intelligence
* **Multi-Provider Search**: DuckDuckGo (free), SerpApi (Google), Bing Web Search
* **Time-Based Filtering**: Research from hours to years ago
* **Domain Filtering**: Focus on authoritative sources (nih.gov, cancer.gov, etc.)
* **Relevance Scoring**: Automated quality assessment

### Academic Research
* **arXiv Integration**: Preprint search and analysis across scientific fields
* **Category-Specific**: cs.AI, math.PR, physics.optics, and more
* **Citation Analysis**: Research network and trend identification
* **Paper Metadata**: Abstracts, authors, publication details

### Code Intelligence
* **GitHub Repository Analysis**: Code search and implementation patterns
* **Language Filtering**: Focus on specific programming languages
* **Recent Activity**: Commit tracking and issue analysis
* **Repository Structure**: Code organization insights

### Narrative Intelligence
* **TV Tropes Analysis**: Character archetypes and storytelling patterns
* **Creative Writing**: Plot structure and genre conventions
* **⚠️ Ethical Compliance**: Full adherence to TV Tropes terms of service

### Document Processing
* **Multi-Format Support**: PDF, EPUB, text files, Markdown
* **RAG Vector Search**: Semantic similarity with ChromaDB
* **Large Document Analysis**: Beyond LLM context limits
* **Quote Extraction**: Primary source integration

### Skill Creation
* **Research-Driven Generation**: Multi-source intelligence synthesis
* **FastMCP 2.14.3 Sampling**: Direct LLM interrogation
* **Academic Rigor**: Peer-reviewed content integration
* **Claude Skills Format**: Bidirectional export/import

## 🚀 Quick Start

### Installation

```bash
# Install the package
pip install advanced-memory-mcp

# Or install from source
git clone https://github.com/sandraschi/advanced-memory-mcp.git
cd advanced-memory-mcp
pip install -e ".[dev]"
```

### Configuration

Create configuration at `~/.advanced-memory/config.yaml`:

```yaml
advanced_memory:
  home: "~/.advanced-memory"
  database: "memory.db"
  log_level: "INFO"

research:
  web_search:
    default_provider: "duckduckgo"
    serpapi_key: ""  # Optional for Google search
    bing_key: ""     # Optional for Bing search
  github:
    token: ""        # Optional for higher rate limits
  arxiv:
    max_results: 50

skills:
  export_path: "~/claude-skills"
  import_path: "~/anthropic-skills"
```

### Running the Server

#### MCP Protocol (stdio)
```bash
# Direct execution
python -m advanced_memory.mcp.server

# With custom config
python -m advanced_memory.mcp.server --config ~/.advanced-memory/config.yaml
```

#### Claude Desktop Configuration
Add to `claude_desktop_config.json`:
```json
{
  "mcpServers": {
    "advanced-memory": {
      "command": "python",
      "args": ["-m", "advanced_memory.mcp.server"]
    }
  }
}
```

#### Cursor IDE (Portmanteau Mode)
```json
{
  "mcpServers": {
    "advanced-memory": {
      "command": "python",
      "args": ["-m", "advanced_memory.mcp.server"],
      "env": {
        "ADVANCED_MEMORY_PORTMANTEAU_ONLY": "true"
      }
    }
  }
}
```

## 🛠️ Core Tools

### Research Suite (8 tools)
* `adn_web_search` - Multi-provider web search with filtering
* `adn_github_research` - Code repository analysis and search
* `adn_arxiv_research` - Academic paper search and analysis
* `adn_tvtropes_research` - Narrative patterns and creative writing
* `adn_document_ingest` - Document processing and chunking
* `adn_rag` - Vector search and knowledge retrieval
* `make_skill_advanced` - Research-driven skill creation
* `help` - Documentation access

### Content Management (3 tools)
* `adn_content` - Write, read, edit, move, delete notes
* `adn_project` - Project creation, switching, management
* `adn_search` - Full-text search across all content

### Advanced Features (4 tools)
* `adn_export` - Multi-format export (PDF, HTML, Skills, etc.)
* `adn_import` - Import from Obsidian, Notion, Joplin, Skills
* `adn_knowledge` - Analytics, bulk operations, validation
* `adn_navigation` - Context building, recent activity, exploration

## 🛠️ Usage Examples

### Research & Skill Creation
```python
# Create expert skill from current research
await make_skill_advanced({
    "topic": "glioblastoma treatment expert",
    "enable_web_search": True,
    "web_search_provider": "auto",
    "include_academic": True,
    "academic_categories": ["q-bio.NC", "q-bio.BM"]
})

# Multi-source research for conspiracy analysis
await adn_web_search("qanon origins 2024", {
    provider: "auto",
    time_filter: "year",
    sources_filter: ["snopes.com", "factcheck.org"]
})
```

### Document Analysis
```python
# Ingest research paper for analysis
await adn_document_ingest("research_paper.pdf", {
    "chunk_strategy": "semantic",
    "embedding_model": "sentence-transformers"
})

# Semantic search across documents
await adn_rag("search", {
    query: "machine learning bias",
    similarity_threshold: 0.8
})
```

### Claude Skills Integration
```python
# Export knowledge as skills
await adn_export("claude_skills", {
    export_path: "~/claude-skills/",
    source_folder: "medical-research"
})

# Import community skills
await adn_import("claude_skills", {
    source_path: "~/anthropic-skills/",
    destination_folder: "imported-skills"
})
```

## 📁 Project Structure

```
advanced-memory-mcp/
├── src/advanced_memory/
│   ├── mcp/
│   │   ├── server.py          # Main FastMCP server
│   │   └── tools/             # MCP tool implementations
│   │       ├── research/      # Research tools (web, arxiv, github)
│   │       ├── content/       # Content management tools
│   │       └── skills/        # Skill creation and management
│   ├── services/
│   │   ├── research/          # Research service implementations
│   │   ├── rag/              # Vector search and document processing
│   │   └── skill_creator/     # Skill generation logic
│   ├── models/                # SQLAlchemy ORM models
│   └── schemas/               # Pydantic validation schemas
├── docs/
│   ├── RESEARCH_DRIVEN_SKILLS.md
│   ├── PORTMANTEAU_TOOLS_REFERENCE.md
│   ├── ARCHITECTURE_DEEP_DIVE.md
│   └── user-guide/            # User documentation
├── tests/
│   ├── unit/                  # Unit tests
│   ├── integration/           # Integration tests
│   └── fixtures/              # Test data and fixtures
├── scripts/
│   └── testing/               # Test automation scripts
└── mcpb/                      # MCPB packaging configuration
```

## 🧪 Testing

### Run All Tests
```bash
# Unit and integration tests
pytest

# With coverage report
pytest --cov=advanced_memory --cov-report=html

# Specific test categories
pytest tests/unit/              # Unit tests only
pytest tests/integration/       # Integration tests only
```

### Tool Exerciser Suite
```powershell
# PowerShell test runner (Windows)
.\scripts\testing\run-all-tool-exercisers.ps1

# Individual exercisers
.\scripts\testing\adn-research-tools-exerciser.ps1
.\scripts\testing\adn-core-tools-exerciser.ps1
```

### Quality Checks
```bash
# Code formatting and linting
ruff check .
ruff format .

# Type checking
mypy src/

# All quality checks
just check  # if just is available
```

## 🔧 Development

### Code Quality
```bash
# Format code
ruff format src/ tests/

# Lint code
ruff check src/ tests/

# Type checking
mypy src/

# Run tests
pytest
```

### Project Structure
- **MCP Server**: `src/advanced_memory/mcp/` - FastMCP implementation
- **Core Services**: `src/advanced_memory/services/` - Business logic
- **Database Models**: `src/advanced_memory/models/` - SQLAlchemy ORM
- **API Schemas**: `src/advanced_memory/schemas/` - Pydantic models

### Architecture
- **Unified Database**: Single SQLite database with project isolation
- **Portmanteau Tools**: 10 consolidated tools for Cursor IDE compatibility
- **Research Pipeline**: Multi-source intelligence aggregation
- **Skill Generation**: FastMCP 2.14.3 sampling for expert creation

## 🤝 Contributing

Contributions welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## 📄 License

AGPL-3.0-or-later - see [LICENSE](LICENSE) for details.

## 🙏 Acknowledgments

Built with inspiration from:
- [Anthropic Claude Skills](https://github.com/anthropics/anthropic-skills) - Agent skills framework
- [Zettelkasten Method](https://zettelkasten.de/) - Knowledge management methodology
- [Model Context Protocol](https://modelcontextprotocol.io/) - LLM integration standard
- [FastMCP](https://github.com/jlowin/fastmcp) - High-performance MCP framework

---

**Advanced Memory MCP** - Research-Driven Knowledge Platform for AI Assistants
