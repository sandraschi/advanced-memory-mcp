# Node Modules Filter Implementation

## Overview

Basic Memory v0.14.2 includes a built-in filter system that excludes `node_modules` and other common build/cache directories from being scanned and indexed. This document describes the implementation details and how the filtering works.

## Problem Statement

Without proper filtering, Basic Memory would attempt to scan and index all files in a project directory, including:
- `node_modules` directories (can contain 100,000+ files)
- Build artifacts (`dist`, `build`, `target`, etc.)
- Cache directories (`__pycache__`, `.pytest_cache`, etc.)
- IDE files (`.vscode`, `.idea`)

This leads to:
- Performance issues during sync operations
- Unnecessary database entries
- Resource consumption
- Sync errors for missing files

## Solution: IGNORE_PATTERNS System

Basic Memory implements a comprehensive ignore pattern system that excludes common directories and files that shouldn't be indexed.

### Pattern Definition

The ignore patterns are defined in two key files:

**File: `src/basic_memory/sync/sync_service.py` (lines 22-36)**
```python
# Common directories to ignore during file scanning and sync
IGNORE_PATTERNS = {
    # Node.js
    "node_modules",
    # Build outputs
    "dist", "build", "target", "out", ".next", ".nuxt",
    # Python
    "__pycache__", ".pytest_cache", ".tox", "venv", ".venv",
    # Other package managers / build tools
    "vendor", ".gradle", ".cargo", "coverage",
    # IDE and editor files
    ".vscode", ".idea",
    # OS files
    ".DS_Store", "Thumbs.db"
}
```

**File: `src/basic_memory/sync/watch_service.py` (lines 19-33)**
```python
# Common directories to ignore during file watching and sync
IGNORE_PATTERNS = {
    # Node.js
    "node_modules",
    # Build outputs
    "dist", "build", "target", "out", ".next", ".nuxt",
    # Python
    "__pycache__", ".pytest_cache", ".tox", "venv", ".venv",
    # Other package managers / build tools
    "vendor", ".gradle", ".cargo", "coverage",
    # IDE and editor files
    ".vscode", ".idea",
    # OS files
    ".DS_Store", "Thumbs.db"
}
```

## Implementation Details

### 1. Directory Scanning Filter

**File: `src/basic_memory/sync/sync_service.py` (lines 579-586)**

During directory scanning, the filter modifies the `dirnames` list in-place to skip ignored directories:

```python
for root, dirnames, filenames in os.walk(str(directory)):
    # Skip dot directories and common ignore patterns in-place
    dirnames[:] = [d for d in dirnames if not d.startswith(".") and d not in IGNORE_PATTERNS]

    for filename in filenames:
        # Skip dot files and files in ignore patterns
        if filename.startswith(".") or filename in IGNORE_PATTERNS:
            continue

        path = Path(root) / filename
        rel_path = str(path.relative_to(directory))
        checksum = await self.file_service.compute_checksum(rel_path)
        result.files[rel_path] = checksum
        result.checksums[checksum] = rel_path
```

**Key Points:**
- `dirnames[:] = [...]` modifies the list in-place, preventing `os.walk()` from descending into ignored directories
- Both directory names and file names are checked against `IGNORE_PATTERNS`
- Hidden files (starting with ".") are also excluded

### 2. File Watching Filter

**File: `src/basic_memory/sync/watch_service.py` (lines 161-182)**

The watch service uses a filter function to exclude paths containing ignored patterns:

```python
def filter_changes(self, change: Change, path: str) -> bool:
    """Filter to only watch non-hidden files and directories, excluding common build/cache dirs.

    Returns:
        True if the file should be watched, False if it should be ignored
    """

    # Skip hidden directories and files
    path_parts = Path(path).parts
    for part in path_parts:
        if part.startswith("."):
            return False
        
        # Skip common ignore patterns (node_modules, build dirs, etc.)
        if part in IGNORE_PATTERNS:
            return False

    # Skip temp files used in atomic operations
    if path.endswith(".tmp"):
        return False

    return True
```

**Key Points:**
- The function is used as a `watch_filter` parameter in the `awatch()` call
- Each path component is checked against `IGNORE_PATTERNS`
- Hidden files and temporary files are also excluded
- Returns `False` to ignore, `True` to watch

### 3. Watch Service Integration

**File: `src/basic_memory/sync/watch_service.py` (lines 122-127)**

The filter is applied when setting up file watching:

```python
async for changes in awatch(
    *project_paths,
    debounce=self.app_config.sync_delay,
    watch_filter=self.filter_changes,  # <-- Filter applied here
    recursive=True,
):
```

## Filtered Patterns

The following patterns are excluded from scanning and watching:

### Node.js/JavaScript
- `node_modules` - NPM package dependencies

### Build Outputs
- `dist` - Distribution/build output
- `build` - Build artifacts
- `target` - Maven/Gradle build output
- `out` - General build output
- `.next` - Next.js build output
- `.nuxt` - Nuxt.js build output

### Python
- `__pycache__` - Python bytecode cache
- `.pytest_cache` - Pytest cache
- `.tox` - Tox virtual environments
- `venv` - Python virtual environment
- `.venv` - Python virtual environment (alternative)

### Other Package Managers
- `vendor` - Go vendor directory
- `.gradle` - Gradle cache
- `.cargo` - Rust Cargo cache
- `coverage` - Test coverage reports

### IDE/Editor Files
- `.vscode` - VS Code settings
- `.idea` - IntelliJ IDEA settings

### OS Files
- `.DS_Store` - macOS metadata
- `Thumbs.db` - Windows thumbnail cache

## Performance Impact

The filter system provides significant performance improvements:

- **Reduced File Scanning**: Excludes thousands of unnecessary files
- **Faster Sync Operations**: Less data to process and index
- **Lower Resource Usage**: Reduced memory and CPU consumption
- **Fewer Errors**: Avoids sync errors for missing build artifacts

## Historical Data Cleanup

If a Basic Memory database contains historical entries for ignored patterns (e.g., from before the filter was implemented), cleanup scripts can be used:

```sql
-- Remove all node_modules entries
DELETE FROM entity WHERE file_path LIKE '%node_modules%';

-- Remove other build artifacts
DELETE FROM entity WHERE file_path LIKE '%/build/%' OR file_path LIKE '%\\build\\%';
DELETE FROM entity WHERE file_path LIKE '%/dist/%' OR file_path LIKE '%\\dist\\%';
DELETE FROM entity WHERE file_path LIKE '%__pycache__%';
```

## Configuration

Currently, the ignore patterns are hardcoded in the source code. Future versions may support:

- User-configurable ignore patterns
- `.gitignore` file support
- Project-specific ignore rules
- Environment-based filtering

## Testing

To verify the filter is working:

1. Create a test project with a `node_modules` directory
2. Run Basic Memory sync
3. Check that no `node_modules` files appear in the database
4. Verify that the watch service doesn't monitor `node_modules` changes

## Conclusion

The node_modules filter implementation in Basic Memory v0.14.2 provides robust protection against indexing unnecessary files. The dual-layer approach (scanning filter + watch filter) ensures that both initial sync and ongoing file monitoring respect the ignore patterns, resulting in better performance and cleaner data.
