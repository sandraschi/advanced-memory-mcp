# Advanced Memory MCP - Troubleshooting Guide

**Version:** 1.0.0b2
**Purpose:** Comprehensive troubleshooting for common issues

## Quick Diagnosis

### Check System Status
```python
# In Claude Desktop
adn_navigation("status", level="basic")
adn_navigation("sync_status")
```

### Check Logs
```bash
# Windows
Get-Content "$env:APPDATA\Claude\logs\mcp-server-advanced-memory-mcp.log" -Tail 20

# macOS/Linux
tail -20 ~/.config/claude/logs/mcp-server-advanced-memory-mcp.log
```

---

## Common Issues

### 1. Claude Can't Connect to Advanced Memory

#### Symptoms
- "Server disconnected" in Claude Desktop
- Advanced Memory tools not available
- Connection timeout errors

#### Diagnosis
```bash
# Check if Advanced Memory is installed
python -c "import advanced_memory; print('âœ… Installed')"

# Check MCP server
python -m advanced_memory.mcp.server --help
```

#### Solutions

**Solution 1: Verify Configuration**
```json
// claude_desktop_config.json
{
  "mcpServers": {
    "advanced-memory-mcp": {
      "command": "python",
      "args": ["-m", "advanced_memory.mcp.server"],
      "env": {
        "ADVANCED_MEMORY_HOME": "C:/Users/username"
      }
    }
  }
}
```

**Solution 2: Check Environment Variables**
```bash
# Windows PowerShell
$env:ADVANCED_MEMORY_HOME = "C:\Users\username"
python -m advanced_memory.mcp.server

# macOS/Linux
export ADVANCED_MEMORY_HOME="$HOME"
python -m advanced_memory.mcp.server
```

**Solution 3: Restart Claude Desktop**
1. Close Claude Desktop completely
2. Wait 10 seconds
3. Restart Claude Desktop
4. Check MCP server status

### 2. Notes save via MCP but never appear in webapp (NSSM split-brain)

**Platform:** Windows only — NSSM service running as `LocalSystem`.

#### Symptoms

- `adn_notes(write)` returns `success: true` but the note is missing in the webapp (port 10704)
- Problem persists for days/weeks; restarting Cursor or Claude does not help
- MCP may later return `attempt to write a readonly database` after a partial fix
- Markdown file may exist under your user vault but `read` / search still fails (index out of sync)

#### Cause

NSSM backend and user-session webapp/MCP resolved **different** `Path.home()` → two `.advanced-memory` stores (often `systemprofile` vs `C:\Users\<you>`). Writes succeeded to the wrong store.

#### Fix and full write-up

See **[troubleshooting/BUG_REPORT_NSSM_SPLIT_BRAIN.md](troubleshooting/BUG_REPORT_NSSM_SPLIT_BRAIN.md)** — NSSM env pin, orphan recovery, HTTP daemon single-writer pattern, verification checklist.

Fleet trap: [mcp-central-docs TRAPS_AND_PITFALLS §14](https://github.com/sandraschi/mcp-central-docs/blob/main/standards/TRAPS_AND_PITFALLS.md#14-nssm-services-run-as-localsystem-so-pathhome-silently-resolves-to-systemprofile---two-databases-zero-errors).

Quick check: `adn_nav(operation="status")` — DB/vault paths must be under **your user profile**, not `systemprofile`.

### 3. Database Locked Errors

#### Symptoms
```
sqlite3.OperationalError: database is locked
Error: Unable to sync project
```

#### Diagnosis
```python
# Check for running processes
adn_navigation("sync_status")
```

#### Solutions

**Solution 1: Kill Background Processes**
```bash
# Windows PowerShell
Get-Process | Where-Object {$_.ProcessName -match "python"} | Stop-Process -Force

# macOS/Linux
pkill -f "advanced_memory"
```

**Solution 2: Manual Database Unlock**
```bash
# Close all Advanced Memory processes
# Wait 30 seconds
advanced-memory sync
```

**Solution 3: Database Recovery**
```bash
# Backup database
cp ~/.advanced-memory/memory.db ~/.advanced-memory/memory.db.backup

# Try to recover
sqlite3 ~/.advanced-memory/memory.db "PRAGMA integrity_check;"
```

### 4. File Watcher Not Working

#### Symptoms
- Files not auto-syncing
- Manual sync works but auto-sync doesn't
- No file change detection

#### Diagnosis
```python
# Check watcher status
adn_navigation("sync_status")

# Check configuration
adn_navigation("status", level="intermediate", focus="sync")
```

#### Solutions

**Solution 1: Restart File Watcher**
```bash
# Restart Claude Desktop to reinitialize watcher
# Or manually restart MCP server
```

**Solution 2: Check File Permissions**
```bash
# Windows
icacls "C:\Users\username\Documents\notes" /grant Everyone:F

# macOS/Linux
chmod -R 755 ~/Documents/notes
```

**Solution 3: Verify Configuration**
```json
// ~/.advanced-memory/config.json
{
  "sync_changes": true,
  "sync_delay": 1000
}
```

### 5. Import Failures

#### Symptoms
- Import tools fail with errors
- Partial imports
- "File not found" errors

#### Diagnosis
```python
# Check source paths
import os
print(os.path.exists("~/source-path"))
```

#### Solutions

**Solution 1: Verify Source Paths**
```bash
# Check if source exists
ls -la ~/obsidian-vault
ls -la ~/joplin-export
```

**Solution 2: Check File Permissions**
```bash
# Ensure read access
chmod -R 644 ~/source-directory
```

**Solution 3: Use Absolute Paths**
```python
# Instead of ~/path, use full path
adn_import("obsidian",
    vault_path="/Users/username/obsidian-vault",
    destination_folder="imported/obsidian")
```

### 6. Search Not Working

#### Symptoms
- Search returns no results
- Search errors
- Slow search performance

#### Diagnosis
```python
# Test basic search
adn_search("notes", query="test")

# Check database
adn_navigation("status", level="intermediate")
```

#### Solutions

**Solution 1: Rebuild Search Index**
```bash
# Force reindex
advanced-memory sync --force-reindex
```

**Solution 2: Check Database Integrity**
```bash
sqlite3 ~/.advanced-memory/memory.db "PRAGMA integrity_check;"
```

**Solution 3: Clear Search Cache**
```bash
# Delete search cache files
rm ~/.advanced-memory/search_cache.db
advanced-memory sync
```

### 7. Export Failures

#### Symptoms
- Export tools fail
- Empty exports
- Format errors

#### Diagnosis
```python
# Test simple export
adn_export("html", export_path="~/test-export")
```

#### Solutions

**Solution 1: Check Output Directory**
```bash
# Ensure output directory exists and is writable
mkdir -p ~/export-directory
chmod 755 ~/export-directory
```

**Solution 2: Check Dependencies**
```bash
# For PDF exports
pip install pandoc
# Or install system pandoc
```

**Solution 3: Use Different Format**
```python
# Try HTML instead of PDF
adn_export("html", export_path="~/export")
```

### 8. Project Management Issues

#### Symptoms
- Can't create projects
- Project switching fails
- Sync specific project doesn't work

#### Diagnosis
```python
# Check project list
adn_project("list")

# Check current project
adn_project("get_current")
```

#### Solutions

**Solution 1: Verify Project Paths**
```bash
# Check if project directories exist
ls -la ~/Documents/project-directory
```

**Solution 2: Fix Project Configuration**
```json
// ~/.advanced-memory/config.json
{
  "projects": {
    "main": "C:/Users/username/Documents/notes",
    "research": "C:/Users/username/Documents/research"
  },
  "default_project": "main"
}
```

**Solution 3: Recreate Project**
```python
# Delete and recreate
adn_project("delete", project_name="problematic-project")
adn_project("create",
    project_name="new-project",
    project_path="~/Documents/new-project")
```

---

## Advanced Troubleshooting

### Database Issues

#### Database Corruption
```bash
# Check integrity
sqlite3 ~/.advanced-memory/memory.db "PRAGMA integrity_check;"

# If corrupted, restore from backup
cp ~/.advanced-memory/memory.db.backup ~/.advanced-memory/memory.db
```

#### Database Performance
```sql
-- Check database size
SELECT page_count * page_size as size FROM pragma_page_count(), pragma_page_size();

-- Analyze query performance
EXPLAIN QUERY PLAN SELECT * FROM entity WHERE title LIKE '%search%';
```

### File System Issues

#### Permission Problems
```bash
# Windows - Check permissions
icacls "C:\Users\username\Documents\notes"

# macOS/Linux - Check permissions
ls -la ~/Documents/notes
```

#### Disk Space
```bash
# Check available space
df -h ~/.advanced-memory
df -h ~/Documents/notes
```

### Network Issues

#### MCP Connection Problems
```bash
# Test MCP server directly
python -m advanced_memory.mcp.server --test

# Check port availability
netstat -an | grep :8080
```

---

## Debug Mode

### Enable Debug Logging

```bash
# Set environment variable
export ADVANCED_MEMORY_DEBUG=1

# Or in PowerShell
$env:ADVANCED_MEMORY_DEBUG = "1"

# Restart Claude Desktop
```

### Debug Commands

```python
# In Claude Desktop
adn_navigation("status", level="diagnostic")

# Check detailed sync status
adn_navigation("sync_status")

# Test individual operations
adn_content("read", identifier="test-note")
```

### Log Analysis

#### Common Log Patterns
```
# Success patterns
âœ… Operation completed successfully
[INFO] File synced: /path/to/file.md
[INFO] Entity created: entity-id

# Error patterns
âŒ Error: Database is locked
[ERROR] File not found: /path/to/file.md
[ERROR] Permission denied: /path/to/directory
```

#### Log Locations
- **Windows**: `%APPDATA%\Claude\logs\`
- **macOS**: `~/Library/Logs/Claude/`
- **Linux**: `~/.config/claude/logs/`

---

## Performance Issues

### Slow Operations

#### Database Performance
```sql
-- Check slow queries
EXPLAIN QUERY PLAN SELECT * FROM entity WHERE content LIKE '%search%';

-- Optimize database
VACUUM;
ANALYZE;
```

#### File System Performance
```bash
# Check file system performance
time find ~/Documents/notes -name "*.md" | wc -l

# Check disk I/O
iostat -x 1
```

### Memory Issues

#### High Memory Usage
```bash
# Check memory usage
ps aux | grep advanced_memory

# Monitor memory over time
top -p $(pgrep -f advanced_memory)
```

#### Memory Leaks
```python
# Enable memory profiling
import tracemalloc
tracemalloc.start()

# Check memory usage
current, peak = tracemalloc.get_traced_memory()
print(f"Current: {current / 1024 / 1024:.1f} MB")
print(f"Peak: {peak / 1024 / 1024:.1f} MB")
```

---

## Recovery Procedures

### Complete System Reset

#### Backup Data
```bash
# Backup database
cp ~/.advanced-memory/memory.db ~/backup/memory.db.$(date +%Y%m%d)

# Backup configuration
cp ~/.advanced-memory/config.json ~/backup/config.json.$(date +%Y%m%d)

# Backup notes
tar -czf ~/backup/notes.$(date +%Y%m%d).tar.gz ~/Documents/notes
```

#### Reset System
```bash
# Stop all processes
pkill -f advanced_memory

# Remove database
rm ~/.advanced-memory/memory.db

# Remove configuration
rm ~/.advanced-memory/config.json

# Reinitialize
advanced-memory init
```

#### Restore Data
```bash
# Restore database
cp ~/backup/memory.db.20241016 ~/.advanced-memory/memory.db

# Restore configuration
cp ~/backup/config.json.20241016 ~/.advanced-memory/config.json

# Restore notes
tar -xzf ~/backup/notes.20241016.tar.gz -C ~/Documents/

# Resync
advanced-memory sync
```

### Partial Recovery

#### Rebuild Search Index
```bash
# Delete search indexes
rm ~/.advanced-memory/search_*.db

# Force reindex
advanced-memory sync --force-reindex
```

#### Fix Project Configuration
```python
# Recreate project configuration
adn_project("create",
    project_name="main",
    project_path="~/Documents/notes",
    set_default=True)
```

---

## Prevention Strategies

### Regular Maintenance

#### Daily
- Check sync status: `adn_navigation("sync_status")`
- Monitor log files for errors
- Verify file permissions

#### Weekly
- Backup database: `cp ~/.advanced-memory/memory.db ~/backup/`
- Check disk space
- Review error logs

#### Monthly
- Database optimization: `VACUUM; ANALYZE;`
- Clean up old log files
- Update dependencies

### Best Practices

#### File Organization
- Use consistent naming conventions
- Avoid special characters in filenames
- Keep file sizes reasonable (< 1MB per file)

#### Project Management
- Use descriptive project names
- Keep project paths simple
- Regular project cleanup

#### Configuration
- Backup configuration files
- Use absolute paths in config
- Test configuration changes

---

## Getting Help

### Self-Help Resources

1. **Documentation**: Check the complete guide
2. **Logs**: Analyze error messages
3. **Status Commands**: Use diagnostic tools
4. **Community**: GitHub Issues and Discussions

### Support Channels

1. **GitHub Issues**: Bug reports and feature requests
2. **GitHub Discussions**: Community support
3. **Documentation**: Comprehensive guides
4. **Examples**: Sample configurations and workflows

### Information to Include

When reporting issues, include:

1. **System Information**
   - Operating System
   - Python version
   - Advanced Memory version

2. **Error Details**
   - Exact error messages
   - Steps to reproduce
   - Log file excerpts

3. **Configuration**
   - Relevant config files
   - Environment variables
   - Project structure

4. **Attempted Solutions**
   - What you've tried
   - Results of troubleshooting steps

---

This troubleshooting guide should help resolve most common issues with Advanced Memory MCP. For persistent problems, please create a GitHub issue with detailed information.
---

## Sync Performance

### Symptom: sync takes hours on a large vault

**Root cause (fixed in 1.7.1):** Prior to 1.7.1, `handle_move` called `index_entity`
on every detected move — including pure Windows path-separator normalisation (`/` → `\`).
Each call re-read the full file and rebuilt FTS trigram stems. On a vault with thousands
of entities indexed on another OS (or with forward-slash paths in the db), the first sync
on Windows would re-index every single entity.

**Also:** `resolve_relations` called `index_entity` on every resolved wikilink target,
adding further unnecessary re-indexing after every sync.

**Fix:** Upgrade to 1.7.1+. Path-only moves now use a cheap SQL path update; relation
resolution no longer triggers re-indexing.

**If still slow after 1.7.1:** The remaining time in `resolve_relations` is genuine —
each unresolved wikilink does a hybrid vector search to find the target entity. If you
have many unresolved relations this is expected. Check the sync log for `Resolving
forward references count=N` to see how many there are.

### Symptom: sync hangs and never completes

Check if a very large file (>1MB markdown) is being indexed. The trigram FTS indexer
is O(n) on content length. Files over ~500KB with dense prose will take 30-60 seconds
each. Check the sync log tail for which `entity_id` it last processed.

To identify large files in your vault:
```powershell
Get-ChildItem "C:\Users\sandr\Documents\claude-depot" -Recurse -Filter "*.md" |
  Sort-Object Length -Descending | Select-Object -First 10 FullName, Length
```