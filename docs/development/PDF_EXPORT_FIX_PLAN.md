# PDF Export Fix - Zero External Dependencies

**Problem**: Current `export_pandoc` requires manual installation of:
- ❌ Pandoc (external binary)
- ❌ LaTeX/MiKTeX (2GB+ download!)
- ❌ Hardcoded Windows path: `C:\\Program Files\\Pandoc\\pandoc.exe`

**User expectation**: One `pip install`, everything works.

---

## Current Issues

### Issue 1: Hardcoded Pandoc Path
```python
# Line 278 in export_pandoc.py
cmd = ["C:\\Program Files\\Pandoc\\pandoc.exe", input_path, "-o", output_path]
```
❌ Breaks on non-Windows  
❌ Breaks if Pandoc not installed  
❌ Breaks if Pandoc installed elsewhere

### Issue 2: No Error Handling
```python
# Line 239-246
result = await asyncio.create_subprocess_exec(*cmd, ...)
# If pandoc.exe doesn't exist, process fails silently
```

### Issue 3: LaTeX Requirement
```python
# Line 282-283
if format_type == "pdf":
    cmd.extend(["--pdf-engine", pdf_engine])  # Needs pdflatex/xelatex!
```
❌ 2GB+ LaTeX installation required

---

## Solution: Python-Only PDF Export

### Option 1: `weasyprint` (HTML→PDF) ⭐ RECOMMENDED

**Pros**:
- ✅ Pure Python (no external tools)
- ✅ Excellent rendering (CSS3, web fonts)
- ✅ Handles images, tables, diagrams
- ✅ Professional output

**Cons**:
- C dependencies (but pip handles them)

**Implementation**:
```python
from weasyprint import HTML, CSS

def markdown_to_pdf(md_content: str, output_path: str):
    # Convert markdown → HTML
    html_content = markdown.markdown(md_content, extensions=['extra', 'toc'])
    
    # Add CSS styling
    css = CSS(string='''
        @page { size: A4; margin: 2cm; }
        body { font-family: Arial; line-height: 1.6; }
        h1 { color: #333; border-bottom: 2px solid #ccc; }
    ''')
    
    # Generate PDF
    HTML(string=html_content).write_pdf(output_path, stylesheets=[css])
```

### Option 2: `markdown-pdf` (Simpler)

**Pros**:
- ✅ Dead simple API
- ✅ Pure Python

**Cons**:
- Less mature
- Limited styling

### Option 3: `pypandoc` (Auto-install Pandoc)

**Pros**:
- ✅ Auto-downloads Pandoc binary
- ✅ Full Pandoc features

**Cons**:
- ⚠️ Still downloads 100MB+ binary
- ⚠️ Still needs LaTeX for PDF

---

## Implementation Plan

### Step 1: Add Dependencies

```toml
# pyproject.toml
dependencies = [
    # ... existing ...
    "weasyprint>=62.3",  # PDF generation (HTML→PDF)
    "markdown[extra]>=3.9",  # Already have this
    "pygments>=2.18.0",  # Syntax highlighting in PDFs
]
```

### Step 2: Create Python-Only PDF Export

**New file**: `src/advanced_memory/mcp/tools/export_pdf_native.py`

```python
"""Native Python PDF export (no external tools required)."""

from pathlib import Path
from markdown import markdown
from weasyprint import HTML, CSS
from pygments.formatters import HtmlFormatter

async def export_pdf_native(
    export_path: str,
    source_folder: str = "/",
    include_subfolders: bool = True,
    css_theme: str = "default",
    project: str | None = None,
) -> str:
    """
    Export notes to PDF using pure Python (no Pandoc/LaTeX needed).
    
    Features:
    - Zero external dependencies
    - Professional styling
    - Syntax highlighting
    - Mermaid diagrams (as images)
    - Tables, lists, images
    """
    export_dir = Path(export_path)
    export_dir.mkdir(parents=True, exist_ok=True)
    
    # Get notes
    notes = await _get_notes_from_folder(source_folder, include_subfolders, project)
    
    exported = []
    errors = []
    
    for note in notes:
        try:
            # Convert markdown → HTML
            html = markdown(
                note["content"],
                extensions=['extra', 'codehilite', 'toc', 'tables', 'fenced_code']
            )
            
            # Add professional CSS
            css = _get_pdf_stylesheet(css_theme)
            
            # Generate PDF
            output_file = export_dir / f"{_sanitize(note['title'])}.pdf"
            HTML(string=_wrap_html(html, note['title'])).write_pdf(
                output_file,
                stylesheets=[CSS(string=css)]
            )
            
            exported.append(str(output_file))
            
        except Exception as e:
            errors.append(f"{note['title']}: {e}")
    
    return _generate_summary(exported, errors)


def _wrap_html(content: str, title: str) -> str:
    """Wrap content in proper HTML document."""
    return f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>{title}</title>
</head>
<body>
    <h1 class="document-title">{title}</h1>
    {content}
</body>
</html>"""


def _get_pdf_stylesheet(theme: str = "default") -> str:
    """Professional PDF styling."""
    return """
    @page {
        size: A4;
        margin: 2.5cm 2cm;
        @top-center {
            content: counter(page);
            font-size: 10pt;
            color: #666;
        }
    }
    
    body {
        font-family: 'Segoe UI', Arial, sans-serif;
        font-size: 11pt;
        line-height: 1.6;
        color: #333;
    }
    
    h1, h2, h3 {
        color: #2c3e50;
        margin-top: 1.5em;
        margin-bottom: 0.5em;
        page-break-after: avoid;
    }
    
    h1 {
        font-size: 24pt;
        border-bottom: 3px solid #3498db;
        padding-bottom: 0.3em;
    }
    
    h2 {
        font-size: 18pt;
        border-bottom: 1px solid #bdc3c7;
        padding-bottom: 0.2em;
    }
    
    code {
        background: #f4f4f4;
        padding: 2px 6px;
        border-radius: 3px;
        font-family: 'Consolas', 'Monaco', monospace;
        font-size: 10pt;
    }
    
    pre {
        background: #2c3e50;
        color: #ecf0f1;
        padding: 15px;
        border-radius: 5px;
        overflow-x: auto;
        page-break-inside: avoid;
    }
    
    pre code {
        background: transparent;
        color: inherit;
    }
    
    table {
        width: 100%;
        border-collapse: collapse;
        margin: 1em 0;
        page-break-inside: avoid;
    }
    
    table th {
        background: #3498db;
        color: white;
        padding: 10px;
        text-align: left;
    }
    
    table td {
        border: 1px solid #bdc3c7;
        padding: 8px;
    }
    
    blockquote {
        border-left: 4px solid #3498db;
        margin: 1em 0;
        padding-left: 1em;
        color: #555;
        font-style: italic;
    }
    
    img {
        max-width: 100%;
        height: auto;
        display: block;
        margin: 1em auto;
    }
    
    a {
        color: #3498db;
        text-decoration: none;
    }
    
    .document-title {
        text-align: center;
        margin-bottom: 2em;
        page-break-after: avoid;
    }
    """
```

### Step 3: Update `adn_export` Portmanteau

```python
# In adn_export.py, add new operation

elif operation == "pdf":
    # Native Python PDF (no external tools)
    from advanced_memory.mcp.tools.export_pdf_native import export_pdf_native
    return await export_pdf_native(
        export_path,
        source_folder,
        include_subfolders,
        project=project
    )
```

### Step 4: Keep Pandoc as Optional

```python
elif operation == "pandoc":
    # Advanced users who have Pandoc installed
    try:
        import shutil
        if not shutil.which("pandoc"):
            return """# Pandoc Not Found

Native PDF export is available via:
    adn_export("pdf", export_path="output/")

For advanced Pandoc features, install:
    https://pandoc.org/installing.html

Or use Python-only export (works now):
    - PDF: adn_export("pdf", ...)
    - HTML: adn_export("html", ...)
    - DOCX: Coming soon with python-docx
"""
        
        # Proceed with pandoc if installed
        return await export_pandoc.fn(...)
        
    except Exception as e:
        return f"Pandoc export failed: {e}\n\nTry native PDF: adn_export('pdf', ...)"
```

---

## Benefits

### ✅ Zero External Dependencies
- Pure Python installation
- Works immediately after `pip install`
- No manual steps required

### ✅ Cross-Platform
- Windows, Mac, Linux
- No path issues
- Consistent behavior

### ✅ Professional Output
- Beautiful PDFs
- Syntax highlighting
- Tables, images, diagrams
- Custom themes

### ✅ Optional Pandoc
- Advanced users can still use it
- Clear error messages if not found
- Graceful fallback

---

## Testing Plan

1. **Clean install test**:
   ```bash
   pip install advanced-memory
   # Should work without any additional setup
   ```

2. **PDF export test**:
   ```python
   adn_export("pdf", export_path="test.pdf", source_folder="/")
   ```

3. **Quality test**:
   - Code blocks render correctly
   - Tables format properly
   - Images embed
   - Professional appearance

4. **Error handling test**:
   - Missing notes
   - Invalid paths
   - Large files

---

## Migration

### For Existing Users

**No breaking changes!**

- `export_pandoc(...)` still works if Pandoc installed
- New `adn_export("pdf", ...)` uses Python-only method
- Users can choose which to use

### Documentation Updates

1. Update `docs/TOOLS_REFERENCE.md`:
   - Native PDF export (recommended)
   - Pandoc export (optional, advanced)

2. Update `docs/user-guide/import-export.md`:
   - Remove "Prerequisites: Pandoc, LaTeX"
   - Add "Works out of the box!"

3. Update `README.md`:
   - Emphasize zero-dependency export

---

## Implementation Timeline

- **Step 1**: Add `weasyprint` dependency (5 min)
- **Step 2**: Create `export_pdf_native.py` (1 hour)
- **Step 3**: Update `adn_export` (15 min)
- **Step 4**: Fix Pandoc error handling (15 min)
- **Step 5**: Test + documentation (30 min)

**Total**: ~2 hours for complete solution

---

## Alternatives Considered

### ❌ Bundle Pandoc Binary
- **Why not**: 100MB+ per platform
- **Why not**: Complex build process
- **Why not**: Maintenance burden

### ❌ Require Manual Installation
- **Why not**: Bad UX
- **Why not**: Users expect pip install to work
- **Why not**: "What's LaTeX?"

### ✅ Python-Only Solution (Chosen)
- **Why yes**: Zero dependencies
- **Why yes**: Works immediately
- **Why yes**: Cross-platform
- **Why yes**: Professional output

---

## Implement Now?

Want me to implement this Python-only PDF export solution?

**Changes**:
1. Add `weasyprint` to `pyproject.toml`
2. Create `export_pdf_native.py`
3. Update `adn_export.py`
4. Fix `export_pandoc.py` error handling
5. Update documentation

**Time**: 2 hours

**Result**: PDF export that "just works" out of the box!



























