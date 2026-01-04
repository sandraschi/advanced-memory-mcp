# Modern PDF Generation Options - Dec 2025

**Problem**: Current setup requires LaTeX (2GB+) or hangs with weasyprint
**Goal**: Lightweight, pure Python PDF generation from Markdown

---

## Recommended Solutions (Pure Python, No LaTeX!)

### 1. **fpdf2** ⭐ BEST OPTION
- **Pure Python** - minimal dependencies (Pillow, defusedxml, fontTools)
- **GitHub**: https://github.com/py-pdf/fpdf2
- **No system dependencies** - works immediately after pip install
- **Basic markdown support**: `**bold**`, `__italic__`, `--underline--`
- **Perfect for**: Simple documents, reports, notes

```python
from fpdf import FPDF

pdf = FPDF()
pdf.add_page()
pdf.set_font("Times", size=12)
pdf.cell(text="**Bold** __Italic__", markdown=True)
pdf.output("output.pdf")
```

**Installation**: `pip install fpdf2`

---

### 2. **pypdf** (Pure Python)
- **Pure Python** - no external dependencies
- **GitHub**: https://github.com/py-pdf/pypdf (1.5k stars)
- **Good for**: PDF manipulation (split, merge, transform)
- **Note**: More for editing existing PDFs, less for creation from scratch

**Installation**: `pip install pypdf`

---

### 3. **borb** (Modern API)
- **Clean JSON-like API**
- **GitHub**: https://github.com/borb-pdf/borb (153 stars)
- **Supports**: Tables, images, annotations, complex layouts
- **Modern design** - easy to use

```python
from borb.pdf import Document, Page, Paragraph
from borb.pdf.pdf import PDF

doc = Document()
page = Page()
doc.add_page(page)
page.add(Paragraph("Hello World"))
with open("output.pdf", "wb") as pdf_file:
    PDF.dumps(pdf_file, doc)
```

**Installation**: `pip install borb`

---

### 4. **PyMuPDF (fitz)** - High Performance
- **GitHub**: https://github.com/pymupdf (8.6k stars - VERY popular!)
- **High performance** - fastest PDF library
- **Note**: May have system dependencies (C libraries)
- **Best for**: When performance matters

**Installation**: `pip install pymupdf`

---

## Markdown → PDF Conversion Options

### Option A: Markdown → HTML → PDF (Current)
- Use `markdown` library to convert MD → HTML
- Then use PDF library to render HTML
- **fpdf2** can render basic HTML

### Option B: Markdown → Direct PDF
- Parse markdown ourselves
- Use **fpdf2** or **borb** to render directly
- More control, less dependencies

### Option C: Use Existing MCP Server
- **markdown2pdf-mcp** (TypeScript/Puppeteer)
- But requires Node.js - not pure Python

---

## Recommended Implementation Strategy

### Phase 1: Quick Win - fpdf2
```python
# Simple markdown → PDF with fpdf2
from fpdf import FPDF
from markdown import markdown

def markdown_to_pdf(md_content: str, output_path: str):
    # Convert markdown → HTML (lightweight)
    html = markdown(md_content, extensions=['extra', 'codehilite'])

    # Use fpdf2 to render (pure Python, no LaTeX!)
    pdf = FPDF()
    pdf.add_page()
    # ... render HTML content ...
    pdf.output(output_path)
```

**Benefits**:
- ✅ Pure Python
- ✅ Minimal dependencies
- ✅ Works immediately
- ✅ No 2GB LaTeX needed!

---

### Phase 2: Enhanced - borb (if needed)
- More advanced styling
- Better typography
- Complex layouts
- Tables, images, annotations

---

## Comparison Table

| Library | Dependencies | Markdown Support | Performance | Stars | Recommendation |
|---------|-------------|------------------|-------------|-------|----------------|
| **fpdf2** | Minimal (Pillow) | Basic | Fast | - | ⭐ **START HERE** |
| **pypdf** | None | None | Fast | 1.5k | For editing only |
| **borb** | Some | None | Good | 153 | Modern API |
| **PyMuPDF** | C libs | None | ⚡ Very Fast | 8.6k | If performance critical |
| **weasyprint** | Many | Full | Slow/hangs | - | ❌ Current problem |
| **LaTeX** | 2GB+ | Full | Slow | - | ❌ Absolutely not |

---

## Action Plan

1. **Replace weasyprint** with **fpdf2** for PDF generation
2. **Keep markdown parsing** (already lightweight)
3. **Test with single note** export
4. **No LaTeX dependencies** - ever!

---

## Code Example: fpdf2 Implementation

```python
from fpdf import FPDF
from markdown import markdown
from pathlib import Path

class MarkdownPDF(FPDF):
    def __init__(self):
        super().__init__()
        self.set_auto_page_break(auto=True, margin=15)

    def render_markdown(self, md_content: str):
        """Convert markdown content to PDF."""
        # Parse markdown
        html = markdown(md_content, extensions=['extra', 'codehilite'])

        # Simple HTML parsing for fpdf2
        # (or use fpdf2's built-in markdown support)

        lines = md_content.split('\n')
        for line in lines:
            if line.startswith('# '):
                self.set_font('Arial', 'B', 24)
                self.cell(0, 10, line[2:], ln=1)
            elif line.startswith('## '):
                self.set_font('Arial', 'B', 18)
                self.cell(0, 8, line[3:], ln=1)
            elif line.strip():
                self.set_font('Arial', '', 12)
                self.cell(0, 6, line, ln=1)

# Usage
pdf = MarkdownPDF()
pdf.add_page()
pdf.render_markdown("# Hello\n\nThis is **bold** text.")
pdf.output("output.pdf")
```

---

## MCP Server Option (Alternative)

If we want to use existing MCP server:
- **markdown2pdf-mcp**: https://github.com/2b3pro/markdown2pdf-mcp
- Uses Puppeteer (Chrome headless)
- Requires Node.js
- But works out of the box

**Not recommended** - adds Node.js dependency. Better to use pure Python.

---

## Conclusion

**Use fpdf2** - pure Python, minimal dependencies, works immediately, no 2GB LaTeX bullshit!
