# External Integrations (adn_external)

Unified portmanteau tool for external integrations and specialized operations. This tool consolidates audio processing, content workflows, and integration with external editors like Typora.

## Operations

| Operation | Description | Sub-operations / Features |
|:---|:---|:---|
| `audio` | Audio processing operations | `dictate`, `speak`, `status` |
| `workflow` | Agentic content workflows | - |
| `batch` | Intelligent batch processing | - |
| `canvas` | Knowledge canvas management | - |
| `typora` | Control Typora markdown editor | `open`, `close`, `status` |
| `zettel` | Zettelkastel note creation | - |
| `content_workflow`| Advanced content generation | - |
| `sampling` | AI sampling capability status | - |
| `restart_watch` | Restart the file watcher service | - |

## Parameters

- `operation` (str): External integration operation to perform.
- `content` (str, optional): Content for processing operations (e.g., text for TTS).
- `path` (str, optional): File path for file-based operations (e.g., audio file).
- `parameters` (dict, optional): Additional operation-specific parameters (e.g., `sub_operation`).

## Examples

### Audio dictation
```python
adn_external("audio", parameters={"sub_operation": "dictate"}, path="audio_file.wav")
```

### Speech synthesis
```python
adn_external("audio", parameters={"sub_operation": "speak"}, content="Hello world")
```

### Typora editor control
```python
adn_external("typora", parameters={"sub_operation": "open"}, path="/path/to/file.md")
```

### Zettelkastel creation
```python
adn_external("zettel", content="Note content for Zettel")
```
