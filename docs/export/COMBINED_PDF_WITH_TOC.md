# Combined PDF Export with Clickable TOC

**Date**: 2025-12-02  
**Status**: ✅ Implementation Complete

---

## ✅ New Feature: Combined PDF with TOC

You can now search for notes and export them into **ONE big PDF** with a **clickable table of contents**!

### Example Usage

```python
# Search for "docker" notes and combine into one PDF with TOC
adn_export(
    operation="pdf",
    search_query="docker",
    combine_into_one=True,
    make_toc=True,  # Add clickable TOC page
    book_title="Docker Notes Collection",
    export_path="d:/Dev/repos/docker-notes.pdf"
)

# Or combine without TOC page (bookmarks still work for navigation)
adn_export(
    operation="pdf",
    search_query="docker",
    combine_into_one=True,
    make_toc=False,  # No TOC page, but bookmarks still available
    book_title="Docker Notes Collection",
    export_path="d:/Dev/repos/docker-notes-no-toc.pdf"
)
```

This will:
1. ✅ Search for all notes about "docker"
2. ✅ Combine them into a single PDF
3. ✅ Add a clickable table of contents
4. ✅ Add bookmarks for navigation

---

## 📋 Parameters

- **`search_query`**: Search query to find notes (e.g., "docker", "python", "mcp")
- **`combine_into_one`**: Set to `True` to create single PDF
- **`make_toc`**: Set to `True` to add clickable table of contents page (default: True)
- **`book_title`**: Title for the combined PDF
- **`export_path`**: File path (not directory) for the combined PDF

---

## 🎯 Features

- ✅ Search by keyword/query
- ✅ Multiple notes in one PDF
- ✅ Clickable table of contents
- ✅ Bookmarks for navigation
- ✅ Professional formatting
- ✅ Pure Python (fpdf2, no LaTeX!)

---

## 📝 Notes

The combined PDF uses fpdf2's outline/bookmark functionality for:
- Table of contents (clickable)
- Bookmark navigation (PDF viewer sidebar)
- Section headers (each note is a section)

**Ready to use!**
