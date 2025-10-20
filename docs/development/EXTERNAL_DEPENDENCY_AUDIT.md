# External Dependency Audit - Complete Analysis

**Goal**: Identify and eliminate ALL external tool requirements.

---

## External Dependencies Found

### 1. ✅ Pandoc (FIXED)
**Used for**: Multi-format export (PDF, DOCX, HTML, EPUB, etc.)  
**Status**: ✅ Auto-installs via `pypandoc`  
**Size**: ~100MB  
**Solution**: Auto-download on first use

### 2. ❌ LaTeX (PROBLEM)
**Used for**: PDF generation via Pandoc  
**Size**: 2GB+ (MiKTeX/TinyTeX)  
**Status**: ❌ Required manual install  
**Problem**: USERS DON'T KNOW WHAT LATEX IS!

**Solution**: Use `weasyprint` (pure Python, already added!)

### 3. ✅ Obsidian/Notion/Joplin/Evernote (NOT OUR PROBLEM)
**Used for**: Importing FROM those apps  
**Status**: ✅ Optional - user already has them if importing  
**Our job**: Just parse their export files  
**No action needed**: These are SOURCE apps, not dependencies

### 4. ✅ Typora/Notepad++ (OPTIONAL)
**Used for**: External editor integration  
**Status**: ✅ Optional features  
**Our job**: Provide integration IF user has them  
**No action needed**: Clearly documented as optional

---

## Critical Issue: LaTeX for PDF

### Current State

**Problem flow**:
```
User: "Export to PDF"
System: Uses Pandoc
Pandoc: Calls pdflatex
pdflatex: NOT FOUND
Export: FAILS
User: "What's LaTeX? Why do I need surgical gloves??" 😡
```

### Solution: Pure-Python PDF

**Use `weasyprint`** (already in dependencies!):

```python
from markdown import markdown
from weasyprint import HTML, CSS

# Convert markdown → HTML
html = markdown(content, extensions=['extra', 'codehilite', 'toc'])

# Generate PDF (NO LaTeX needed!)
HTML(string=html).write_pdf('output.pdf', stylesheets=[CSS(string=css)])
```

**Benefits**:
- ✅ Pure Python (no 2GB LaTeX)
- ✅ Works immediately after `pip install`
- ✅ Professional output
- ✅ Syntax highlighting
- ✅ Tables, images, formatting
- ✅ Cross-platform

---

## Implementation Plan

### Step 1: Create Native PDF Export

**File**: `src/advanced_memory/mcp/tools/export_pdf_native.py`

```python
"""Pure-Python PDF export using weasyprint (no LaTeX required)."""

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
    
    Works immediately after pip install - no external tools!
    """
    # Get notes
    notes = await _get_notes(source_folder, include_subfolders, project)
    
    exported = []
    for note in notes:
        # Markdown → HTML
        html = markdown(
            note["content"],
            extensions=['extra', 'codehilite', 'toc', 'tables', 'fenced_code']
        )
        
        # HTML → PDF
        output = Path(export_path) / f"{_sanitize(note['title'])}.pdf"
        HTML(string=_wrap_html(html, note['title'])).write_pdf(
            output,
            stylesheets=[CSS(string=_get_stylesheet())]
        )
        
        exported.append(str(output))
    
    return f"✅ Exported {len(exported)} PDFs (pure Python, no LaTeX!)"
```

### Step 2: Update `adn_export` Portmanteau

```python
# In adn_export.py

elif operation == "pdf":
    # Pure-Python PDF (NO LaTeX!)
    from advanced_memory.mcp.tools.export_pdf_native import export_pdf_native
    return await export_pdf_native(
        export_path,
        source_folder,
        include_subfolders,
        project=project
    )

elif operation == "pandoc":
    # Advanced Pandoc export (requires LaTeX for PDF)
    # Auto-installs Pandoc, but PDF needs LaTeX
    ...
```

### Step 3: Make `pdf` the Default

**User wants PDF**:
```python
# Use pure-Python (works immediately!)
adn_export("pdf", export_path="output/")
```

**Advanced user wants Pandoc**:
```python
# Uses Pandoc (for special formats, templates)
adn_export("pandoc", export_path="output/", format_type="pdf")
```

---

## Dependency Matrix

| Tool | Purpose | Status | Solution |
|------|---------|--------|----------|
| **Pandoc** | Multi-format export | ✅ Auto-installs | pypandoc |
| **LaTeX** | PDF via Pandoc | ❌ Manual 2GB | ✅ Use weasyprint |
| **weasyprint** | PDF (Python) | ✅ In dependencies | Already added! |
| **Obsidian** | Import source | ✅ Optional | User's app |
| **Notion** | Import source | ✅ Optional | User's app |
| **Joplin** | Import source | ✅ Optional | User's app |
| **Evernote** | Import source | ✅ Optional | User's app |
| **Typora** | Editor integration | ✅ Optional | User's app |
| **Notepad++** | Editor integration | ✅ Optional | User's app |

---

## Result After Implementation

### ✅ Zero External Tools Required

**After `pip install advanced-memory`**:

| Feature | Works? | External Tool? |
|---------|--------|----------------|
| Content management | ✅ YES | None |
| Project management | ✅ YES | None |
| Search | ✅ YES | None |
| Import Obsidian | ✅ YES | None (just reads files) |
| Import Notion | ✅ YES | None (just reads files) |
| Export HTML | ✅ YES | None |
| Export Docsify | ✅ YES | None |
| **Export PDF** | ✅ **YES** | **None (weasyprint!)** |
| Export DOCX | ✅ YES | None (Pandoc auto-installs) |
| Export EPUB | ✅ YES | None (Pandoc auto-installs) |
| Skills export | ✅ YES | None |
| Mermaid rendering | ✅ YES | None (CDN) |

**100% of advertised features work out of the box!**

---

## Implementation Now

**Files to create**:
1. `src/advanced_memory/mcp/tools/export_pdf_native.py` - Pure-Python PDF
2. `src/advanced_memory/utils/pdf_styles.py` - Professional CSS themes
3. `tests/mcp/test_export_pdf_native.py` - Tests

**Files to modify**:
1. `src/advanced_memory/mcp/tools/adn_export.py` - Add "pdf" operation
2. `docs/TOOLS_REFERENCE.md` - Document native PDF
3. `README.md` - Update "LaTeX needed" → "Works now!"

**Time**: 1 hour

**Result**: 
- ✅ PDF export works immediately
- ✅ No LaTeX needed
- ✅ No "what's LaTeX?" confusion
- ✅ Professional output

---

## Implement Now?

**Say "implement" and I'll**:
1. Create native PDF export
2. Add to adn_export portmanteau
3. Update all documentation
4. Test it works

**Result**: Users can export PDFs immediately after `pip install`!


