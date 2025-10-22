# Pandoc Auto-Installation - How It Works

**TL;DR**: Pandoc automatically downloads on first export. No manual setup required!

---

## What Happens on First Use

### Step 1: You Request an Export

```python
# First time using Pandoc export
adn_export("pandoc", export_path="document.pdf", format_type="pdf")
```

### Step 2: System Checks for Pandoc

```
Checking for Pandoc... Not found!
```

### Step 3: Auto-Download Begins

```
⏳ Downloading Pandoc binary (~100MB)...
⏳ This is a one-time download...
⏳ Installing to ~/.advanced-memory/bin/...
✅ Pandoc installed successfully!
```

### Step 4: Export Proceeds

```
⏳ Exporting document.pdf...
✅ Export complete!
```

**Total time**: ~30-60 seconds (depending on internet speed)

---

## Subsequent Uses

**Every export after first time**:

```python
adn_export("pandoc", export_path="document2.pdf", format_type="pdf")
# ✅ Export complete! (instant, uses cached Pandoc)
```

**No delay** - Pandoc is already installed!

---

## Installation Details

### Where Pandoc Gets Installed

**Location**: `~/.advanced-memory/bin/`

**Platform-specific**:
- Windows: `C:\Users\YourName\.advanced-memory\bin\`
- Mac: `/Users/YourName/.advanced-memory/bin/`
- Linux: `/home/yourname/.advanced-memory/bin/`

**Binary details**:
- Size: ~100MB compressed, ~300MB installed
- Version: Latest stable (auto-selected by pypandoc)
- Permissions: User-only (no admin needed)

### What Gets Downloaded

**Pandoc includes**:
- Core pandoc executable
- Filters and extensions
- Template system
- Format converters

**Does NOT include**:
- LaTeX (needed separately for PDF - see below)
- Custom templates (you can add these)

---

## Supported Export Formats

### Works Immediately (No LaTeX)

```python
# Word documents
adn_export("pandoc", export_path="doc.docx", format_type="docx")

# HTML
adn_export("pandoc", export_path="page.html", format_type="html")

# OpenDocument
adn_export("pandoc", export_path="doc.odt", format_type="odt")

# EPUB
adn_export("pandoc", export_path="book.epub", format_type="epub")

# Markdown (different flavor)
adn_export("pandoc", export_path="doc.md", format_type="markdown")

# Plain text
adn_export("pandoc", export_path="doc.txt", format_type="txt")

# And 40+ more formats!
```

**These all work immediately** after Pandoc auto-installs!

### Requires LaTeX

```python
# PDF via LaTeX
adn_export("pandoc", export_path="doc.pdf", format_type="pdf", pdf_engine="pdflatex")

# LaTeX source
adn_export("pandoc", export_path="doc.tex", format_type="tex")
```

**LaTeX engines**:
- `pdflatex` (default, most compatible)
- `xelatex` (Unicode support)
- `lualatex` (modern, flexible)

**Install LaTeX**:
- Windows: [MiKTeX](https://miktex.org/) (~2GB)
- Mac: [MacTeX](https://www.tug.org/mactex/) or [TinyTeX](https://yihui.org/tinytex/)
- Linux: `sudo apt install texlive-latex-base texlive-latex-extra`

**Alternative**: Coming in v1.1 - pure-Python PDF (no LaTeX needed)!

---

## Troubleshooting

### Issue: "Failed to install Pandoc"

**Possible causes**:
1. **No internet connection**
   - Solution: Connect to internet, try again
   
2. **Firewall/proxy blocking**
   - Solution: Configure proxy or download manually
   
3. **Disk full**
   - Solution: Free up ~500MB space

**Manual installation fallback**:
1. Download from: https://pandoc.org/installing.html
2. Install normally
3. Pandoc will be found in system PATH
4. Auto-install skipped

### Issue: "PDF generation failed"

**If you see LaTeX errors**:
```
! LaTeX Error: File 'xyz.sty' not found
```

**Solution**: Install LaTeX distribution
- Windows: [MiKTeX](https://miktex.org/)
- Mac: [TinyTeX](https://yihui.org/tinytex/)
- Linux: `texlive-latex-extra`

**Alternative**: Use DOCX export instead:
```python
adn_export("pandoc", export_path="doc.docx", format_type="docx")
# Then convert to PDF in Word/LibreOffice
```

### Issue: Download is slow

**Why**: Pandoc binary is ~100MB

**Solutions**:
1. **Wait it out** (one-time only)
2. **Use other formats** meanwhile (HTML, DOCX work without waiting)
3. **Manual install** (faster if you have good connection to pandoc.org)

---

## Behind the Scenes

### How Auto-Install Works

**Technology**: `pypandoc` Python package

**Process**:
1. Check if `pandoc` command exists in PATH
2. If not found, download from GitHub releases
3. Extract to `~/.advanced-memory/bin/`
4. Set executable permissions
5. Cache path for future use

**Code** (`utils/pandoc_installer.py`):
```python
import pypandoc

# Check if exists
try:
    pandoc_path = pypandoc.get_pandoc_path()
except OSError:
    # Download if not found
    target = Path.home() / ".advanced-memory" / "bin"
    pypandoc.download_pandoc(targetfolder=str(target))
    pandoc_path = pypandoc.get_pandoc_path()
```

### Security

**Download source**: Official Pandoc GitHub releases  
**Verification**: pypandoc handles integrity checks  
**Installation**: User directory only (no admin needed)

---

## Comparison

| Aspect | Before Fix | After Fix |
|--------|------------|-----------|
| **Setup** | Manual download + install | Auto-install |
| **Platforms** | Windows only (hardcoded path) | All platforms |
| **User steps** | 5+ steps | 0 steps |
| **Error messages** | Silent failure | Clear instructions |
| **First export** | Broken | ~30s download |
| **Subsequent** | Works (if installed manually) | Instant |
| **Path handling** | Hardcoded | Dynamic detection |

---

## FAQ

### Q: Can I use my existing Pandoc installation?

**A: Yes!** If Pandoc is in your system PATH, Advanced Memory will use it automatically. No download needed.

### Q: Can I update Pandoc later?

**A: Yes!** Either:
1. Manual update: Download new version from pandoc.org
2. Delete `~/.advanced-memory/bin/pandoc*` and next export will download latest

### Q: Does this work offline after first download?

**A: Yes!** Pandoc is cached locally. Only first download needs internet.

### Q: What about disk space?

**A:** Pandoc uses ~300MB installed. Negligible for modern systems.

### Q: Can I skip the download?

**A: No.** Pandoc is required for export features. But:
- One-time download
- Used for many export formats
- Worth the wait!

---

## Summary

**User experience before**:
1. Run export → error
2. Google "why doesn't it work"
3. Find Pandoc website
4. Download installer
5. Run installer
6. Configure PATH
7. Restart everything
8. Try export again → works

**User experience now**:
1. Run export → **it works!** (after ~30s first-time download)

🎉 **Zero-config exports - just as you expected!**





