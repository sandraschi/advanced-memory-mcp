# Advanced Memory Installation Guide for LLMs

This guide is specifically designed to help AI assistants like Cline install and configure Advanced Memory. Follow these
steps in order.

## Installation Steps

### 1. Install Advanced Memory Package

Use one of the following package managers to install:

```bash
# Install with uv (recommended)
uv tool install advanced-memory

# Or with pip
pip install advanced-memory
```

### 2. Configure MCP Server

Add the following to your config:

```json
{
  "mcpServers": {
    "advanced-memory": {
      "command": "uvx",
      "args": [
        "advanced-memory",
        "mcp"
      ]
    }
  }
}
```

For Claude Desktop, this file is located at:

macOS: ~/Library/Application Support/Claude/claude_desktop_config.json
Windows: %APPDATA%\Claude\claude_desktop_config.json

### 3. Start Synchronization (optional)

To synchronize files in real-time, run:

```bash
advanced-memory sync --watch
```

Or for a one-time sync:

```bash
advanced-memory sync
```

## Configuration Options

### Custom Directory

To use a directory other than the default `~/advanced-memory`:

```bash
advanced-memory project add custom-project /path/to/your/directory
advanced-memory project default custom-project
```

### Multiple Projects

To manage multiple knowledge bases:

```bash
# List all projects
advanced-memory project list

# Add a new project
advanced-memory project add work ~/work-advanced-memory

# Set default project
advanced-memory project default work
```

## Importing Existing Data

### From Claude.ai

```bash
advanced-memory import claude conversations path/to/conversations.json
advanced-memory import claude projects path/to/projects.json
```

### From ChatGPT

```bash
advanced-memory import chatgpt path/to/conversations.json
```

### From MCP Memory Server

```bash
advanced-memory import memory-json path/to/memory.json
```

## Troubleshooting

If you encounter issues:

1. Check that Advanced Memory is properly installed:
   ```bash
   advanced-memory --version
   ```

2. Verify the sync process is running:
   ```bash
   ps aux | grep advanced-memory
   ```

3. Check sync output for errors:
   ```bash
   advanced-memory sync --verbose
   ```

4. Check log output:
   ```bash
   cat ~/.advanced-memory/advanced-memory.log
   ```

For more detailed information, refer to the [full documentation](https://memory.basicmachines.co/).