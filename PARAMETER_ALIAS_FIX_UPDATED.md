# Parameter Alias Fix - Updated

**Date:** 2025-10-30  
**Status:** ✅ Corrected  
**Issue:** Removed problematic `type` parameter alias

## Issue Found

The `type` parameter alias caused a critical bug because `type` is a Python builtin. When used as a parameter name, it shadows the builtin `type()` function, causing unpredictable behavior including notes being created without tags.

## Fix Applied

### Removed from `adn_navigation.py`:

**Before (BROKEN):**
```python
async def adn_navigation(
    ...
    type_filter: Literal[...] | None = "",
    type: str | list[str] | None = None,  # ❌ Shadows Python builtin
    ...
):
    # Alias handling logic
```

**After (FIXED):**
```python
async def adn_navigation(
    ...
    type_filter: Literal["entity", "observation", "relation", ""] | None = "",
    # No 'type' parameter - removed to avoid builtin shadowing
    ...
):
```

## Why Type Filter is Better

The portmanteau tools' newer parameter names (`type_filter` instead of `type`) are actually better because:
- ✅ Avoids Python builtin conflicts
- ✅ More explicit about what it does (filters by type)
- ✅ Can't be confused with Python's `type()` function

## Final Parameter Aliases (Safe Ones Only)

### ✅ Keep: `adn_content`
- `title` → `identifier` (safe, no builtin conflict)
- `results_per_page` → `page_size` (safe, no builtin conflict)

### ✅ Keep: `adn_search`
- `results_per_page` → `page_size` (safe, no builtin conflict)

### ❌ Removed: `adn_navigation`
- ~~`type` → `type_filter`~~ (REMOVED - conflicts with Python builtin)

## Lessons Learned

1. **Don't shadow Python builtins** - Never use builtin names like `type`, `list`, `dict`, `str` as parameters
2. **Newer names can be better** - `type_filter` is actually clearer than `type`
3. **When Claude gets confused, check for builtin shadowing** - This is a common cause of mysterious bugs

## Recommendation

**Use `type_filter` consistently** - don't add alias back. The newer parameter name is better and avoids builtin conflicts.

## Files Modified

- `src/advanced_memory/mcp/tools/adn_navigation.py` - Removed `type` parameter alias

