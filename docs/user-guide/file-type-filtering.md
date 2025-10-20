# File Type Filtering Configuration

## Overview

Advanced Memory can index either **all file types** or **only markdown files**, depending on your use case. This is controlled by the `index_all_files` configuration option.

## Configuration

### Default Behavior (All Files)

By default, `index_all_files` is set to `true`, meaning Advanced Memory will index:
- Markdown files (`.md`)
- Source code files (`.py`, `.js`, `.cpp`, `.java`, etc.)
- Configuration files (`.json`, `.yaml`, `.ini`, `.toml`, etc.)
- Documentation files (`.txt`, `.rst`, etc.)
- Any other human-readable text files

This is ideal for:
- Code repositories
- Mixed-content knowledge bases
- Documentation projects
- Technical research

### Markdown-Only Mode

Set `index_all_files` to `false` to only index markdown files (`.md`).

This is ideal for:
- Pure note-taking
- Writing projects
- Knowledge management focused on markdown
- Reducing index size

## How to Configure

### Option 1: Configuration File

Edit your `~/.advanced-memory/config.json`:

```json
{
  "index_all_files": false
}
```

### Option 2: Environment Variable

Set the environment variable:

```bash
export ADVANCED_MEMORY_INDEX_ALL_FILES=false
```

On Windows PowerShell:

```powershell
$env:ADVANCED_MEMORY_INDEX_ALL_FILES="false"
```

### Option 3: Claude Desktop Configuration

In your Claude Desktop MCP configuration (`claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "advanced-memory": {
      "command": "uv",
      "args": [
        "--directory",
        "path/to/advanced-memory-mcp",
        "run",
        "advanced-memory"
      ],
      "env": {
        "ADVANCED_MEMORY_INDEX_ALL_FILES": "false"
      }
    }
  }
}
```

## What Files Are Always Ignored

Regardless of the `index_all_files` setting, these are always skipped:

### Ignored Folders
- `node_modules`, `dist`, `build`, `target`, `out`, `.next`, `.nuxt`
- `__pycache__`, `.pytest_cache`, `.tox`, `venv`, `.venv`
- `vendor`, `.gradle`, `.cargo`, `coverage`
- `.vscode`, `.idea`
- Any folder starting with a dot (`.`)

### Ignored Files
- Hidden files (starting with `.`)
- `.DS_Store`, `Thumbs.db`

## Use Case Examples

### Use Case 1: Code Repository

**Scenario**: Indexing a Python project with code, configs, and docs.

**Configuration**:
```json
{
  "index_all_files": true
}
```

**What gets indexed**:
- `src/main.py` ✓
- `config.yaml` ✓
- `README.md` ✓
- `requirements.txt` ✓
- `docs/api.md` ✓

**What gets skipped**:
- `node_modules/` (ignored folder)
- `__pycache__/` (ignored folder)
- `.git/` (hidden folder)

### Use Case 2: Personal Notes

**Scenario**: Pure markdown note-taking.

**Configuration**:
```json
{
  "index_all_files": false
}
```

**What gets indexed**:
- `notes/daily-log.md` ✓
- `projects/ideas.md` ✓

**What gets skipped**:
- `todo.txt` ✗ (not markdown)
- `config.json` ✗ (not markdown)
- `script.py` ✗ (not markdown)

## Checking Current Configuration

Use the diagnostic script to see what files will be indexed:

```bash
python scripts/diagnose_sync.py "path/to/your/project"
```

This will show:
- Files that will be indexed
- Folders being skipped
- Current configuration being used

## Performance Considerations

### All Files Mode (`index_all_files: true`)
- **Pros**: Complete repository indexing, search across all content
- **Cons**: Larger database, more processing time
- **Best for**: Code repositories, comprehensive knowledge bases

### Markdown Only Mode (`index_all_files: false`)
- **Pros**: Faster sync, smaller database, focused content
- **Cons**: Non-markdown content not searchable
- **Best for**: Note-taking, writing projects, pure markdown workflows

## Troubleshooting

### "No files found" after sync

**Check these**:
1. Are your files in ignored folders? (See list above)
2. If `index_all_files: false`, do files have `.md` extension?
3. Are files hidden (starting with `.`)?

**Solutions**:
- Move files out of ignored folders
- Rename files to add `.md` extension
- Set `index_all_files: true` for non-markdown files
- Check logs: `%APPDATA%\Claude\logs\mcp*.log` (Windows)

### Files in subfolder not indexed

**Common causes**:
- Subfolder name is in ignore list (e.g., "build", "dist")
- Subfolder starts with `.`

**Solutions**:
- Rename the folder
- Check diagnostic output: `python scripts/diagnose_sync.py "path"`

## Migration Guide

### Switching from Markdown-Only to All Files

1. Update configuration:
   ```json
   {"index_all_files": true}
   ```

2. Restart Claude Desktop

3. Trigger re-sync (delete and recreate project, or wait for auto-sync)

### Switching from All Files to Markdown-Only

1. Update configuration:
   ```json
   {"index_all_files": false}
   ```

2. Restart Claude Desktop

3. Non-markdown files will no longer be indexed (existing entries remain until re-sync)

## See Also

- [Project Setup Guide](project-setup-quick-guide.md)
- [Sync Troubleshooting](../TROUBLESHOOTING_GUIDE.md)
- [Configuration Reference](../ADVANCED_MEMORY_MCP_COMPLETE_GUIDE.md#configuration)




