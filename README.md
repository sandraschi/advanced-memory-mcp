[![License: AGPL v3](https://img.shields.io/badge/License-AGPL_v3-blue.svg)](https://www.gnu.org/licenses/agpl-3.0)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Tests](https://img.shields.io/badge/tests-1113%20passing-brightgreen)](https://github.com/sandraschi/advanced-memory-mcp/actions)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
![MCP Server](https://badge.mcpx.dev?type=server 'MCP Server')

# Advanced Memory MCP

> **The ONLY knowledge management system with native Claude Skills integration**

Transform your knowledge into AI skills. Advanced Memory combines powerful knowledge graphs with Anthropic's Claude Skills, making your zettelkasten notes discoverable and usable by Claude Desktop.

**NEW in v1.0.0b3**: 🎯 Export your 87+ zettelkasten templates as Claude Skills!

[Quick Start](#-quick-start) | [Documentation](docs/) | [Claude Skills Integration](docs/user-guide/claude-skills.md)

---

## 🌟 What Makes This Special

### 1. 🎯 **Claude Skills Integration** (First of its Kind!)

```python
# Export your knowledge as Claude Skills
adn_export("claude_skills", export_path="~/claude-skills/")

# Claude Desktop discovers your notes as agent skills
# Your team's best practices → Claude's guidance!
```

**Why this matters**: Claude can now access your knowledge as **procedural skills**, not just passive storage. Your documented workflows become Claude's operational guides.

### 2. 📚 **87+ Curated Zettelkasten Templates**

Get a production-ready knowledge base from day one:
- **Developer**: Python, Git, Docker, CI/CD, Clean Code (30+ templates)
- **DevOps**: Kubernetes, Infrastructure as Code, Observability (15+ templates)
- **Data Scientist**: ML, MLOps, Python for Data Science (10+ templates)
- **Researcher**: Research Methods, Literature Review, Critical Thinking (12+ templates)
- **Product Manager**: Strategy, Analytics, Metrics (8+ templates)
- **Plus**: Entrepreneur, Creative, Writer, UX Designer, Knowledge Worker, AI, Philosophy

### 3. 🎯 **Cursor IDE Compatible**

**Problem**: Most MCPs have 40+ tools → breaks Cursor's 50-tool limit  
**Solution**: 10 portmanteau tools with full functionality

```
adn_content    → write, read, edit, move, delete, view
adn_project    → create, switch, list, status, sync
adn_export     → pandoc, docsify, html, pdf, skills!
adn_import     → obsidian, notion, joplin, skills!
adn_search     → search everywhere
adn_knowledge  → analytics, research, bulk ops
adn_navigation → explore, recent, context
adn_editor     → notepad++, typora integration
adn_zettelmaker→ generate, expand, suggest
adn_inbox      → file drop processing
```

**10 tools total** = fully compatible with Cursor IDE

### 4. 🔧 **Unified Database Architecture**

- ✅ Single global database (`~/.advanced-memory/memory.db`)
- ✅ Project isolation via `project_id`
- ✅ Fast sync (2000+ notes in seconds)
- ✅ Configurable file indexing (all files or .md only)

---

## 🚀 Quick Start

### Installation

**Python Package**:
```bash
pip install advanced-memory-mcp
```

**Claude Desktop Extension** (MCPB):
1. Download `advanced-memory-mcp.mcpb` from [Releases](https://github.com/sandraschi/advanced-memory-mcp/releases)
2. Open Claude Desktop → Settings → Extensions
3. Drop the `.mcpb` file
4. Configure in Extensions UI (project path, settings)

### Configure Claude Desktop

**If using Python package** (add to `claude_desktop_config.json`):
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

**If using MCPB**: Configuration is in Claude Desktop Settings → Extensions UI

### First Steps

```
You: "Create a new project for my research notes"
Claude: ✓ Created project "research-notes"

You: "Generate starter zettelkasten for developer topics"
Claude: ✓ Created 30+ interconnected notes on Python, Git, Docker, etc.

You: "Export my notes as Claude Skills"
Claude: ✓ Exported 30 skills to ~/claude-skills/
       → Configure Claude Desktop to discover them!
```

[Full Quick Start Guide →](QUICKSTART.md)

---

## 💎 Killer Features

### Claude Skills Export/Import

**Export your zettelkasten**:
```python
adn_export("claude_skills", export_path="~/claude-skills/")
```

**Import Anthropic's official skills**:
```python
adn_import("claude_skills", source_path="~/anthropic-skills/", 
           destination_folder="skills/anthropic")
```

**Result**: Bidirectional integration - your knowledge IS agent skills!

[Claude Skills Guide →](docs/user-guide/claude-skills.md)

### Intelligent File Sync

**Index everything** or **markdown only**:
```json
{
  "index_all_files": true  // Code repos: true, Pure notes: false
}
```

**Archive old content** without deletion:
- Folders with `-backup-`, `.obsolete`, `-archived` automatically skipped
- Preserves files but excludes from indexing
- Perfect for keeping history without clutter

[File Sync Guide →](docs/user-guide/file-type-filtering.md)

### Multi-Format Export

```python
adn_export("pandoc", export_path="book.pdf", format_type="pdf")  # PDF
adn_export("docsify", export_path="docs/")  # Website
adn_export("claude_skills", export_path="skills/")  # Agent Skills!
adn_export("html", export_path="website/")  # Standalone HTML
adn_export("pdf_book", export_path="book.pdf", book_title="My Research")
```

### Import from Anywhere

```python
adn_import("obsidian", source_path="~/obsidian-vault/")
adn_import("notion", source_path="notion-export.zip")
adn_import("joplin", source_path="~/joplin-export/")
adn_import("evernote", source_path="export.enex")
adn_import("claude_skills", source_path="~/anthropic-skills/")  # NEW!
```

---

## 📖 Documentation

### Getting Started
- [Installation Guide](INSTALLATION.md) - Step-by-step setup
- [Quick Start](QUICKSTART.md) - Get productive in 5 minutes
- [Troubleshooting](docs/TROUBLESHOOTING_GUIDE.md) - Common issues

### Core Features
- [Claude Skills Integration](docs/user-guide/claude-skills.md) - **NEW!** Export zettel as agent skills
- [Zettelkasten Templates](docs/zettelkasten/) - 87+ curated templates
- [Portmanteau Tools](docs/PORTMANTEAU_TOOLS_REFERENCE.md) - Cursor IDE compatibility
- [Database Architecture](docs/architecture/DATABASE_ARCHITECTURE.md) - Unified global database

### Advanced
- [MCP Integration](docs/integrations/claude.md) - Deep dive into MCP
- [Developer Guide](docs/DEVELOPER_GUIDE.md) - Extend and customize
- [Architecture](docs/ARCHITECTURE_DEEP_DIVE.md) - System design

[Complete Documentation →](docs/)

---

## 🎯 Use Cases

### For Development Teams

**Problem**: Team knowledge scattered across wikis, Slack, docs  
**Solution**: Centralized knowledge graph + Claude Skills

```python
# 1. Document your team's standards in Advanced Memory
# 2. Export as Claude Skills
adn_export("claude_skills", export_path="~/team-skills/", source_folder="team/standards")

# 3. Team members' Claude uses YOUR standards automatically!
```

### For Researchers

**87+ research templates ready to use**:
- Research Methods Overview
- Systematic Literature Review
- Critical Thinking
- Data Analysis Fundamentals
- Academic Writing

**Plus**: Export your findings as Skills → Claude guides your future research!

### For Solo Developers

**Cursor IDE + Advanced Memory + Skills**:
1. Index your codebase (all files)
2. Generate developer zettelkasten (30+ templates)
3. Export as Skills for Claude
4. Claude has YOUR code + YOUR knowledge + YOUR procedures

**Result**: Context-aware AI coding assistant with your entire knowledge base!

---

## 🏗️ Architecture Highlights

### Unified Database (v1.0.0b3)

- **Single global database**: `~/.advanced-memory/memory.db`
- **Project isolation**: via `project_id` (not separate databases)
- **Fast sync**: 2000+ notes indexed in seconds
- **Portable**: Export/import entire system as archive

### Portmanteau Tools

**40+ individual tools consolidated into 10 comprehensive tools**:

| Portmanteau Tool | Consolidates | Operations |
|-----------------|--------------|------------|
| `adn_content` | 6 tools | write, read, edit, move, delete, view |
| `adn_project` | 8 tools | create, switch, list, status, sync, delete, set_default, get_current |
| `adn_export` | 9 tools | pandoc, docsify, html, joplin, pdf, archive, **skills** |
| `adn_import` | 6 tools | obsidian, notion, joplin, evernote, archive, **skills** |
| `adn_search` | 5 tools | notes, obsidian, notion, joplin, evernote |
| `adn_knowledge` | 9 tools | analytics, research, bulk ops, validation |
| `adn_navigation` | 5 tools | context, recent, list, status, sync_status |
| `adn_editor` | 5 tools | notepad++, typora, canvas, read_content |
| `adn_zettelmaker` | 6 tools | generate, expand, suggest, connect, analyze |
| `adn_inbox` | 4 tools | status, process, info, watch |

**Result**: Full functionality in 10 tools (Cursor IDE: ✅ Compatible!)

---

## 🔥 What's New in v1.0.0b3

### 🎯 Claude Skills Integration (KILLER FEATURE!)

- ✅ Export zettelkasten → Claude Skills format
- ✅ Import Anthropic skills → Advanced Memory
- ✅ Bidirectional conversion preserves metadata
- ✅ 87+ templates ready as agent skills
- ✅ First knowledge management system with Skills integration!

### 🔧 Database Architecture Fixes

- ✅ Fixed `ADVANCED_MEMORY_HOME` defaulting to `~/.advanced-memory/`
- ✅ Removed per-project databases (unified global database)
- ✅ Fixed MCPB config pointing to wrong location
- ✅ Project isolation via `project_id`

### 📁 File Sync Improvements

- ✅ `index_all_files` config (index all files or .md only)
- ✅ `ARCHIVE_PATTERNS` (skip backup/obsolete folders)
- ✅ Enhanced diagnostic logging

### ✅ MCPB Portmanteau-Only

- ✅ MCPB exposes ONLY 10 tools (not 50+)
- ✅ Achieves Cursor IDE compatibility
- ✅ Full functionality via portmanteau tools

### 🐍 Python Compatibility

- ✅ Python 3.11, 3.12, 3.13 tested
- ✅ Python 3.10 compatible
- ✅ All 1113 tests passing

[Full Changelog →](CHANGELOG.md)

---

## 🎓 Learning Resources

### Zettelkasten Templates (87+)

**Developer** (30+ templates):
- Python: Fundamentals, Type Hints, Async, Testing
- Git: Version Control, Workflows
- Docker: Containers, Compose
- CI/CD: GitHub Actions, Pipelines
- Clean Code: Principles, Patterns, OOP
- System Design: Microservices, Event-Driven, Distributed Systems

**Data Scientist** (10+ templates):
- Machine Learning Fundamentals
- Python for Data Science
- ML Model Deployment

**Researcher** (12+ templates):
- Research Methods Overview
- Systematic Literature Review
- Critical Thinking
- Academic Writing

**Plus**: DevOps, Product Manager, Entrepreneur, Creative, Writer, UX Designer, Knowledge Worker, AI, Philosophy

[Browse All Templates →](zettelkasten/templates/)

### Documentation

- [Complete User Guide](docs/user-guide/) - Everything you need
- [Claude Skills Integration](docs/user-guide/claude-skills.md) - Skills export/import
- [Troubleshooting](docs/TROUBLESHOOTING_GUIDE.md) - Common issues
- [Developer Guide](docs/DEVELOPER_GUIDE.md) - Extend and customize

---

## 🛠️ Technical Details

### Built With

- **MCP Protocol**: Model Context Protocol for LLM integration
- **FastMCP**: High-performance MCP server framework
- **SQLAlchemy**: Robust database ORM with async support
- **Pydantic**: Type-safe configuration and validation
- **Whoosh**: Full-text search indexing
- **Python-Frontmatter**: YAML frontmatter parsing

### Requirements

- Python 3.11+ (3.10 compatible, 3.13 tested)
- Claude Desktop or any MCP-compatible client
- Windows, macOS, or Linux

### Compatibility

- ✅ **Claude Desktop**: Native MCP integration
- ✅ **Cursor IDE**: 10 portmanteau tools (fully compatible)
- ✅ **Claude Skills**: Bidirectional export/import
- ✅ **Obsidian**: Import vaults, export to Obsidian format
- ✅ **Notion**: Import/export workspaces
- ✅ **Joplin**: Import/export knowledge bases
- ✅ **Evernote**: Import ENEX files

---

## 💡 Example Workflows

### Workflow 1: Team Knowledge → Claude Skills

```python
# 1. Document team standards in Advanced Memory
adn_content("write", identifier="Python Standards", 
            content="# Our Python Standards\n\n...", folder="team/standards")

# 2. Export as Claude Skills
adn_export("claude_skills", export_path="~/team-skills/", source_folder="team")

# 3. Team members configure Claude Desktop
# Settings → Skills → Add Directory → ~/team-skills/

# Result: Everyone's Claude follows the SAME team standards!
```

### Workflow 2: Learn from Anthropic + Enhance

```python
# 1. Import Anthropic's official MCP Builder skill
adn_import("claude_skills", source_path="~/anthropic-skills/mcp-builder/",
           destination_folder="skills/mcp")

# 2. Enhance with your team's patterns
# ... edit in Advanced Memory, add links, observations ...

# 3. Export enhanced version
adn_export("claude_skills", export_path="~/enhanced-mcp-skills/",
           source_folder="skills/mcp")

# 4. Share with community!
```

### Workflow 3: Zettelkasten for Learning

```python
# 1. Generate starter zettelkasten
adn_zettelmaker("generate", category="data-scientist", topic="machine-learning")

# 2. Study and enhance notes
# ... add your own examples, insights ...

# 3. Export as Skills
adn_export("claude_skills", export_path="~/ml-skills/",
           source_folder="data-scientist")

# 4. Claude teaches ML using YOUR notes!
```

---

## 🚀 Installation Options

### Option 1: Python Package (Flexible)

```bash
# Install
pip install advanced-memory-mcp

# Run
advanced-memory mcp

# Configure Claude Desktop
# Add to claude_desktop_config.json
```

**Best for**: Development, customization, running from source

### Option 2: MCPB Extension (Easy)

```bash
# Download .mcpb from releases
# Drag into Claude Desktop Extensions
# Configure in Settings UI
```

**Best for**: Non-technical users, quick setup, GUI configuration

[Detailed Installation →](INSTALLATION.md)

---

## 📊 Project Stats

- **1113 tests** passing (100% pass rate)
- **87+ zettelkasten templates** (12 categories)
- **10 portmanteau tools** (Cursor IDE compatible)
- **54% test coverage** (growing)
- **Python 3.11-3.13** supported (3.10 compatible)
- **Zero ruff errors** (strict linting)

---

## 🤝 Contributing

We welcome contributions! See:

- [Contributing Guide](CONTRIBUTING.md) - How to contribute
- [Developer Guide](docs/DEVELOPER_GUIDE.md) - Development setup
- [Code of Conduct](CODE_OF_CONDUCT.md) - Community standards

### Quick Contribution Ideas

- 🎨 Create new zettelkasten templates for your domain
- 📝 Improve documentation
- 🐛 Report bugs or suggest features
- 🌐 Translate documentation
- 🔧 Add new export/import formats

---

## 📜 License

**AGPL-3.0-or-later** - Free and open source

This ensures:
- ✅ You can use it freely (personal or commercial)
- ✅ You can modify and extend it
- ✅ You must share improvements (keeps it open source)

[Full License →](LICENSE)

---

## 🙏 Credits

Built with inspiration from:
- [Anthropic Claude Skills](https://github.com/anthropics/anthropic-skills) - Agent skills framework
- [Zettelkasten Method](https://zettelkasten.de/) - Knowledge management methodology  
- [Model Context Protocol](https://modelcontextprotocol.io/) - LLM integration standard
- [FastMCP](https://github.com/jlowin/fastmcp) - High-performance MCP framework

---

## 🔗 Links

- **Documentation**: [docs/](docs/)
- **Releases**: [GitHub Releases](https://github.com/sandraschi/advanced-memory-mcp/releases)
- **Issues**: [Bug Reports & Features](https://github.com/sandraschi/advanced-memory-mcp/issues)
- **Claude Skills**: [Integration Guide](docs/user-guide/claude-skills.md)

---

## ⚡ Quick Command Reference

```python
# Content Management
adn_content("write", identifier="Title", content="...", folder="notes")
adn_content("read", identifier="Title")
adn_content("edit", identifier="Title", operation="append", content="...")

# Project Management  
adn_project("create", project_name="research", project_path="~/Documents/research")
adn_project("switch", project_name="research")
adn_project("list")

# Claude Skills (NEW!)
adn_export("claude_skills", export_path="~/claude-skills/")
adn_import("claude_skills", source_path="~/anthropic-skills/")

# Zettelkasten Generation
adn_zettelmaker("generate", category="developer", topic="python-core")

# Search
adn_search("notes", query="async programming")

# Export
adn_export("pandoc", export_path="output.pdf", format_type="pdf")
adn_export("docsify", export_path="docs/")
```

[Complete Tool Reference →](docs/PORTMANTEAU_TOOLS_REFERENCE.md)

---

## 🌟 Why Advanced Memory?

**Most knowledge management tools**:
- ❌ Proprietary (vendor lock-in)
- ❌ Cloud-only (privacy concerns)
- ❌ No AI integration (manual workflow)
- ❌ Markdown silos (can't interact with AI)

**Advanced Memory**:
- ✅ **Open source** (AGPL-3.0, your data is yours)
- ✅ **Local-first** (files on your computer, works offline)
- ✅ **AI-native** (designed for Claude Desktop)
- ✅ **Claude Skills** (your knowledge becomes agent skills!)
- ✅ **Cursor IDE** (compatible via portmanteau tools)
- ✅ **Extensible** (import/export everywhere)

**The future**: Your knowledge graph IS your AI's skill library.

---

<p align="center">
  <strong>Built for knowledge workers who refuse to compromise.</strong><br>
  <sub>Local-first. Open source. AI-native.</sub>
</p>

<p align="center">
  <a href="INSTALLATION.md">Get Started</a> •
  <a href="docs/user-guide/claude-skills.md">Claude Skills</a> •
  <a href="docs/">Documentation</a> •
  <a href="https://github.com/sandraschi/advanced-memory-mcp/issues">Report Bug</a>
</p>
