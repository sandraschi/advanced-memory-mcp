# System Management (adn_system)

Unified portmanteau tool for system management and external integrations. This tool consolidates status monitoring, external MCP server communication, inter-server tools, and system utility operations.

## Operations

| Operation | Description | Required Parameters |
|:---|:---|:---|
| `status` | Get comprehensive system health and status | - |
| `sync_status` | Get detailed synchronization status | - |
| `external_call` | Call a tool on an external MCP server | `server_name`, `tool_name` |
| `inter_server` | Perform agentic content workflows across servers | `topic` |
| `sampling_status` | Check AI sampling capability status | - |
| `batch_process` | Perform intelligent batch processing | `topic` |
| `workflow` | Execute specialized system workflows | `topic` |
| `help` | Access the multilevel help system | - |

## Parameters

- `operation` (str): System operation to perform.
- `level` (str, optional): Status detail level ("basic", "intermediate", "advanced", "diagnostic").
- `focus` (str, optional): Status focus area (e.g., "sync", "tools", "system", "projects").
- `server_name` (str, optional): External MCP server identifier.
- `tool_name` (str, optional): External tool name to call.
- `parameters` (dict, optional): Parameters for external tool calls.
- `topic` (str, optional): Topic for help, workflow, or batch operations.

## Examples

### System status
```python
adn_system("status", level="diagnostic")
```

### Call external MCP tool
```python
adn_system("external_call", server_name="mcp-server", tool_name="tool", parameters={"param": "value"})
```

### Inter-server workflow
```python
adn_system("inter_server", operation="workflow", topic="content generation")
```

### Batch processing
```python
adn_system("batch_process", topic="document analysis")
```

### System help
```python
adn_system("help", topic="tools")
```
