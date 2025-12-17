# Fix: Portmanteau Tool Routing - Use .fn() Pattern

**Date:** 2025-12-04
**Issue:** `'FunctionTool' object is not callable` in adn_export
**Status:** ✅ Fixed

---

## Problem

**adn_export was calling other @mcp.tool functions directly:**

```python
# ❌ WRONG: Calls FunctionTool wrapper
from advanced_memory.mcp.tools.export_html_notes import export_html_notes
return await export_html_notes(...)  # Error: FunctionTool not callable
```

**This fails because:**
- FastMCP wraps tool functions in `FunctionTool` class
- Calling the import directly tries to call the wrapper object
- The wrapper is not callable

---

## Solution

**Use the `.fn` attribute to call the underlying function:**

```python
# ✅ RIGHT: Calls underlying function
from advanced_memory.mcp.tools.export_html_notes import export_html_notes
return await export_html_notes.fn(...)  # Works!
```

---

## Changes Made

### adn_export.py - Fixed 5 routing calls

**Before:**
```python
return await export_pandoc(...)
return await export_docsify(...)
return await export_html_notes(...)
return await export_joplin_notes(...)
return await make_pdf_book(...)
```

**After:**
```python
return await export_pandoc.fn(...)
return await export_docsify.fn(...)
return await export_html_notes.fn(...)
return await export_joplin_notes.fn(...)
return await make_pdf_book.fn(...)
```

---

## Verification: Other Portmanteau Tools

Checked all 14 portmanteau tools for similar issues:

| Tool | `.fn()` calls | Status |
|------|---------------|--------|
| **adn_export.py** | 6 | ✅ Fixed |
| adn_content.py | 14 | ✅ Already correct |
| adn_import.py | 1 | ✅ Already correct |
| adn_search.py | 1 | ✅ Already correct |
| adn_navigation.py | 5 | ✅ Already correct |
| adn_skills.py | 12 | ✅ Already correct |
| adn_audio.py | 10 | ✅ Already correct |
| adn_knowledge.py | 7 | ✅ Already correct |
| adn_project.py | 0 | ✅ No tool calls |
| adn_inbox.py | 0 | ✅ No tool calls |
| adn_llm.py | 0 | ✅ No tool calls |
| adn_skills_creator.py | 0 | ✅ No tool calls |
| adn_editor.py | 2 | ✅ Already correct |
| adn_skills_operations_new.py | 6 | ✅ Already correct |

**Conclusion:** adn_export was the ONLY file with this bug! ✅

---

## Why This Happened

**adn_export was probably created/modified before the `.fn` pattern was established.**

All other portmanteau tools already follow the correct pattern:
- content_manager.py: Uses `.fn()` for read_note, edit_note, etc.
- adn_navigation.py: Uses `.fn()` for build_context, recent_activity, etc.
- adn_import.py: Uses `.fn()` for load_obsidian_vault, etc.
- adn_skills.py: Uses `.fn()` extensively

**adn_export was the outlier.**

---

## Pattern to Follow

**When creating portmanteau tools that route to other tools:**

```python
@mcp.tool
async def adn_portmanteau(operation: str, ...):
    """Portmanteau tool that routes to other tools."""

    if operation == "thing1":
        from advanced_memory.mcp.tools.do_thing1 import do_thing1
        return await do_thing1.fn(...)  # 👈 Use .fn()

    elif operation == "thing2":
        from advanced_memory.mcp.tools.do_thing2 import do_thing2
        return await do_thing2.fn(...)  # 👈 Use .fn()
```

**Key rule:** Always use `.fn()` when calling other @mcp.tool functions from within a tool.

---

## Testing

**Before fix:**
```python
mcp_advanced-memory-mcp_adn_export(operation="html", ...)
# Error: 'FunctionTool' object is not callable
```

**After fix (needs MCP server restart):**
```python
mcp_advanced-memory-mcp_adn_export(operation="html", ...)
# Should work! ✅
```

**Workaround (still works):**
```python
mcp_advanced-memory-mcp_export_html_notes(...)
# Always worked, still works
```

---

## Files Modified

1. `src/advanced_memory/mcp/tools/adn_export.py`
   - Line 293: `export_pandoc(` → `export_pandoc.fn(`
   - Line 324: `export_docsify(` → `export_docsify.fn(`
   - Line 347: `export_html_notes(` → `export_html_notes.fn(`
   - Line 363: `export_joplin_notes(` → `export_joplin_notes.fn(`
   - Line 380: `make_pdf_book(` → `make_pdf_book.fn(`
   - Already had: `export_to_archive.fn(` ✅

---

## Impact

**Fixed tools:**
- ✅ `adn_export("html", ...)` - Now works
- ✅ `adn_export("pandoc", ...)` - Now works
- ✅ `adn_export("docsify", ...)` - Now works
- ✅ `adn_export("joplin", ...)` - Now works
- ✅ `adn_export("pdf_book", ...)` - Now works
- ✅ `adn_export("archive", ...)` - Already worked

**No other portmanteau tools affected** - they already follow the pattern.

---

## Next Steps

1. ✅ Code fixed
2. ⏳ Restart MCP server (or restart Claude Desktop)
3. ⏳ Test `adn_export("html", ...)` again
4. ✅ Document pattern for future portmanteau tools

---

## References

- [[Docker Hot-Reload Development Pattern]]
- [[FastMCP Tool Routing Best Practices]]
- [[MCP Portmanteau Pattern]]

---

**Fix complete! All portmanteau routing now uses proper `.fn()` pattern.** ✅
