# Project Setup Edge Cases

**What happens when you copy files or point at large directories**

---

## Question 1: "If I Copy Files Into Project, Do They Get Ingested?"

### Short Answer

**With auto-sync enabled**: ✅ YES (automatic)  
**Without auto-sync**: ⏳ NO (need manual sync)

---

### Scenario A: Auto-Sync Enabled (WatchService Running)

**Setup**:
```bash
# Enable auto-sync in config
# ~/.advanced-memory/config.toml
sync_changes = true

# Start MCP server
advanced-memory mcp
```

**What happens**:
```bash
# You copy a file
cp ~/Downloads/new-note.md ~/Documents/Notes/

# Within 1-2 seconds:
# 1. WatchService detects file addition
# 2. Calls SyncService.sync_file()
# 3. File is indexed
# 4. Console output: [green]OK[/green] new-note.md
```

**Result**: ✅ **Automatic ingestion** (no manual action needed)

**Latency**: ~100-500ms from file copy → indexed in database

---

### Scenario B: Auto-Sync Disabled (Manual Sync)

**Setup**:
```bash
# Auto-sync disabled (default)
sync_changes = false  # or not set

# No MCP server running
```

**What happens**:
```bash
# You copy a file
cp ~/Downloads/new-note.md ~/Documents/Notes/

# Nothing happens automatically!
# File exists on disk but NOT in database

# Later, you run manual sync
advanced-memory sync

# Output:
# Project 'notes': Synced 1 files (1 new, 0 modified, 0 moved, 0 deleted)
```

**Result**: ⏳ **Manual ingestion required** (must run `sync`)

---

### Practical Example

**Without auto-sync**:
```bash
# Your workflow
1. Copy 10 files into project directory
2. Edit some files
3. When ready: advanced-memory sync
4. All changes indexed at once
```

**With auto-sync**:
```bash
# Your workflow
1. Copy 10 files into project directory
2. Files auto-sync in background (watch console output)
3. Edit files → auto-sync
4. Just work normally!
```

---

## Question 2: "What If I Point Project at D:/Dev/Repos?"

### Short Answer

Advanced Memory would **recursively scan EVERY subdirectory**, finding **ALL** `.md` files in **ALL** repos.

**Result**: Could be 1000s of files, long sync time, huge database.

---

### What Actually Happens

**Command**:
```bash
advanced-memory project add allmyrepos D:/Dev/repos
advanced-memory sync
```

**Scanning Process**:
```
D:/Dev/repos/
├── repo1/
│   ├── README.md ✅ (indexed)
│   ├── docs/
│   │   ├── guide.md ✅ (indexed)
│   │   └── api.md ✅ (indexed)
│   ├── node_modules/ ❌ (ignored)
│   └── .git/ ❌ (ignored)
├── repo2/
│   ├── README.md ✅ (indexed)
│   ├── CHANGELOG.md ✅ (indexed)
│   └── .vscode/ ❌ (ignored)
├── repo3/
│   ├── docs/
│   │   └── architecture.md ✅ (indexed)
│   └── __pycache__/ ❌ (ignored)
└── ...
```

**Result**:
- All READMEs from all repos: ✅ indexed
- All markdown in `docs/`: ✅ indexed
- All markdown anywhere in repos: ✅ indexed
- Total files: Could be 100s or 1000s!

---

### Performance Impact

**Example**: 50 repos, average 10 `.md` files each = 500 files

**Initial sync**:
```bash
advanced-memory sync

# Progress:
Syncing project: allmyrepos
Project path: D:/Dev/repos

# Takes 30-60 seconds (depending on machine)
Project 'allmyrepos': Synced 487 files (487 new, 0 modified, 0 moved, 0 deleted)
```

**Database size**: ~50-100 MB (for 500 files)

**Search**: Now searches across **all** repos simultaneously

---

### Is This A Good Idea?

**Pros**:
- ✅ Universal search across all your repos
- ✅ Find documentation anywhere
- ✅ Cross-repo knowledge graph
- ✅ "Where did I document this?" → instant answer

**Cons**:
- ❌ Slow initial sync (30-60 seconds for 500 files)
- ❌ Large database
- ❌ Search results might be overwhelming
- ❌ Mixes unrelated projects

---

### Alternative: Per-Repo Projects

**Instead of**:
```bash
# One mega-project
advanced-memory project add allmyrepos D:/Dev/repos
```

**Consider**:
```bash
# Individual projects
advanced-memory project add project-alpha D:/Dev/repos/project-alpha
advanced-memory project add project-beta D:/Dev/repos/project-beta
advanced-memory project add shared-docs D:/Dev/repos/shared-docs
```

**Benefits**:
- Faster sync (per project)
- Targeted search
- Better organization
- Switch between projects as needed

---

## Detailed Example: Large Directory Sync

### Setup

You have:
```
D:/Dev/repos/
├── advanced-memory-mcp/
│   ├── README.md
│   ├── docs/ (50 .md files)
│   ├── node_modules/ (ignored)
│   └── .git/ (ignored)
├── virtualization-mcp/
│   ├── README.md
│   ├── docs/ (30 .md files)
│   └── node_modules/ (ignored)
├── dbops-mcp/
│   ├── README.md
│   └── docs/ (20 .md files)
└── ... (47 more repos)
```

**Total**: ~250 markdown files across 50 repos

---

### Sync Process

```bash
advanced-memory project add allmyrepos D:/Dev/repos
advanced-memory sync --verbose
```

**Output** (abbreviated):
```
Syncing project: allmyrepos
Project path: D:/Dev/repos

Scanning files...
Found 250 markdown files

Processing:
[OK] advanced-memory-mcp/README.md
[OK] advanced-memory-mcp/docs/architecture/SYNC_ARCHITECTURE_EXPLAINED.md
[OK] advanced-memory-mcp/docs/user-guide/cli-command-reference.md
...
[OK] virtualization-mcp/README.md
[OK] virtualization-mcp/docs/setup.md
...
[OK] dbops-mcp/README.md
...

Project 'allmyrepos': Synced 250 files (250 new, 0 modified, 0 moved, 0 deleted)

Duration: 45 seconds
```

---

### Database Impact

**Before**:
```bash
ls -lh ~/.advanced-memory/advanced_memory.db
# 2 MB (empty database)
```

**After**:
```bash
ls -lh ~/.advanced-memory/advanced_memory.db
# 45 MB (with 250 files indexed)
```

---

### Search Behavior

**Query**:
```bash
advanced-memory tool search-notes "API documentation"
```

**Results** (searches ACROSS all repos):
```json
{
  "results": [
    {
      "title": "API Guide",
      "path": "advanced-memory-mcp/docs/api-guide.md",
      "snippet": "...API documentation for MCP tools..."
    },
    {
      "title": "REST API",
      "path": "virtualization-mcp/docs/api.md",
      "snippet": "...API endpoints for VM management..."
    },
    {
      "title": "Database API",
      "path": "dbops-mcp/docs/api-reference.md",
      "snippet": "...API for database operations..."
    }
  ]
}
```

**Useful?** Depends on use case!

---

## What Gets Ignored (Automatically)

Advanced Memory **skips** these directories:

```python
IGNORE_PATTERNS = {
    # Node.js
    "node_modules",
    
    # Build outputs
    "dist",
    "build",
    "target",
    "out",
    ".next",
    ".nuxt",
    
    # Python
    "__pycache__",
    ".pytest_cache",
    ".tox",
    "venv",
    ".venv",
    
    # Other package managers
    "vendor",
    ".gradle",
    ".cargo",
    "coverage",
    
    # IDE and editor files
    ".vscode",
    ".idea",
    
    # Version control
    ".git",
    
    # OS files
    ".DS_Store",
    "Thumbs.db",
}
```

**Also skips**:
- Hidden files (starting with `.`)
- Non-markdown files (`.txt`, `.py`, `.js`, etc.)

---

## Real-World Scenarios

### Scenario 1: "I Have 100 Repos"

**Bad idea**:
```bash
advanced-memory project add all-repos D:/Dev/repos
advanced-memory sync  # Could take 5+ minutes!
```

**Better**:
```bash
# Create projects for active repos only
advanced-memory project add current-project D:/Dev/repos/current-work
advanced-memory project add docs D:/Dev/repos/shared-docs

# Sync is fast (10-20 seconds)
advanced-memory sync
```

---

### Scenario 2: "I Want Universal Search"

**If you really want to search everything**:

```bash
# Option 1: One mega-project
advanced-memory project add everything D:/Dev/repos
advanced-memory sync  # Wait patiently...

# Option 2: Multiple projects (better!)
advanced-memory project add work D:/Dev/repos/work-projects
advanced-memory project add personal D:/Dev/repos/personal-projects
advanced-memory project add learning D:/Dev/repos/learning

# Switch between as needed
advanced-memory --project work sync
advanced-memory --project personal sync
```

---

### Scenario 3: "I Copy Files Frequently"

**If you're constantly adding files**:

**Enable auto-sync**:
```toml
# ~/.advanced-memory/config.toml
sync_changes = true
```

**Start MCP server**:
```bash
advanced-memory mcp
# Leave running in background
```

**Now**:
- Copy files → auto-indexed
- Edit files → auto-updated
- Delete files → auto-removed
- No manual sync needed!

---

## Performance Guidelines

### File Count Recommendations

| Files | Initial Sync Time | Database Size | Recommendation |
|-------|-------------------|---------------|----------------|
| < 100 | < 10 seconds | < 10 MB | ✅ Perfect |
| 100-500 | 10-30 seconds | 10-50 MB | ✅ Good |
| 500-1000 | 30-60 seconds | 50-100 MB | ⚠️ Acceptable |
| 1000-5000 | 1-5 minutes | 100-500 MB | ⚠️ Slow |
| > 5000 | 5+ minutes | 500+ MB | ❌ Not recommended |

---

### When to Use Large Projects

**Good use cases**:
- ✅ Personal zettelkasten (1000s of small notes)
- ✅ Documentation repos (hundreds of docs)
- ✅ Research papers (organized in folders)
- ✅ Digital garden (interconnected notes)

**Bad use cases**:
- ❌ All your GitHub repos (too many)
- ❌ Entire home directory (way too many)
- ❌ System directories (no markdown files anyway)

---

## Advanced: Selective Syncing

**Currently NOT supported** (but could be added):

**Feature request**: Exclude patterns
```bash
# Hypothetical future feature
advanced-memory project add repos D:/Dev/repos \
  --exclude "*/test/*" \
  --exclude "*/archived/*" \
  --only-include "*/docs/*"
```

**Workaround today**: Create multiple targeted projects

---

## Troubleshooting

### "Sync Takes Forever"

**Problem**: Pointing at too large directory

**Solution**:
1. Check how many files:
   ```bash
   # Linux/macOS
   find D:/Dev/repos -name "*.md" | wc -l
   
   # Windows PowerShell
   (Get-ChildItem -Path D:/Dev/repos -Filter *.md -Recurse).Count
   ```

2. If > 1000 files, consider splitting into smaller projects

---

### "Database is Huge"

**Problem**: Indexed too many files

**Solution**:
```bash
# Option 1: Remove project and start over
advanced-memory project remove allmyrepos
advanced-memory project add specific-repo D:/Dev/repos/specific-repo

# Option 2: Reset database (nuclear option)
advanced-memory reset
```

---

### "Search Returns Too Many Results"

**Problem**: Too many indexed files

**Solution**:
1. Use more specific search queries
2. Or split into smaller, targeted projects

---

## Best Practices

### ✅ Do

1. **Create targeted projects**:
   ```bash
   advanced-memory project add current-work D:/Dev/repos/active-project
   ```

2. **Enable auto-sync for active projects**:
   ```bash
   # In config.toml: sync_changes = true
   advanced-memory mcp
   ```

3. **Test with small directory first**:
   ```bash
   advanced-memory project add test D:/Dev/repos/small-repo
   advanced-memory sync  # See how long it takes
   ```

---

### ❌ Don't

1. **Don't point at entire home directory**:
   ```bash
   # BAD!
   advanced-memory project add everything C:/Users/You
   # Would scan EVERYTHING (hours!)
   ```

2. **Don't point at system directories**:
   ```bash
   # BAD!
   advanced-memory project add system C:/Windows
   # No markdown files anyway
   ```

3. **Don't create overlapping projects**:
   ```bash
   # BAD! (overlapping paths)
   advanced-memory project add parent D:/Dev
   advanced-memory project add child D:/Dev/repos
   # Confusing!
   ```

---

## Summary

### Copying Files Into Project

**With auto-sync**: ✅ Automatic ingestion (~500ms)  
**Without auto-sync**: ⏳ Manual `sync` required

---

### Pointing at Large Directory (D:/Dev/repos)

**What happens**:
- Scans ALL subdirectories recursively
- Indexes ALL `.md` files
- Could be 100s-1000s of files
- Takes 30 seconds to 5+ minutes
- Large database

**Is it a good idea?**
- **Maybe**: If you want universal search across all repos
- **Probably not**: Better to create targeted projects per repo

**Better approach**:
```bash
# Instead of one mega-project
advanced-memory project add specific-repo1 D:/Dev/repos/repo1
advanced-memory project add specific-repo2 D:/Dev/repos/repo2
```

---

### Key Takeaway

**Advanced Memory will index EVERYTHING you point it at!**

Be thoughtful about scope:
- Small, targeted projects → fast, focused
- Large, broad projects → slow, comprehensive

Choose based on your use case! 🎯

---

*Created: 2025-10-17*  
*Purpose: Clarify edge cases for project setup*

