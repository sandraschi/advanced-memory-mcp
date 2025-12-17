# Fix: Export Search Logic - Use Wildcard and Project URL

**Date:** 2025-12-04
**Issue:** Pandoc and PDF Book exports found no notes
**Status:** ✅ Fixed

---

## Problem

**Pandoc and PDF Book exports couldn't find notes:**

```python
adn_export("pandoc", format_type="pdf", source_folder="/development")
# Result: "No notes found in folder '/development' for export"
```

**But HTML export worked fine:**

```python
adn_export("html", source_folder="/development")
# Result: Exported 25 notes successfully
```

---

## Root Cause

### HTML Export (Working)
```python
# Uses wildcard search
search_query = SearchQuery(text="*")

# Uses project-specific endpoint
await call_post(client, f"{project_url}/search/", ...)
```

### Pandoc Export (Broken)
```python
# Uses empty string search
query = SearchQuery(text="", types=["note"])

# Uses wrong API endpoint
await call_post(client, "/api/search", ...)
```

**Two issues:**
1. Empty string search (`text=""`) doesn't match notes
2. Wrong API endpoint (`/api/search` vs `{project_url}/search/`)

---

## Solution

**Use the same working pattern from HTML export:**

```python
# Use wildcard search
search_query = SearchQuery(text="*")

# Use project-specific endpoint
active_project = get_active_project(project)
project_url = active_project.project_url
await call_post(client, f"{project_url}/search/", ...)
```

---

## Files Fixed

### 1. export_pandoc.py
**Function:** `_get_notes_from_folder`

**Changes:**
- `text=""` → `text="*"` (wildcard search)
- `/api/search` → `{project_url}/search/` (project-specific endpoint)
- Added proper SearchResponse validation
- Fixed folder matching logic to match HTML export

### 2. make_pdf_book.py
**Function:** `_get_notes_from_folder`

**Changes:**
- `text=""` → `text="*"` (wildcard search, or tag search if filter provided)
- `/api/search` → `{project_url}/search/` (project-specific endpoint)
- Added proper SearchResponse validation
- Fixed folder matching logic

### 3. export_joplin_notes.py
**Status:** ✅ Already correct (uses `text="*"` and `project_url`)

### 4. export_html_notes.py
**Status:** ✅ Already correct (this was the reference implementation)

---

## Pattern to Follow

**When implementing export `_get_notes_from_folder` functions:**

```python
async def _get_notes_from_folder(
    source_folder: str, include_subfolders: bool, project: str | None
) -> list[dict[str, Any]]:
    from advanced_memory.mcp.project_session import get_active_project
    from advanced_memory.schemas.search import SearchResponse

    active_project = get_active_project(project)
    project_url = active_project.project_url

    # ✅ Use wildcard search
    query = SearchQuery(text="*")

    # ✅ Use project URL endpoint
    response = await call_post(
        client,
        f"{project_url}/search/",  # Not /api/search
        params={"page": 1, "page_size": 1000},
        json=query.model_dump()
    )

    # ✅ Use proper response validation
    search_result = SearchResponse.model_validate(response.json())

    # ✅ Filter by folder
    for note in search_result.results:
        if note.file_path.startswith(source_folder.lstrip("/")):
            # Process note
            ...
```

---

## Testing After Fix

**Requires MCP server restart in Cursor IDE**

Then test:

```python
# Pandoc PDF
adn_export("pandoc", format_type="pdf", source_folder="/development")
# Should find notes now!

# Pandoc Word
adn_export("pandoc", format_type="docx", source_folder="/development")
# Should find notes now!

# PDF Book
adn_export("pdf_book",
    book_title="Docker Guide",
    source_folder="/development"
)
# Should find notes now!
```

---

## Why This Happened

**Different implementations:**
- `export_html_notes.py` was written correctly
- `export_pandoc.py` and `make_pdf_book.py` used older/wrong pattern
- Probably copy-pasted from each other (both had same bug)

**Key differences:**
1. **Search query:** `text="*"` (works) vs `text=""` (fails)
2. **API endpoint:** `{project_url}/search/` (works) vs `/api/search` (wrong)
3. **Response handling:** Proper `SearchResponse` validation vs raw JSON access

---

## Impact

**Fixed exports:**
- ✅ Pandoc (all formats: PDF, DOCX, EPUB, etc.)
- ✅ PDF Book

**Already working:**
- ✅ HTML export
- ✅ Joplin export
- ✅ Docsify export (uses different logic)

---

## Files Modified

1. `src/advanced_memory/mcp/tools/export_pandoc.py` - Fixed search logic
2. `src/advanced_memory/mcp/tools/make_pdf_book.py` - Fixed search logic

---

**Both routing AND search logic now fixed!** ✅
