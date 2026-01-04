# PDF Export Test Guide - LaTeX Dependencies

**Date**: 2025-12-02
**Purpose**: Test Advanced Memory PDF export with Pandoc + LaTeX/MiKTeX

---

## Dependencies Required

### 1. Pandoc
- **Auto-installs**: Via `pypandoc` package (first-time download ~100MB)
- **Check**: `pandoc --version`
- **Manual install**: https://pandoc.org/installing.html

### 2. LaTeX Engine (for pdflatex/xelatex/lualatex)
- **Option A**: MiKTeX (Windows) - https://miktex.org/download
- **Option B**: TeX Live - https://www.tug.org/texlive/
- **Check**: `pdflatex --version`
- **Size**: ~2GB download

### 3. Python Packages (already in requirements.txt)
- `pypandoc>=1.13` - Auto-installs Pandoc
- `weasyprint>=62.3` - Pure Python PDF (no LaTeX needed)

---

## Testing PDF Export

### Test 1: Default (weasyprint - Pure Python)
```python
from advanced_memory.mcp.tools.export_pandoc import export_pandoc

# Should work immediately (no LaTeX needed)
await export_pandoc(
    export_path="d:/Dev/repos/test-pdf-export",
    format_type="pdf",
    source_folder="tests",
    pdf_engine="weasyprint"  # Default
)
```

### Test 2: With LaTeX (pdflatex)
```python
await export_pandoc(
    export_path="d:/Dev/repos/test-pdf-export",
    format_type="pdf",
    source_folder="tests",
    pdf_engine="pdflatex"  # Requires MiKTeX/TeX Live
)
```

---

## Direct Command Line Test

### Test Pandoc directly:
```powershell
cd d:\Dev\repos\test-pdf-export
pandoc test.md -o test.pdf --pdf-engine=pdflatex
```

### Test with weasyprint:
```powershell
pandoc test.md -o test.pdf --pdf-engine=weasyprint
```

---

## Expected Behavior

1. **First export**:
   - Auto-downloads Pandoc (~30 seconds)
   - Proceeds with export

2. **With pdflatex engine**:
   - Requires LaTeX installation
   - Slower but better typography
   - Better math rendering

3. **With weasyprint engine**:
   - Works immediately (pure Python)
   - Faster export
   - Good enough for most uses

---

## Troubleshooting

### Timeout Issues
- Export times out if LaTeX compilation hangs
- Try `weasyprint` engine instead
- Check if LaTeX is properly installed

### Missing Dependencies
- Check `pypandoc` is installed: `pip show pypandoc`
- Check `weasyprint` is installed: `pip show weasyprint`
- Check Pandoc: `pandoc --version`
- Check LaTeX: `pdflatex --version`

### Auto-install Hanging
- Pandoc auto-install may take 30-60 seconds first time
- Network issues can cause timeouts
- Try manual Pandoc installation if auto-install fails

---

## Quick Test Script

Run this to check all dependencies:

```python
import shutil

# Check Pandoc
if shutil.which("pandoc"):
    print("✅ Pandoc found")
else:
    print("❌ Pandoc not found")

# Check LaTeX engines
for engine in ["pdflatex", "xelatex", "lualatex"]:
    if shutil.which(engine):
        print(f"✅ {engine} found")
    else:
        print(f"❌ {engine} not found")
```

---

## Recommendations

1. **For quick testing**: Use `weasyprint` (default) - no LaTeX needed
2. **For production**: Install MiKTeX if you need advanced typography
3. **For math-heavy docs**: LaTeX engines provide better math rendering
