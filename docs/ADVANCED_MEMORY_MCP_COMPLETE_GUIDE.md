# Advanced Memory MCP - Complete Documentation

**Version:** 1.0.0b2
**Last Updated:** October 16, 2025
**Author:** Sandra Schi

## Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Installation & Setup](#installation--setup)
4. [MCP Tools Reference](#mcp-tools-reference)
5. [Portmanteau Tools](#portmanteau-tools)
6. [Project Management](#project-management)
7. [Knowledge Graph](#knowledge-graph)
8. [File Synchronization](#file-synchronization)
9. [Import/Export Capabilities](#importexport-capabilities)
10. [Configuration](#configuration)
11. [Usage Patterns](#usage-patterns)
12. [Troubleshooting](#troubleshooting)
13. [Development](#development)
14. [API Reference](#api-reference)

---

## Overview

Advanced Memory MCP is a comprehensive knowledge management system built on the Model Context Protocol (MCP). It enables bidirectional communication between LLMs (like Claude) and markdown files, creating a personal knowledge graph that can be traversed using semantic relationships between documents.

### Key Features

- **Semantic Knowledge Graph**: Automatic entity extraction and relationship mapping
- **Multi-Project Support**: Manage multiple knowledge bases simultaneously
- **Real-time File Watching**: Automatic synchronization of markdown files
- **Rich Import/Export**: Support for Obsidian, Joplin, Notion, Evernote, and more
- **Advanced Search**: Full-text search with semantic ranking
- **MCP Integration**: Native Claude Desktop integration via MCP protocol
- **Portmanteau Tools**: Consolidated toolset for reduced complexity

### Use Cases

- **Personal Knowledge Management**: Organize notes, research, and documentation
- **Project Documentation**: Maintain project-specific knowledge bases
- **Research Workflows**: Build interconnected research notes
- **AI-Assisted Writing**: Leverage Claude for content creation and organization
- **Cross-Platform Sync**: Work with multiple tools and platforms

---

## Architecture

### Core Components

```
Advanced Memory MCP
├── MCP Server (FastMCP 2.12+)
│   ├── Tools Layer (50+ tools)
│   ├── Portmanteau Tools (8 consolidated)
│   └── Prompts & Resources
├── API Layer (FastAPI)
│   ├── REST Endpoints
│   ├── Async Client
│   └── Authentication
├── Data Layer
│   ├── SQLite Database
│   ├── Full-Text Search (FTS5)
│   └── Entity-Relationship Model
├── Sync Layer
│   ├── File Watcher
│   ├── Background Sync
│   └── Change Detection
└── Import/Export Layer
    ├── Obsidian Integration
    ├── Joplin Support
    ├── Notion Compatibility
    └── Evernote Migration
```

### Data Model

#### Entities
- **Notes**: Markdown files with metadata
- **Observations**: Categorized facts (`- [category] content`)
- **Relations**: Directional links (`- relation_type [[Target]]`)

#### Database Schema
```sql
-- Core tables
entity (id, title, content, file_path, project_id, permalink)
observation (id, entity_id, category, content)
relation (id, source_id, target_id, relation_type)
project (id, name, path, is_default, is_active)

-- Search indexes
fts_entity (content, title)
fts_observation (content)
```

### Technology Stack

- **Backend**: Python 3.12+, FastAPI, SQLAlchemy 2.0
- **Database**: SQLite with FTS5 for search
- **MCP**: FastMCP 2.12+ for Claude integration
- **Sync**: Watchdog for file monitoring
- **Import/Export**: Custom parsers for various formats

---

## Installation & Setup

### Prerequisites

- Python 3.12 or higher
- Claude Desktop (for MCP integration)
- Git (for development)

### Installation Methods

#### 1. PyPI Installation (Recommended)

```bash
pip install advanced-memory-mcp
```

#### 2. Development Installation

```bash
git clone https://github.com/sandraschi/advanced-memory-mcp.git
cd advanced-memory-mcp
pip install -e ".[dev]"
```

#### 3. MCPB Package Installation

1. Download `advanced-memory-mcp-1.0.0b2.mcpb` from releases
2. Drag to Claude Desktop for one-click installation
3. Follow configuration prompts

### Initial Setup

#### 1. Initialize Database

```bash
advanced-memory init
```

#### 2. Configure Claude Desktop

Add to `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "advanced-memory-mcp": {
      "command": "python",
      "args": ["-m", "advanced_memory.mcp.server"],
      "env": {
        "ADVANCED_MEMORY_HOME": "C:/Users/username"
      }
    }
  }
}
```

#### 3. Create First Project

```bash
advanced-memory project add main "~/Documents/notes"
advanced-memory sync
```

### Directory Structure

```
~/.advanced-memory/
├── memory.db              # SQLite database
├── config.json            # Configuration
├── *.log                  # Log files
└── watch-status.json      # File watcher status

~/Documents/notes/          # Your knowledge base
├── project-notes.md
├── research/
└── meetings/
```

---

## MCP Tools Reference

### Content Management Tools

#### adn_content (Portmanteau)
Consolidates all content operations:

```python
# Write/update notes
adn_content("write", title="Meeting Notes", content="# Meeting\n\nDiscussed...", folder="meetings")

# Read notes
adn_content("read", identifier="Meeting Notes")

# Edit notes
adn_content("edit", identifier="Meeting Notes", operation="append", content="\n\n## Action Items\n- Task 1")

# Move notes
adn_content("move", identifier="Meeting Notes", destination="archive/meetings/meeting-notes.md")

# Delete notes
adn_content("delete", identifier="Meeting Notes")
```

#### Individual Content Tools
- `write_note`: Create/update markdown notes
- `read_note`: Read notes by title/permalink
- `edit_note`: Incremental editing (append, prepend, find/replace)
- `move_note`: Relocate notes with relationship updates
- `delete_note`: Remove notes from knowledge base
- `view_note`: Display formatted artifacts

### Project Management Tools

#### adn_project (Portmanteau)
Complete project management:

```python
# Create projects
adn_project("create", project_name="research", project_path="~/Documents/research")

# List projects
adn_project("list")

# Switch projects
adn_project("switch", project_name="research")

# Sync specific project
adn_project("sync", project_name="research")  # ⭐ Without changing default!

# Get project status
adn_project("status", project_name="research")

# Set default project
adn_project("set_default", project_name="research")

# Delete projects
adn_project("delete", project_name="old-project")
```

### Search & Discovery Tools

#### adn_search (Portmanteau)
Comprehensive search capabilities:

```python
# Search notes
adn_search("notes", query="machine learning", project="research")

# Search external vaults
adn_search("obsidian", vault_path="~/obsidian-vault", query="AI")

# Search Joplin exports
adn_search("joplin", vault_path="~/joplin-export", query="meeting")

# Search Notion exports
adn_search("notion", vault_path="~/notion-export", query="project")
```

### Navigation Tools

#### adn_navigation (Portmanteau)
Knowledge graph navigation:

```python
# Build context from memory URLs
adn_navigation("context", url="memory://research/ai-fundamentals", depth=2)

# Get recent activity
adn_navigation("recent", timeframe="1 week", type="notes")

# List directories
adn_navigation("directory", dir_name="/research", depth=2)

# System status
adn_navigation("status", level="basic")
```

### Import/Export Tools

#### adn_import (Portmanteau)
Import from various platforms:

```python
# Import Obsidian vault
adn_import("obsidian", vault_path="~/obsidian-vault", destination_folder="imported/obsidian")

# Import Joplin export
adn_import("joplin", export_path="~/joplin-export", destination_folder="imported/joplin")

# Import Notion export
adn_import("notion", export_path="~/notion-export", folder="imported/notion")

# Import Evernote ENEX
adn_import("evernote", export_path="~/notes.enex", folder="imported/evernote")
```

#### adn_export (Portmanteau)
Export to various formats:

```python
# Export to PDF book
adn_export("pdf_book", book_title="Research Compendium", source_folder="/research")

# Export to HTML website
adn_export("html", export_path="~/website", include_index=True)

# Export to Docsify
adn_export("docsify", export_path="~/docs", site_title="Knowledge Base")

# Export to Joplin format
adn_export("joplin", export_path="~/joplin-export")
```

### Knowledge Operations

#### adn_knowledge (Portmanteau)
Advanced knowledge management:

```python
# Bulk operations
adn_knowledge("bulk_update", filters={"tags": ["draft"]}, action={"add_tags": ["reviewed"]})

# Tag analytics
adn_knowledge("tag_analytics", action="analyze_usage")

# Research orchestration
adn_knowledge("research", operation="research_plan", topic="quantum computing")
```

### Editor Integration

#### adn_editor (Portmanteau)
External editor support:

```python
# Edit in Notepad++
adn_editor("notepadpp", note_identifier="Meeting Notes")

# Typora control
adn_editor("typora", operation="export", format="pdf", output_path="~/export.pdf")

# Create Obsidian canvas
adn_editor("canvas", title="Project Overview", nodes=[...], edges=[...])
```

---

## Portmanteau Tools

Advanced Memory MCP uses **portmanteau tools** to reduce complexity while maintaining full functionality. Instead of 50+ individual tools, you get 8 consolidated tools:

### Tool Consolidation Strategy

| Portmanteau Tool | Consolidates | Purpose |
|------------------|--------------|---------|
| `adn_content` | write_note, read_note, edit_note, move_note, delete_note, view_note | Content management |
| `adn_project` | create, switch, delete, set_default, get_current, list, sync, status | Project management |
| `adn_search` | search_notes, search_obsidian_vault, search_joplin_vault, search_notion_vault, search_evernote_vault | Search & discovery |
| `adn_navigation` | build_context, recent_activity, list_directory, status, sync_status | Knowledge graph navigation |
| `adn_import` | load_obsidian_vault, load_joplin_vault, load_notion_export, load_evernote_export, import_from_archive, load_obsidian_canvas | Import from platforms |
| `adn_export` | export_pandoc, export_docsify, export_html_notes, export_joplin_notes, make_pdf_book, export_to_archive, export_evernote_compatible, export_notion_compatible | Export to formats |
| `adn_knowledge` | knowledge_operations, research_orchestrator | Advanced knowledge management |
| `adn_editor` | edit_in_notepadpp, import_from_notepadpp, typora_control, canvas, read_content | External editor integration |

### Benefits

- **Reduced Tool Count**: 8 tools instead of 50+
- **Consistent API**: All tools follow same pattern
- **Better UX**: Easier to remember and use
- **Cursor IDE Compatible**: Optimized for AI coding assistants

---

## Project Management

### Project Concepts

A **project** in Advanced Memory is a collection of markdown files organized in a directory structure. Projects are independent knowledge bases that can be managed separately.

### Project Operations

#### Creating Projects

```python
# Create a new project
adn_project("create",
    project_name="my-research",
    project_path="~/Documents/research",
    set_default=False)
```

#### Project Switching

```python
# Switch active project (affects all subsequent operations)
adn_project("switch", project_name="my-research")

# Sync without changing default
adn_project("sync", project_name="my-research")  # ⭐ Key feature!
```

#### Project Status

```python
# Get current project info
adn_project("get_current")

# Get specific project status
adn_project("status", project_name="my-research")
```

### Project Configuration

Projects are stored in `~/.advanced-memory/config.json`:

```json
{
  "projects": {
    "main": "C:/Users/username/Documents/notes",
    "research": "C:/Users/username/Documents/research",
    "work": "C:/Users/username/Documents/work"
  },
  "default_project": "main"
}
```

---

## Knowledge Graph

### Entity Model

The knowledge graph is built from **entities** (notes) with **observations** and **relations**:

#### Entities
- Represent markdown files
- Have titles, content, and metadata
- Linked to projects and file paths

#### Observations
Categorized facts extracted from markdown:
```markdown
- [definition] Machine learning is a subset of AI
- [example] Linear regression predicts continuous values
- [reference] See [[Deep Learning Book]] Chapter 5
```

#### Relations
Directional links between entities:
```markdown
- builds_on [[Machine Learning Fundamentals]]
- related_to [[Neural Networks]]
- contradicts [[Traditional Statistics]]
```

### Semantic Processing

Advanced Memory automatically:

1. **Extracts Entities**: From `[[Entity Name]]` syntax
2. **Creates Observations**: From `- [category] content` patterns
3. **Builds Relations**: From relation patterns
4. **Indexes Content**: For full-text search
5. **Updates Graph**: When files change

### Knowledge Graph Navigation

#### Memory URLs
Navigate the knowledge graph using memory URLs:

```python
# Build context from memory URL
adn_navigation("context",
    url="memory://research/ai-fundamentals",
    depth=2,
    timeframe="1 week")
```

#### Recent Activity
Track changes across the knowledge base:

```python
# Get recent changes
adn_navigation("recent",
    timeframe="2 days",
    type="notes")
```

---

## File Synchronization

### Automatic File Watching

Advanced Memory includes a **file watcher** that monitors all active projects for changes:

#### Features
- **Real-time Monitoring**: Detects file changes instantly
- **Debounced Sync**: Waits 1 second after last change
- **Multi-project Support**: Monitors all active projects
- **Smart Filtering**: Ignores `node_modules/`, `.git/`, etc.

#### Configuration
```json
{
  "sync_changes": true,
  "sync_delay": 1000
}
```

#### What Gets Synced
- **Added Files**: New `.md` files → indexed
- **Modified Files**: Changed content → updated
- **Deleted Files**: Removed files → cleaned up
- **Moved Files**: Renamed/moved → tracked

### Manual Synchronization

#### Sync All Projects
```bash
advanced-memory sync
```

#### Sync Specific Project
```python
adn_project("sync", project_name="research")
```

#### Background Sync Status
```python
adn_navigation("sync_status")
```

---

## Import/Export Capabilities

### Supported Platforms

#### Import Sources
- **Obsidian**: Complete vault import with wikilinks
- **Joplin**: Export directory with metadata
- **Notion**: HTML/Markdown exports
- **Evernote**: ENEX files with attachments
- **Basic Memory**: Archive format

#### Export Formats
- **PDF Books**: Professional documentation
- **HTML Websites**: Self-contained sites
- **Docsify**: Interactive documentation
- **Joplin**: Cross-platform compatibility
- **Pandoc**: Multiple formats (DOCX, EPUB, etc.)

### Import Workflows

#### Obsidian Migration
```python
# Import complete Obsidian vault
adn_import("obsidian",
    vault_path="~/obsidian-vault",
    destination_folder="imported/obsidian",
    convert_links=True)
```

#### Joplin Migration
```python
# Import Joplin export
adn_import("joplin",
    export_path="~/joplin-export",
    destination_folder="imported/joplin",
    preserve_structure=True)
```

### Export Workflows

#### PDF Book Creation
```python
# Create professional PDF book
adn_export("pdf_book",
    book_title="Research Compendium",
    source_folder="/research",
    author="Your Name")
```

#### Website Generation
```python
# Generate HTML website
adn_export("html",
    export_path="~/website",
    include_index=True,
    include_subfolders=True)
```

---

## Configuration

### Configuration Files

#### Main Config (`~/.advanced-memory/config.json`)
```json
{
  "projects": {
    "main": "C:/Users/username/Documents/notes"
  },
  "default_project": "main",
  "sync_changes": true,
  "sync_delay": 1000,
  "database_path": "~/.advanced-memory/memory.db"
}
```

#### Claude Desktop Config
```json
{
  "mcpServers": {
    "advanced-memory-mcp": {
      "command": "python",
      "args": ["-m", "advanced_memory.mcp.server"],
      "env": {
        "ADVANCED_MEMORY_HOME": "C:/Users/username"
      }
    }
  }
}
```

### Environment Variables

- `ADVANCED_MEMORY_HOME`: Base directory for database and config
- `ADVANCED_MEMORY_PROJECT`: Override active project
- `ADVANCED_MEMORY_DEBUG`: Enable debug logging

### Database Configuration

#### SQLite Settings
- **WAL Mode**: For concurrent access
- **Connection Pooling**: Optimized for MCP usage
- **FTS5**: Full-text search engine
- **Automatic Vacuum**: Maintenance

---

## Usage Patterns

### Common Workflows

#### 1. Daily Note-Taking
```python
# Create daily note
adn_content("write",
    title="2025-10-16 Daily Notes",
    content="# Daily Notes\n\n## Tasks\n- [ ] Task 1\n- [ ] Task 2",
    folder="daily")

# Add observations
adn_content("edit",
    identifier="2025-10-16 Daily Notes",
    operation="append",
    content="\n\n- [meeting] Discussed project timeline with team")
```

#### 2. Research Workflow
```python
# Create research note
adn_content("write",
    title="AI Ethics Research",
    content="# AI Ethics\n\n## Key Concepts\n- Fairness\n- Transparency",
    folder="research")

# Add related concepts
adn_content("edit",
    identifier="AI Ethics Research",
    operation="append",
    content="\n\n- builds_on [[Machine Learning Fundamentals]]\n- related_to [[Ethics in Technology]]")
```

#### 3. Project Documentation
```python
# Create project overview
adn_content("write",
    title="Project Alpha Overview",
    content="# Project Alpha\n\n## Goals\n- Goal 1\n- Goal 2",
    folder="projects")

# Link to related documents
adn_content("edit",
    identifier="Project Alpha Overview",
    operation="append",
    content="\n\n## Related Documents\n- [[Project Alpha Requirements]]\n- [[Project Alpha Timeline]]")
```

### Advanced Patterns

#### 1. Knowledge Graph Exploration
```python
# Start from a concept
adn_navigation("context", url="memory://research/ai-fundamentals")

# Follow relationships
adn_navigation("context", url="memory://research/neural-networks", depth=3)

# Find recent developments
adn_navigation("recent", timeframe="1 week", type="notes")
```

#### 2. Cross-Project Research
```python
# Search across all projects
adn_search("notes", query="machine learning")

# Search specific project
adn_search("notes", query="deep learning", project="research")

# Export research compilation
adn_export("pdf_book",
    book_title="ML Research Compilation",
    source_folder="/research",
    tag_filter="important")
```

---

## Troubleshooting

### Common Issues

#### 1. Database Locked
**Symptoms**: Sync fails with "database is locked"
**Solution**:
```bash
# Kill background processes
Get-Process | Where-Object {$_.ProcessName -match "python"} | Stop-Process
advanced-memory sync
```

#### 2. File Watcher Not Working
**Symptoms**: Files not auto-syncing
**Solution**:
```python
# Check watcher status
adn_navigation("sync_status")

# Restart Claude Desktop to reinitialize watcher
```

#### 3. Import Failures
**Symptoms**: Import tools fail
**Solution**:
- Check file paths exist
- Verify file permissions
- Check log files for detailed errors

#### 4. MCP Connection Issues
**Symptoms**: Claude can't connect to Advanced Memory
**Solution**:
1. Verify `claude_desktop_config.json` syntax
2. Check `ADVANCED_MEMORY_HOME` environment variable
3. Restart Claude Desktop
4. Check log files

### Debug Mode

Enable debug logging:
```bash
export ADVANCED_MEMORY_DEBUG=1
advanced-memory sync --verbose
```

### Log Files

- **API Logs**: `~/.advanced-memory/advanced-memory-api.log`
- **Sync Logs**: `~/.advanced-memory/sync.log`
- **MCP Logs**: Claude Desktop logs directory

---

## Development

### Project Structure

```
advanced-memory-mcp/
├── src/advanced_memory/
│   ├── mcp/                 # MCP server implementation
│   │   ├── tools/          # MCP tools
│   │   ├── prompts/        # AI prompts
│   │   └── server.py       # FastMCP server
│   ├── api/                # FastAPI REST API
│   ├── models/             # SQLAlchemy models
│   ├── services/           # Business logic
│   ├── sync/               # File synchronization
│   └── importers/          # Import/export modules
├── tests/                  # Test suite
├── docs/                   # Documentation
└── mcpb/                   # MCPB package files
```

### Development Setup

```bash
# Clone repository
git clone https://github.com/sandraschi/advanced-memory-mcp.git
cd advanced-memory-mcp

# Install in development mode
pip install -e ".[dev]"

# Run tests
pytest

# Run linting
ruff check .

# Run type checking
pyright
```

### Adding New Tools

#### 1. Create Tool File
```python
# src/advanced_memory/mcp/tools/my_tool.py
from mcp.server.fastmcp import Context
from advanced_memory.mcp.server import mcp

@mcp.tool()
async def my_tool(param: str, ctx: Context | None = None) -> str:
    '''Tool description with triple quotes.'''
    # Implementation
    return "Result"
```

#### 2. Register Tool
```python
# src/advanced_memory/mcp/tools/__init__.py
from advanced_memory.mcp.tools.my_tool import my_tool
```

#### 3. Add to Portmanteau (if applicable)
```python
# Add to appropriate portmanteau tool
# e.g., adn_content, adn_project, etc.
```

### Testing

#### Unit Tests
```bash
pytest tests/unit/
```

#### Integration Tests
```bash
pytest tests/integration/
```

#### MCP Tool Tests
```bash
pytest tests/mcp/
```

---

## API Reference

### REST API Endpoints

#### Projects
- `GET /projects/projects` - List all projects
- `POST /projects/projects` - Create new project
- `PUT /projects/{name}/default` - Set default project
- `DELETE /projects/{name}` - Delete project
- `POST /projects/{name}/sync` - Sync specific project

#### Entities
- `GET /{project}/entities` - List entities in project
- `POST /{project}/entities` - Create new entity
- `GET /{project}/entities/{id}` - Get entity details
- `PUT /{project}/entities/{id}` - Update entity
- `DELETE /{project}/entities/{id}` - Delete entity

#### Search
- `GET /{project}/search` - Search entities
- `GET /{project}/search/suggestions` - Get search suggestions

#### Import/Export
- `POST /import/obsidian` - Import Obsidian vault
- `POST /import/joplin` - Import Joplin export
- `POST /export/pdf` - Export to PDF
- `POST /export/html` - Export to HTML

### MCP Tool Parameters

#### Common Parameters
- `ctx: Context | None` - MCP context for progress reporting
- `project: str | None` - Override active project
- `verbose: bool` - Enable detailed output

#### Content Parameters
- `title: str` - Note title
- `content: str` - Markdown content
- `folder: str` - Target folder
- `tags: list[str] | None` - Tags for categorization

#### Search Parameters
- `query: str` - Search terms
- `page: int` - Pagination page
- `page_size: int` - Results per page
- `after_date: str | None` - Date filter

---

## Conclusion

Advanced Memory MCP provides a comprehensive knowledge management solution that seamlessly integrates with Claude Desktop through the Model Context Protocol. Its portmanteau tool design reduces complexity while maintaining full functionality, making it ideal for both personal knowledge management and professional documentation workflows.

### Key Benefits

- **Unified Interface**: Single toolset for all knowledge management needs
- **Semantic Understanding**: Automatic entity extraction and relationship mapping
- **Real-time Sync**: Automatic file watching and synchronization
- **Platform Agnostic**: Import from and export to multiple platforms
- **AI Integration**: Native Claude Desktop integration
- **Extensible**: Easy to add new tools and capabilities

### Getting Started

1. Install Advanced Memory MCP
2. Configure Claude Desktop
3. Create your first project
4. Start building your knowledge graph
5. Explore the portmanteau tools
6. Import existing knowledge bases
7. Export to your preferred formats

For more information, visit the [GitHub repository](https://github.com/sandraschi/advanced-memory-mcp) or check the [MCPB Building Guide](MCPB_BUILDING_GUIDE.md) for packaging and distribution.
