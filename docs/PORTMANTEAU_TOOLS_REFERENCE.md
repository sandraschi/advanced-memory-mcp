# Advanced Memory MCP - Portmanteau Tools Reference

**Version:** 1.0.0b2
**Purpose:** Complete reference for all 12 portmanteau tools

## Overview

Advanced Memory MCP uses **portmanteau tools** to consolidate 50+ individual tools into 12 powerful, consistent interfaces. This reduces complexity while maintaining full functionality.

---

## adn_content - Content Management (Primary for Notes)

**Consolidates:** write_note, read_note, edit_note, move_note, delete_note, view_note, quick, daily, suggest_tags, summarize, enhance, generate

**Available in all modes.** Primary tool for creating, reading, and editing notes with full semantic processing.

### Operations

#### write
Create or update a note.

```python
adn_content(operation="write",
    identifier="Meeting Notes",
    content="# Meeting\n\n## Attendees\n- Alice\n- Bob",
    folder="meetings",
    tags=["work", "important"])
```

**Important:** For write operations, the `identifier` parameter is **REQUIRED** and should be the note **title**. Advanced Memory automatically generates the permalink from the title.

**Parameters:**
- `identifier` (str, **required**): Note title - Advanced Memory will generate the permalink
- `content` (str, required): Markdown content
- `folder` (str, required): Target folder
- `tags` (list[str], optional): Tags for categorization
- `entity_type` (str, optional): "note" (default), "entity", "observation"

#### read
Read a note by identifier.

```python
adn_content(operation="read", identifier="Meeting Notes")
adn_content(operation="read", identifier="memory://meetings/meeting-notes")
```

#### quick
Ultra-fast note creation with smart defaults (auto-folder, auto-title, auto-tags).

```python
adn_content(operation="quick", content="Quick thought or capture...")
```

#### daily
Create or append to today's daily journal note.

```python
adn_content(operation="daily", content="Today's journal entry...")
```

#### edit
Edit a note incrementally (append, prepend, find_replace, replace_section).

```python
adn_content(operation="edit",
    identifier="Meeting Notes",
    edit_operation="append",
    content="\n\n## Action Items\n- [ ] Task 1")

adn_content(operation="edit",
    identifier="Meeting Notes",
    edit_operation="find_replace",
    find_text="old text",
    content="new text")
```

#### move
Move a note to a new location.

```python
adn_content(operation="move",
    identifier="Meeting Notes",
    destination_path="archive/meetings/meeting-notes")
```

#### delete
Delete a note from the knowledge base.

```python
adn_content(operation="delete", identifier="Meeting Notes")
```

#### view / view_rendered
Display a note as a formatted artifact.

```python
adn_content(operation="view", identifier="Meeting Notes")
```

#### enhance
LLM-powered note enhancement. Batch-upgrade weak-LLM notes with a SOTA LLM. Supports typos, factual errors, biographical updates, structure, and targeted expansion.

```python
# Default: fix typos, factual errors, biographical death dates, improve style
adn_content(operation="enhance", identifier="strawberry-facts")

# Expand runt notes with examples and context
adn_content(operation="enhance", identifier="outline",
    add_examples=True, add_context=True, expand_sections=True)

# Update stale tech notes (e.g. FastMCP 2.10 -> 2.14)
adn_content(operation="enhance", identifier="fastmcp-guide",
    update_stale_tech=True)

# Custom instruction via content param (powerful)
adn_content(operation="enhance", identifier="biography",
    content="Person died 2024-03-15, add that")
adn_content(operation="enhance", identifier="tech-note",
    content="We use FastMCP 2.14.3, Python 3.13")
```

**Parameters:**
- `update_content` (bool, default True): Fix typos, factual errors, biographical updates (e.g. death dates)
- `update_style` (bool, default True): Improve clarity, structure, readability
- `add_bibliography` (bool, default False): Add References/Bibliography section
- `add_examples` (bool, default False): Add concrete examples, illustrations, case studies
- `add_context` (bool, default False): Add background, definitions, "why it matters"
- `expand_sections` (bool, default False): Turn bullet points into full paragraphs; runt -> full notes
- `update_stale_tech` (bool, default False): Update outdated lib/tool versions; flag uncertainty
- `content` (str, optional): Custom instruction passed to LLM (scope, facts, version lock, tone)

#### suggest_tags
LLM-powered semantic tag suggestions.

```python
adn_content(operation="suggest_tags", identifier="Meeting Notes")
```

#### summarize
LLM-powered note summarization.

```python
adn_content(operation="summarize", identifier="Long Report")
```

#### generate
LLM-powered content generation for new notes.

```python
adn_content(operation="generate", content="Python async patterns", folder="learning")
```

#### find_runts
Find short/runt notes (content under max_content_length chars) for batch enhancement.

```python
# Default: notes under 500 chars
adn_content(operation="find_runts")

# Custom threshold and folder
adn_content(operation="find_runts", max_content_length=800, folder="content")
```

**Parameters:** `max_content_length` (default 500), `folder` (optional)

#### find_junk
LLM quality assessment of notes. Returns narrative or structured JSON.

```python
# Narrative (default)
adn_content(operation="find_junk", folder="content")

# Structured JSON with criteria scores
adn_content(operation="find_junk", assessment_format="structured", folder="content")
```

**Parameters:** `assessment_format` ("narrative" | "structured"), `folder` (optional)

**Structured output:** `{"permalink", "overall": "good|fair|poor", "criteria": {"clarity", "completeness", "structure", "needs_expansion"}, "summary"}`

---

## adn_knowledge - Knowledge Operations

**Consolidates:** search_notes, list_directory, build_context, recent_activity, status, plus basic create/read/update/delete/move

Complementary to adn_content. Use for search, list, context building, activity, and status.

### Operations

#### create
Create a note (alternative to adn_content write; simpler interface).

```python
adn_knowledge(operation="create",
    title="Meeting Notes",
    content="# Meeting\n\nContent...",
    folder="meetings",
    tags=["work"])
```

#### read
Read a note by identifier.

```python
adn_knowledge(operation="read", identifier="Meeting Notes")
```

#### update / delete / move
Same as adn_content but with different parameter names.

#### search
Search notes.

```python
adn_knowledge(operation="search", query="machine learning")
```

#### list
List directory contents.

```python
adn_knowledge(operation="list", path="research/", depth=2)
```

#### navigate / context
Build context from a note (knowledge graph).

```python
adn_knowledge(operation="context", identifier="AI Fundamentals", depth=2)
```

#### activity
Get recent activity.

```python
adn_knowledge(operation="activity", timeframe="1 week")
```

#### status
Get system status.

```python
adn_knowledge(operation="status")
```

---

## adn_project - Project Management

**Consolidates:** create, switch, delete, set_default, get_current, list, sync, status

### Operations

#### create
Create a new project.

```python
adn_project("create",
    project_name="research",
    project_path="~/Documents/research",
    set_default=False)
```

**Parameters:**
- `project_name` (str): Project name
- `project_path` (str): File system path
- `set_default` (bool, optional): Set as default project

#### list
List all available projects.

```python
adn_project("list")
```

#### switch
Change the active project.

```python
adn_project("switch", project_name="research")
```

**Parameters:**
- `project_name` (str): Project name

#### sync
Sync a specific project without changing default.

```python
adn_project("sync", project_name="research")
```

**Parameters:**
- `project_name` (str): Project name

#### status
Get detailed statistics for a project.

```python
adn_project("status", project_name="research")
```

**Parameters:**
- `project_name` (str): Project name

#### set_default
Set a project as the default.

```python
adn_project("set_default", project_name="research")
```

**Parameters:**
- `project_name` (str): Project name

#### get_current
Display the currently active project.

```python
adn_project("get_current")
```

#### delete
Remove a project from configuration.

```python
adn_project("delete", project_name="old-project")
```

**Parameters:**
- `project_name` (str): Project name

---

## adn_search - Search & Discovery

**Consolidates:** search_notes, search_obsidian_vault, search_joplin_vault, search_notion_vault, search_evernote_vault

### Operations

#### notes
Search within Advanced Memory notes.

```python
adn_search("notes",
    query="machine learning",
    project="research",
    page=1,
    page_size=10)
```

**Parameters:**
- `query` (str): Search terms
- `project` (str, optional): Project to search
- `page` (int, optional): Pagination page
- `page_size` (int, optional): Results per page

#### obsidian
Search external Obsidian vault.

```python
adn_search("obsidian",
    vault_path="~/obsidian-vault",
    query="AI research",
    max_results=20)
```

**Parameters:**
- `vault_path` (str): Path to Obsidian vault
- `query` (str): Search terms
- `max_results` (int, optional): Maximum results

#### joplin
Search external Joplin export.

```python
adn_search("joplin",
    vault_path="~/joplin-export",
    query="meeting notes",
    search_type="combined")
```

**Parameters:**
- `vault_path` (str): Path to Joplin export
- `query` (str): Search terms
- `search_type` (str, optional): "text", "metadata", "combined"

#### notion
Search external Notion export.

```python
adn_search("notion",
    vault_path="~/notion-export",
    query="project documentation")
```

**Parameters:**
- `vault_path` (str): Path to Notion export
- `query` (str): Search terms

#### evernote
Search external Evernote ENEX files.

```python
adn_search("evernote",
    vault_path="~/evernote-export",
    query="important notes",
    notebook_filter="Work")
```

**Parameters:**
- `vault_path` (str): Path to ENEX file/directory
- `query` (str): Search terms
- `notebook_filter` (str, optional): Filter by notebook

---

## adn_navigation - Knowledge Graph Navigation

**Consolidates:** build_context, recent_activity, list_directory, status, sync_status

### Operations

#### context
Build context from memory URLs.

```python
adn_navigation("context",
    url="memory://research/ai-fundamentals",
    depth=2,
    timeframe="1 week")
```

**Parameters:**
- `url` (str): Memory URL or pattern
- `depth` (int, optional): Relationship exploration depth
- `timeframe` (str, optional): Time window for filtering

#### recent
Get recent activity.

```python
adn_navigation("recent",
    timeframe="2 days",
    type="notes",
    max_related=10)
```

**Parameters:**
- `timeframe` (str): Time window ("1d", "1 week", "today")
- `type` (str, optional): Content type filter
- `max_related` (int, optional): Maximum related items

#### directory
List directory contents.

```python
adn_navigation("directory",
    dir_name="/research",
    depth=2,
    file_name_glob="*.md")
```

**Parameters:**
- `dir_name` (str): Directory path
- `depth` (int, optional): Recursion depth
- `file_name_glob` (str, optional): File pattern filter

#### status
Get system status.

```python
adn_navigation("status",
    level="basic",
    focus="sync")
```

**Parameters:**
- `level` (str, optional): Detail level ("basic", "intermediate", "advanced")
- `focus` (str, optional): Focus area ("sync", "tools", "system")

#### sync_status
Get file synchronization status.

```python
adn_navigation("sync_status", project="research")
```

**Parameters:**
- `project` (str, optional): Specific project to check

---

## adn_import - Import from Platforms

**Consolidates:** load_obsidian_vault, load_joplin_vault, load_notion_export, load_evernote_export, import_from_archive, load_obsidian_canvas

### Operations

#### obsidian
Import Obsidian vault.

```python
adn_import("obsidian",
    vault_path="~/obsidian-vault",
    destination_folder="imported/obsidian",
    convert_links=True,
    include_attachments=False)
```

**Parameters:**
- `vault_path` (str): Path to Obsidian vault
- `destination_folder` (str): Target folder
- `convert_links` (bool, optional): Convert [[WikiLinks]]
- `include_attachments` (bool, optional): Import media files

#### joplin
Import Joplin export.

```python
adn_import("joplin",
    export_path="~/joplin-export",
    destination_folder="imported/joplin",
    preserve_structure=True,
    convert_links=True)
```

**Parameters:**
- `export_path` (str): Path to Joplin export
- `destination_folder` (str): Target folder
- `preserve_structure` (bool, optional): Maintain hierarchy
- `convert_links` (bool, optional): Convert Joplin links

#### notion
Import Notion export.

```python
adn_import("notion",
    export_path="~/notion-export",
    folder="imported/notion",
    preserve_hierarchy=True)
```

**Parameters:**
- `export_path` (str): Path to Notion export
- `folder` (str): Target folder
- `preserve_hierarchy` (bool, optional): Maintain page structure

#### evernote
Import Evernote ENEX files.

```python
adn_import("evernote",
    export_path="~/notes.enex",
    folder="imported/evernote",
    include_attachments=True,
    preserve_notebooks=True)
```

**Parameters:**
- `export_path` (str): Path to ENEX file
- `folder` (str): Target folder
- `include_attachments` (bool, optional): Extract media files
- `preserve_notebooks` (bool, optional): Maintain notebook hierarchy

#### archive
Import from Advanced Memory archive.

```python
adn_import("archive",
    archive_path="~/backup.zip",
    restore_mode="merge",
    backup_existing=True)
```

**Parameters:**
- `archive_path` (str): Path to archive file
- `restore_mode` (str, optional): "overwrite", "merge", "skip_existing"
- `backup_existing` (bool, optional): Backup current data

#### canvas
Import Obsidian canvas files.

```python
adn_import("canvas",
    canvas_path="~/mindmap.canvas",
    destination_folder="imported/canvases",
    create_missing_files=False)
```

**Parameters:**
- `canvas_path` (str): Path to .canvas file
- `destination_folder` (str): Target folder
- `create_missing_files` (bool, optional): Create placeholder notes

---

## adn_export - Export to Formats

**Consolidates:** export_pandoc, export_docsify, export_html_notes, export_joplin_notes, make_pdf_book, export_to_archive, export_evernote_compatible, export_notion_compatible

### Operations

#### pdf_book
Create PDF book from notes.

```python
adn_export("pdf_book",
    book_title="Research Compendium",
    source_folder="/research",
    author="Your Name",
    tag_filter="important")
```

**Parameters:**
- `book_title` (str): Book title
- `source_folder` (str, optional): Source folder
- `author` (str, optional): Author name
- `tag_filter` (str, optional): Filter by tags

#### html
Export to HTML website.

```python
adn_export("html",
    export_path="~/website",
    include_index=True,
    include_subfolders=True)
```

**Parameters:**
- `export_path` (str): Output directory
- `include_index` (bool, optional): Generate index page
- `include_subfolders` (bool, optional): Include subfolders

#### docsify
Export to Docsify documentation.

```python
adn_export("docsify",
    export_path="~/docs",
    site_title="Knowledge Base",
    enable_pagination=True,
    enable_theme_toggle=True)
```

**Parameters:**
- `export_path` (str): Output directory
- `site_title` (str, optional): Site title
- `enable_pagination` (bool, optional): Enable pagination
- `enable_theme_toggle` (bool, optional): Enable theme toggle

#### joplin
Export to Joplin format.

```python
adn_export("joplin",
    export_path="~/joplin-export",
    create_notebooks=True,
    include_subfolders=True)
```

**Parameters:**
- `export_path` (str): Output directory
- `create_notebooks` (bool, optional): Create notebook structure
- `include_subfolders` (bool, optional): Include subfolders

#### pandoc
Export using Pandoc.

```python
adn_export("pandoc",
    export_path="~/export",
    format_type="pdf",
    toc=True,
    highlight_style="tango")
```

**Parameters:**
- `export_path` (str): Output directory
- `format_type` (str): Output format ("pdf", "html", "docx", etc.)
- `toc` (bool, optional): Generate table of contents
- `highlight_style` (str, optional): Syntax highlighting style

#### archive
Export complete archive.

```python
adn_export("archive",
    archive_path="~/backup.zip",
    include_projects=["main", "research"],
    exclude_tags=["draft", "temp"])
```

**Parameters:**
- `archive_path` (str): Archive file path
- `include_projects` (list[str], optional): Projects to include
- `exclude_tags` (list[str], optional): Tags to exclude

---

## adn_knowledge - Advanced Knowledge Management

**Consolidates:** knowledge_operations, research_orchestrator

### Operations

#### bulk_update
Batch update multiple notes.

```python
adn_knowledge("bulk_update",
    filters={"tags": ["draft"]},
    action={"add_tags": ["reviewed"]},
    limit=100)
```

**Parameters:**
- `filters` (dict): Filter criteria
- `action` (dict): Update actions
- `limit` (int, optional): Maximum items to process

#### tag_analytics
Analyze tag usage.

```python
adn_knowledge("tag_analytics",
    action="analyze_usage")
```

#### consolidate_tags
Merge similar tags.

```python
adn_knowledge("consolidate_tags",
    semantic_groups=[["mcp", "mcp-server"], ["ai", "artificial-intelligence"]])
```

#### research_plan
Create research roadmap.

```python
adn_knowledge("research",
    operation="research_plan",
    topic="quantum computing",
    research_type="technical")
```

**Parameters:**
- `operation` (str): Research operation
- `topic` (str): Research topic
- `research_type` (str, optional): Type of research

#### validate_content
Check note quality.

```python
adn_knowledge("validate_content",
    checks=["broken_links", "formatting"],
    dry_run=True)
```

---

## adn_editor - External Editor Integration

**Consolidates:** edit_in_notepadpp, import_from_notepadpp, typora_control, canvas, read_content

### Operations

#### notepadpp
Edit note in Notepad++.

```python
adn_editor("notepadpp",
    note_identifier="Meeting Notes",
    workspace_path="~/notepadpp-workspace",
    create_backup=True)
```

**Parameters:**
- `note_identifier` (str): Note to edit
- `workspace_path` (str, optional): Workspace directory
- `create_backup` (bool, optional): Create backup

#### typora
Control Typora editor.

```python
adn_editor("typora",
    operation="export",
    format="pdf",
    output_path="~/export.pdf")
```

**Parameters:**
- `operation` (str): Typora operation
- `format` (str, optional): Export format
- `output_path` (str, optional): Output path

#### canvas
Create Obsidian canvas.

```python
adn_editor("canvas",
    title="Project Overview",
    nodes=[
        {"id": "1", "text": "Project Alpha", "x": 100, "y": 100},
        {"id": "2", "text": "Requirements", "x": 200, "y": 200}
    ],
    edges=[
        {"from": "1", "to": "2", "label": "has"}
    ],
    folder="visualizations")
```

**Parameters:**
- `title` (str): Canvas title
- `nodes` (list): Canvas nodes
- `edges` (list): Canvas edges
- `folder` (str): Target folder

#### read_content
Read raw file content.

```python
adn_editor("read_content",
    path="~/documents/image.png",
    project="main")
```

**Parameters:**
- `path` (str): File path
- `project` (str, optional): Project context

---

## Common Parameters

### Context Parameters
- `ctx: Context | None` - MCP context for progress reporting
- `project: str | None` - Override active project

### Pagination Parameters
- `page: int` - Page number (default: 1)
- `page_size: int` - Items per page (default: 10)

### Filter Parameters
- `after_date: str | None` - Date filter ("7d", "2024-01-01")
- `tags: list[str] | None` - Tag filters
- `folder: str | None` - Folder filter

### Output Parameters
- `verbose: bool` - Enable detailed output
- `dry_run: bool` - Preview changes without applying

---

## Error Handling

All portmanteau tools return structured error messages:

```python
# Success
"✅ Operation completed successfully\n\nDetails: ..."

# Error
"❌ Error: Description\n\nSuggestion: Try this instead\n\n<!-- Project: current-project -->"
```

## Best Practices

1. **Use Portmanteau Tools**: Prefer consolidated tools over individual ones
2. **Check Project Context**: Verify active project before operations
3. **Handle Errors Gracefully**: Check return values for error indicators
4. **Use Pagination**: For large result sets, use page/page_size parameters
5. **Backup Before Bulk Operations**: Use dry_run for destructive operations

---

---

## adn_skills_creator - Skill Creation Facility

**Purpose:** Mirror Anthropic’s skill-creator workflow (scaffold → validate → inspect → upgrade → package) while enforcing Advanced Memory’s modular requirements.

### Operations

#### scaffold
Generate a new modular skill skeleton.

```python
adn_skills_creator(
    operation="scaffold",
    skill_name="brand-guidelines",
    output_dir="skills/company",
    category="enterprise"
)
```

**Parameters:**
- `skill_name` (str, **required**): Hyphen-case name for the new skill.
- `output_dir` (str, optional): Target directory (default: `skills/`).
- `category` (str, optional): Metadata category.
- `confidence` (str, optional): Initial confidence (`low`, `medium`, `high`).
- `overwrite` (bool, optional): Replace existing directory if present.

#### validate
Ensure the skill complies with mandatory modules and metadata.

```python
adn_skills_creator(
    operation="validate",
    skill_path="skills/company/brand-guidelines"
)
```

**Returns:** Validation status plus list of issues (path, issue, fix).

#### inspect
Retrieve frontmatter metadata for quick review.

```python
adn_skills_creator(
    operation="inspect",
    skill_path="skills/company/brand-guidelines"
)
```

#### upgrade
Convert a legacy single-file skill into the modular format.

```python
adn_skills_creator(
    operation="upgrade",
    skill_path="skills/legacy/old-skill"
)
```

#### package
Create a distributable ZIP archive (with manifest) after validation passes.

```python
adn_skills_creator(
    operation="package",
    skill_path="skills/company/brand-guidelines",
    output_dir="dist"
)
```

**Outputs:** `dist/brand-guidelines.zip` plus `dist/brand-guidelines.manifest.json`.

### CLI Equivalents
```bash
uv run am-skill-creator scaffold brand-guidelines --output-dir skills/company
uv run am-skill-creator validate skills/company/brand-guidelines
uv run am-skill-creator package skills/company/brand-guidelines --output-dir dist
uv run am-skill-creator upgrade skills/legacy/old-skill
```

### Best Practices
1. Complete the research checklist and update `metadata.sources` before packaging.
2. Store generated manifests alongside release notes for traceability.
3. Integrate validation into CI/CD (call the CLI from pre-commit or pipeline scripts).

---

This reference covers all 12 portmanteau tools with their operations, parameters, and examples. For more details, see the [Complete Guide](ADVANCED_MEMORY_MCP_COMPLETE_GUIDE.md).
