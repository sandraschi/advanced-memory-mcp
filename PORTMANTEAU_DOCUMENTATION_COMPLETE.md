# Portmanteau Tool Documentation Complete

**Date:** 2025-10-30  
**Status:** ✅ Complete  
**Files Updated:** 4 files (2 docstrings, 2 templates)

## Summary

Fixed and enhanced documentation to clearly explain portmanteau tools to Claude, addressing the confusion about why `identifier` exists and how it works.

## Changes Made

### 1. ✅ Enhanced `adn_content` Docstring

Added comprehensive explanation at the top of the docstring:

```python
WHY PORTMANTEAU TOOLS?
Claude Desktop has a limit on the number of available tools. Portmanteau tools like adn_content
combine multiple related operations (write, read, edit, delete, etc.) into a single tool interface,
dramatically reducing the tool count while maintaining full functionality.

PARAMETER DESIGN:
The 'identifier' parameter is intentionally flexible:
- For write operations: Pass the note title (e.g., "My Meeting Notes")
  Advanced Memory will automatically generate the permalink from the title.
- For read/view operations: Can pass title, permalink, or memory:// URL
  This flexibility allows reading notes in multiple ways.

TIP FOR CLAUDE:
When using this tool, always specify the operation first (write, read, edit, etc.),
then provide the required parameters.
```

### 2. ✅ Clarified Identifier Parameter Documentation

Made it crystal clear what to pass:
```python
identifier: Note identifier - what you pass depends on the operation:
            * Write operations: REQUIRED - The note title as a string (e.g., "My Meeting Notes")
              Advanced Memory will automatically create the permalink from the title.
            * Read/View operations: Can be any of:
              - Note title (e.g., "My Meeting Notes")
              - Permalink (e.g., "meetings/my-meeting-notes")
              - Memory URL (e.g., "memory://meetings/my-meeting-notes")
            * Edit/Move/Delete operations: Usually the note title, but permalinks also work
```

### 3. ✅ Updated Prompt Templates

Updated both `continue_conversation.hbs` and `search.hbs` to:
- Show both standalone and portmanteau tool usage
- Recommend portmanteau tools as primary approach
- Explain why both exist (backward compatibility)

**Example additions:**
```handlebars
You can view this content with: `read_note("{{ permalink }}")` or `adn_content("read", identifier="{{ permalink }}")`

# Using portmanteau tool (adn_content is the recommended approach):
await adn_content("write", identifier="[Note Title]", ...)

# Or using standalone tool:
await write_note(title="[Note Title]", ...)
```

## Key Insights Addressed

### Why Identifier Instead of Title?

**The Answer:** `identifier` is more versatile and semantically correct:
- ✅ Works for all operations (write, read, edit, delete, etc.)
- ✅ Accepts different types of input (title, permalink, URL) depending on operation
- ✅ Clearer than using different parameter names for different operations

### For Write Operations:
- User provides: **note title** (e.g., "My Meeting Notes")
- Advanced Memory generates: permalink automatically
- User should NOT pass permalink - it's generated from title

### For Read Operations:
- User can provide: **title, permalink, or memory:// URL**
- This flexibility makes reading notes easier in different contexts

## Documentation Benefits

1. **Clearer for Claude:** Explains why portmanteau tools exist
2. **Parameter Guidance:** Explicitly states what to pass for each operation
3. **Design Rationale:** Explains why `identifier` is used instead of `title`
4. **Template Integration:** Prompts now show both tool approaches
5. **Best Practices:** Recommends portmanteau tools as primary approach

## Files Modified

1. ✅ `src/advanced_memory/mcp/tools/content_manager.py` - Enhanced docstring
2. ✅ `src/advanced_memory/templates/prompts/continue_conversation.hbs` - Added portmanteau examples
3. ✅ `src/advanced_memory/templates/prompts/search.hbs` - Added portmanteau examples
4. ✅ All linting passes

## Outcome

Claude now has:
- ✅ Clear explanation of why portmanteau tools exist
- ✅ Explicit guidance on what to pass to the `identifier` parameter
- ✅ Examples showing both standalone and portmanteau approaches
- ✅ Understanding that Advanced Memory generates permalinks from titles

This should completely eliminate the confusion about `identifier` vs `title` and make it clear that for write operations, you pass the note title, not a permalink.

