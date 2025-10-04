# Advanced Memory MCP - Complete User Guide

## Overview

Advanced Memory MCP is a powerful knowledge management system that consolidates 40+ individual tools into 8 comprehensive portmanteau tools. This guide will help you master all the capabilities.

## 🎯 Portmanteau Tools (Recommended)

### 1. Content Management (`adn_content`)
**Purpose**: Create, read, edit, move, and delete notes and content.

**Operations**:
- `write` - Create new notes or update existing ones
- `read` - Retrieve note content by identifier
- `view` - Display formatted note content
- `edit` - Modify existing notes (append, prepend, find/replace, section replace)
- `move` - Relocate notes between folders
- `delete` - Remove notes from the knowledge base

**Examples**:
```python
# Create a new note
adn_content("write", identifier="Project Planning", content="# Project Planning\n\n## Goals\n- Complete feature X\n- Test system Y", folder="projects", tags=["planning", "urgent"])

# Read a note
adn_content("read", identifier="Project Planning")

# Edit a note (append content)
adn_content("edit", identifier="Project Planning", edit_operation="append", content="\n\n## Next Steps\n- Review with team\n- Schedule demo")

# Move a note
adn_content("move", identifier="Project Planning", destination_path="archive/completed-projects/project-planning.md")

# Delete a note
adn_content("delete", identifier="Old Meeting Notes")
```

### 2. Project Management (`adn_project`)
**Purpose**: Manage multiple knowledge base projects and switch between them.

**Operations**:
- `create` - Create new projects
- `switch` - Change active project
- `delete` - Remove projects
- `set_default` - Set default project
- `get_current` - Get current project info
- `list` - List all available projects

**Examples**:
```python
# List all projects
adn_project("list")

# Create a new project
adn_project("create", project_name="work-notes", project_path="/Users/me/Documents/work-notes")

# Switch to a project
adn_project("switch", project_name="work-notes")

# Set default project
adn_project("set_default", project_name="work-notes")

# Get current project info
adn_project("get_current")
```

### 3. Export Management (`adn_export`)
**Purpose**: Export your knowledge base to various formats.

**Operations**:
- `pandoc` - Export using Pandoc (PDF, HTML, DOCX, etc.)
- `docsify` - Create Docsify documentation website
- `html` - Generate standalone HTML files
- `joplin` - Export to Joplin format
- `pdf_book` - Create PDF books with TOC
- `archive` - Create backup archives
- `evernote` - Export to Evernote format
- `notion` - Export to Notion format

**Examples**:
```python
# Export to PDF using Pandoc
adn_export("pandoc", export_path="output.pdf", format_type="pdf", source_folder="/notes")

# Create Docsify website
adn_export("docsify", export_path="docs-website/", site_title="My Knowledge Base")

# Export to HTML
adn_export("html", export_path="html-export/", include_index=True)

# Create PDF book
adn_export("pdf_book", book_title="My Research Notes", source_folder="/research", author="Your Name")

# Export to Joplin
adn_export("joplin", export_path="joplin-export/", source_folder="/notes")
```

### 4. Import Management (`adn_import`)
**Purpose**: Import knowledge from other systems into Advanced Memory.

**Operations**:
- `obsidian` - Import Obsidian vaults
- `joplin` - Import Joplin exports
- `notion` - Import Notion exports
- `evernote` - Import Evernote exports
- `archive` - Import from backup archives
- `canvas` - Import Obsidian canvas files

**Examples**:
```python
# Import Obsidian vault
adn_import("obsidian", source_path="/path/to/obsidian-vault", destination_folder="imported/obsidian")

# Import Joplin export
adn_import("joplin", source_path="/path/to/joplin-export", destination_folder="imported/joplin")

# Import Notion export
adn_import("notion", source_path="/path/to/notion-export.zip", destination_folder="imported/notion")

# Import Evernote export
adn_import("evernote", source_path="/path/to/notes.enex", destination_folder="imported/evernote")

# Import from archive
adn_import("archive", source_path="backup.zip", destination_folder="restored/")
```

### 5. Search Management (`adn_search`)
**Purpose**: Search across your knowledge base and external systems.

**Operations**:
- `notes` - Search within Advanced Memory notes
- `obsidian` - Search external Obsidian vaults
- `joplin` - Search external Joplin exports
- `notion` - Search external Notion exports
- `evernote` - Search external Evernote exports

**Examples**:
```python
# Search notes in Advanced Memory
adn_search("notes", query="machine learning", search_type="full_text", page=1, page_size=10)

# Search with tags
adn_search("notes", query="tag:urgent", search_type="tags")

# Search external Obsidian vault
adn_search("obsidian", query="project planning", source_path="/path/to/vault")

# Search external Joplin export
adn_search("joplin", query="meeting notes", source_path="/path/to/joplin-export")
```

### 6. Knowledge Management (`adn_knowledge`)
**Purpose**: Advanced knowledge operations, analytics, and research orchestration.

**Operations**:
- `bulk_update` - Update multiple notes at once
- `tag_analytics` - Analyze tag usage and statistics
- `consolidate_tags` - Merge similar tags
- `validate_content` - Check note quality
- `research_plan` - Create research plans
- `research_methodology` - Get research approaches
- `research_questions` - Generate research questions
- `note_blueprint` - Design note structures
- `research_workflow` - Execute research workflows
- `project_stats` - Analyze project content
- `find_duplicates` - Identify duplicate content

**Examples**:
```python
# Analyze tag usage
adn_knowledge("tag_analytics", action={"analyze_usage": True})

# Consolidate similar tags
adn_knowledge("consolidate_tags", semantic_groups=[["mcp", "mcp-server"], ["ai", "artificial-intelligence"]])

# Create research plan
adn_knowledge("research_plan", topic="quantum computing", research_type="technical")

# Validate content quality
adn_knowledge("validate_content", checks=["broken_links", "formatting"])

# Get project statistics
adn_knowledge("project_stats", filters={"project": "work-notes"})

# Find duplicate content
adn_knowledge("find_duplicates", limit=50)
```

### 7. Navigation Management (`adn_navigation`)
**Purpose**: Navigate and explore your knowledge base.

**Operations**:
- `build_context` - Build context from memory URLs
- `recent_activity` - Get recent changes
- `list_directory` - List directory contents
- `status` - Get system status
- `sync_status` - Check sync status

**Examples**:
```python
# Build context from memory URL
adn_navigation("build_context", url="memory://projects/ai", depth=2, timeframe="7d")

# Get recent activity
adn_navigation("recent_activity", timeframe="today", type_filter="notes")

# List directory contents
adn_navigation("list_directory", dir_name="/projects", depth=2, file_name_glob="*.md")

# Get system status
adn_navigation("status", level="basic", focus="health")

# Check sync status
adn_navigation("sync_status")
```

### 8. Editor Management (`adn_editor`)
**Purpose**: Integrate with external editors and create visual content.

**Operations**:
- `notepadpp_edit` - Edit notes in Notepad++
- `notepadpp_import` - Import edited content back
- `typora_control` - Control Typora editor
- `canvas_create` - Create Obsidian canvas files
- `read_content` - Read raw file content

**Examples**:
```python
# Edit note in Notepad++
adn_editor("notepadpp_edit", note_identifier="Meeting Notes", workspace_path="temp/")

# Import edited content back
adn_editor("notepadpp_import", note_identifier="Meeting Notes")

# Control Typora
adn_editor("typora_control", typora_operation="export", typora_format="pdf", output_path="export.pdf")

# Create canvas visualization
adn_editor("canvas_create", nodes=[{"id": "node1", "text": "Main Topic"}, {"id": "node2", "text": "Sub Topic"}], edges=[{"from": "node1", "to": "node2"}], title="My Canvas", folder="visualizations")

# Read raw content
adn_editor("read_content", path="/path/to/file.md")
```

## 🔄 Workflow Examples

### Daily Knowledge Management
```python
# 1. Check recent activity
recent = adn_navigation("recent_activity", timeframe="today")

# 2. Create daily note
adn_content("write", identifier=f"Daily Note {date.today()}", content="# Daily Note\n\n## Tasks\n- [ ] Task 1\n- [ ] Task 2", folder="daily")

# 3. Search for relevant information
results = adn_search("notes", query="project status", page=1, page_size=5)

# 4. Update project notes
adn_content("edit", identifier="Project Status", edit_operation="append", content=f"\n\n## {date.today()}\n- Completed: Task 1\n- Next: Task 2")
```

### Research Workflow
```python
# 1. Create research plan
plan = adn_knowledge("research_plan", topic="machine learning ethics", research_type="academic")

# 2. Generate research questions
questions = adn_knowledge("research_questions", topic="machine learning ethics", research_type="academic")

# 3. Create research notes
for question in questions:
    adn_content("write", identifier=f"Research: {question}", content=f"# {question}\n\n## Notes\n\n## Sources\n\n## Analysis", folder="research")

# 4. Export research as PDF book
adn_export("pdf_book", book_title="ML Ethics Research", source_folder="/research", author="Researcher Name")
```

### Project Management
```python
# 1. Create project
adn_project("create", project_name="new-project", project_path="/path/to/project")

# 2. Switch to project
adn_project("switch", project_name="new-project")

# 3. Create project structure
adn_content("write", identifier="Project Overview", content="# Project Overview\n\n## Goals\n## Timeline\n## Resources", folder="docs")
adn_content("write", identifier="Meeting Notes", content="# Meeting Notes\n\n## Attendees\n## Agenda\n## Decisions", folder="meetings")

# 4. Export project documentation
adn_export("docsify", export_path="project-docs/", site_title="Project Documentation")
```

## 🎨 Advanced Features

### Entity Relationships
Advanced Memory automatically creates relationships between entities:
```markdown
# Meeting Notes

## Attendees
- [[John Smith]] - Developer
- [[Jane Doe]] - Designer

## Decisions
- Use [[React]] for frontend
- Deploy to [[AWS]] infrastructure
```

### Observations and Relations
```markdown
# Project Alpha

- [status] In development
- [priority] High
- [deadline] 2024-12-31
- [stakeholder] [[Product Team]]
- [depends_on] [[Design System]]
```

### Memory URLs
Access content using memory URLs:
```python
# Build context from memory URL
context = adn_navigation("build_context", url="memory://projects/alpha", depth=2)
```

## 🔧 Configuration Tips

### Cursor IDE Compatibility
- Enable portmanteau tools in settings
- Set maximum tools to 50 or fewer
- Use `adn_*` tools instead of individual tools

### Performance Optimization
- Use pagination for large search results
- Limit directory listing depth
- Use specific search types when possible

### Backup and Sync
- Regular exports to archive format
- Sync status monitoring
- Multiple project isolation

## 🆘 Troubleshooting

### Common Issues
1. **Tools not appearing**: Check portmanteau tools are enabled
2. **Import failures**: Verify source paths exist and are readable
3. **Search not working**: Check project is synced and indexed
4. **Export errors**: Ensure output directory is writable

### Getting Help
- Check system status: `adn_navigation("status")`
- Check sync status: `adn_navigation("sync_status")`
- Validate content: `adn_knowledge("validate_content")`

## 📚 Additional Resources

- **GitHub**: https://github.com/advanced-memory-mcp/advanced-memory-mcp
- **Documentation**: See individual tool help for detailed parameters
- **Examples**: Check the examples folder for more use cases
- **Community**: Join discussions for tips and best practices

---

*This guide covers the core functionality. Each tool has additional parameters and options - use the tool descriptions for complete parameter lists.*
