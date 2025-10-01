# Archive & Migration Guide 📦

Complete backup and migration tools for Basic Memory knowledge bases.

## Overview

The archive tools provide complete system backup and migration capabilities for Basic Memory. These tools allow you to create full backups of your entire knowledge base and restore them on new machines or recover from system failures.

## Tools

### `export_to_archive` - Create System Backup

Creates a complete, compressed archive of your entire Basic Memory installation.

#### Features
- **Complete System Backup**: Includes database, all projects, and configuration
- **Compressed Archives**: Efficient ZIP format for storage and transfer
- **Selective Project Export**: Choose which projects to include
- **Metadata Tracking**: Archive includes creation date, file counts, and contents
- **Cross-Platform Compatible**: Archives work on any operating system

#### Usage Examples

```python
# Create complete backup of all projects
await export_to_archive.fn(
    archive_path="basic-memory-backup.zip"
)

# Backup only specific projects
await export_to_archive.fn(
    archive_path="my-projects-backup.zip",
    include_projects=["work", "personal"]
)

# Create uncompressed archive for local storage
await export_to_archive.fn(
    archive_path="backup.tar",
    compress=False
)

# Clean archive excluding test/draft content
await export_to_archive.fn(
    archive_path="production-backup.zip",
    exclude_tags=["test", "draft", "obsolete"]
)

# Recent data only (last 6 months)
await export_to_archive.fn(
    archive_path="recent-backup.zip",
    since_date="6m"
)

# Exclude specific projects
await export_to_archive.fn(
    archive_path="work-only-backup.zip",
    exclude_projects=["personal", "archive"]
)

# Combined filtering
await export_to_archive.fn(
    archive_path="clean-recent-backup.zip",
    exclude_tags=["obsolete", "temp"],
    since_date="2024-01-01",
    include_projects=["work", "personal"]
)
```

#### Parameters
- `archive_path` (str, REQUIRED): Path for the archive file
- `include_projects` (List[str], optional): Specific projects to include (default: all)
- `exclude_projects` (List[str], optional): Projects to exclude (takes precedence over include_projects)
- `exclude_tags` (List[str], optional): Tags to exclude (e.g., ["obsolete", "test", "draft"])
- `since_date` (str, optional): Only include data since date (ISO format: "2024-01-01" or relative: "30d", "1y")
- `compress` (bool, optional): Create ZIP archive (default: True)
- `project` (str, optional): Active project context

#### Advanced Filtering (Now Available!)
✅ **Tag and date filtering are now fully implemented!**

**Available Filters:**
- **Project Filtering**: Include or exclude specific projects
- **Tag Exclusion**: Skip notes/entities with specified tags
- **Time-based Filtering**: Only include data since specified date
- **Semantic Link Cleanup**: Foreign key constraints automatically clean up broken references

*Note: Filtered archives may have broken semantic links. Run rescan after import to rebuild relationships.*

#### Filtering Logic

**Priority Order:**
1. `exclude_projects` (highest priority - removes projects completely)
2. `include_projects` (if exclude_projects not specified)
3. `exclude_tags` (filters database entities)
4. `since_date` (filters by creation/update date)

**Database Filtering:**
- Tag filtering searches entity metadata for tag arrays
- Date filtering uses `created_at` and `updated_at` timestamps
- Foreign key constraints automatically clean up orphaned relationships
- Only entities passing all filters are included

**File Filtering:**
- Project directories are filtered based on project selection
- Files are included based on database entity filtering
- Orphaned files (without database entities) are excluded

**Example Filter Results:**
```python
# Exclude "test" and "obsolete" tags, only since 2024
exclude_tags=["test", "obsolete"], since_date="2024-01-01"
# Result: Only entities created/updated in 2024+ that don't have test/obsolete tags
```

#### Archive Contents

```
basic-memory-backup.zip/
├── database/
│   └── memory.db          # SQLite database with all knowledge
├── config/
│   └── config.json        # Global configuration
├── projects/
│   ├── work/              # Project directories
│   │   ├── notes/
│   │   └── docs/
│   └── personal/
│       └── journal/
└── metadata.json          # Archive information
```

### `import_from_archive` - Restore from Backup

Restores a complete Basic Memory system from an archive created with `export_to_archive`.

#### Features
- **Complete System Restoration**: Restores database, projects, and configuration
- **Safety Checks**: Validates archive integrity before restoration
- **Backup Protection**: Optional backup of existing data
- **Multiple Restore Modes**: Overwrite, merge, or skip existing data
- **Dry-Run Preview**: Preview changes without applying them
- **Rollback Capability**: Easy recovery if issues occur

#### Restore Modes

- **`"overwrite"`** (default): Replace existing data completely
- **`"merge"`**: Combine with existing data (future feature)
- **`"skip_existing"`**: Only restore missing items

#### Usage Examples

```python
# Restore complete system (with backup)
await import_from_archive.fn(
    archive_path="basic-memory-backup.zip"
)

# Preview what would be restored
await import_from_archive.fn(
    archive_path="backup.zip",
    dry_run=True
)

# Restore without backing up existing data
await import_from_archive.fn(
    archive_path="backup.zip",
    backup_existing=False
)

# Merge mode (when implemented)
await import_from_archive.fn(
    archive_path="backup.zip",
    restore_mode="merge"
)
```

#### Parameters
- `archive_path` (str, REQUIRED): Path to archive file
- `restore_mode` (str, optional): "overwrite", "merge", or "skip_existing"
- `backup_existing` (bool, optional): Backup current data (default: True)
- `dry_run` (bool, optional): Preview changes only (default: False)
- `project` (str, optional): Active project context

## Migration Workflow

### Migrating to a New PC

1. **On Old Machine:**
   ```python
   await export_to_archive.fn(
       archive_path="migration-backup.zip"
   )
   ```

2. **Transfer Archive:**
   - Copy `migration-backup.zip` to new machine
   - Install Basic Memory on new machine

3. **On New Machine:**
   ```python
   await import_from_archive.fn(
       archive_path="migration-backup.zip"
   )
   ```

4. **Verify Restoration:**
   - Check that all projects are accessible
   - Verify knowledge content is intact
   - Test search and navigation functionality

### Backup Strategy

#### Regular Backups
```python
# Weekly backup
await export_to_archive.fn(
    archive_path="weekly-backup.zip"
)
```

#### Project-Specific Backups
```python
# Backup only work-related projects
await export_to_archive.fn(
    archive_path="work-backup.zip",
    include_projects=["work", "projects"]
)
```

#### Before Major Changes
```python
# Backup before system updates
await export_to_archive.fn(
    archive_path="pre-update-backup.zip"
)
```

## Safety & Recovery

### Automatic Backups
The import tool automatically creates backups of existing data:
```
~/basic-memory-backups/pre-import-[timestamp]/
```

### Manual Recovery
If restoration fails or causes issues:

1. **Stop Basic Memory**
2. **Restore from backup:**
   ```python
   await import_from_archive.fn(
       archive_path="~/basic-memory-backups/pre-import-[timestamp]/backup.zip"
   )
   ```

### Validation Checks

#### Archive Validation
- Verifies archive structure
- Checks for required components
- Validates metadata integrity

#### System Validation
- Confirms database integrity
- Verifies project structure
- Checks configuration validity

## Archive Format Details

### Compression
- **ZIP Format**: Standard compression for cross-platform compatibility
- **TAR Format**: Uncompressed option for local storage

### Metadata
Each archive includes `metadata.json`:
```json
{
  "version": "1.0",
  "created_at": "2025-01-29T10:30:00",
  "total_files": 1250,
  "total_size_bytes": 52428800,
  "projects_exported": ["work", "personal", "research"],
  "compressed": true,
  "database_included": true,
  "config_included": true
}
```

### File Organization
- **Database**: `database/memory.db` - SQLite database
- **Configuration**: `config/config.json` - Global settings
- **Projects**: `projects/[name]/` - Project directories
- **Metadata**: `metadata.json` - Archive information

## Troubleshooting

### Common Issues

#### "Archive Not Found"
- Verify the archive path is correct
- Check file permissions
- Ensure archive wasn't corrupted during transfer

#### "Invalid Archive Structure"
- Confirm archive was created with `export_to_archive`
- Check for corruption during creation/transfer
- Verify archive isn't password-protected

#### "Permission Denied"
- Run Basic Memory with appropriate permissions
- Check write access to restoration directories
- Ensure database files aren't locked by other processes

#### "Database Conflicts"
- Close any running Basic Memory instances
- Ensure no other applications are using the database
- Try restore mode "overwrite" if merge fails

### Recovery Options

#### Partial Restoration
Currently restores complete archives. Future versions may support selective restoration.

#### Manual Recovery
For advanced users, archives can be manually extracted:
```bash
unzip basic-memory-backup.zip
# Then manually copy files to appropriate locations
```

## Best Practices

### Backup Frequency
- **Daily**: For active knowledge bases
- **Weekly**: For regular usage
- **Before Changes**: Major updates, migrations, or experiments

### Storage Locations
- **Local**: Keep recent backups on local storage
- **External**: Store weekly backups on external drives
- **Cloud**: Archive monthly backups to cloud storage

### Archive Naming
```python
# Include timestamp and purpose
archive_path="backup-2025-01-29-weekly.zip"
archive_path="migration-to-new-pc.zip"
archive_path="pre-major-update.zip"
```

### Testing Restorations
Regularly test backup restoration:
```python
# Test on separate system or directory
await import_from_archive.fn(
    archive_path="test-backup.zip",
    dry_run=True  # Preview first
)
```

## Future Enhancements

### Planned Features
- **Incremental Backups**: Only backup changes since last backup
- **Selective Restoration**: Restore individual projects or components
- **Cloud Integration**: Direct backup to cloud storage
- **Encryption**: Password-protected archives
- **Compression Options**: Custom compression levels

### Version Compatibility
Archives are versioned to ensure compatibility:
- **v1.0**: Current format
- Future versions will maintain backward compatibility

---

**Need Help?** Use `help("archive")` for detailed tool documentation or check the troubleshooting section above.
