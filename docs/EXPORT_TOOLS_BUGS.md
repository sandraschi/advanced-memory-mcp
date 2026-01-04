# Export Tools - Known Bugs

## Overview

Export tools had **ZERO test coverage** before this testing initiative. Tests immediately revealed critical bugs that would cause silent failures for users.

## Critical Issues Found

### 1. Docsify Export - 'md_path' Error ✅ FIXED

**Tool**: `export_docsify_enhanced`
**Severity**: HIGH
**Status**: ✅ FIXED

**Symptoms**:
```
# Docsify Export Failed

Unexpected error: 'md_path'
```

**Root Cause**:
- Sidebar creation happened BEFORE note export
- `_create_enhanced_sidebar()` was called with `notes_data` instead of `exported_files`
- `notes_data` doesn't have `md_path` key
- `exported_files` is populated during note export

**The Fix**:
1. Added `md_path` key to `exported_files` dictionary (line 187)
2. Moved note export loop BEFORE sidebar creation (line 162)
3. Changed sidebar creation to use `exported_files` parameter (line 190)

**Test Coverage**: 10 comprehensive tests, all passing
**Test File**: `tests/mcp/test_export_docsify.py`

---

## Test Coverage Status

| Export Tool | Test File | Coverage | Status |
|------------|-----------|----------|--------|
| export_docsify.py | test_export_docsify.py | 1 test (skipped) | ⚠️  Bugs found |
| export_html_notes.py | None | 0% | ❌ Not tested |
| export_pandoc.py | None | 0% | ❌ Not tested |
| export_joplin_notes.py | None | 0% | ❌ Not tested |
| export_evernote_compatible.py | None | 0% | ❌ Not tested |
| export_notion_compatible.py | None | 0% | ❌ Not tested |
| export_to_archive.py | None | 0% | ❌ Not tested |

---

## Next Steps

1. **Fix Docsify 'md_path' bug** (HIGH PRIORITY)
   - Debug the export_docsify_enhanced function
   - Find where 'md_path' is accessed incorrectly
   - Add proper error handling

2. **Create tests for remaining export tools**
   - export_html_notes.py
   - export_pandoc.py
   - export_joplin_notes.py
   - Others

3. **Add error handling to all export tools**
   - Catch file I/O errors
   - Validate paths before writing
   - Provide clear error messages

4. **Test edge cases**
   - Empty folders
   - Special characters in filenames
   - Large note collections
   - Nested folder structures

---

## Why This Matters

Export tools are **critical for user workflows**:
- Users rely on exports for backups
- Documentation generation is a key feature
- Silent failures could cause data loss
- No validation means bugs go unnoticed

**Before this testing**: All 7 export tools were completely untested
**After creating 1 test**: Found critical bug immediately

This proves the value of comprehensive testing!
