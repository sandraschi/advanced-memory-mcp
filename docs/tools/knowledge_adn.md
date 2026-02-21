# Knowledge Management (adn_knowledge)

Unified portmanteau tool for all core knowledge management operations. This tool consolidates basic CRUD operations for knowledge management, including note creation, reading, updating, and deletion, as well as content navigation and exploration.

## Operations

| Operation | Description | Required Parameters |
|:---|:---|:---|
| `create` | Create a new note | `title`, `content` |
| `read` | Read existing note | `identifier` |
| `update` | Update note content | `identifier`, `content` |
| `delete` | Delete a note | `identifier` |
| `move` | Move a note to a different folder | `identifier`, `folder` |
| `list` | List directory contents | `path` |
| `search` | Search notes | `query` |
| `navigate` | Navigate the knowledge graph | `path` |
| `context` | Get context for a specific entity | `identifier` |
| `activity` | Get recent activity | `timeframe` |
| `status` | Get sync status | - |

## Parameters

- `operation` (str): The specific knowledge operation to perform.
- `identifier` (str, optional): Note or entity identifier for targeted operations.
- `title` (str, optional): Note title for creation.
- `content` (str, optional): Note content for creation or updates.
- `folder` (str, optional): Target folder for organization.
- `tags` (list[str], optional): Tags for categorization.
- `query` (str, optional): Search terms.
- `path` (str, optional): File or directory path for navigation.
- `depth` (int, optional): Navigation depth for context building.
- `timeframe` (str, optional): Time-based filtering (e.g., "1 week", "7d").
- `entity_type` (str, optional): Entity type filtering (e.g., "person", "project").

## Examples

### Create a new note
```python
adn_knowledge("create", title="My Note", content="Note content", folder="research")
```

### Read existing note
```python
adn_knowledge("read", identifier="note-id")
```

### Update note content
```python
adn_knowledge("update", identifier="note-id", content="Updated content")
```

### Search notes
```python
adn_knowledge("search", query="machine learning")
```

### List directory
```python
adn_knowledge("list", path="research/")
```

### Get recent activity
```python
adn_knowledge("activity", timeframe="1 week")
```
