# PDF Export Test Instructions

**Date**: 2025-12-02  
**Status**: ✅ Code Complete - Needs fpdf2 installation

---

## Installation Required

The server needs fpdf2 installed:

```powershell
cd d:\Dev\repos\advanced-memory-mcp
pip install fpdf2
```

Or if using a virtual environment:

```powershell
# Activate venv first, then:
pip install fpdf2
```

---

## Test Single Note Export

Once fpdf2 is installed and server restarted:

```python
# Export single test note
adn_export(
    operation="pdf",
    export_path="d:/Dev/repos/test-pdf-export",
    source_folder="tests",
    include_subfolders=False
)
```

This should export "Pandoc PDF Export Test" note to PDF using fpdf2.

---

## Expected Result

- ✅ PDF file created: `Pandoc_PDF_Export_Test.pdf`
- ✅ No LaTeX dependencies needed
- ✅ No weasyprint needed
- ✅ Pure Python fpdf2 generation
- ✅ Fast export (no hanging)

---

## Files Changed

1. ✅ `mcpb/requirements.txt` - fpdf2 added
2. ✅ `pyproject.toml` - fpdf2 added
3. ✅ `export_pdf_native.py` - NEW: fpdf2 PDF export
4. ✅ `adn_export.py` - PDF operation added
5. ✅ `export_pandoc.py` - PDF format blocked

---

## Next Steps

1. Install fpdf2: `pip install fpdf2`
2. Restart MCP server
3. Run test export
4. Verify PDF is created
