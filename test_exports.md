# Export Testing Plan - Post .fn() Fix

**Date:** 2025-12-04
**Status:** Ready to test after MCP server restart

---

## Formats to Test

### ✅ Already Tested (Before Fix)
1. **export_html_notes (standalone)** - ✅ Works perfectly
   - Exported 25 Docker notes
   - Location: `C:\Users\sandr\Desktop\docker-notes-test\`

---

### 🔄 Need to Test (After Fix)

#### 1. HTML via adn_export
```python
adn_export("html", source_folder="/development")
```
**Expected:** Should now work (was broken, now fixed)

---

#### 2. Pandoc PDF
```python
adn_export("pandoc", format_type="pdf", source_folder="/development/docker")
```
**Expected:** Should work (fixed .fn() routing)

---

#### 3. Pandoc DOCX
```python
adn_export("pandoc", format_type="docx", source_folder="/development/docker")
```
**Expected:** Editable Word document

---

#### 4. Docsify Site
```python
adn_export("docsify",
    source_folder="/development/docker",
    site_title="Docker Dev Guide",
    site_description="Stop wasting time on rebuilds"
)
```
**Expected:** Full documentation website

---

#### 5. PDF Book
```python
adn_export("pdf_book",
    book_title="Docker Development Mastery",
    source_folder="/development/docker"
)
```
**Expected:** Professional PDF book with chapters

---

#### 6. Archive
```python
adn_export("archive")
```
**Expected:** Complete backup of entire knowledge base

---

#### 7. Claude Skills
```python
adn_export("claude_skills", source_folder="/skills")
```
**Expected:** Anthropic-compatible skill folders

---

## Test Procedure

**After MCP server restart:**

1. Test HTML export (was broken):
   ```python
   adn_export("html", source_folder="/development/docker")
   ```

2. If HTML works, test Pandoc:
   ```python
   adn_export("pandoc", format_type="pdf", source_folder="/development/docker")
   ```

3. If both work, test Docsify:
   ```python
   adn_export("docsify", source_folder="/development/docker")
   ```

4. Verify all exports in Desktop folder:
   ```
   C:\Users\sandr\Desktop\advanced-memory-exports\
   ├── html\
   ├── pandoc\
   └── docsify\
   ```

---

## Expected Results

### HTML Export
- 5-6 Docker notes exported
- index.html with TOC
- Clean styling
- Mermaid diagrams rendered

### Pandoc PDF
- Professional PDF
- All 5-6 notes
- Table of contents
- Syntax highlighting

### Docsify
- Full website
- Sidebar navigation
- Search functionality
- Markdown source

---

## Success Criteria

✅ **All formats export without errors**
✅ **Output files created in expected locations**
✅ **Content properly formatted**
✅ **No "FunctionTool" errors**

---

**Ready to test after Claude Desktop restart!** 🚀
