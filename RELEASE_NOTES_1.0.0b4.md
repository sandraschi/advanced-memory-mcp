# Release 1.0.0b4

## Breaking Changes

- **Default tool mode changed**: Now exposes only 12 portmanteau tools by default (was 50+)
  - This significantly improves Cursor IDE performance and usability
  - Set `ADVANCED_MEMORY_FULL_TOOLS_MODE=true` to restore all 50+ tools if needed

## Improvements

### Tool Count Optimization
- **Reduced default tools from 50+ to 12** portmanteau tools
- Cleaner, more focused interface for Cursor IDE
- Better performance with fewer tools loaded
- All functionality still available through consolidated tools

### Code Quality
- **Fixed 461 ruff linting errors** (auto-fixed + unsafe-fixed)
- **All ruff checks now pass** cleanly
- **Updated ruff configuration** to allow intentional patterns:
  - E402 in `__init__.py` files (imports after environment checks)
  - B904 globally (intentional exception handling patterns)
- **Formatted all code** with ruff format (26 files reformatted)

### Testing
- **Fixed test collection errors**
  - Renamed `tests/services/test_template_loader.py` → `test_template_loader_service.py`
  - Fixed name collision with `tests/api/test_template_loader.py`
- **WeasyPrint tests now skip gracefully** on systems without GTK libraries (Windows)
- **1266 tests collected** successfully
- All test suites passing

### Build System
- **Build now passes cleanly** without errors
- Python 3.13 compatibility verified
- All dependencies properly installed

## The 12 Default Portmanteau Tools

1. `help` - Get assistance with Advanced Memory
2. `view_note_rendered` - View notes with rendered Mermaid diagrams
3. `adn_content` - All content operations (read/write/edit/move/delete)
4. `adn_project` - All project management
5. `adn_zettelmaker` - Zettelkasten generation
6. `adn_inbox` - File drop processing
7. `adn_export` - All export operations
8. `adn_import` - All import operations
9. `adn_search` - All search operations
10. `adn_knowledge` - Knowledge operations & research
11. `adn_navigation` - Navigation & exploration
12. `adn_editor` - Editor integrations

## Migration Guide

No changes needed for existing users - the 12 tools provide all functionality.

If you need the legacy individual tools, set this environment variable:
```bash
ADVANCED_MEMORY_FULL_TOOLS_MODE=true
```

