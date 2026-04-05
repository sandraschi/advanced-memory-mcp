# Cursor IDE – Advanced Memory (MemOps) MCP Setup

If Advanced Memory MCP does not start in Cursor, the MCP config is usually missing the **mcp** subcommand and **--transport stdio**.

## Correct configuration

Cursor must run the MCP server in stdio mode. Use this in your Cursor MCP config:

```json
{
  "mcpServers": {
    "advanced-memory": {
      "command": "uv",
      "args": [
        "--directory",
        "D:/Dev/repos/advanced-memory-mcp",
        "run",
        "advanced-memory",
        "mcp",
        "--transport",
        "stdio"
      ]
    }
  }
}
```

Adjust `--directory` to your actual repo path (Windows or Unix).

## Where to put this

- **Cursor (Windows):**  
  MCP server config is usually in Cursor Settings → MCP, or in a config file under your Cursor user data (e.g. `%APPDATA%\Cursor\` or the path shown in Cursor’s MCP / Settings UI). Add or edit the `advanced-memory` entry so its `args` match the snippet above.

- **Claude Desktop:**  
  Edit `claude_desktop_config.json` (see Claude Desktop docs for its location) and add the same `advanced-memory` entry under `mcpServers`.

## Why it was failing

If the config had only:

```json
"args": ["--directory", "D:/Dev/repos/advanced-memory-mcp", "run", "advanced-memory"]
```

then the process runs the Advanced Memory CLI with **no subcommand**. The CLI prints help and exits; it never starts the MCP server. The server is started only by the **mcp** subcommand with **--transport stdio**.

## Requirements

- **uv** installed and on PATH (Cursor runs `uv`).
- **Python 3.12+** (uv will use the project’s environment from the repo).
- Repo path in `--directory` must be the real path to `advanced-memory-mcp` (no symlinks or wrong drive if on Windows).

## Verify

After saving the config, restart Cursor (or reload MCP). Advanced Memory should appear in the MCP server list and tools should be available. If it still fails, check Cursor’s MCP or developer logs for the exact command run and any error output.
