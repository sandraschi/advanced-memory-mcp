# Tools Reference - Complete Guide

**Comprehensive documentation for all Advanced Memory MCP tools.**

[Portmanteau Tools](#portmanteau-tools-12-total) | [Standard Tools](#standard-tools-46-total) | [Tool Mode Selection](user-guide/tool-mode-selection.md)

---

## Quick Navigation

### By Category
- [Content Management](#1-adn_content---content-management) - Write, read, view, edit, move, delete
- [Project Management](#2-adn_project---project-management) - Create, switch, configure projects
- [Zettelkasten](#3-adn_zettelmaker---zettelkasten-generation) - Generate templates, suggest topics
- [Inbox Processing](#4-adn_inbox---file-drop-processing) - Monitor and process dropped files
- [Export Operations](#5-adn_export---export-operations) - PDF, HTML, Skills, Archives
- [Import Operations](#6-adn_import---import-operations) - Obsidian, Notion, Joplin, Evernote
- [Search Operations](#7-adn_search---search-operations) - Search everywhere
- [Knowledge Operations](#8-adn_knowledge---knowledge-operations) - Analytics, research, bulk ops
- [Navigation](#9-adn_navigation---navigation--exploration) - Explore, context, status
- [Editor Integration](#10-adn_editor---editor-integration) - Notepad++, Typora, canvas
- [Help System](#11-help---documentation-system) - Interactive documentation
- [Skill Creator](#12-adn_skills_creator---skill-creation-facility) - Scaffold, validate, package skills

---

## Portmanteau Tools (12 Total)

**What are portmanteau tools?**

Consolidated tools that combine multiple related operations into a single powerful interface. Perfect for Cursor IDE (50-tool limit) while maintaining full functionality.

**Enable portmanteau-only mode**:
```json
{
  "env": {
    "ADVANCED_MEMORY_PORTMANTEAU_ONLY": "true"
  }
}
```

---

### 1. `adn_content` - Content Management

**Consolidates**: `write_note`, `read_note`, `view_note`, `view_note_rendered`, `edit_note`, `move_note`, `delete_note`

**Purpose**: Complete content lifecycle management

#### Operations

##### `write` - Create or Update Notes

```python
adn_content(
    "write",
    identifier="Project Plan",
    content="# Project Overview\n\nThis is the plan...",
    folder="projects",
    tags=["planning", "2024"],
    entity_type="note"
)
```

**Important:** For write operations, `identifier` is **REQUIRED** and should be the note **title**. Advanced Memory automatically generates the permalink from the title.

**Parameters**:
- `identifier` (str, **required**): Note title - Advanced Memory generates permalink from this
- `content` (str, required): Markdown content
- `folder` (str, required): Destination folder
- `tags`: List of tags or comma-separated string (optional)
- `entity_type`: "note" (default), "entity", "observation" (optional)

**Features**:
- Automatic `[[WikiLink]]` detection
- Semantic relationship extraction
- Tag processing
- Frontmatter generation

##### `read` - Retrieve Note Content

```python
adn_content("read", identifier="Project Plan")
```

**Features**:
- Intelligent lookup (title, permalink, memory:// URL)
- Full content with frontmatter
- Pagination support

##### `view` - Display as Formatted Artifact

```python
adn_content("view", identifier="Project Plan")
```

**Returns**: Markdown artifact for Claude Desktop display

##### `view_rendered` - Display with Rendered Mermaid

```python
adn_content("view_rendered", identifier="System Architecture")
```

**Returns**: HTML artifact with live Mermaid diagram rendering

**Features**:
- Renders flowcharts, sequence diagrams, Gantt charts
- Professional styling
- Theme support (default, dark, forest, neutral)

##### `edit` - Targeted Modifications

```python
# Append content
adn_content(
    "edit",
    identifier="Project Plan",
    edit_operation="append",
    content="\n## New Section\n\nAdditional content..."
)

# Find and replace
adn_content(
    "edit",
    identifier="Project Plan",
    edit_operation="find_replace",
    find_text="old text",
    content="new text",
    expected_replacements=1
)

# Replace section
adn_content(
    "edit",
    identifier="Project Plan",
    edit_operation="replace_section",
    section="## Summary",
    content="## Summary\n\nUpdated summary..."
)
```

**Edit operations**:
- `replace`: Full content replacement
- `append`: Add to end
- `prepend`: Add to beginning
- `find_replace`: Replace specific text
- `replace_section`: Update specific section

##### `move` - Relocate Notes

```python
adn_content(
    "move",
    identifier="Project Plan",
    destination_path="archive/2024/project-plan.md"
)
```

**Features**:
- Preserves relationships
- Updates all references
- Maintains semantic links

##### `delete` - Remove Notes

```python
adn_content("delete", identifier="Project Plan")
```

**Features**:
- Relationship cleanup
- Reference integrity maintenance
- Safety checks

---

### 2. `adn_project` - Project Management

**Consolidates**: `create_memory_project`, `switch_project`, `delete_project`, `set_default_project`, `get_current_project`, `list_memory_projects`

**Purpose**: Complete project lifecycle management

#### Operations

##### `create` - New Project

```python
adn_project(
    "create",
    project_name="work",
    project_path="/path/to/work-notes",
    set_default=False
)
```

##### `switch` - Change Active Project

```python
adn_project("switch", project_name="work")
```

##### `list` - Show All Projects

```python
adn_project("list")
```

**Returns**: All projects with status indicators (active, default)

##### `get_current` - Show Active Project

```python
adn_project("get_current")
```

**Returns**: Current project with statistics (note count, entities, relationships)

##### `set_default` - Configure Default Project

```python
adn_project("set_default", project_name="work")
```

**Effect**: This project loads on server startup

##### `delete` - Remove Project

```python
adn_project("delete", project_name="old-project")
```

**Note**: Files on disk are preserved (only removes from database)

##### `status` - Project Statistics

```python
adn_project("status", project_name="work")
```

**Returns**: Detailed stats (files, entities, relationships, activity)

##### `sync` - Force Sync

```python
adn_project("sync", project_name="work")
```

**Use**: Force file system scan and index update

---

### 3. `adn_zettelmaker` - Zettelkasten Generation

**Purpose**: AI-powered knowledge template generation

#### Operations

##### `generate` - Create Templates

```python
adn_zettelmaker(
    "generate",
    category="developer",
    topic="python-core"
)
```

**Categories**:
- `developer`: Python, Git, Docker, Testing
- `researcher`: Research methods, critical thinking
- `writer`: Storytelling, craft, publishing
- `knowledge-worker`: Productivity, PKM
- `devops`: Kubernetes, observability
- `data-scientist`: ML, statistics, data analysis
- `uiux-designer`: Design systems, Figma
- `product-manager`: Strategy, metrics, OKRs
- `entrepreneur`: Business models, growth
- `creative`: Photography, video, design
- `ai`: LLMs, prompt engineering, agents
- `philosophy`: Ethics, logic, epistemology

##### `suggest` - Get Topic Suggestions

```python
adn_zettelmaker(
    "suggest",
    category="developer",
    count=5
)
```

**Returns**: Suggested topics based on existing knowledge

##### `analyze` - Knowledge Gap Analysis

```python
adn_zettelmaker(
    "analyze",
    category="developer",
    depth=3
)
```

**Returns**: Gap analysis, recommended topics, coverage stats

##### `expand` - Extend Existing Note

```python
adn_zettelmaker(
    "expand",
    note_identifier="Python Fundamentals",
    depth=2
)
```

**Returns**: Related topics and expansion suggestions

---

### 4. `adn_inbox` - File Drop Processing

**Purpose**: Monitor and process files dropped into inbox directory

#### Operations

##### `status` - Check Inbox

```python
adn_inbox("status")
```

**Returns**: File count, types, sizes

##### `process` - Process All Files

```python
adn_inbox("process")
```

**Supported formats**:
- `.md` - Markdown (direct import)
- `.docx` - Word documents (Pandoc conversion)
- `.html` - HTML files (Pandoc conversion)
- `.pdf` - PDF documents (text extraction)
- `.txt` - Text files (markdown wrapper)

##### `info` - Inbox Information

```python
adn_inbox("info")
```

**Returns**: Inbox directory path, supported formats, configuration

---

### 5. `adn_export` - Export Operations

**Consolidates**: `export_pandoc`, `export_docsify`, `export_html_notes`, `export_joplin_notes`, `make_pdf_book`, `export_to_archive`

**Purpose**: Export notes to various formats

#### Operations

##### `pandoc` - Universal Document Export

```python
adn_export(
    "pandoc",
    export_path="output/document.pdf",
    format_type="pdf",
    source_folder="/",
    pdf_engine="pdflatex",
    toc=True
)
```

**Formats**: PDF, DOCX, HTML, ODT, RTF, TEX, EPUB, TXT, and 40+ more

**Requirements**: ✅ Pandoc auto-installs on first use! (~100MB, one-time)  
**For PDF**: LaTeX needed ([MiKTeX](https://miktex.org/) / [TinyTeX](https://yihui.org/tinytex/))

See [Pandoc Auto-Install Guide](user-guide/PANDOC_AUTO_INSTALL.md)

##### `docsify` - Documentation Website

```python
adn_export(
    "docsify",
    export_path="docs-site/",
    source_folder="/",
    site_title="Knowledge Base",
    enable_pagination=True,
    enable_theme_toggle=True
)
```

**Creates**: Professional documentation website with search, TOC, navigation

##### `html` - Standalone HTML Website

```python
adn_export(
    "html",
    export_path="website/",
    source_folder="/projects",
    include_index=True
)
```

**Features**: Mermaid rendering, search, responsive design

##### `joplin` - Joplin-Compatible Export

```python
adn_export(
    "joplin",
    export_path="joplin-export/",
    create_notebooks=True
)
```

**Creates**: Markdown + JSON metadata for Joplin import

##### `pdf_book` - Professional PDF Book

```python
adn_export(
    "pdf_book",
    book_title="Research Papers 2024",
    source_folder="/research",
    tag_filter="published",
    author="Your Name"
)
```

**Features**: Title page, TOC, chapters, professional formatting

##### `claude_skills` - Export as Claude Skills

```python
adn_export(
    "claude_skills",
    export_path="~/claude-skills/",
    source_folder="/zettelkasten"
)
```

**Creates**: SKILL.md files with Anthropic frontmatter format

##### `archive` - Complete Backup

```python
adn_export(
    "archive",
    export_path="backup.zip",
    include_projects=["work", "personal"],
    exclude_tags=["draft"]
)
```

**Creates**: Complete system archive (database + files)

---

### 6. `adn_import` - Import Operations

**Consolidates**: `load_obsidian_vault`, `load_joplin_vault`, `load_notion_export`, `load_evernote_export`, `import_from_archive`, `load_obsidian_canvas`

**Purpose**: Import notes from external systems

#### Operations

##### `obsidian` - Import Obsidian Vault

```python
adn_import(
    "obsidian",
    source_path="/path/to/vault",
    destination_folder="imported/obsidian",
    preserve_structure=True,
    convert_links=True,
    include_attachments=True
)
```

**Features**: WikiLink conversion, attachment import, folder structure

##### `joplin` - Import Joplin Export

```python
adn_import(
    "joplin",
    source_path="/path/to/joplin-export",
    destination_folder="imported/joplin",
    skip_existing=True
)
```

**Requirements**: Joplin export directory (.md + .json files)

##### `notion` - Import Notion Export

```python
adn_import(
    "notion",
    source_path="Notion-Export.zip",
    destination_folder="imported/notion",
    preserve_hierarchy=True
)
```

**Supports**: ZIP or directory exports, HTML or Markdown

##### `evernote` - Import Evernote ENEX

```python
adn_import(
    "evernote",
    source_path="notes.enex",
    destination_folder="imported/evernote",
    preserve_notebooks=True,
    include_attachments=True
)
```

**Features**: ENEX parsing, attachment extraction, notebook structure

##### `canvas` - Import Obsidian Canvas

```python
adn_import(
    "canvas",
    source_path="mindmap.canvas",
    destination_folder="imported/canvases",
    create_missing_files=False
)
```

**Converts**: Visual canvas to structured notes with relationships

##### `claude_skills` - Import Claude Skills

```python
adn_import(
    "claude_skills",
    source_path="~/anthropic-skills/",
    destination_folder="imported/skills",
    preserve_structure=True
)
```

**Converts**: SKILL.md files to Advanced Memory notes

##### `archive` - Restore from Backup

```python
adn_import(
    "archive",
    source_path="backup.zip",
    restore_mode="merge",
    backup_existing=True
)
```

**Modes**: overwrite, merge, skip_existing

---

### 7. `adn_search` - Search Operations

**Consolidates**: `search_notes`, `search_obsidian_vault`, `search_joplin_vault`, `search_notion_vault`, `search_evernote_vault`

**Purpose**: Search across knowledge base and external systems

#### Operations

##### `notes` - Search Advanced Memory

```python
adn_search(
    "notes",
    query="machine learning",
    types=["note"],
    entity_types=None,
    after_date="2024-01-01",
    page=1,
    page_size=10
)
```

**Features**: Full-text search, metadata filtering, date ranges

##### `obsidian` - Search External Vault

```python
adn_search(
    "obsidian",
    query="project planning",
    source_path="/path/to/vault",
    search_type="text",
    include_content=True
)
```

**Use**: Search without importing

##### `joplin` - Search Joplin Export

```python
adn_search(
    "joplin",
    query="meeting notes",
    source_path="/path/to/export",
    search_type="combined"
)
```

**Types**: text, metadata, combined

##### `notion` - Search Notion Export

```python
adn_search(
    "notion",
    query="database",
    source_path="/notion-export/",
    file_type="html"
)
```

##### `evernote` - Search ENEX Files

```python
adn_search(
    "evernote",
    query="research",
    source_path="/exports/",
    notebook_filter="Research",
    tag_filter="important"
)
```

---

### 8. `adn_knowledge` - Knowledge Operations

**Consolidates**: `knowledge_operations`, `research_orchestrator`

**Purpose**: Bulk operations, analytics, research planning

#### Operations

##### `bulk_update` - Batch Modifications

```python
adn_knowledge(
    "bulk_update",
    filters={"tags": ["draft"]},
    action={"add_tags": ["reviewed"]},
    dry_run=True
)
```

##### `tag_analytics` - Tag Analysis

```python
adn_knowledge(
    "tag_analytics",
    action={"analyze_usage": True}
)
```

**Returns**: Tag frequency, orphaned tags, suggestions

##### `consolidate_tags` - Merge Similar Tags

```python
adn_knowledge(
    "consolidate_tags",
    action={"semantic_groups": [["mcp", "mcp-server"]]}
)
```

##### `validate_content` - Quality Checks

```python
adn_knowledge(
    "validate_content",
    action={"checks": ["broken_links", "formatting"]}
)
```

##### `find_duplicates` - Detect Similar Content

```python
adn_knowledge(
    "find_duplicates",
    filters={"folder": "/research"}
)
```

##### `research_plan` - Create Research Roadmap

```python
adn_knowledge(
    "research_plan",
    topic="quantum computing",
    topic_type="technical"
)
```

**Returns**: Structured research plan with questions, methodology, sources

##### `research_methodology` - Get Research Approaches

```python
adn_knowledge(
    "research_methodology",
    topic_type="academic"
)
```

##### `project_stats` - Project Analysis

```python
adn_knowledge(
    "project_stats",
    project="work"
)
```

---

### 9. `adn_navigation` - Navigation & Exploration

**Consolidates**: `build_context`, `recent_activity`, `list_directory`, `status`, `sync_status`

**Purpose**: Explore and monitor knowledge base

#### Operations

##### `build_context` - Navigate Knowledge Graph

```python
adn_navigation(
    "build_context",
    url="memory://projects/ai",
    depth=2,
    timeframe="7d",
    max_related=10
)
```

**Returns**: Note content + relationships + recent activity

##### `recent_activity` - View Recent Changes

```python
adn_navigation(
    "recent_activity",
    timeframe="today",
    type_filter="notes"
)
```

**Timeframes**: "today", "7d", "2 days ago", "last week"

##### `list_directory` - Browse Structure

```python
adn_navigation(
    "list_directory",
    dir_name="/projects",
    depth=2,
    file_name_glob="*.md"
)
```

##### `status` - System Health

```python
adn_navigation(
    "status",
    level="basic",
    focus="sync"
)
```

**Levels**: basic, intermediate, advanced, diagnostic

##### `sync_status` - Monitor Sync

```python
adn_navigation("sync_status", project="work")
```

**Returns**: File indexing progress, errors, background operations

---

### 10. `adn_editor` - Editor Integration

**Consolidates**: `edit_in_notepadpp`, `import_from_notepadpp`, `typora_control`, `canvas`, `read_content`

**Purpose**: External editor integration and canvas creation

#### Operations

##### `notepadpp_edit` - Edit in Notepad++

```python
adn_editor(
    "notepadpp_edit",
    note_identifier="Meeting Notes",
    workspace_path="temp/",
    create_backup=True
)
```

**Free alternative to Typora** for markdown editing

##### `notepadpp_import` - Import from Notepad++

```python
adn_editor(
    "notepadpp_import",
    note_identifier="Meeting Notes",
    keep_workspace=False
)
```

##### `typora_control` - Control Typora (requires plugin)

```python
adn_editor(
    "typora_control",
    typora_operation="export",
    typora_format="pdf",
    typora_output_path="/exports/doc.pdf"
)
```

**Requirements**: obgnail/typora_plugin with json_rpc

##### `canvas_create` - Create Obsidian Canvas

```python
adn_editor(
    "canvas_create",
    nodes=[
        {"id": "1", "type": "text", "text": "Central Idea", "x": 0, "y": 0, "width": 250, "height": 100}
    ],
    edges=[
        {"id": "e1", "fromNode": "1", "toNode": "2"}
    ],
    canvas_title="Mind Map",
    canvas_folder="visuals"
)
```

**Creates**: .canvas file for visual knowledge mapping

##### `read_content` - Read Raw Files

```python
adn_editor(
    "read_content",
    path="images/diagram.png"
)
```

**Supports**: Text, images (auto-optimized), binary files

---

### 11. `help` - Documentation System

**Purpose**: Interactive documentation and guidance

#### Usage

```python
# Basic overview
help()

# Intermediate detail
help("intermediate")

# Topic-specific help
help("advanced", "semantic-net")
help("intermediate", "mermaid")
help("basic", "tools")
```

**Topics**:
- `semantic-net`: Knowledge graph concepts
- `claude`: AI integration patterns
- `tools`: Complete tool reference
- `import`: Data migration guides
- `export`: Publishing options
- `mermaid`: Diagram creation
- `obsidian`, `joplin`, `notion`, `evernote`: Platform-specific

**Levels**:
- `basic`: Quick start, essential commands
- `intermediate`: Detailed tool descriptions, workflows
- `advanced`: Technical architecture, implementation
- `expert`: Development, troubleshooting, internals

### 12. `adn_skills_creator` - Skill Creation Facility

**Purpose**: Scaffold, validate, inspect, upgrade, and package Claude skills using the modular architecture.

#### Operations

- `scaffold` – Generate a new skill folder with `SKILL.md`, `_toc.md`, modules, and placeholder resources.
- `validate` – Ensure required modules, metadata fields, and research checklist are present.
- `inspect` – Return frontmatter metadata for quick review.
- `upgrade` – Convert legacy single-file skills into the modular layout.
- `package` – Create a ZIP archive (with manifest) for distribution.

#### Usage

```python
# Create a new scaffold
adn_skills_creator(
    operation="scaffold",
    skill_name="brand-guidelines",
    output_dir="skills/company",
    category="enterprise"
)

# Validate an existing skill
adn_skills_creator(
    operation="validate",
    skill_path="skills/company/brand-guidelines"
)

# Package the skill for sharing
adn_skills_creator(
    operation="package",
    skill_path="skills/company/brand-guidelines",
    output_dir="dist"
)
```

**Outputs**:
- `success`: Boolean status.
- `data`: Result payload (paths, archives, validation issues).
- `metadata`: Operation context (skill path, action).
- On failure, structured error with actionable suggestions.

---

## Standard Tools (46 Total)

**Note**: These are individual tools included in **Full Mode** for backward compatibility. All functionality is also available through portmanteau tools.

### Content Management (7 tools)

1. **`write_note`** - Create or update notes
2. **`read_note`** - Retrieve note content
3. **`view_note`** - Display as markdown artifact
4. **`view_note_rendered`** - Display with rendered Mermaid diagrams
5. **`edit_note`** - Modify existing notes
6. **`move_note`** - Relocate notes
7. **`delete_note`** - Remove notes

### Project Management (6 tools)

8. **`create_memory_project`** - Create new project
9. **`switch_project`** - Change active project
10. **`delete_project`** - Remove project
11. **`set_default_project`** - Configure default
12. **`get_current_project`** - Show active project
13. **`list_memory_projects`** - List all projects

### Export Operations (6 tools)

14. **`export_pandoc`** - Universal document export
15. **`export_docsify`** - Documentation website
16. **`export_html_notes`** - HTML website with Mermaid
17. **`export_joplin_notes`** - Joplin-compatible export
18. **`make_pdf_book`** - PDF book generation
19. **`export_to_archive`** - Complete backup

### Import Operations (5 tools)

20. **`load_obsidian_vault`** - Import Obsidian
21. **`load_joplin_vault`** - Import Joplin
22. **`load_notion_export`** - Import Notion
23. **`load_evernote_export`** - Import Evernote ENEX
24. **`import_from_archive`** - Restore from backup
25. **`load_obsidian_canvas`** - Import canvas files

### Search Operations (5 tools)

26. **`search_notes`** - Search Advanced Memory
27. **`search_obsidian_vault`** - Search external Obsidian
28. **`search_joplin_vault`** - Search external Joplin
29. **`search_notion_vault`** - Search external Notion
30. **`search_evernote_vault`** - Search ENEX files

### Knowledge Operations (2 tools)

31. **`knowledge_operations`** - Bulk ops, analytics
32. **`research_orchestrator`** - Research planning

### Navigation (5 tools)

33. **`build_context`** - Navigate knowledge graph
34. **`recent_activity`** - View recent changes
35. **`list_directory`** - Browse structure
36. **`status`** - System health
37. **`sync_status`** - Monitor synchronization

### Editor Integration (5 tools)

38. **`edit_in_notepadpp`** - Edit with Notepad++
39. **`import_from_notepadpp`** - Import from Notepad++
40. **`typora_control`** - Control Typora
41. **`canvas`** - Create Obsidian canvas
42. **`read_content`** - Read raw files

### Utility (4 tools)

43. **`help`** - Documentation (also in portmanteau mode)
44. **`export_docsify_enhanced`** - Enhanced Docsify export
45. **`knowledge_operations`** - Advanced operations
46. **`research_orchestrator`** - Research automation

---

## Comparison Matrix

| Feature | Portmanteau Mode | Full Mode |
|---------|------------------|-----------|
| **Tool Count** | 11 | ~50+ |
| **Content Ops** | ✅ `adn_content` (1 tool) | ✅ 7 individual tools |
| **Projects** | ✅ `adn_project` (1 tool) | ✅ 6 individual tools |
| **Export** | ✅ `adn_export` (1 tool) | ✅ 6 individual tools |
| **Import** | ✅ `adn_import` (1 tool) | ✅ 5 individual tools |
| **Search** | ✅ `adn_search` (1 tool) | ✅ 5 individual tools |
| **Functionality** | ✅ 100% | ✅ 100% |
| **Cursor Compatible** | ✅ Yes | ❌ Exceeds 50 limit |
| **Backward Compatible** | ✅ Via portmanteau | ✅ Direct |

---

## Tool Mode Selection

Choose which tools to expose:

### Portmanteau Mode (11 tools)

**For**: Cursor IDE, restrictive clients

**Setup**:
```json
{
  "env": {
    "ADVANCED_MEMORY_PORTMANTEAU_ONLY": "true"
  }
}
```

### Full Mode (~50+ tools)

**For**: Claude Desktop, API usage

**Setup**: Default (no configuration needed)

**See**: [Tool Mode Selection Guide](user-guide/tool-mode-selection.md)

---

## Additional Resources

- **[Quick Start Guide](QUICK_START_GUIDE.md)** - Get started quickly
- **[Tool Mode Selection](user-guide/tool-mode-selection.md)** - Choose your mode
- **[User Guides](user-guide/)** - Feature-specific guides
- **[Technical Documentation](TECHNICAL.md)** - Architecture details
- **[Troubleshooting](TROUBLESHOOTING_GUIDE.md)** - Problem solving

---

## Examples

See [User Guide Examples](user-guide/examples/) for:
- Content management workflows
- Project organization strategies
- Import/export recipes
- Search patterns
- Knowledge graph navigation
- Editor integration setups

---

**Last Updated**: 2024-10-20  
**Version**: 1.0.0b3+

