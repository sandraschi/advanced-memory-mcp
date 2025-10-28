# Release Notes - v1.0.0b6

**Release Date**: 2025-10-28  
**Type**: Beta Release  
**Status**: Production-Ready

## 🎯 Highlights

### One-Click Installation
Install Advanced Memory in **5 seconds** with new deeplink system!

```bash
advanced-memory deeplink cursor  # Cursor IDE
advanced-memory deeplink vscode  # VS Code
advanced-memory setup            # Interactive wizard
```

### Multi-Project Support
Search and export across multiple projects with flexible new `projects` parameter:

```python
# Search all projects
search_notes("query", projects="ALL")

# Search specific projects
search_notes("query", projects="work,personal")

# Export all projects
adn_export("pandoc", format_type="pdf", project="ALL")
```

### Starter Knowledge Base
**87+ professional zettelkasten templates** included:
- Developer (30+ templates)
- AI Category (7 templates) 🆕
- DevOps, Data Science, Product, Research, and more!
- 20,000+ lines of curated content
- Ready to use immediately

## ✨ New Features

### 1. Deeplink System
- One-click installation for Cursor and VS Code
- Interactive setup wizard (`advanced-memory setup`)
- Auto-detection of AI client
- Support for all 3 transport types (stdio, HTTP, SSE)

**New Commands**:
```bash
advanced-memory deeplink cursor
advanced-memory deeplink vscode  
advanced-memory deeplink claude-desktop
advanced-memory setup
```

**Documentation**: [DEEPLINK_INSTALLATION.md](docs/user-guide/DEEPLINK_INSTALLATION.md)

### 2. Multi-Project Parameters

**Unified `projects` parameter** across all tools:
- `projects=None` - current project (default)
- `projects="project-name"` - single project
- `projects="proj1,proj2,proj3"` - comma-delimited list
- `projects="ALL"` - all projects
- `projects="ALL_EXCEPT:archived"` - exclusion list

**Supported in**:
- `search_notes()` - Multi-project search with result grouping
- `adn_export()` - Export all projects to separate folders
- `adn_content()` - Project context in responses
- `adn_navigation()` - Consistent project handling
- `adn_import()` - Project-aware imports

**Documentation**: [TOOL_PARAMETER_IMPROVEMENTS.md](docs/TOOL_PARAMETER_IMPROVEMENTS.md)

### 3. Project Context in Responses

All tools now show which project they operated on:

```
# Created note
project: work-project
file_path: notes/example.md
permalink: notes/example
```

### 4. Starter Knowledge Base

**87+ zettelkasten templates** included in distribution:
- Developer: Python, Git, Docker, System Design (30+)
- AI: History, Ethics, Controversies, Business (7) 🆕
- DevOps: Kubernetes, IaC, Monitoring (15+)
- Data Science: ML, MLOps, Python (10+)
- Researcher: Methods, Literature Review (12+)
- Product Manager: Analytics, Strategy (8+)
- Plus: Entrepreneur, Creative, Writer, UX Designer, Knowledge Worker

See `zettelkasten/STARTER_PACK.md` for full guide.

## 🔄 Breaking Changes

### search_notes() Parameter Renamed

**Before**:
```python
search_notes("query", search_all_projects=True)
```

**After**:
```python
search_notes("query", projects="ALL")
```

**Migration**:
- Simple find-replace in custom scripts
- More powerful (supports comma-lists, exclusions, etc.)
- Better UX (explicit vs implicit)

## 🐛 Fixes

### MCPB Package
- Fixed "Basic Memory" → "Advanced Memory" in all templates
- Fixed Handlebars template branding (.hbs files)
- Synced prompt resources
- Fixed ai_assistant_guide references

### Code Quality
- Fixed 40+ ruff whitespace/formatting issues
- Organized imports (ruff I001)
- Removed unused imports
- Fixed trailing whitespace

### Tests
- Fixed deprecated adn_editor tests (properly skipped)
- All 45 tests now passing

## 📚 Documentation Updates

### New Documentation
1. `docs/user-guide/DEEPLINK_INSTALLATION.md` - Complete installation guide
2. `docs/development/Handlebars_Prompt_Templates_Documentation.md` - Technical guide
3. `docs/TOOL_PARAMETER_IMPROVEMENTS.md` - Parameter reference
4. `zettelkasten/STARTER_PACK.md` - Template guide

### Updated Documentation
1. `README.md` - One-click installation section
2. All tool docstrings - FastMCP 2.12 compliant (200+ lines each)
3. `zettelkasten/INDEX.md` - Updated template index

### Total Documentation
- **2,500+ new lines** of user-facing documentation
- All tools have comprehensive examples
- Migration guides included

## 🧪 Testing

**Test Results**:
- ✅ **45/45 tests passing**
- ✅ 20 new deeplink tests
- ✅ 25 portmanteau tool tests
- ✅ 4 deprecated tests properly skipped
- ✅ Zero ruff errors

**Code Quality**:
- Ruff: 0 errors
- FastMCP 2.12: Compliant
- Type hints: Complete
- Async/await: Proper

## 🎁 What's in the Box

### For First-Time Users
- **One-click installation** - No complex setup
- **87+ starter templates** - Immediate value
- **Interactive wizard** - Guided onboarding
- **Triple-interface flexibility** - Local, network, or legacy

### For Developers
- **Multi-project support** - Work with multiple knowledge bases
- **Flexible project parameters** - ALL, comma-lists, exclusions
- **Project context** - Always know which project you're in
- **Production quality** - Zero ruff errors, comprehensive tests

### For Teams
- **Network mode** - Share knowledge via HTTP
- **Multi-project export** - Batch operations
- **Professional templates** - Standard knowledge base
- **Full open source** - Complete transparency

## 🏆 Competitive Advantages

vs Rube MCP:
- ✅ **Triple-interface** (stdio + HTTP + SSE) vs single (HTTP only)
- ✅ **Privacy-first** (local by default) vs cloud-only
- ✅ **Full open source** vs client-only
- ✅ **One-click install** (now matched!)
- ✅ **Knowledge management** vs app integrations (different focus)

## 📦 Installation

### One-Click (Recommended)
```bash
advanced-memory deeplink cursor
```

### Interactive Wizard
```bash
advanced-memory setup
```

### Traditional
```bash
pip install advanced-memory-mcp
```

### Claude Desktop (MCPB)
Download `advanced-memory-mcp.mcpb` from [Releases](https://github.com/sandraschi/advanced-memory-mcp/releases/tag/v1.0.0b6)

## 🔗 Links

- **GitHub**: https://github.com/sandraschi/advanced-memory-mcp
- **Documentation**: https://github.com/sandraschi/advanced-memory-mcp/tree/master/docs
- **Smithery**: https://smithery.ai/server/advanced-memory-mcp
- **Issues**: https://github.com/sandraschi/advanced-memory-mcp/issues

## 🙏 Acknowledgments

- Anthropic for Model Context Protocol
- Composio for Rube inspiration (deeplinks)
- FastMCP framework contributors
- Community feedback and testing

## 📝 Changelog

### Added
- One-click installation via deeplinks (Cursor, VS Code)
- Interactive setup wizard (`advanced-memory setup`)
- Multi-project search (`projects="ALL"`)
- Multi-project export (`projects="ALL"`)
- Project context in all tool responses
- Starter zettelkasten pack (87+ templates)
- Handlebars template documentation

### Changed
- **BREAKING**: `search_notes()` parameter `search_all_projects` → `projects`
- Enhanced project parameter documentation (all 6 portmanteau tools)
- Improved MCPB template branding
- Updated README with one-click installation

### Fixed
- MCPB "Basic Memory" → "Advanced Memory" branding
- Handlebars template references
- 40+ ruff formatting issues
- Deprecated test handling (adn_editor)
- Import organization

## 🚀 Upgrade Instructions

### From v1.0.0b5 or earlier

**1. Update package**:
```bash
pip install --upgrade advanced-memory-mcp
```

**2. Update custom scripts** (if using search_all_projects):
```python
# OLD
search_notes("query", search_all_projects=True)

# NEW
search_notes("query", projects="ALL")
```

**3. Enjoy new features**:
```bash
# Try the new deeplink system
advanced-memory deeplink cursor

# Try multi-project search
search_notes("your-query", projects="ALL")
```

## 🎬 What's Next

### v1.0.0rc1 (Planned)
- Response format standardization
- Enhanced cross-project operations
- Performance optimizations
- Additional integration tests

### v1.1.0 (Future)
- Atomic zettelkasten notes (classic format)
- Advanced relationship types
- Knowledge graph visualization
- Web UI (optional)

---

**Quality**: Production-ready ✅  
**Tests**: 45/45 passing ✅  
**Ruff**: Zero errors ✅  
**Documentation**: Comprehensive ✅  

**Install now**: `advanced-memory deeplink cursor` 🚀

