# AI Observability (adn_observability)

Unified tool for AI agent observability and provenance via Entire.io Checkpoints. This tool provides session recording, repository checkpointing, and workflow versioning for agentic audit trails.

## Operations

| Operation | Description | Required Parameters |
|:---|:---|:---|
| `enable` | Enable checkpoint tracking for the repository | - |
| `disable` | Disable checkpoint tracking | - |
| `list` | List existing checkpoints and session history | - |
| `rewind` | Revert workspace to a specific checkpoint | `checkpoint_id` |
| `clean` | Cleanup checkpoint metadata and history | - |
| `status` | Get observability system status | - |

## Parameters

- `operation` (str): The observability operation to perform.
- `checkpoint_id` (str, optional): Unique ID for identifying a specific state for rewinding.
- `repo_path` (str, optional): Target repository path (defaults to current project).

## Examples

### Enable observability
```python
adn_observability("enable")
```

### List checkpoints
```python
adn_observability("list")
```

### Rewind to checkpoint
```python
adn_observability("rewind", checkpoint_id="a1b2c3d4")
```

### Check status
```python
adn_observability("status")
```
