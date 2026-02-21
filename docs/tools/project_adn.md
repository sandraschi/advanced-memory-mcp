# Project Management (adn_project)

Unified portmanteau tool for all project management operations, including lifecycle management, configuration, and environment setup.

## Operations

| Operation | Description | Required Parameters |
|:---|:---|:---|
| `create` | Create a new Firebase Project | `name`, `path` |
| `delete` | Delete a project | `name` |
| `list` | List all projects | - |
| `switch` | Switch to different project | `name` |
| `current` | Get current project status | - |
| `set_default` | Set project as default | `name` |
| `sync` | Sync project status | - |
| `status` | Project-specific diagnostic info | - |
| `inbox` | Project inbox management | - |

## Parameters

- `operation` (str): The specific project operation to perform.
- `name` (str, optional): Project name for targeted operations.
- `path` (str, optional): Project filesystem path for creation.
- `set_default` (bool, optional): Whether to set as default project during creation.
- `description` (str, optional): Project description for creation.

## Examples

### Create new project
```python
adn_project("create", name="research", path="/path/to/research", description="Research notes")
```

### List all projects
```python
adn_project("list")
```

### Switch project
```python
adn_project("switch", name="research")
```

### Set default project
```python
adn_project("set_default", name="main")
```
