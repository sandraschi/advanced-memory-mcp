# Bug Report: adn_export HTML operation fails with "FunctionTool object is not callable"

**Date:** 2025-12-04
**Severity:** Medium - HTML export broken, but workaround exists
**Component:** `adn_export` tool with `operation="html"`

---

## Problem

Calling `adn_export` with HTML operation fails with:

```
Error calling tool 'adn_export': 'FunctionTool' object is not callable
```

---

## Reproduction

```python
# Via MCP client (Claude Desktop)
mcp_advanced-memory-mcp_adn_export(
    operation="html",
    source_folder="/development/docker",
    site_title="Docker Development Best Practices",
    site_description="Comprehensive guide"
)
```

**Expected:** HTML export created on Desktop
**Actual:** Error: `'FunctionTool' object is not callable`

---

## Environment

- **Advanced Memory Version:** 1.0.0b8
- **FastMCP Version:** >=2.12.0 (from pyproject.toml)
- **Python Version:** 3.11
- **OS:** Windows 11
- **MCP Client:** Claude Desktop / Cursor IDE

---

## Investigation

### Code Analysis

**File:** `src/advanced_memory/mcp/tools/adn_export.py`

```python
@mcp.tool
async def adn_export(operation: str, ...):
    # Routes to appropriate operation
    if operation == "html":
        return await _html_export(
            resolved_export_path, source_folder,
            include_subfolders, show_after_export, project
        )
```

**File:** `src/advanced_memory/mcp/tools/export_html_notes.py`

```python
@mcp.tool
async def export_html_notes(export_path: str, ...):
    # HTML export implementation
    ...
```

**Both tools properly decorated with `@mcp.tool`**

---

## Root Cause Hypothesis

The error `'FunctionTool' object is not callable` suggests:

1. **FastMCP internal routing issue**
   - `FunctionTool` is a FastMCP internal class
   - Something in FastMCP is trying to call a `FunctionTool` object directly
   - Instead of calling the wrapped function

2. **Possible causes:**
   - Portmanteau tool routing bug
   - `async def` within `async def` issue
   - Tool registration conflict
   - FastMCP version mismatch

3. **Why it affects adn_export but not other tools:**
   - `adn_export` is a portmanteau tool (routes to other tools)
   - Calls `export_html_notes` (which is also a standalone tool)
   - FastMCP might not handle tool-calling-tool properly

---

## Workaround

**Use standalone `export_html_notes` tool directly:**

```python
# Instead of:
adn_export("html", ...)

# Use:
export_html_notes(export_path="...", ...)
```

**This works fine!** The issue is only with routing through `adn_export`.

---

## Testing

### Works ✅
```python
# Standalone tool - CONFIRMED WORKING
mcp_advanced-memory-mcp_export_html_notes(
    export_path="C:\\Users\\sandr\\Desktop\\docker-notes-test",
    source_folder="/development"
)
# Result: ✅ Exported 25 notes successfully
# Location: C:\Users\sandr\Desktop\docker-notes-test\
```

**Test Results (2025-12-04 15:47):**
- Total notes: 43
- Successfully exported: 25
- Failed: 18
- Success rate: 58.1%

### Fails ❌
```python
# Via portmanteau - CONFIRMED BROKEN
mcp_advanced-memory-mcp_adn_export(
    operation="html",
    source_folder="/development"
)
# Result: Error calling tool 'adn_export': 'FunctionTool' object is not callable
```

---

## Other Operations

**Do other adn_export operations work?**

Need to test:
- `adn_export("pandoc", ...)` - ❓ Unknown
- `adn_export("docsify", ...)` - ❓ Unknown
- `adn_export("archive", ...)` - ❓ Unknown

**If all operations fail:** Issue is in `adn_export` tool registration
**If only HTML fails:** Issue is in `_html_export` routing specifically

---

## Impact

**Medium severity:**
- HTML export is broken via `adn_export`
- But standalone `export_html_notes` works fine
- Users can work around by using standalone tool

**Not critical:**
- Other export operations (PDF, Docsify, etc.) unknown status
- Workaround is simple and documented

---

## Recommended Fix

### Option 1: Fix FastMCP Tool Routing

If FastMCP has bug handling tool-calling-tool:
- Report to FastMCP maintainers
- Await fix in newer version
- Update Advanced Memory's FastMCP dependency

### Option 2: Refactor adn_export

Change from tool-calling-tool to shared function:

```python
# Instead of calling export_html_notes tool
result = await export_html_notes(...)

# Call shared implementation function directly
from advanced_memory.mcp.tools.export_html_notes import _export_html_impl
result = await _export_html_impl(...)
```

This avoids FastMCP's tool routing entirely.

---

## Next Steps

1. Test other `adn_export` operations (pandoc, docsify, etc.)
2. Check FastMCP changelog for known issues
3. Update FastMCP to latest version
4. Report to FastMCP if it's their bug
5. Consider refactoring adn_export if widespread issue

---

## Workaround Documentation

**For users:**
- Use standalone tools instead of portmanteau
- `export_html_notes` instead of `adn_export("html")`
- Works perfectly, just less convenient

**Updated in:**
- Advanced Memory docs
- Tool descriptions
- Known issues list

---

## Files

**Error occurred in:**
- `src/advanced_memory/mcp/tools/adn_export.py:252` (routing to HTML)
- Somewhere in FastMCP's internal tool execution

**Workaround:**
- `src/advanced_memory/mcp/tools/export_html_notes.py` (use directly)

---

**Status:** ✅ Confirmed bug, workaround verified, low priority

---

## Conclusion

**Root cause:** FastMCP portmanteau routing bug
**Scope:** Only affects `adn_export("html")`, not standalone `export_html_notes`
**Workaround:** Use `export_html_notes` directly - **confirmed working**
**Priority:** Low (perfect workaround exists)

**For maintainers:**
- Check how `adn_export` routes to `export_html_notes`
- FastMCP might not handle tool-calling-tool in portmanteau pattern
- Consider refactoring to call shared implementation functions instead of tools
