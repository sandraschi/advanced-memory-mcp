# Navigation Manager (adn_navigation)

Comprehensive navigation management tool for Advanced Memory knowledge base. This point-of-entry tool provides high-level navigation, diagnostic, and context-building operations. It is used to traverse the knowledge graph, monitor system health, and browse the physical file organization.

## Operations

| Operation | Description | Required Parameters |
|:---|:---|:---|
| `build_context` | Navigate the knowledge graph via memory:// URLs | `url` |
| `recent_activity` | Get recently updated information | - |
| `list_directory` | Browse directory contents with filtering | - |
| `backlinks` | Find all notes that reference a specific note | `identifier` |
| `status` | Comprehensive system status and diagnostics | - |
| `sync_status` | Monitor file synchronization status | - |

## Parameters

- `operation` (str): The navigation operation to perform.
- `identifier` (str, optional): Note Title or Permalink (Required for `backlinks`).
- `url` (str, optional): Memory URL (memory://...) (Required for `build_context`).
- `dir_name` (str, optional): Directory path to list (Default: "/").
- `depth` (int, optional): Relationship exploration depth or directory recursion depth (Default: 1).
- `timeframe` (str, optional): Time window for activity filtering (e.g., "1d", "7d", "last week").
- `page` (int, optional): Page number for paginated results (Default: 1).
- `page_size` (int, optional): Number of items per page (Default: 10).
- `max_related` (int, optional): Maximum related items to include (Default: 10).
- `file_name_glob` (str, optional): Glob pattern for file filtering (e.g., "*.md").
- `type_filter` (str, optional): Filter for activity ("entity", "observation", "relation", "").
- `level` (str, optional): Status detail level ("basic", "intermediate", "advanced").
- `focus` (str, optional): Specific area to focus on for status (e.g., "sync", "database").
- `project` (str, optional): Optional override for active project name.

## Examples

### Build semantic context
```python
adn_navigation("build_context", url="memory://projects/ai", depth=2)
```

### Check recent notes
```python
adn_navigation("recent_activity", timeframe="1d", type_filter="entity")
```

### Find backlinks
```python
adn_navigation("backlinks", identifier="Python Basics")
```

### Check system diagnostics
```python
adn_navigation("status", level="advanced", focus="database")
```
