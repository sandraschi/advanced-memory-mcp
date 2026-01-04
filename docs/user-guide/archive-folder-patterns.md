# Archive and Obsolete Folder Patterns

## Overview

Advanced Memory automatically **skips folders marked as obsolete or archived** during sync. This allows you to keep old versions, backups, and deprecated content in your project directory without them being indexed.

## How It Works

Folders containing these patterns in their name are **automatically ignored**:

### Backup Patterns
- `-backup-` - e.g., `claude-depot-backup-20251010`
- `.backup` - e.g., `project.backup`
- `_backup` - e.g., `old_backup`

### Obsolete Patterns
- `.obsolete` - e.g., `old-version.obsolete`
- `-obsolete` - e.g., `deprecated-code-obsolete`
- `_obsolete` - e.g., `legacy_code_obsolete`

### Archived Patterns
- `.archived` - e.g., `2024-work.archived`
- `-archived` - e.g., `completed-project-archived`
- `_archived` - e.g., `old_research_archived`

## Use Cases

### Use Case 1: Keeping Old Backups

**Scenario**: You reorganized your `claude-depot` folder but want to keep the old version.

**Solution**:
```bash
# Rename to mark as obsolete
mv claude-depot-backup-20251010 claude-depot-backup-20251010.obsolete
```

**Result**:
- ✅ Folder preserved on disk
- ✅ Not indexed during sync
- ✅ Not searched
- ✅ Doesn't clutter your knowledge base

### Use Case 2: Archiving Completed Projects

**Scenario**: Project is done but you want to keep the files for reference.

**Solution**:
```bash
# Rename to mark as archived
mv old-research old-research.archived
```

**Result**:
- ✅ Files stay on disk
- ✅ Not indexed
- ✅ Easy to find if you need to reference later
- ✅ Clear visual indicator it's archived

### Use Case 3: Multiple Versions

**Scenario**: You have multiple iterations of documentation.

**Structure**:
```
documentation/
├── current/                 ← Actively indexed
├── v1.0.obsolete/          ← Skipped
├── v2.0.obsolete/          ← Skipped
└── draft-old-backup/       ← Skipped (contains -backup-)
```

**Result**: Only `current/` is indexed!

## Examples

### Folder Names That Will Be Skipped

✅ Automatically ignored:
- `claude-depot-backup-20251010-044425` (contains `-backup-`)
- `old-version.obsolete`
- `legacy-code-obsolete`
- `2024-work.archived`
- `project_backup`
- `deprecated.obsolete`
- `archive-2024.archived`

### Folder Names That Will Be Indexed

❌ Will still be indexed:
- `backup-notes` (doesn't match pattern `-backup-` with hyphens on both sides)
- `obsolete-ideas` (pattern at start, not marked as obsolete)
- `my-archive` (pattern at start, not marked as archived)

**Tip**: Put the pattern at the **end** of the folder name for clarity!

## Renaming Guidelines

### Best Practices

**Good naming** (clear what it is):
```
project-name.obsolete              ← Clear it's obsolete
project-name-backup-20251019       ← Timestamped backup
project-name.archived              ← Clearly archived
```

**Avoid** (might still be indexed):
```
obsolete-project-name              ← Pattern at wrong end
backup_project                     ← Might be ambiguous
old-version                        ← Unclear if obsolete
```

### Recommended Pattern

**Use ISO dates for backups**:
```
claude-depot-backup-20251019       ← Contains -backup-, auto-skipped
my-project-backup-2025-10-19       ← Contains -backup-, auto-skipped
```

**Use .obsolete suffix for deprecated content**:
```
old-implementation.obsolete        ← Clear and skipped
legacy-version.obsolete            ← Clear and skipped
```

## PowerShell Commands

### Rename to Mark as Obsolete

```powershell
Rename-Item "C:\path\to\old-folder" "old-folder.obsolete"
```

### Rename to Mark as Backup

```powershell
$date = Get-Date -Format "yyyyMMdd"
Rename-Item "C:\path\to\project" "project-backup-$date"
```

### Batch Rename Multiple Folders

```powershell
# Mark all folders ending with -old as obsolete
Get-ChildItem -Directory "*-old" | ForEach-Object {
    Rename-Item $_.FullName "$($_.Name).obsolete"
}
```

## What Gets Ignored vs What Doesn't

### Ignored Folders (Not Indexed)
- Hidden folders (starting with `.`)
- Build folders (`node_modules`, `dist`, `build`, etc.)
- **Archive patterns** (`-backup-`, `.obsolete`, `.archived`)

### Still Indexed
- Regular folders
- Archive folders (if named `archive` without a pattern marker)
- Old folders (if not marked with a pattern)

## Checking What Will Be Indexed

Use the diagnostic script:

```powershell
python scripts\diagnose_sync.py "C:\Users\sandr\Documents\claude-depot"
```

This will show:
- ✅ Folders that will be scanned
- ❌ Folders that will be skipped
- 📁 Reason for skipping

## Example Output

```
SKIPPED FOLDER: claude-depot-backup-20251010.obsolete (reason: archive pattern)
SKIPPED FOLDER: old-version.obsolete (reason: archive pattern)
SKIPPED FOLDER: node_modules (reason: in ignore list)
FOUND MARKDOWN: current-docs/guide.md
```

## Migration Guide

### Step 1: Identify Old Content

List folders you want to preserve but not index:
- Old backups
- Deprecated code
- Completed projects
- Legacy documentation

### Step 2: Rename Them

Add a marker pattern:
```powershell
Rename-Item "old-project" "old-project.obsolete"
```

### Step 3: Verify

```powershell
python scripts\diagnose_sync.py "C:\your\project"
```

Check that obsolete folders appear as "SKIPPED".

### Step 4: Re-sync

If using Claude Desktop:
- Restart Claude Desktop
- Wait for auto-sync

Or manually:
```bash
advanced-memory sync
```

## FAQ

### Q: Will my files be deleted?

**No!** Files are **preserved** - they just won't be indexed in the database.

### Q: Can I still access archived content?

**Yes!** Files are still on disk. You can:
- Browse them directly in File Explorer
- Open them in your editor
- Temporarily remove the `.obsolete` marker to re-index

### Q: What if I want to search archived content?

Remove the marker temporarily:
```powershell
Rename-Item "project.obsolete" "project"
# Wait for sync
# Search...
# Then rename back
Rename-Item "project" "project.obsolete"
```

### Q: Are archive folders backed up?

**Yes!** If you back up your project directory, archived folders are included. They're just not indexed in the database.

### Q: Can I customize the patterns?

Currently patterns are hardcoded in `sync_service.py`. To add custom patterns, modify the `ARCHIVE_PATTERNS` set and rebuild.

## See Also

- [File Type Filtering](file-type-filtering.md)
- [Project Setup Guide](project-setup-quick-guide.md)
- [Database Architecture](../architecture/DATABASE_ARCHITECTURE.md)
