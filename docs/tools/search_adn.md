# Search Manager (adn_search)

Comprehensive search management tool for Advanced Memory knowledge base. This unified interface supports full-text search, pattern matching, and metadata filtering across internal notes and external vault formats.

## Operations

| Operation | Description | Required Parameters |
|:---|:---|:---|
| `notes` | Full-text search across local knowledge base | `query` |
| `obsidian` | Search through external Obsidian vaults | `query`, `source_path` |
| `joplin` | Search through external Joplin exports | `query`, `source_path` |
| `notion` | Search through external Notion exports | `query`, `source_path` |
| `evernote` | Search through external Evernote exports | `query`, `source_path` |

## Parameters

- `operation` (str): Search operation to perform.
- `query` (str): Search terms with boolean operators and phrases.
- `source_path` (str, optional): Path to external vault/export (Required for external operations).
- `search_type` (str, optional): Type of search ("text", "title", "permalink", "tag", "file", "link", "frontmatter").
- `page` (int, optional): Result page for pagination (Default: 1).
- `page_size` (int, optional): Results per page (Default: 10).
- `max_results` (int, optional): Maximum results for external searches (Default: 20).
- `case_sensitive` (bool, optional): Whether search should be case-sensitive (Default: False).
- `include_content` (bool, optional): Include content previews in results (Default: False).
- `types` (list[str], optional): Content type filters (e.g., ["note", "person"]).
- `entity_types` (list[str], optional): Entity category filters (e.g., ["entity", "observation"]).
- `after_date` (str, optional): Date filter - content FROM this date.
- `before_date` (str, optional): Date filter - content UNTIL this date.
- `tags` (list[str]|str, optional): Tag filter - notes must have ALL specified tags.
- `file_type` (str, optional): File type filter for external searches (e.g., "md", "html").
- `notebook_filter` (str, optional): Evernote specific - filter by notebook name.
- `tag_filter` (str, optional): Evernote specific - filter by tag name.
- `project` (str, optional): Optional override for active project name.

## Examples

### Internal note search
```python
adn_search("notes", query="machine learning", page_size=10)
```

### External Obsidian search
```python
adn_search("obsidian", query="planning", source_path="/path/to/vault")
```

### Combined filter search
```python
adn_search("notes", query="research AND python", after_date="2024-01-01")
```

### Tag search
```python
adn_search("notes", query="benny", tags="dog, training")
```
