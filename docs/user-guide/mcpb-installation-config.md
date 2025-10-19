# MCPB Installation Configuration

## Overview

When Advanced Memory is installed from a `.mcpb` package (via Claude Desktop's extension installer), configuration is handled through the Claude Desktop config file, not a GUI.

## How MCPB Configuration Works

### Installation

When you install the MCPB package:
1. Claude Desktop extracts it to an extensions folder
2. Reads `manifest.json` for configuration schema
3. Uses defaults from `user_config` section
4. Allows overrides in `claude_desktop_config.json`

### Default Configuration

The MCPB package has these defaults (from `manifest.json`):

```json
{
  "user_config": {
    "project_path": {
      "title": "Project Path",
      "description": "Path to your main Advanced Memory project directory",
      "default": "~/Documents/claude-depot",
      "env_var": "ADVANCED_MEMORY_HOME"
    }
  }
}
```

## Configuring After Installation

### Option 1: Edit Claude Desktop Config

**Location**: `%APPDATA%\Claude\claude_desktop_config.json` (Windows)

**Add/edit the `env` section**:

```json
{
  "mcpServers": {
    "advanced-memory-mcp": {
      "env": {
        "ADVANCED_MEMORY_HOME": "C:/Users/YourName/Documents/claude-depot"
      }
    }
  }
}
```

**Important**: Use forward slashes (`/`) even on Windows!

### Option 2: Use Default Location

If you don't set `ADVANCED_MEMORY_HOME`, it defaults to:
```
~/Documents/claude-depot/
```

Which expands to:
- **Windows**: `C:\Users\YourName\Documents\claude-depot\`
- **macOS**: `/Users/YourName/Documents/claude-depot/`
- **Linux**: `/home/YourName/Documents/claude-depot/`

## Environment Variables Used

### `ADVANCED_MEMORY_HOME`

**Purpose**: Sets the path to your main project directory

**If not set**: Defaults to home directory (`C:\Users\YourName`)

**Where database is stored**:
```
$ADVANCED_MEMORY_HOME/.advanced-memory/memory.db
```

**Examples**:

```json
// Point to Documents folder
"ADVANCED_MEMORY_HOME": "C:/Users/sandr/Documents/claude-depot"
→ Database: C:\Users\sandr\Documents\claude-depot\.advanced-memory\memory.db

// Point to home directory
"ADVANCED_MEMORY_HOME": "C:/Users/sandr"
→ Database: C:\Users\sandr\.advanced-memory\memory.db
```

## Common Mistakes

### ❌ Wrong: `advanced-memory` without dot

**Bad configuration**:
```python
# Old buggy code would create:
C:\Users\sandr\advanced-memory\.advanced-memory\memory.db
```

**Fixed**: Code now uses `Path.home()` directly, creating:
```
C:\Users\sandr\.advanced-memory\memory.db  ✅
```

### ❌ Wrong: Backslashes in JSON

**Bad**:
```json
{
  "ADVANCED_MEMORY_HOME": "C:\\Users\\sandr\\Documents\\claude-depot"
}
```

**Good**:
```json
{
  "ADVANCED_MEMORY_HOME": "C:/Users/sandr/Documents/claude-depot"
}
```

### ❌ Wrong: Relative paths

**Bad**:
```json
{
  "ADVANCED_MEMORY_HOME": "~/Documents/claude-depot"
}
```

**Good**:
```json
{
  "ADVANCED_MEMORY_HOME": "C:/Users/sandr/Documents/claude-depot"
}
```

Use **absolute paths** for reliability!

## Configuration Priority

Advanced Memory checks for settings in this order:

1. **Environment variable** (`ADVANCED_MEMORY_HOME`) from Claude Desktop config
2. **Config file** (`~/.advanced-memory/config.json`)
3. **Default** (home directory)

**Example**:

```json
// Claude Desktop config.json
{
  "mcpServers": {
    "advanced-memory-mcp": {
      "env": {
        "ADVANCED_MEMORY_HOME": "C:/Users/sandr/Documents/claude-depot"  ← Highest priority
      }
    }
  }
}
```

```json
// ~/.advanced-memory/config.json
{
  "projects": {
    "main": "C:\\Users\\sandr\\Documents\\claude-depot",  ← Used for project path
    "chitchat": "C:\\Users\\sandr\\Documents\\chitchat"
  },
  "default_project": "main"
}
```

## Verifying Configuration

### Check Current Paths

**Global database**:
```powershell
# Should be at:
# C:\Users\sandr\.advanced-memory\memory.db
Test-Path "$env:USERPROFILE\.advanced-memory\memory.db"
```

**Project paths**:
```powershell
# Check config
Get-Content "$env:USERPROFILE\.advanced-memory\config.json"
```

### Use Diagnostic Tool

```bash
python scripts/diagnose_sync.py "C:\Users\sandr\Documents\claude-depot"
```

Shows what will be indexed and which folders are skipped.

## Troubleshooting

### Problem: Files written to wrong location

**Symptoms**: Files appear in `C:\Users\sandr\advanced-memory` (without dot)

**Cause**: Old buggy code defaulted to `Path.home() / "advanced-memory"`

**Solution**: 
1. ✅ Fixed in version 1.0.0b2+ (both src/ and mcpb/)
2. Set `ADVANCED_MEMORY_HOME` explicitly in Claude Desktop config
3. Delete wrong folder after moving any important files

### Problem: Database not found

**Symptoms**: "No notes" after sync

**Check**:
1. Verify `ADVANCED_MEMORY_HOME` is set correctly
2. Check database exists: `~/.advanced-memory/memory.db`
3. Check project config: `~/.advanced-memory/config.json`

**Fix**:
```powershell
# Restart Claude Desktop to trigger re-sync
# Or manually sync:
advanced-memory sync
```

### Problem: Multiple databases created

**Symptoms**: Databases in multiple locations

**Locations to check**:
- `C:\Users\YourName\.advanced-memory\memory.db` ✅ Correct
- `C:\Users\YourName\advanced-memory\.advanced-memory\memory.db` ❌ Bug
- `<project-path>\.advanced-memory\memory.db` ❌ Legacy

**Solution**: Use consolidation script:
```bash
python scripts/consolidate_databases.py --analyze
```

## MCPB Package Specifics

When installed as MCPB, the manifest sets:

```json
{
  "env": {
    "ADVANCED_MEMORY_HOME": "${__dirname}/data"
  }
}
```

This means **data is stored in the extension directory** by default, which is:
```
%APPDATA%\Claude\extensions\advanced-memory-mcp\data\.advanced-memory\memory.db
```

**To override** (recommended), add to `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "advanced-memory-mcp": {
      "env": {
        "ADVANCED_MEMORY_HOME": "C:/Users/sandr/Documents/claude-depot"
      }
    }
  }
}
```

## Best Practices

### For MCPB Installation

1. **Always set `ADVANCED_MEMORY_HOME` explicitly** in Claude Desktop config
2. **Use absolute paths** (not relative or `~`)
3. **Use forward slashes** even on Windows
4. **Point to your main project** (e.g., `claude-depot`)

### Example Production Config

```json
{
  "mcpServers": {
    "advanced-memory-mcp": {
      "command": "python",
      "args": ["-m", "advanced_memory.mcp.server"],
      "env": {
        "ADVANCED_MEMORY_HOME": "C:/Users/sandr/Documents/claude-depot",
        "ADVANCED_MEMORY_LOG_LEVEL": "INFO",
        "ADVANCED_MEMORY_INDEX_ALL_FILES": "true"
      }
    }
  }
}
```

## See Also

- [Database Architecture](../architecture/DATABASE_ARCHITECTURE.md)
- [Project Setup Guide](project-setup-quick-guide.md)
- [File Type Filtering](file-type-filtering.md)
- [Archive Patterns](archive-folder-patterns.md)

