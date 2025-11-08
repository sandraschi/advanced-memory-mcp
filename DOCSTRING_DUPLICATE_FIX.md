# Docstring Duplicate Parameter Fix

**Date:** 2025-10-30  
**Issue:** Duplicate `destination_path` parameter documentation in `content_manager.py`

## Problem Found

In `src/advanced_memory/mcp/tools/content_manager.py`, the `destination_path` parameter was documented twice in the Args section:

```python
destination_path: New path for move operations
                * Move operations: REQUIRED - Full destination path
                * Other operations: NOT USED
edit_operation: Edit type for edit operations
...
destination_path: New path for move operations  # ❌ DUPLICATE
expected_replacements: Expected replacement count for find_replace validation (default: 1)
```

## Fix Applied

Removed the second duplicate entry. The parameter is now only documented once with the correct operation-specific details.

## Verification

✅ Linting passes  
✅ No duplicate documentation  
✅ All parameters correctly documented  

