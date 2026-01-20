[![License: AGPL v3](https://img.shields.io/badge/License-AGPL_v3-blue.svg)](https://www.gnu.org/licenses/agpl-3.0)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Tests](https://img.shields.io/badge/tests-1244%20passing-brightgreen)](https://github.com/sandraschi/advanced-memory-mcp/actions)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
![MCP Server](https://badge.mcpx.dev?type=server 'MCP Server')

# Advanced Memory MCP

A Model Context Protocol server that integrates personal knowledge management with Claude Desktop. Features include knowledge graphs, zettelkasten note-taking, and experimental Claude Skills integration.

**New in v1.1.0b3**: FastMCP 2.14.3 advanced features with SEP-1577 sampling implementation, conversational response patterns, Zed IDE support, and Claude Skills January 2026 standardization. Complete MCP ecosystem expansion with multi-IDE compatibility.

[Quick Start](#quick-start) | [Tools Reference](docs/TOOLS_REFERENCE.md) | [Documentation](docs/) | [Technical Docs](TECHNICAL.md)

---

## ✨ Tool Modes

**PORTMANTEAU MODE (Default):** 15 clean, organized tools - Perfect for Claude Desktop
**FULL MODE (Opt-in):** 56 individual tools - For testing/development only

**Result:** No tool explosion! Clean, usable interface.

See [docs/TOOL_MODES.md](docs/TOOL_MODES.md) for details.

---

## Features

### 1. MCP Studio ADN Documentation (New!)

Complete knowledge base with 10 detailed ADN notes covering architecture, API design, frontend implementation, testing strategies, security, DevOps, performance monitoring, and future roadmap. Built for enterprise-scale MCP server development.

### 2. Claude Skills Format Conversion (Experimental)

```python
# Export zettelkasten → Claude Skills format
adn_export("claude_skills", export_path="~/claude-skills/")

# Import Claude Skills → Advanced Memory notes
adn_import("claude_skills", source_path="~/anthropic-skills/")
```

Bidirectional format conversion between zettelkasten notes and Anthropic's Claude Skills format. Conversion tools are functional. Deployment to Claude interfaces varies (claude.ai/API verified, Claude Desktop pending verification). Part of the emerging Claude Skills ecosystem with growing community repositories.

### 3. ADN LLM Integration (New!)

Multi-provider LLM support with intelligent provider switching:
```python
# Switch between providers dynamically
adn_llm("select_model", provider="openai", model="gpt-4")
adn_llm("select_model", provider="anthropic", model="claude-3-sonnet")
adn_llm("select_model", provider="ollama", model="llama3.2:3b")
```

### 4. Reference Library (Experimental)

87+ curated reference templates across 12 categories for systematic learning:
- **Developer**: Python, Git, Docker, CI/CD, Clean Code (30+ templates)
- **DevOps**: Kubernetes, Infrastructure as Code, Observability (15+ templates)
- **Data Scientist**: ML, MLOps, Python for Data Science (10+ templates)
- **Researcher**: Research Methods, Literature Review, Critical Thinking (12+ templates)
- **Product Manager**: Strategy, Analytics, Metrics (8+ templates)
- **Plus**: Entrepreneur, Creative, Writer, UX Designer, Knowledge Worker, AI, Philosophy

**Note**: These are comprehensive reference documents (1000-5000 words), not classic atomic zettelkasten notes. See [Zettelkasten Philosophy](docs/zettelkasten/ZETTELKASTEN_PHILOSOPHY.md) for the distinction. Classic zettelkasten support (atomic notes) planned for v1.1.

### 5. Audio Soul 2026 (New!)

High-performance, soulful voice stack built with SOTA FOSS components:

#### 🎯 Dual STT Architecture (ikubaysan Integration)
- **Revolutionary Pipeline**: Sphinx wake-word detection + Google Cloud accurate transcription
- **Character State Machine**: Wandering → Conversing → Performing Actions
- **Multi-Provider LLM**: Local (Ollama) + Cloud (OpenAI, Anthropic, Gemini)
- **Advanced Voice Commands**: `adn_audio_dual_stt()` with enhanced capabilities

#### Core Audio Features
- **High-Fidelity TTS**: Integrated Kokoro for expressive, human-like speech.
- **Rapid Transcription**: Accelerated faster-whisper for near-instant STT.
- **GPU Optimized**: Powered by `onnxruntime-gpu` for peak efficiency on modern hardware.
- **Background Listening**: Wake word detection for hands-free operation.
- **Voice Commands**: Intelligent parsing with LLM fallback for complex commands.

### 6. Cursor IDE Compatible - Tool Mode Selection

**Problem**: Most MCPs have 40+ tools → breaks Cursor's 50-tool limit
**Solution**: Choose between 11 portmanteau tools or full 50+ tools

#### Portmanteau Mode (11 tools - Cursor compatible)

```
adn_content    → write, read, view, view_rendered, edit, move, delete
adn_project    → create, switch, list, status, sync
adn_export     → pandoc, docsify, html, pdf, skills!
adn_import     → obsidian, notion, joplin, skills!
adn_search     → search everywhere
adn_knowledge  → analytics, research, bulk ops
adn_navigation → explore, recent, context
adn_editor     → notepad++, typora integration
adn_zettelmaker→ generate, expand, suggest
adn_inbox      → file drop processing
help           → documentation
```

**Enable portmanteau-only mode** (for Cursor IDE):
```json
{
  "mcpServers": {
    "advanced-memory": {
      "env": {
        "ADVANCED_MEMORY_PORTMANTEAU_ONLY": "true"
      }
    }
  }
}
```

**11 tools total** = fully compatible with Cursor IDE
**Zero functionality loss** - all features available through portmanteau tools

See [Tool Mode Selection](docs/user-guide/tool-mode-selection.md) for details.

### 4. Unified Database Architecture

- Single global database (`~/.advanced-memory/memory.db`)
- Project isolation via `project_id`
- Fast sync (2000+ notes in seconds)
- Configurable file indexing (all files or .md only)

---

## Quick Start

### Installation

**Step 1: Install the package**
```bash
pip install advanced-memory-mcp
```

**Step 2: Configure your MCP client**

#### Cursor IDE or VS Code (One-Click)
```bash
# Generate deeplink for Cursor
advanced-memory deeplink cursor

# Generate configuration for VS Code
advanced-memory deeplink vscode

# Interactive setup wizard
advanced-memory setup
```

#### Claude Desktop

**Option 1: MCPB Package** (Recommended for Claude Desktop)
1. Download `advanced-memory-mcp.mcpb` from [Releases](https://github.com/sandraschi/advanced-memory-mcp/releases)
2. Open Claude Desktop → Settings → Extensions
3. Drop the `.mcpb` file
4. Configure project path in Extensions UI

**Option 2: Manual Configuration**

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

Or generate the configuration:
```bash
advanced-memory deeplink claude-desktop
```

**Option 3: Windows Bootstrap (No MCPB)**

Use this when you cannot install the `.mcpb` package (e.g., Windsurf/Cursor on Windows).

Prerequisites: Node.js 18+, Git for Windows, Python 3.11+, [`uv`](https://docs.astral.sh/uv/).

```powershell
# Clones to D:\Dev\repos\advanced-memory-mcp by default
npx --yes github:sandraschi/advanced-memory-mcp/scripts/bootstrap/windows

# Custom target location
npx --yes github:sandraschi/advanced-memory-mcp/scripts/bootstrap/windows -- --target C:\Work\mcp

# Also emit Cursor/Windsurf/Claude config templates
npx --yes github:sandraschi/advanced-memory-mcp/scripts/bootstrap/windows -- --generate-configs
```

What it does:
- Verifies dependencies (Git, Python, uv)
- Clones or updates `advanced-memory-mcp`
- Runs `uv sync`, `uv run ruff check .`, and a skills validation smoke test
- Optionally writes ready-to-use config templates into `bootstrap-configs/`

An npm-published bootstrapper will follow; the script above is ready for `npm publish` when we are.

**📖 Complete Installation Guide**: [Deeplink Installation](docs/user-guide/DEEPLINK_INSTALLATION.md) | [MCPB Installation](docs/user-guide/mcpb-installation-config.md)

### First Steps

```
You: "Create a new project for my research notes"
Claude: Created project "research-notes"

You: "Generate starter zettelkasten for developer topics" (experimental)
Claude: Created 30+ interconnected notes on Python, Git, Docker, etc.

You: "Export my notes as Claude Skills" (experimental)
Claude: Exported 30 skills to ~/claude-skills/
```

[Full Quick Start Guide](QUICKSTART.md)

---

## Testing & Diagnostics

- `pwsh ./scripts/testing/run-all-tool-exercisers.ps1`
  Runs the four portmanteau exerciser suites (core tools, import/export, skills, health/status) and stops at the first failure.
- Flags: `-SkipHeavy` (skip archive export/import), `-SkipNetwork` (skip Wikipedia/arXiv calls), `-SkipPackaging` (skip skills ZIP packaging). Combine flags as needed.
- Individual Python scripts live in `scripts/testing/` if you need to probe a single tool group.

---

## Core Capabilities

### Claude Skills Format Conversion (Experimental)

**Export to Skills format**:
```python
adn_export("claude_skills", export_path="~/claude-skills/")
# Creates proper SKILL.md files for claude.ai, API, or community sharing
```

**Import from Skills format**:
```python
adn_import("claude_skills", source_path="~/anthropic-skills/",
           destination_folder="skills/anthropic")
# Imports community skills into your knowledge base
```

**Status**: Format conversion fully functional. Deploy to claude.ai (paid), Claude API, or share via GitHub. Claude Desktop integration pending verification.

**Resources**:
- [User Guide](docs/user-guide/claude-skills.md) - How to use
- [Ecosystem Overview](docs/integrations/CLAUDE_SKILLS_ECOSYSTEM.md) - Complete ecosystem tracking
- [Anthropic Skills Repo](https://github.com/anthropics/anthropic-skills) - Official examples
- [Skills Spec](https://github.com/anthropics/anthropic-skills/blob/main/agent_skills_spec.md) - Format specification
- [Claude Skills Docs](https://support.claude.com/en/sections/12512173-skills) - Official support

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

**All exports work out of the box!** ✨ No paths needed!

```python
adn_export("pdf")                    # → Desktop/advanced-memory-exports/pdf/
adn_export("pandoc", format_type="docx")  # → Desktop/advanced-memory-exports/pandoc/
adn_export("docsify")                # → Desktop/advanced-memory-exports/docsify/
adn_export("claude_skills")          # → Desktop/advanced-memory-exports/claude_skills/
adn_export("html")                   # → Desktop/advanced-memory-exports/html/
```

**Smart defaults**: Exports go to your Desktop (or specify custom path)
**Zero setup**: Everything auto-installs on first use
**PDF**: Pure Python (weasyprint) - no LaTeX needed! ⚡
**DOCX/EPUB**: Pandoc auto-downloads (~100MB, one-time)

**Documentation**: [Export Guide](docs/user-guide/import-export.md)

### Import from Anywhere

**Prerequisites**: Requires existing exports/vaults from respective applications.

```python
adn_import("obsidian", source_path="~/obsidian-vault/")  # Requires: Obsidian vault
adn_import("notion", source_path="notion-export.zip")    # Requires: Notion export
adn_import("joplin", source_path="~/joplin-export/")     # Requires: Joplin export
adn_import("evernote", source_path="export.enex")        # Requires: Evernote ENEX file
adn_import("claude_skills", source_path="~/skills/")     # Requires: Skills repository
```

**External Tools**:
- [Obsidian](https://obsidian.md/) - Local-first note-taking
- [Notion](https://notion.so/) - Collaborative workspace
- [Joplin](https://joplinapp.org/) - Open-source notes
- [Evernote](https://evernote.com/) - Note organization

**Documentation**: [Import/Export Guide](docs/user-guide/import-export.md)

---

## 📖 Documentation

### Getting Started
- [Installation Guide](INSTALLATION.md) - Step-by-step setup
- [Quick Start](QUICKSTART.md) - Get productive in 5 minutes
- [Troubleshooting](docs/TROUBLESHOOTING_GUIDE.md) - Common issues

### Core Features
- [Claude Skills Format Conversion](docs/user-guide/claude-skills.md) - Bidirectional conversion (experimental, [ecosystem overview](docs/integrations/CLAUDE_SKILLS_ECOSYSTEM.md))
- [Reference Library](docs/zettelkasten/) - 87+ learning templates (experimental, [philosophy](docs/zettelkasten/ZETTELKASTEN_PHILOSOPHY.md))
- [Portmanteau Tools](docs/PORTMANTEAU_TOOLS_REFERENCE.md) - Cursor IDE compatibility (10 tools)
- [Database Architecture](docs/architecture/DATABASE_ARCHITECTURE.md) - Unified global database

### Technical & Development
- [Technical Documentation](TECHNICAL.md) - Architecture, dependencies, build system, CI/CD
- [Developer Guide](docs/DEVELOPER_GUIDE.md) - Extend and customize
- [Architecture Deep Dive](docs/ARCHITECTURE_DEEP_DIVE.md) - System design
- [Testing Checklist](docs/testing/REAL_WORLD_TESTING_CHECKLIST.md) - Feature verification status

[Complete Documentation →](docs/)

---

## Use Cases

### For Development Teams

Centralize team knowledge in a structured format:

```python
# Document team standards in Advanced Memory
# Export as Claude Skills (experimental)
adn_export("claude_skills", export_path="~/team-skills/", source_folder="team/standards")
```

### For Researchers

Research-focused templates include:
- Research Methods Overview
- Systematic Literature Review
- Critical Thinking
- Data Analysis Fundamentals
- Academic Writing

Templates are experimental and coverage varies by domain.

### For Solo Developers

Integration options for Cursor IDE:
1. Index your codebase (all files)
2. Generate developer zettelkasten templates (experimental)
3. Export as Skills for Claude (experimental)

Provides context-aware AI assistance with your knowledge base.

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

## What's New in v1.0.0b3

### Claude Skills Format Conversion (Experimental)

- Export: zettelkasten → Claude Skills format (SKILL.md)
- Import: Claude Skills → Advanced Memory notes
- Bidirectional metadata preservation
- Compatible with claude.ai, Claude API, emerging community ecosystem
- Claude Desktop deployment pending verification

### Database Architecture Fixes

- Fixed `ADVANCED_MEMORY_HOME` defaulting to `~/.advanced-memory/`
- Unified global database (removed per-project databases)
- Fixed MCPB config path issues
- Project isolation via `project_id`

### File Sync Improvements

- `index_all_files` config option (index all files or .md only)
- `ARCHIVE_PATTERNS` (skip backup/obsolete folders)
- Enhanced diagnostic logging

### MCPB Portmanteau-Only

- MCPB exposes 10 portmanteau tools (not 50+ individual tools)
- Cursor IDE compatibility
- Full functionality via consolidated tools

### Python Compatibility

- Python 3.11, 3.12, 3.13 tested
- Python 3.10 compatible
- All 1113 tests passing

[Full Changelog](CHANGELOG.md)

---

## Learning Resources

### Zettelkasten Templates (Experimental)

87+ templates across 12 categories:

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

**Additional categories**: DevOps, Product Manager, Entrepreneur, Creative, Writer, UX Designer, Knowledge Worker, AI, Philosophy

Template quality and coverage vary. Consider them starting points for customization.

[Browse All Templates](zettelkasten/templates/)

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

## Example Workflows

### Workflow 1: Team Knowledge to Claude Skills (Experimental)

```python
# 1. Document team standards in Advanced Memory
adn_content("write", identifier="Python Standards",
            content="# Our Python Standards\n\n...", folder="team/standards")

# 2. Export as Claude Skills (experimental)
adn_export("claude_skills", export_path="~/team-skills/", source_folder="team")

# 3. Configure Claude Desktop: Settings → Skills → Add Directory → ~/team-skills/
```

### Workflow 2: Import and Enhance Skills (Experimental)

```python
# 1. Import Anthropic's official skills
adn_import("claude_skills", source_path="~/anthropic-skills/mcp-builder/",
           destination_folder="skills/mcp")

# 2. Enhance with your own notes and links

# 3. Export enhanced version
adn_export("claude_skills", export_path="~/enhanced-mcp-skills/",
           source_folder="skills/mcp")
```

### Workflow 3: Zettelkasten Generation (Experimental)

```python
# 1. Generate starter templates
adn_zettelmaker("generate", category="data-scientist", topic="machine-learning")

# 2. Customize and enhance notes

# 3. Export as Skills (experimental)
adn_export("claude_skills", export_path="~/ml-skills/",
           source_folder="data-scientist")
```

---

## 🚀 Installation Options

### For Cursor IDE and VS Code

One-click installation via deeplinks provides the fastest setup:

```bash
pip install advanced-memory-mcp
advanced-memory deeplink cursor  # or 'vscode'
```

Deeplinks automatically configure the MCP connection in your IDE.

### For Claude Desktop

**MCPB Package** (Recommended):
- Download `.mcpb` from [Releases](https://github.com/sandraschi/advanced-memory-mcp/releases)
- Drag into Claude Desktop Settings → Extensions
- Configure via GUI

**Manual Configuration**:
- Install via `pip install advanced-memory-mcp`
- Add configuration to `claude_desktop_config.json`
- See [installation guide](INSTALLATION.md) for details

### For Zed IDE

**Zed Extension Installation** (Required for Zed IDE):
```bash
pip install advanced-memory-mcp
```

The Zed extension is distributed via PyPI. After installing the Python package:

1. Open Zed IDE
2. Go to Extensions → Install Dev Extension
3. Select the repository directory containing `Cargo.toml`
4. The extension will build and install automatically

**Alternative**: Download the compiled extension from [Releases](https://github.com/sandraschi/advanced-memory-mcp/releases) if available.

### For Other MCP Clients

Install the Python package and configure manually per your client's documentation:

```bash
pip install advanced-memory-mcp
advanced-memory mcp  # Verify installation
```

[Complete Installation Guide →](INSTALLATION.md)

---

## 📊 Project Stats

- **1113 tests** passing (100% pass rate)
- **87+ reference templates** (12 categories, experimental - comprehensive guides, not atomic zettelkasten)
- **10 portmanteau tools** (Cursor IDE compatible)
- **54% test coverage** (growing)
- **Python 3.11-3.13** supported (3.10 compatible)
- **Zero ruff errors** (strict linting)

## ⚠️ Testing Status

**Public Repo Notice**: We're committed to transparency about feature verification.

**Verified** ✅:
- Core content management (write, read, edit, delete)
- Project management (create, switch, list)
- Claude Skills export/import (format conversion)
- Database architecture (global db with project isolation)

**Pending Real-World Verification** ⏳:
- Import/export features (Obsidian, Notion, Joplin, Evernote)
- Reference template quality and coverage
- Editor integrations (Notepad++, Typora)

**Auto-Installed** ✅:
- **Pandoc**: Downloads automatically on first export (~100MB, one-time)
- **Mermaid.js**: Loaded from CDN for diagram rendering
- **weasyprint**: Pure-Python PDF generation (no LaTeX needed!)

**Optional Dependencies** 🔧:
- **wkhtmltopdf**: Alternative PDF engine (if weasyprint has issues)
  - Windows: `winget install wkhtmltopdf`
  - macOS: `brew install wkhtmltopdf`
  - Linux: `sudo apt install wkhtmltopdf`
- **LaTeX** (MiKTeX/TinyTeX): For advanced PDF typography

**External Tools** (optional for specific imports) 🔧:
- **Obsidian/Notion/Joplin/Evernote**: Only needed if importing FROM those platforms (we just read their export files)

**Everything else**: ✅ Works immediately after `pip install`!
- See [Testing Checklist](docs/testing/REAL_WORLD_TESTING_CHECKLIST.md) for details

We're actively testing and will update status as features are verified. [Help us test!](CONTRIBUTING.md)

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

## Quick Command Reference

```python
# Content Management
adn_content("write", identifier="Title", content="...", folder="notes")
adn_content("read", identifier="Title")
adn_content("edit", identifier="Title", operation="append", content="...")

# Project Management
adn_project("create", project_name="research", project_path="~/Documents/research")
adn_project("switch", project_name="research")
adn_project("list")

# Claude Skills (Experimental)
adn_export("claude_skills", export_path="~/claude-skills/")
adn_import("claude_skills", source_path="~/anthropic-skills/")

# Zettelkasten Generation (Experimental)
adn_zettelmaker("generate", category="developer", topic="python-core")

# Search
adn_search("notes", query="async programming")

# Export
adn_export("pandoc", export_path="output.pdf", format_type="pdf")
adn_export("docsify", export_path="docs/")
```

[Complete Tool Reference](docs/PORTMANTEAU_TOOLS_REFERENCE.md)

---

## Why Advanced Memory?

**Key characteristics**:
- **Open source** (AGPL-3.0)
- **Local-first** (files on your computer, works offline)
- **MCP integration** (designed for Claude Desktop)
- **Cursor IDE compatible** (via portmanteau tools)
- **Extensible** (import/export from multiple sources)

**Experimental features**:
- Claude Skills export/import
- Reference template library (comprehensive learning guides)
- Classic zettelkasten (atomic notes) planned for v1.1

---

<p align="center">
  <sub>Local-first knowledge management with MCP integration</sub>
</p>

<p align="center">
  <a href="INSTALLATION.md">Get Started</a> •
  <a href="docs/user-guide/claude-skills.md">Claude Skills</a> •
  <a href="docs/">Documentation</a> •
  <a href="https://github.com/sandraschi/advanced-memory-mcp/issues">Report Bug</a>
</p>
