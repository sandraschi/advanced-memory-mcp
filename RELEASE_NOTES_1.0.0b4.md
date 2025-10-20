# Release 1.0.0b4

## Breaking Changes

- **Default tool mode changed**: Now exposes only 12 portmanteau tools by default (was 50+)
  - This significantly improves Cursor IDE performance and usability
  - Set `ADVANCED_MEMORY_FULL_TOOLS_MODE=true` to restore all 50+ tools if needed
- **Removed WeasyPrint dependency**: PDF export now uses Pandoc exclusively
  - WeasyPrint required GTK libraries on Windows (installation nightmare)
  - Pandoc auto-installs on first use and works cross-platform

## Improvements

### Tool Count Optimization
- **Reduced default tools from 50+ to 12** portmanteau tools
- Cleaner, more focused interface for Cursor IDE
- Better performance with fewer tools loaded
- All functionality still available through consolidated tools

### PDF Export Simplified
- **Removed redundant `export_pdf_native`** (WeasyPrint-based)
- **PDF export works** via `adn_export("pandoc", format_type="pdf")`
- **Pandoc auto-installs** on first use (pypandoc)
- **Cross-platform** - Works on Windows, Mac, Linux
- **No manual setup required** - Just works!

### Code Quality
- **Fixed 461 ruff linting errors** (auto-fixed + unsafe-fixed)
- **All ruff checks now pass** cleanly
- **Updated ruff configuration** to allow intentional patterns
- **Formatted all code** with ruff format

### Testing
- **Fixed test collection errors**
  - Renamed conflicting test file
  - Removed WeasyPrint-dependent tests
- **1259 tests collected** successfully
- All test suites passing

### Build System
- **Build passes cleanly** without errors
- Python 3.13 compatibility verified
- **Removed problematic WeasyPrint dependency**
- All dependencies install reliably

## The 12 Default Portmanteau Tools

1. `help` - Get assistance with Advanced Memory
2. `view_note_rendered` - View notes with rendered Mermaid diagrams
3. `adn_content` - All content operations (read/write/edit/move/delete)
4. `adn_project` - All project management
5. `adn_zettelmaker` - Zettelkasten generation
6. `adn_inbox` - File drop processing
7. `adn_export` - All export operations (Pandoc, HTML, Docsify, etc.)
8. `adn_import` - All import operations
9. `adn_search` - All search operations
10. `adn_knowledge` - Knowledge operations & research
11. `adn_navigation` - Navigation & exploration
12. `adn_editor` - Editor integrations

## PDF Export Guide

**Use Pandoc for PDF export** (recommended):
```python
# Export to PDF
adn_export("pandoc", format_type="pdf")

# Create professional PDF book
adn_export("pdf_book", book_title="My Research")
```

Pandoc auto-installs on first use and works on all platforms!

## Migration Guide

No changes needed for existing users - the 12 tools provide all functionality.

**If you were using `export_pdf_native`:**
- Use `adn_export("pandoc", format_type="pdf")` instead
- Better quality, auto-installs, works everywhere!

**If you need legacy individual tools:**
```bash
ADVANCED_MEMORY_FULL_TOOLS_MODE=true
```
