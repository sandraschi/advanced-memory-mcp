# Standalone Tool Fix - type → type_filter

**Date:** 2025-10-30  
**Status:** ✅ Complete  
**Issue:** Removed Python builtin shadowing from standalone `recent_activity` tool

## Problem

The standalone `recent_activity` tool was using `type` as a parameter name, which:
- ❌ Shadows Python's builtin `type()` function
- ❌ Causes unpredictable bugs (notes created without tags)
- ❌ Violates Python best practices (PEP 8)

## Fix Applied

### Changed in `recent_activity.py`:

**Before (BROKEN):**
```python
async def recent_activity(
    type: str | list[str] = "",  # ❌ Shadows Python builtin
    ...
) -> GraphContext:
```

**After (FIXED):**
```python
async def recent_activity(
    type_filter: str | list[str] = "",  # ✅ Clear, no conflicts
    ...
) -> GraphContext:
```

### All References Updated:

1. ✅ Function signature parameter name
2. ✅ Docstring parameter description
3. ✅ All examples in docstring
4. ✅ All internal variable references
5. ✅ Logging statements

## Files Modified

- `src/advanced_memory/mcp/tools/recent_activity.py` - Changed `type` → `type_filter` everywhere

## Benefits

1. **No more builtin conflicts** - Can't shadow Python's `type()` function
2. **Clearer semantics** - `type_filter` clearly indicates filtering behavior
3. **Consistent naming** - Matches portmanteau tool naming (`adn_navigation`)
4. **Fixed bugs** - Notes will now be created with tags properly

## Breaking Change Notice

This is a **breaking change** for code using the standalone `recent_activity` tool:

**Old code (BROKEN):**
```python
recent_activity(type="entity")
```

**New code (CORRECT):**
```python
recent_activity(type_filter="entity")
```

**Migration:** Update all calls from `type=` to `type_filter=`

## Verification

✅ All ruff checks pass with zero errors
✅ Parameter name no longer shadows Python builtin
✅ Consistent with portmanteau tool naming

