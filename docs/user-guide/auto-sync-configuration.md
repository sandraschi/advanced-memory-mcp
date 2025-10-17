# Auto-Sync Configuration Guide

**How to enable, disable, and understand auto-sync**

---

## TL;DR

```toml
# Edit: ~/.advanced-memory/config.json
{
  "sync_changes": true   // Enable auto-sync
}
```

**Default**: ✅ **ON** (enabled by default!)

---

## How to Enable/Disable Auto-Sync

### Method 1: Edit Config File (Recommended)

**Location**: `~/.advanced-memory/config.json`

**Enable auto-sync**:
```json
{
  "sync_changes": true
}
```

**Disable auto-sync**:
```json
{
  "sync_changes": false
}
```

**After editing**: Restart MCP server (if running)

---

### Method 2: Environment Variable

```bash
# Enable
export ADVANCED_MEMORY_SYNC_CHANGES=true

# Disable
export ADVANCED_MEMORY_SYNC_CHANGES=false

# Then start MCP server
advanced-memory mcp
```

---

## What Is The Default?

**Default**: ✅ **`sync_changes = true`** (ENABLED)

**This means**:
- Auto-sync is **ON by default**
- When you start MCP server, file watcher starts automatically
- Changes are synced in real-time

**Source** (`src/advanced_memory/config.py`):
```python
sync_changes: bool = Field(
    default=True,
    description="Whether to sync changes in real time. default (True)",
)
```

---

## Why Isn't It Always On?

Great question! Here are the valid reasons for disabling auto-sync:

---

### Reason 1: Performance (Large Projects)

**Problem**: Watching 1000s of files is resource-intensive

**Scenario**:
```bash
# You have 5000 markdown files
advanced-memory project add everything ~/massive-zettelkasten

# With auto-sync enabled:
# - Watches 5000 files continuously
# - CPU usage ~2-5% idle
# - Memory usage ~50-100 MB
```

**Solution**: Disable auto-sync, use manual sync
```json
{
  "sync_changes": false
}
```

**Result**:
- No background watcher
- CPU: 0% when not syncing
- Memory: Minimal
- You sync manually when ready

---

### Reason 2: Batch Operations

**Problem**: You're doing bulk edits and don't want constant syncing

**Scenario**:
```bash
# You're reorganizing 100 notes
# - Moving files
# - Renaming files
# - Editing content

# With auto-sync:
# - Every change triggers sync (annoying!)
# - 100 sync operations (slow!)
# - Console spam with "EDIT" messages
```

**Solution**: Temporarily disable auto-sync
```bash
# 1. Disable in config
# 2. Do your bulk edits
# 3. One manual sync at end
advanced-memory sync

# 4. Re-enable if desired
```

---

### Reason 3: Conflicting Tools

**Problem**: Using another tool that also watches files

**Scenario**:
```bash
# You're using:
# - Obsidian (watches files)
# - Advanced Memory (watches files)
# - Git auto-commit tool (watches files)
# - Backup tool (watches files)

# Result: 4 tools fighting over file system events!
```

**Solution**: Disable auto-sync in Advanced Memory, sync manually

---

### Reason 4: Testing/Development

**Problem**: You're testing Advanced Memory itself

**Scenario**:
```bash
# You're developing Advanced Memory
# - Running tests
# - Debugging sync logic
# - Don't want background watcher interfering
```

**Solution**: Disable auto-sync during development

---

### Reason 5: CI/CD Pipelines

**Problem**: Automated scripts don't need real-time sync

**Scenario**:
```bash
# GitHub Actions workflow:
- name: Generate docs
  run: |
    generate-docs.sh
    advanced-memory sync  # Manual sync at end
```

**Why**: Background watcher is unnecessary in automated environments

---

### Reason 6: Battery Life (Laptops)

**Problem**: Background watcher drains battery

**Scenario**:
```bash
# On battery:
# - Background watcher uses CPU
# - File system monitoring uses power
# - Reduces battery life by ~5-10%
```

**Solution**: Disable when on battery, enable when plugged in

---

### Reason 7: Network Filesystems

**Problem**: Watching network drives is slow/unreliable

**Scenario**:
```bash
# Project on network drive:
advanced-memory project add shared \\server\shared\docs

# With auto-sync:
# - File change events delayed
# - Network overhead
# - Unreliable detection
```

**Solution**: Disable auto-sync, use manual sync

---

## When To Enable Auto-Sync

**✅ Enable when**:
- Small to medium projects (< 1000 files)
- Active note-taking
- Using Claude/AI with MCP (want real-time updates)
- Desktop with good performance
- Local filesystem (not network)
- You want "magic" experience (no manual sync)

---

## When To Disable Auto-Sync

**❌ Disable when**:
- Very large projects (> 5000 files)
- Doing bulk edits/reorganization
- Battery-powered device
- Network filesystem
- CI/CD environment
- Multiple file-watching tools
- Performance concerns
- You prefer manual control

---

## How To Check Current Setting

### Method 1: Check Config File

```bash
# Linux/macOS
cat ~/.advanced-memory/config.json | grep sync_changes

# Windows PowerShell
Get-Content ~\.advanced-memory\config.json | Select-String sync_changes
```

---

### Method 2: Check Project Info

```bash
advanced-memory project info
```

**Output includes**:
```
System Status:
  Watch Service: Running ✅ (if enabled)
  Watch Service: Stopped ❌ (if disabled)
```

---

### Method 3: Check Watch Status File

```bash
# Linux/macOS
cat ~/.advanced-memory/watch-status.json

# Windows
type %USERPROFILE%\.advanced-memory\watch-status.json
```

**If auto-sync enabled**:
```json
{
  "running": true,
  "start_time": "2025-10-17T10:30:00Z",
  "synced_files": 42
}
```

**If disabled**:
```
File not found (or "running": false)
```

---

## Complete Config Example

**Full `~/.advanced-memory/config.json`**:

```json
{
  "projects": {
    "main": "/home/user/notes",
    "work": "/home/user/work-notes"
  },
  "default_project": "main",
  "sync_changes": true,
  "sync_delay": 1000,
  "log_level": "INFO"
}
```

**Key settings**:
- `sync_changes: true` - Enable auto-sync
- `sync_delay: 1000` - Wait 1000ms after changes before syncing (debounce)

---

## Advanced: Conditional Auto-Sync

**Use case**: Enable auto-sync for some projects, not others

**Current limitation**: Global setting (applies to all projects)

**Workaround**: Toggle setting when switching projects
```bash
# Working on large project
# Edit config.json: sync_changes = false
advanced-memory --project huge-project mcp

# Working on small project
# Edit config.json: sync_changes = true
advanced-memory --project small-notes mcp
```

**Future enhancement**: Per-project auto-sync settings

---

## Troubleshooting

### "Auto-sync not working"

**Checklist**:
1. Is MCP server running? (`advanced-memory mcp`)
2. Is `sync_changes: true` in config?
3. Did you restart MCP server after changing config?
4. Check watch status: `cat ~/.advanced-memory/watch-status.json`

---

### "Too many sync events"

**Problem**: Console spam from constant syncing

**Solution 1**: Increase debounce delay
```json
{
  "sync_delay": 5000  // Wait 5 seconds instead of 1
}
```

**Solution 2**: Temporarily disable, do bulk edits, re-enable

---

### "High CPU usage"

**Problem**: Background watcher using too much CPU

**Causes**:
- Too many files being watched
- Rapid file changes
- Network filesystem

**Solution**: Disable auto-sync
```json
{
  "sync_changes": false
}
```

Then use manual sync: `advanced-memory sync`

---

## Best Practices

### 1. Enable for Active Projects

If you're actively editing notes, enable auto-sync for seamless experience.

---

### 2. Disable for Archives

If you have large archives you rarely edit, disable auto-sync:
```bash
# Don't watch archived projects
advanced-memory --project archive sync  # Manual sync only
```

---

### 3. Adjust Debounce Delay

If you're doing rapid edits (like refactoring), increase delay:
```json
{
  "sync_delay": 3000  // Wait 3 seconds
}
```

**Why**: Batches multiple rapid changes into one sync

---

### 4. Monitor Performance

Check CPU/memory usage:
```bash
# Linux/macOS
top -p $(pgrep -f "advanced-memory mcp")

# Windows
tasklist /FI "WINDOWTITLE eq advanced-memory*"
```

If high usage, consider disabling auto-sync.

---

## Quick Reference

| Task | Command/Config |
|------|----------------|
| **Enable auto-sync** | Set `sync_changes: true` in config.json |
| **Disable auto-sync** | Set `sync_changes: false` in config.json |
| **Check if enabled** | `advanced-memory project info` |
| **Adjust delay** | Set `sync_delay: 3000` in config.json |
| **Manual sync** | `advanced-memory sync` |
| **View watch status** | `cat ~/.advanced-memory/watch-status.json` |

---

## Summary

### Answers to Your Questions

**1. How do I enable/disable?**
- Edit `~/.advanced-memory/config.json`
- Set `sync_changes: true` (enable) or `false` (disable)
- Restart MCP server

**2. What is the default?**
- ✅ **Enabled by default** (`sync_changes: true`)
- Auto-sync is ON unless you disable it

**3. Why isn't it always on?**
- **Performance**: Large projects (1000s of files)
- **Batch operations**: Bulk edits trigger too many syncs
- **Battery life**: Background watcher drains power
- **Network filesystems**: Slow/unreliable
- **CI/CD**: Unnecessary in automated environments
- **Manual control**: Some users prefer explicit sync

---

## Philosophy

**Default = ON**: Most users want "magic" real-time sync

**Option to disable**: Power users can optimize for their use case

**Balance**: Convenience vs. control

---

*Created: 2025-10-17*  
*Purpose: Comprehensive guide to auto-sync configuration*

