# Tools Documentation

**Purpose**: Comprehensive documentation for all tools used in Advanced Memory MCP

**Organization**: Separated into developer tools and end-user tools

---

## Directory Structure

```
docs/tools/
├── README.md (this file)
├── dev-tools/          # Tools for development
│   ├── just.md         # Command runner
│   ├── pytest-cov.md   # Test coverage
│   ├── ruff.md         # Linter & formatter
│   ├── uv.md           # Package manager
│   └── pre-commit.md   # Git hooks
└── user-tools/         # Tools for end users
    ├── pandoc.md       # Document conversion
    ├── 7-zip.md        # Compression
    └── typora.md       # Markdown editor
```

---

## Development Tools

Tools used during development of Advanced Memory MCP:

### Core Development

| Tool | Purpose | Doc | Status |
|------|---------|-----|--------|
| **just** | Command runner | [just.md](./dev-tools/just.md) | ✅ |
| **uv** | Package manager | [uv.md](./dev-tools/uv.md) | ⏳ |
| **pytest** | Testing framework | [pytest.md](./dev-tools/pytest.md) | ⏳ |
| **pytest-cov** | Test coverage | [pytest-cov.md](./dev-tools/pytest-cov.md) | ✅ |

### Code Quality

| Tool | Purpose | Doc | Status |
|------|---------|-----|--------|
| **ruff** | Linting & formatting | [ruff.md](./dev-tools/ruff.md) | ⏳ |
| **pyright** | Type checking | [pyright.md](./dev-tools/pyright.md) | ⏳ |
| **mypy** | Type checking (legacy) | [mypy.md](./dev-tools/mypy.md) | ⏳ |
| **pre-commit** | Git hooks | [pre-commit.md](./dev-tools/pre-commit.md) | ⏳ |

### Security

| Tool | Purpose | Doc | Status |
|------|---------|-----|--------|
| **bandit** | Security linter | [bandit.md](./dev-tools/bandit.md) | ⏳ |
| **safety** | Dependency vulnerabilities | [safety.md](./dev-tools/safety.md) | ⏳ |
| **trivy** | Comprehensive scanner | [trivy.md](./dev-tools/trivy.md) | ⏳ |
| **semgrep** | Pattern-based analysis | [semgrep.md](./dev-tools/semgrep.md) | ⏳ |

### Build & Release

| Tool | Purpose | Doc | Status |
|------|---------|-----|--------|
| **build** | Python package builder | [build.md](./dev-tools/build.md) | ⏳ |
| **twine** | PyPI publishing | [twine.md](./dev-tools/twine.md) | ⏳ |
| **mcpb** | MCP bundle packaging | [mcpb.md](./dev-tools/mcpb.md) | ⏳ |

---

## User Tools

Tools that end users of Advanced Memory can use:

### Document Conversion

| Tool | Purpose | Doc | Status |
|------|---------|-----|--------|
| **Pandoc** | Convert notes to PDF/DOCX/HTML | [pandoc.md](./user-tools/pandoc.md) | ⏳ |

### Compression

| Tool | Purpose | Doc | Status |
|------|---------|-----|--------|
| **7-Zip** | Archive compression | [7-zip.md](./user-tools/7-zip.md) | ⏳ |
| **WinRAR** | Archive compression | [winrar.md](./user-tools/winrar.md) | ⏳ |

### Markdown Editing

| Tool | Purpose | Doc | Status |
|------|---------|-----|--------|
| **Typora** | WYSIWYG markdown editor | [typora.md](./user-tools/typora.md) | ⏳ |
| **Obsidian** | Knowledge management | [obsidian.md](./user-tools/obsidian.md) | ⏳ |

### Note Management

| Tool | Purpose | Doc | Status |
|------|---------|-----|--------|
| **Obsidian** | Vault integration | See [integrations](../../integrations/obsidian-integration-guide.md) | ✅ |
| **Joplin** | Export/import | See [integrations](../../integrations/) | ✅ |
| **Notion** | Export/import | See [integrations](../../integrations/notion-integration-plan.md) | ✅ |
| **Evernote** | Export/import | See [integrations](../../integrations/evernote-integration-plan.md) | ✅ |

---

## Quick Tool Comparison

### Package Managers

| Tool | Language | Speed | Advanced Memory Uses |
|------|----------|-------|---------------------|
| **uv** | Python (Rust) | ⚡⚡⚡ Very fast | ✅ Primary |
| **pip** | Python | Medium | Fallback |
| **poetry** | Python | Slow | ❌ Not used |
| **conda** | Python | Slow | ❌ Not used |

---

### Linters

| Tool | Speed | Features | Advanced Memory Uses |
|------|-------|----------|---------------------|
| **ruff** | ⚡⚡⚡ 10-100x faster | Linting + formatting | ✅ Primary |
| **flake8** | Medium | Linting only | ❌ Replaced by ruff |
| **pylint** | Slow | Comprehensive | ❌ Too slow |
| **black** | Medium | Formatting only | ❌ Replaced by ruff |

---

### Type Checkers

| Tool | Speed | Strictness | Advanced Memory Uses |
|------|-------|-----------|---------------------|
| **pyright** | Fast | Medium | ✅ Primary |
| **mypy** | Medium | High | ⚠️ Some files |
| **pyre** | Fast | High | ❌ Not used |

---

### Compression Tools

| Tool | Compression | Speed | License | Advanced Memory Uses |
|------|-------------|-------|---------|---------------------|
| **7-Zip** | Best | Medium | Open-source | ✅ Preferred |
| **WinRAR** | Good | Fast | Commercial | ✅ Fallback |
| **zip** (built-in) | Basic | Very fast | Built-in | Fallback |

---

## MCP Portmanteau Tools (API Reference)

These unified tools consolidate multiple operations into single interfaces for efficient AI interaction.

| Tool | Purpose | Documentation | Status |
|------|---------|---------------|--------|
| **adn_content** | Content lifecycle management | [content_adn.md](content_adn.md) | ✅ |
| **adn_knowledge** | Core knowledge CRUD | [knowledge_adn.md](knowledge_adn.md) | ✅ |
| **adn_search** | Unified search manager | [search_adn.md](search_adn.md) | ✅ |
| **adn_skills** | Skill system orchestration | [skills_adn.md](skills_adn.md) | ✅ |
| **adn_project** | Multi-project management | [project_adn.md](project_adn.md) | ✅ |
| **adn_system** | System status & health | [system_adn.md](system_adn.md) | ✅ |
| **adn_navigation** | Activity & graph exploration | [navigation_adn.md](navigation_adn.md) | ✅ |
| **adn_import_export**| Data migration portmanteau | [import_export_adn.md](import_export_adn.md) | ✅ |
| **adn_observability** | Agent provenance & audit | [observability_adn.md](observability_adn.md) | ✅ |
| **adn_research** | AI research & discovery | [research_adn.md](research_adn.md) | ✅ |
| **adn_external** | System & inter-server tools | [external_adn.md](external_adn.md) | ✅ |

---

## Installation Quick Reference

### Development Tools (All at Once)

```bash
# Install all dev dependencies
uv sync --dev

# Includes:
# - pytest, pytest-cov, pytest-asyncio, pytest-xdist
# - ruff, pyright, mypy
# - bandit, safety
# - build, twine
# - pre-commit
```

---

### User Tools (Separate Installations)

**Pandoc**:
```bash
# Windows
scoop install pandoc
choco install pandoc

# macOS
brew install pandoc
```

**7-Zip**:
```bash
# Windows
scoop install 7zip
choco install 7zip
```

**Typora**:
```bash
# Download from: https://typora.io/
# Commercial license required
```

---

## Tool Categories

### 1. Essential (Can't develop without)

- ✅ **Python 3.11+** - Runtime
- ✅ **uv** - Package management
- ✅ **pytest** - Testing
- ✅ **ruff** - Linting & formatting

---

### 2. Highly Recommended (Professional development)

- ⭐ **just** - Command runner
- ⭐ **pytest-cov** - Coverage
- ⭐ **pyright** - Type checking
- ⭐ **pre-commit** - Git hooks
- ⭐ **bandit** - Security

---

### 3. Optional (Enhanced workflows)

- 📦 **7-Zip** - Backups
- 📝 **Pandoc** - Document conversion
- 🖊️ **Typora** - Markdown editing
- 🔐 **Safety** - Vulnerability scanning

---

### 4. User Tools (End users, not developers)

- 📄 **Pandoc** - Export notes to PDF/DOCX
- 📝 **Typora** - Rich markdown editing
- 📓 **Obsidian** - Vault integration
- 💼 **Notion/Evernote** - Import/export

---

## See Also

- **Development Setup**: [INSTALLATION.md](../../INSTALLATION.md)
- **GitHub Workflows**: [docs/github/README.md](../github/README.md)
- **Testing Guide**: [docs/testing/RUNNING_TESTS_GUIDE.md](../testing/RUNNING_TESTS_GUIDE.md)
- **Integrations**: [docs/integrations/](../integrations/)

---

**Created**: October 17, 2025
**Updated**: 2026-02-21
**Purpose**: Centralized tool documentation
**Status**: All core MCP portmanteau tools documented.
