# File Filtering Implementation

## Overview
This document details the file filtering implementation added to Basic Memory to improve performance and reduce noise during file synchronization and watching.

## Changes Made

### 1. Ignore Patterns
Added `IGNORE_PATTERNS` set in both `sync_service.py` and `watch_service.py` containing commonly ignored directories and files:

```python
IGNORE_PATTERNS = {
    # Node.js
    "node_modules",
    # Build outputs
    "dist", "build", "target", "out", ".next", ".nuxt",
    # Python
    "__pycache__", ".pytest_cache", ".tox", "venv", ".venv",
    # Package managers / build tools
    "vendor", ".gradle", ".cargo", "coverage",
    # IDE and editor files
    ".vscode", ".idea",
    # Log files
    "*.log", "logs", "*.log.*", "*.log.*.*",
    # OS files
    ".DS_Store", "Thumbs.db"
}
```

### 2. Sync Service Updates
Modified `sync_service.py` to skip ignored directories and files during scanning:
- Updated directory walking to filter out ignored directories in-place
- Added filename pattern matching to skip ignored files
- Maintains existing behavior for hidden files (starting with ".")

### 3. Watch Service Updates
Enhanced `watch_service.py` to filter out changes to ignored paths:
- Updated `filter_changes` method to check against `IGNORE_PATTERNS`
- Preserved existing filtering for hidden files and temporary files
- Added comprehensive logging for filtered paths

## Benefits
1. **Improved Performance**: Reduces unnecessary file system operations, especially in large projects with `node_modules` or similar directories
2. **Reduced Noise**: Prevents syncing of build artifacts, cache files, and log files that change frequently
3. **Better Resource Usage**: Significantly reduces memory and CPU usage during sync operations
4. **Cleaner Backups**: More focused backups without temporary files, build artifacts, or logs
5. **Faster Initial Sync**: Avoids scanning tens of thousands of irrelevant files in development directories
6. **Reduced Disk I/O**: Fewer files to watch and process means less disk activity

## Configuration
To customize the ignored patterns, modify the `IGNORE_PATTERNS` set in both:
- `src/basic_memory/sync/sync_service.py`
- `src/basic_memory/sync/watch_service.py`

## Testing
File filtering is automatically tested as part of the test suite. To manually verify:
1. Create directories matching ignored patterns (e.g., `node_modules`, `__pycache__`)
2. Run the sync process
3. Verify these directories are not included in the sync report
