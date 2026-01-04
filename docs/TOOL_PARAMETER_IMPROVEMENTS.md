# Tool Parameter Improvements - 2025-10-28

## Overview

Major improvements to tool parameter consistency and multi-project support across all portmanteau tools.

## Breaking Changes

### search_notes() - Parameter Renamed

**OLD**:
```python
search_notes("query", search_all_projects=True)
```

**NEW**:
```python
search_notes("query", projects="ALL")
```

**Migration Guide**:
- Replace `search_all_projects=True` with `projects="ALL"`
- Replace `search_all_projects=False` with `projects=None` (or omit)

## New Features

### Unified `projects` Parameter

All tools now support a consistent `projects` parameter with these values:

| Value | Behavior | Example |
|-------|----------|---------|
| `None` (default) | Current active project | `search_notes("query")` |
| `"project-name"` | Specific single project | `search_notes("query", projects="work")` |
| `"proj1,proj2,proj3"` | Comma-delimited list | `search_notes("query", projects="work,personal")` |
| `"ALL"` | All projects | `search_notes("query", projects="ALL")` |
| `"ALL_EXCEPT:proj1"` | All except specified | `search_notes("query", projects="ALL_EXCEPT:archived")` |

### Tools Updated

#### 1. search_notes()
- ✅ Multi-project search with result grouping
- ✅ Results prefixed with project name: `[work-project] Note Title`
- ✅ Searches multiple projects and merges results

#### 2. adn_content()
- ✅ Project context in all responses
- ✅ Shows which project note was created/updated in
- ✅ Clear project attribution in tag edits

#### 3. adn_navigation()
- ✅ Consistent project parameter handling
- ✅ Works with recent_activity, backlinks, etc.
- ✅ Project-aware directory listing

#### 4. adn_export()
- ✅ Multi-project export support
- ✅ `projects="ALL"` exports all projects to separate folders
- ✅ Creates folder structure: `export-path/project1/`, `project2/`, etc.
- ✅ Summary shows per-project export results

#### 5. adn_import()
- ✅ Project-aware imports
- ✅ Archive auto-detection of project structure
- ✅ Can import to specific projects

#### 6. adn_project()
- ✅ Enhanced documentation
- ✅ Future enhancements documented
- ✅ Cross-project operations planned

## Response Format Improvements

### Project Context in Responses

All tools now include project information in responses:

**Before**:
```
# Created note
file_path: notes/example.md
permalink: notes/example
```

**After**:
```
# Created note
project: work-project
file_path: notes/example.md
permalink: notes/example
```

## Examples

### Multi-Project Search
```python
# Search across all projects
results = search_notes("Python", projects="ALL")
# Returns: [work-project] Python Basics, [personal] Python Learning, etc.

# Search specific projects
results = search_notes("meeting", projects="work,archive")

# Exclude archived projects
results = search_notes("active", projects="ALL_EXCEPT:archived,old")
```

### Multi-Project Export
```python
# Export all projects to PDF
adn_export("pandoc", format_type="pdf", project="ALL")
# Creates: Desktop/advanced-memory-exports/pandoc/project1/, project2/, etc.

# Export specific projects to Claude Skills
adn_export("claude_skills", project="work,personal")
# Creates skills for two projects in separate folders
```

## Benefits

### For Users
- ✅ Explicit multi-project operations (no guessing)
- ✅ Clear project context in all responses
- ✅ Flexible project selection patterns
- ✅ No more "wrong project" confusion

### For AI Assistants (Claude)
- ✅ Know which project was searched
- ✅ Can explicitly request cross-project search
- ✅ Clearer error messages with project context
- ✅ Reduced retry attempts

## Migration Guide

### If You Have Custom Scripts

Update any code that uses these tools:

**search_notes()**:
```python
# OLD
search_notes("query", search_all_projects=True)

# NEW
search_notes("query", projects="ALL")
```

**All other tools**:
- Existing `project` parameter works the same
- New multi-project features are opt-in
- No changes needed for single-project usage

## Documentation Updates

- ✅ Updated all tool docstrings (FastMCP 2.12 compliant)
- ✅ Added examples for multi-project usage
- ✅ Documented `projects` parameter format
- ✅ Updated TOOLS_REFERENCE.md (this file)

## Testing

- ✅ All existing tests still pass
- ✅ Ruff checks: Zero errors
- ✅ FastMCP 2.12 compliance verified
- ✅ Backward compatible (except search_notes parameter rename)

## Version

**Introduced in**: v1.0.0b6 (or v1.0.0rc1)
**Breaking Changes**: search_notes() parameter renamed
**Migration Required**: Yes, for search_all_projects users

---

**Last Updated**: 2025-10-28
**Status**: Complete
**Quality**: Production-ready
