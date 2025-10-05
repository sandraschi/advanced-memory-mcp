# Advanced Memory MCP - Complete User Guide

## Overview

Advanced Memory MCP is a comprehensive knowledge management system that solves the "tool explosion" problem for MCP clients with strict tool limits (like Cursor IDE's 50-tool maximum). Through innovative **Portmanteau Tools**, it consolidates 40+ individual tools into just 8 comprehensive tools while maintaining 100% functionality.

## The Tool Explosion Problem

### Why Portmanteau Tools Exist

Advanced Memory provides comprehensive knowledge management requiring many specialized tools:
- Content operations: write, read, edit, move, delete, view
- Project management: create, switch, delete, list, status
- Import/export: 8 different formats (Obsidian, Joplin, Notion, Evernote, Pandoc, Docsify, HTML, Archive)
- Search capabilities: notes + 4 external vault types
- Knowledge operations: bulk updates, analytics, research orchestration
- Navigation: context building, recent activity, directory listing, status monitoring
- Editor integration: Notepad++, Typora, Canvas creation, content reading

**Result**: 40+ individual tools for complete functionality.

### Client Limitations

Many MCP clients impose strict tool limits:
- **Cursor IDE**: 50 tools maximum (most popular AI coding environment)
- **VS Code MCP**: 25-100 tools (may hit limits with other extensions)
- **Mobile clients**: 10-20 tools (severely limited)
- **Web clients**: 15-30 tools (poor functionality)

Without portmanteau tools, Advanced Memory would be **incompatible with Cursor IDE** and severely limited in other clients.

## Portmanteau Tool Architecture

### The Solution

Portmanteau tools consolidate related functionality into single tools with operation parameters:

```
Individual Tools (40+) → Portmanteau Tools (8)
```

### Complete Tool Suite

#### 1. Content Management (`adn_content`)
Consolidates 6 tools into 1:
- **Operations**: `write`, `read`, `view`, `edit`, `move`, `delete`
- **Purpose**: All note content operations
- **Example**: `adn_content("write", identifier="Meeting Notes", content="# Summary...", folder="meetings")`

#### 2. Project Management (`adn_project`)
Consolidates 6 tools into 1:
- **Operations**: `create`, `switch`, `delete`, `set_default`, `get_current`, `list`
- **Purpose**: Multi-project knowledge base management
- **Example**: `adn_project("switch", project_name="work-project")`

#### 3. Export Management (`adn_export`)
Consolidates 8 tools into 1:
- **Operations**: `pandoc`, `docsify`, `html`, `joplin`, `pdf_book`, `archive`, `evernote`, `notion`
- **Purpose**: Export knowledge base to various formats
- **Example**: `adn_export("pandoc", export_path="output.pdf", format_type="pdf")`

#### 4. Import Management (`adn_import`)
Consolidates 6 tools into 1:
- **Operations**: `obsidian`, `joplin`, `notion`, `evernote`, `archive`, `canvas`
- **Purpose**: Import from other knowledge management systems
- **Example**: `adn_import("obsidian", source_path="/path/to/vault")`

#### 5. Search Management (`adn_search`)
Consolidates 5 tools into 1:
- **Operations**: `notes`, `obsidian`, `joplin`, `notion`, `evernote`
- **Purpose**: Search across knowledge base and external vaults
- **Example**: `adn_search("notes", query="machine learning")`

#### 6. Knowledge Management (`adn_knowledge`)
Consolidates 2 tools into 1:
- **Operations**: `bulk_update`, `tag_analytics`, `research_plan`, `research_methodology`, `research_questions`, `note_blueprint`, `research_workflow`, `consolidate_tags`, `validate_content`, `project_stats`, `find_duplicates`
- **Purpose**: Advanced knowledge operations and research orchestration
- **Example**: `adn_knowledge("tag_analytics", action={"analyze_usage": True})`

#### 7. Navigation Management (`adn_navigation`)
Consolidates 5 tools into 1:
- **Operations**: `build_context`, `recent_activity`, `list_directory`, `status`, `sync_status`
- **Purpose**: Navigate and monitor the knowledge base
- **Example**: `adn_navigation("build_context", url="memory://projects/ai")`

#### 8. Editor Management (`adn_editor`)
Consolidates 5 tools into 1:
- **Operations**: `notepadpp_edit`, `notepadpp_import`, `typora_control`, `canvas_create`, `read_content`
- **Purpose**: External editor integration and content access
- **Example**: `adn_editor("notepadpp_edit", note_identifier="Meeting Notes")`

## Benefits of Portmanteau Tools

### 1. Client Compatibility
- **✅ Cursor IDE**: 8 tools << 50 limit
- **✅ Mobile clients**: Manageable tool count
- **✅ Web clients**: Fast loading and discovery

### 2. Performance
- **Faster tool discovery**: 8 tools vs 40+ tools
- **Reduced memory usage**: Fewer tool objects
- **Quicker client startup**: Less tool registration overhead

### 3. User Experience
- **Cleaner tool palette**: Logical grouping by function
- **Easier navigation**: Related operations in single tool
- **Consistent interface**: Operation-based parameter pattern

### 4. Developer Experience
- **Maintainable codebase**: Related functionality grouped
- **Scalable architecture**: Easy to add new operations
- **Backward compatibility**: Legacy tools still available

## Usage Patterns

### Basic Content Operations
```python
# Create a note
adn_content("write", identifier="Project Plan", content="# Overview\n\nProject details...", folder="projects")

# Read a note
adn_content("read", identifier="Project Plan")

# Edit a note (append content)
adn_content("edit", identifier="Project Plan", edit_operation="append", content="\n## Updates\n\nNew information...")

# Move a note
adn_content("move", identifier="Project Plan", destination_path="archive/completed/project-plan.md")

# Delete a note
adn_content("delete", identifier="Project Plan")
```

### Project Management
```python
# List all projects
adn_project("list")

# Create new project
adn_project("create", project_name="research", project_path="~/Documents/research")

# Switch to project
adn_project("switch", project_name="work")

# Get current project info
adn_project("get_current")
```

### Export Operations
```python
# Export to PDF using Pandoc
adn_export("pandoc", export_path="output.pdf", format_type="pdf", source_folder="/notes")

# Export to Docsify website
adn_export("docsify", export_path="website/", site_title="My Knowledge Base")

# Create PDF book
adn_export("pdf_book", export_path="book.pdf", book_title="Research Papers", tag_filter="research")
```

### Import Operations
```python
# Import from Obsidian
adn_import("obsidian", source_path="/path/to/vault", destination_folder="imported/obsidian")

# Import from Joplin
adn_import("joplin", source_path="/path/to/export", destination_folder="imported/joplin")

# Import from Notion
adn_import("notion", source_path="Notion-Export.zip", destination_folder="imported/notion")
```

### Search Operations
```python
# Search notes
adn_search("notes", query="machine learning", page=1, page_size=10)

# Search external Obsidian vault
adn_search("obsidian", query="project planning", source_path="/path/to/vault")

# Search with filters
adn_search("notes", query="urgent", entity_types=["task"], after_date="2024-01-01")
```

### Knowledge Operations
```python
# Analyze tag usage
adn_knowledge("tag_analytics", action={"analyze_usage": True})

# Bulk update tags
adn_knowledge("bulk_update", filters={"tags": ["draft"]}, action={"add_tags": ["reviewed"]})

# Create research plan
adn_knowledge("research_plan", topic="quantum computing", topic_type="technical")
```

### Navigation Operations
```python
# Build context from knowledge graph
adn_navigation("build_context", url="memory://projects/ai", depth=2, timeframe="7d")

# Get recent activity
adn_navigation("recent_activity", timeframe="today", type_filter="notes")

# List directory contents
adn_navigation("list_directory", dir_name="/projects", depth=2)

# Check system status
adn_navigation("status", level="intermediate", focus="sync")
```

### Editor Operations
```python
# Export to Notepad++ for editing
adn_editor("notepadpp_edit", note_identifier="Meeting Notes", workspace_path="temp/")

# Import from Notepad++
adn_editor("notepadpp_import", note_identifier="Meeting Notes", keep_workspace=False)

# Control Typora
adn_editor("typora_control", typora_operation="export", typora_format="pdf", typora_output_path="/exports/doc.pdf")

# Create Obsidian canvas
adn_editor("canvas_create", nodes=[...], edges=[...], canvas_title="Project Overview", canvas_folder="visuals")

# Read raw content
adn_editor("read_content", path="images/diagram.png")
```

## Best Practices

### 1. Use Portmanteau Tools for New Projects
- **Recommended**: Use `adn_*` tools for all new integrations
- **Benefits**: Better performance, cleaner interface, future-proof

### 2. Operation Parameter Naming
- **Consistent**: All tools use `operation` as the first parameter
- **Descriptive**: Operation names clearly indicate functionality
- **Extensible**: Easy to add new operations without breaking changes

### 3. Error Handling
- **Validation**: All tools validate operation parameters
- **Clear Messages**: Helpful error messages for invalid operations
- **Graceful Degradation**: Fallback options when operations fail

### 4. Performance Optimization
- **Batch Operations**: Use knowledge operations for bulk updates
- **Pagination**: Use page/page_size for large result sets
- **Filtering**: Use filters to limit scope of operations

## Migration from Legacy Tools

### For Existing Users
- **Backward Compatible**: All legacy tools (`write_note`, `read_note`, etc.) still work
- **Gradual Migration**: Can switch to portmanteau tools over time
- **No Breaking Changes**: Existing workflows continue to function

### Migration Examples
```python
# Old way
write_note(title="Meeting Notes", content="# Summary...", folder="meetings")

# New way (recommended)
adn_content("write", identifier="Meeting Notes", content="# Summary...", folder="meetings")
```

## Troubleshooting

### Common Issues

#### Invalid Operation Error
```
Error: Invalid operation: "invalid_op". Valid operations: write, read, view, edit, move, delete
```
**Solution**: Check the operation parameter against the tool's valid operations list.

#### Missing Required Parameters
```
Error: Missing required parameter 'identifier' for operation 'read'
```
**Solution**: Ensure all required parameters are provided for the operation.

#### Tool Not Found
```
Error: Tool 'adn_content' not available
```
**Solution**: Verify Advanced Memory MCP is properly installed and running.

### Getting Help

1. **Check Documentation**: Refer to this guide and examples
2. **Validate Parameters**: Ensure all required parameters are provided
3. **Check Logs**: Review MCP server logs for detailed error information
4. **Test with Simple Operations**: Start with basic operations before complex workflows

## Conclusion

Advanced Memory's Portmanteau Tools solve the critical compatibility problem between comprehensive knowledge management systems and tool-limited MCP clients. By consolidating 40+ tools into 8 comprehensive tools, Advanced Memory achieves universal compatibility while maintaining full functionality.

This architecture ensures Advanced Memory can deliver comprehensive knowledge management capabilities while remaining compatible with the most popular AI coding environments like Cursor IDE, making it accessible to the widest possible audience of users and developers.
