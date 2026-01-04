# Project Setup Quick Guide

**How to point Advanced Memory at repos and directories**

---

## TL;DR

```bash
# Add any directory as a project
advanced-memory project add <project-name> /path/to/directory

# Sync it once
advanced-memory sync

# Done! All markdown files in that directory are now indexed
```

---

## Basic Concept

**Project** = A directory containing markdown files

**Advanced Memory can index ANY directory**:
- 📁 GitHub repo
- 📁 Obsidian vault
- 📁 Notes folder
- 📁 Documentation directory
- 📁 Zettelkasten
- 📁 Any folder with `.md` files

---

## Step-by-Step Guide

### Step 1: Add a Project

**Command**:
```bash
advanced-memory project add <name> <path>
```

**Examples**:

```bash
# Your GitHub repo
advanced-memory project add my-repo D:/Dev/repos/my-project

# Your notes folder
advanced-memory project add notes C:/Users/You/Documents/Notes

# Obsidian vault
advanced-memory project add obsidian-vault ~/Documents/ObsidianVault

# Work documentation
advanced-memory project add work-docs ~/work/documentation

# Personal zettelkasten
advanced-memory project add zettelkasten ~/zettelkasten
```

**What happens**:
- Creates project entry in config (`~/.advanced-memory/config.toml`)
- Creates project entry in database
- **Does NOT** index files yet (that's next step)

---

### Step 2: Sync the Project

**Command**:
```bash
advanced-memory sync
```

**What happens**:
- Scans all `.md` files in project directory
- Parses markdown (YAML frontmatter, wikilinks, etc.)
- Stores in database
- Builds search index

**Output**:
```
Syncing project: my-repo
Project path: D:/Dev/repos/my-project

Project 'my-repo': Synced 42 files (15 new, 0 modified, 0 moved, 0 deleted)
```

---

### Step 3 (Optional): Set as Default

**Command**:
```bash
advanced-memory project default <name>
```

**Example**:
```bash
advanced-memory project default my-repo
```

**What this does**:
- Makes this project the default for all commands
- Future `sync` commands use this project
- MCP tools use this project by default

---

## Complete Examples

### Example 1: Index Your GitHub Repo

```bash
# 1. Add project
advanced-memory project add advanced-memory-mcp D:/Dev/repos/advanced-memory-mcp

# 2. Set as default
advanced-memory project default advanced-memory-mcp

# 3. Sync
advanced-memory sync

# Done! Now you can search your repo
advanced-memory tool search-notes "sync architecture"
```

---

### Example 2: Import Your Obsidian Vault

```bash
# 1. Add vault as project
advanced-memory project add obsidian ~/Documents/ObsidianVault

# 2. Sync
advanced-memory sync

# Done! Your Obsidian notes are now searchable in Advanced Memory
```

**Note**: You can continue editing in Obsidian! Both tools can use the same files.

---

### Example 3: Multiple Projects

```bash
# Add multiple projects
advanced-memory project add work ~/work/notes
advanced-memory project add personal ~/personal/notes
advanced-memory project add research ~/research/papers

# Sync specific project
advanced-memory --project work sync

# Or set default and sync
advanced-memory project default work
advanced-memory sync

# Switch to different project
advanced-memory --project personal sync
```

---

## Auto-Sync (Optional)

If you want **automatic syncing** when files change:

### Enable File Watcher

**Edit config** (`~/.advanced-memory/config.toml`):
```toml
[app]
sync_changes = true
```

**Then start MCP server**:
```bash
advanced-memory mcp
```

**Result**:
- Initial sync on startup
- Watches for file changes
- Auto-syncs when you edit files
- "Magic" experience (no manual sync needed)

---

## Common Use Cases

### Use Case 1: "Index My Entire Code Repo"

**Goal**: Search your codebase's documentation

```bash
# Add repo
advanced-memory project add myproject ~/code/myproject

# Sync only markdown files
advanced-memory sync

# Search
advanced-memory tool search-notes "API documentation"
```

**Result**: All `*.md` files in repo indexed (README, docs/, etc.)

---

### Use Case 2: "Index Multiple Note Directories"

**Goal**: Search across all your notes

```bash
# Add all your note locations
advanced-memory project add work ~/work/notes
advanced-memory project add personal ~/personal/notes
advanced-memory project add learning ~/learning

# Sync all
advanced-memory project default work
advanced-memory sync

advanced-memory --project personal sync
advanced-memory --project learning sync

# Search across all (when using MCP)
# Uses current default project
```

---

### Use Case 3: "Keep Obsidian + Advanced Memory in Sync"

**Goal**: Use both tools on same vault

```bash
# Point Advanced Memory at Obsidian vault
advanced-memory project add obsidian ~/Documents/ObsidianVault

# Enable auto-sync
# Edit config.toml: sync_changes = true

# Start MCP server
advanced-memory mcp

# Now:
# - Edit in Obsidian → auto-syncs to Advanced Memory
# - Search in Advanced Memory → sees Obsidian changes
# - Use both tools simultaneously!
```

---

## Path Formats

### Absolute Paths (Recommended)

```bash
# Windows (forward slashes work!)
advanced-memory project add notes C:/Users/You/Documents/Notes
advanced-memory project add repo D:/Dev/repos/my-project

# Linux/macOS
advanced-memory project add notes /home/you/Documents/Notes
advanced-memory project add repo /home/you/code/my-project
```

---

### Relative Paths (Converted to Absolute)

```bash
# Current directory
advanced-memory project add current .

# Parent directory
advanced-memory project add parent ..

# Relative path
advanced-memory project add docs ./documentation
```

**Note**: Relative paths are **converted to absolute** when added.

---

### Home Directory Shortcut

```bash
# Using ~
advanced-memory project add notes ~/Documents/Notes

# Expands to (Windows):
# C:/Users/You/Documents/Notes

# Expands to (Linux/macOS):
# /home/you/Documents/Notes
```

---

## What Gets Indexed?

### Included

✅ `.md` files (markdown)
✅ Nested directories (recursive)
✅ YAML frontmatter
✅ Wikilinks `[[Note Name]]`
✅ Observations `- [category] content`
✅ Relations `- relation_type [[Target]]`

---

### Excluded (Automatically)

❌ `.git/` directory
❌ `node_modules/` directory
❌ `.vscode/`, `.idea/` (IDE files)
❌ `__pycache__/` (Python cache)
❌ `.DS_Store`, `Thumbs.db` (OS files)
❌ Hidden files (starting with `.`)
❌ Non-markdown files (`.txt`, `.pdf`, etc.)

**Full list**: See `IGNORE_PATTERNS` in `src/advanced_memory/sync/watch_service.py`

---

## Managing Projects

### List All Projects

```bash
advanced-memory project list
```

**Output**:
```
┏━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━┳━━━━━━━━┓
┃ Name        ┃ Path                ┃ Default ┃ Active ┃
┡━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━╇━━━━━━━━┩
│ my-repo     │ ~/code/my-project   │ YES     │ YES    │
│ notes       │ ~/Documents/Notes   │         │        │
│ obsidian    │ ~/ObsidianVault     │         │        │
└─────────────┴─────────────────────┴─────────┴────────┘
```

---

### Check Project Info

```bash
advanced-memory project info
```

**Output**:
```
Project: my-repo
Path: D:/Dev/repos/my-project
Default Project: my-repo

Statistics:
  Entities: 42
  Observations: 156
  Relations: 89

Recent Activity:
  README.md (updated 2 hours ago)
  docs/architecture.md (updated 5 hours ago)
```

---

### Remove Project

```bash
advanced-memory project remove <name>
```

**Example**:
```bash
advanced-memory project remove old-project
```

**Note**: Files are **NOT deleted** from disk, only project config is removed.

---

### Switch Projects

```bash
# Option 1: Set default
advanced-memory project default work
advanced-memory sync

# Option 2: Use --project flag
advanced-memory --project personal sync
advanced-memory --project research status
```

---

## Typical Workflows

### Workflow 1: Daily Use (Single Project)

```bash
# One-time setup
advanced-memory project add notes ~/Documents/Notes
advanced-memory project default notes
advanced-memory sync

# Daily use
# 1. Edit notes in your favorite editor
# 2. Run sync when ready
advanced-memory sync

# Search
advanced-memory tool search-notes "topic"
```

---

### Workflow 2: Development (Multiple Projects)

```bash
# Setup
advanced-memory project add project-a ~/code/project-a
advanced-memory project add project-b ~/code/project-b
advanced-memory project add docs ~/code/shared-docs

# Work on project A
advanced-memory project default project-a
advanced-memory sync
# ... edit docs ...
advanced-memory sync

# Switch to project B
advanced-memory project default project-b
advanced-memory sync
# ... work ...
```

---

### Workflow 3: Auto-Sync (Set It and Forget It)

```bash
# One-time setup
advanced-memory project add notes ~/Documents/Notes

# Enable auto-sync (edit config.toml)
# sync_changes = true

# Start MCP server (leave running)
advanced-memory mcp

# Now just edit files!
# Changes auto-sync in background
```

---

## Troubleshooting

### "Project not found"

**Problem**:
```bash
advanced-memory sync
Error: Project 'my-project' not found
```

**Solution**:
```bash
# List projects
advanced-memory project list

# Set correct default
advanced-memory project default <correct-name>
```

---

### "No markdown files found"

**Problem**: Sync reports 0 files

**Causes**:
1. Directory doesn't contain `.md` files
2. Files are in subdirectory (should still work - check path)
3. All files are ignored (in `node_modules/`, etc.)

**Solution**:
```bash
# Check directory contents
ls ~/path/to/project

# Ensure it has .md files
# Run sync with verbose to see what's happening
advanced-memory sync --verbose
```

---

### "Database is locked"

**Problem**:
```bash
Error: database is locked
```

**Cause**: Another sync process is running

**Solution**:
```bash
# Kill all advanced-memory processes
# Windows
taskkill /F /IM python.exe /FI "WINDOWTITLE eq advanced-memory*"

# Linux/macOS
pkill -f advanced-memory

# Try again
advanced-memory sync
```

---

### "Can't sync multiple projects simultaneously"

**Current Limitation**: SQLite database can only handle one sync at a time

**Workaround**: Sync projects sequentially
```bash
advanced-memory --project project1 sync
advanced-memory --project project2 sync
advanced-memory --project project3 sync
```

---

## Best Practices

### 1. Use Descriptive Project Names

**Good**:
- `work-docs`
- `personal-notes`
- `research-papers`
- `project-alpha-docs`

**Bad**:
- `temp`
- `test`
- `x`
- `aaa`

---

### 2. Set a Default Project

Avoids having to use `--project` flag constantly:

```bash
advanced-memory project default my-main-project
```

---

### 3. Sync After Major Changes

After:
- Importing files
- Bulk edits
- Reorganizing directories

Run:
```bash
advanced-memory sync --verbose
```

---

### 4. Use Auto-Sync for Active Projects

For projects you edit frequently:
- Enable `sync_changes = true`
- Start MCP server: `advanced-memory mcp`
- Edit files freely, changes auto-sync

---

### 5. Keep Projects Separate

**Don't**:
```bash
# Overlapping paths - confusing!
advanced-memory project add root ~/
advanced-memory project add docs ~/Documents
```

**Do**:
```bash
# Separate, non-overlapping directories
advanced-memory project add work ~/work/notes
advanced-memory project add personal ~/personal/notes
```

---

## Quick Reference

| Task | Command |
|------|---------|
| **Add project** | `advanced-memory project add <name> <path>` |
| **List projects** | `advanced-memory project list` |
| **Set default** | `advanced-memory project default <name>` |
| **Sync project** | `advanced-memory sync` |
| **Sync specific** | `advanced-memory --project <name> sync` |
| **Check status** | `advanced-memory status` |
| **Project info** | `advanced-memory project info` |
| **Remove project** | `advanced-memory project remove <name>` |
| **Search notes** | `advanced-memory tool search-notes "query"` |

---

## Summary

**Adding a project = Pointing Advanced Memory at a directory**

**Simple 3-step process**:
1. `project add <name> <path>` - Tell Advanced Memory where files are
2. `sync` - Index the files
3. Done! Search, query, use MCP tools

**Auto-sync** (optional):
- Enable in config: `sync_changes = true`
- Start MCP server: `advanced-memory mcp`
- Files auto-sync when changed

**That's it!** No complex setup, just point and sync. 🎯

---

*Created: 2025-10-17*
*Purpose: Simple guide for project setup*
