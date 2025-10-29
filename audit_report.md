# Portmanteau Tools Audit Report - Return Type Issues

## Overview
Auditing all portmanteau tools to identify places where underlying tools return Pydantic objects (SearchResponse, GraphContext) instead of strings.

## Tools Audited
1. ✅ `adn_navigation` - FIXED (converts GraphContext to string)
2. ❌ `adn_search` - POTENTIAL ISSUE (may return SearchResponse object)
3. ⚠️ `adn_content` - NEEDS CHECK (called by other portmanteau tools)
4. ❓ `adn_knowledge` - NEEDS CHECK
5. ❓ `adn_skills` - NEEDS CHECK  
6. ❓ `adn_export` - NEEDS CHECK
7. ❓ `adn_import` - NEEDS CHECK
8. ❓ `adn_audio` - NEEDS CHECK
9. ❓ `adn_inbox` - NEEDS CHECK

## Issues Found

### 1. `adn_search.py` - `_notes_search` operation
**Problem**: Calls `search_notes` which returns `SearchResponse | str` but may return `SearchResponse` object.

**Location**: `src/advanced_memory/mcp/tools/adn_search.py:106-120`

```python
async def _notes_search(...) -> str:
    """Handle Advanced Memory notes search operation."""
    from advanced_memory.mcp.tools.search import search_notes

    return await search_notes(
        query, page, page_size, "text", types, entity_types, after_date, project
    )  # ❌ May return SearchResponse object instead of string
```

**Fix Required**: Convert `SearchResponse` to formatted string before returning.

**Similar Issue**: All external search operations (obsidian, joplin, notion, evernote) appear to return strings, so they should be OK.

### 2. `adn_navigation.py` - FIXED ✅
**Status**: Already fixed for `build_context` and `recent_activity` operations.
**Remaining Operations**: 
- `list_directory` - calls underlying tool that returns string ✅
- `status` - calls underlying tool that returns string ✅
- `sync_status` - calls underlying tool that returns string ✅
- `backlinks` - builds custom string response ✅

## Recommendations

### Priority 1: Fix `adn_search._notes_search`
The `search_notes` tool returns `SearchResponse | str`. The portmanteau should:
1. Always convert SearchResponse to formatted string
2. Handle the case where search_notes returns a string (error cases)

### Priority 2: Add formatting helper
Create a helper function to convert SearchResponse to markdown:

```python
def format_search_response(search_response: SearchResponse) -> str:
    """Convert SearchResponse to formatted markdown string."""
    output = [f"# Search Results: {len(search_response.results)} matches\n"]
    
    for idx, item in enumerate(search_response.results, 1):
        title = item.title or "Untitled"
        permalink = item.permalink or ""
        item_type = item.entity_type or "note"
        
        output.append(f"## {idx}. {title}")
        output.append(f"**Type:** {item_type}")
        output.append(f"**Permalink:** `{permalink}`")
        
        # Add content snippet if available
        if hasattr(item, 'content') and item.content:
            snippet = item.content[:200] + "..." if len(item.content) > 200 else item.content
            output.append(f"**Preview:** {snippet}")
        
        output.append("")
    
    # Add pagination info
    if hasattr(search_response, 'current_page'):
        output.append(f"\n**Page:** {search_response.current_page}")
    
    return "\n".join(output)
```

### Priority 3: Test all portmanteau tools
Run comprehensive tests to ensure all portmanteau tools always return strings, not Pydantic objects.

## Files Modified
1. ✅ `src/advanced_memory/mcp/tools/adn_search.py` - Added SearchResponse formatting (FIXED)

## Changes Made
- Modified `_notes_search` to convert `SearchResponse` objects to formatted markdown strings
- Added proper handling for error cases (when search_notes returns a string)
- Added content previews and pagination info to search results
- Fixed linting errors (whitespace, unused imports)

## Related Files
- `src/advanced_memory/mcp/tools/search.py` - source of SearchResponse
- `src/advanced_memory/schemas/search.py` - SearchResponse definition
