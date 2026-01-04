# Sync Error Handling

## Overview

Advanced Memory's sync system now includes robust error handling to prevent hangs and crashes when encountering corrupted or unusual files.

## Protection Features

### 1. File Size Limits
- **Limit**: 10MB maximum file size
- **Behavior**: Files larger than 10MB are skipped with a warning
- **Why**: Prevents memory issues and hanging on extremely large files
- **Log Message**: `"File too large to sync: {path} ({size} MB)"`

### 2. Encoding Error Handling
- **Feature**: Automatic UTF-8 fallback with replacement characters
- **Behavior**: Invalid UTF-8 bytes are replaced with � characters
- **Why**: Prevents crashes on files with encoding issues
- **Log Message**: `"UTF-8 decode failed for {path}, trying with error handling"`

### 3. Markdown Parsing Errors
- **Feature**: Graceful degradation on parsing failures
- **Behavior**: Parse errors are caught and logged, sync continues
- **Why**: One bad file doesn't stop entire sync operation
- **Log Message**: `"Failed to parse markdown file {path}: {error}"`

### 4. Early Validation
- **Feature**: File validation before processing
- **Checks**:
  - File size
  - UTF-8 encoding
  - File existence
- **Why**: Catches issues early, faster feedback

### 5. Malformed Content Handling
- **Feature**: Robust wikilink parsing with safety limits
- **Behavior**: Malformed links are skipped, valid ones parsed
- **Limits**:
  - 5000 links maximum per file
  - 500 character maximum per link target
- **Why**: Prevents infinite loops on malformed markdown

## Error Messages

### File Too Large
```
WARNING: File too large to sync: huge_file.md (15.23 MB)
ERROR: Failed to sync file: path=huge_file.md, error_type=ValueError, error=File exceeds 10MB limit
```

### Encoding Issues
```
WARNING: UTF-8 decode failed for bad_file.md, trying with error handling
INFO: File synced with replacement characters for invalid UTF-8
```

### Parsing Errors
```
ERROR: Failed to parse markdown file corrupt.md: YAMLError: Invalid syntax
INFO: File corrupt.md will be skipped due to YAML syntax error
```

## Testing

### Test Suite
See `tests/sync/test_sync_error_handling.py` for comprehensive error handling tests:

1. `test_sync_large_file` - File size limits
2. `test_sync_invalid_encoding_with_frontmatter` - Encoding fallback
3. `test_sync_malformed_wikilinks` - Malformed link handling
4. `test_validate_large_file` - Early validation
5. `test_validate_bad_encoding` - Encoding validation
6. `test_sync_file_size_limit_prevents_hang` - Hang prevention
7. `test_sync_handles_parse_errors_gracefully` - Parse error recovery

### Running Tests
```bash
pytest tests/sync/test_sync_error_handling.py -v
```

## Implementation Details

### Modified Files

#### `src/advanced_memory/sync/sync_service.py`
- Added file size check in `sync_markdown_file()`
- Added encoding fallback with `errors='replace'`
- Added parse error catching
- Enhanced `validate_file_frontmatter()` with size and encoding checks

#### `src/advanced_memory/markdown/plugins.py`
- Added safety limits to fallback link parser
- Added malformed link skipping
- Added link count limits (5000 max)
- Added link length limits (500 chars max)

## Best Practices

### For Users
1. **Keep files under 10MB** - Split large files if needed
2. **Use UTF-8 encoding** - Avoid legacy encodings
3. **Check logs** - Review warnings for skipped files
4. **Validate frontmatter** - Use proper YAML syntax

### For Developers
1. **Always use try/except** for file operations
2. **Log warnings, not errors** for recoverable issues
3. **Return None gracefully** instead of crashing
4. **Validate early** before heavy processing
5. **Add tests** for new error conditions

## Future Improvements

### Planned
- [ ] Configurable file size limits
- [ ] More detailed progress reporting
- [ ] Automatic file splitting suggestions
- [ ] Enhanced link parser with timeout protection

### Nice to Have
- [ ] Encoding auto-detection and conversion
- [ ] YAML auto-correction for common mistakes
- [ ] Repair mode for corrupted files
- [ ] Health check command for entire knowledge base

## Troubleshooting

### "File too large" warnings
**Solution**: Split file into smaller parts or increase limit in code

### "Invalid UTF-8" errors
**Solution**: Convert file to UTF-8 using a text editor

### "Parse error" messages
**Solution**: Check YAML frontmatter syntax, validate markdown structure

### Sync hanging (should no longer happen!)
**If still occurs**: Report as bug with file characteristics

## Related Documentation
- [Sync Service Architecture](../architecture/sync-service.md)
- [Error Handling Guide](../development/error-handling.md)
- [Testing Guide](../development/testing.md)
