# Advanced Memory MCP - Technical Documentation

**Audience**: Developers, contributors, system administrators, technical users

**For users**: See [README.md](README.md) for user-focused documentation.

---

## Table of Contents

- [Architecture Overview](#architecture-overview)
- [Technical Dependencies](#technical-dependencies)
- [Build System](#build-system)
- [CI/CD Pipeline](#cicd-pipeline)
- [Development Setup](#development-setup)
- [Testing](#testing)
- [Deployment](#deployment)
- [Integration Technologies](#integration-technologies)
- [Performance Considerations](#performance-considerations)

---

## Architecture Overview

### High-Level Architecture

```
┌─────────────────────────────────────────────────────┐
│                  Claude Desktop                      │
│              (MCP Client via stdio)                  │
└────────────────────┬────────────────────────────────┘
                     │
                     │ MCP Protocol (stdio transport)
                     │
┌────────────────────▼────────────────────────────────┐
│            Advanced Memory MCP Server                │
│                                                      │
│  ┌──────────────┐  ┌──────────────┐  ┌───────────┐ │
│  │  FastMCP     │  │  Portmanteau │  │  Content  │ │
│  │  Framework   │  │  Tools (10)  │  │  Manager  │ │
│  └──────────────┘  └──────────────┘  └───────────┘ │
│                                                      │
│  ┌──────────────┐  ┌──────────────┐  ┌───────────┐ │
│  │  Sync        │  │  Search      │  │  Export/  │ │
│  │  Service     │  │  Engine      │  │  Import   │ │
│  └──────────────┘  └──────────────┘  └───────────┘ │
└────────────────────┬────────────────────────────────┘
                     │
                     │ SQLAlchemy ORM
                     │
┌────────────────────▼────────────────────────────────┐
│              SQLite Database                         │
│        (~/.advanced-memory/memory.db)                │
│                                                      │
│  - Entities (notes, documents)                       │
│  - Observations (metadata, properties)               │
│  - Relations (semantic links)                        │
│  - Projects (isolation via project_id)               │
└─────────────────────────────────────────────────────┘
                     │
                     │ File I/O
                     │
┌────────────────────▼────────────────────────────────┐
│          User's Markdown Files                       │
│     (~/Documents/project-name/*.md)                  │
└─────────────────────────────────────────────────────┘
```

**Key Design Decisions**:
- **SQLite**: Single-file database for portability and simplicity
- **Global database**: Shared across projects with `project_id` isolation
- **Markdown-first**: User files remain as standard markdown
- **Sync service**: Bidirectional sync between files and database
- **Portmanteau tools**: Consolidate 40+ tools → 10 for IDE compatibility

**Detailed Architecture**: [docs/ARCHITECTURE_DEEP_DIVE.md](docs/ARCHITECTURE_DEEP_DIVE.md)

---

## Technical Dependencies

### Core Framework

#### FastMCP
**What**: High-performance Model Context Protocol framework
**Why**:
- Simplifies MCP server implementation
- Handles stdio transport automatically
- Provides tool registration and validation
- Active development and community

**Homepage**: https://github.com/jlowin/fastmcp
**Documentation**: [FastMCP Docs](https://github.com/jlowin/fastmcp#readme)
**Our Usage**: [docs/integrations/fastmcp.md](docs/integrations/fastmcp.md)

**Alternatives Considered**:
- Official MCP Python SDK (more verbose, less ergonomic)
- Custom implementation (reinventing the wheel)

### Database

#### SQLAlchemy + SQLite
**What**: ORM with async support + embedded database
**Why**:
- SQLite: Zero-config, single file, cross-platform
- SQLAlchemy: Powerful ORM with async/await support
- No server required (vs PostgreSQL, MySQL)
- Portable database (easy backup/migration)

**SQLite Homepage**: https://www.sqlite.org/
**SQLAlchemy Docs**: https://docs.sqlalchemy.org/
**Our Schema**: [docs/architecture/DATABASE_ARCHITECTURE.md](docs/architecture/DATABASE_ARCHITECTURE.md)

**Performance**:
- Handles 2000+ notes efficiently
- Async queries for responsiveness
- Full-text search via Whoosh

#### Alembic
**What**: Database migration tool
**Why**: Version control for database schema
**Docs**: https://alembic.sqlalchemy.org/

### Search

#### Whoosh
**What**: Pure-Python full-text search library
**Why**:
- No external dependencies (vs Elasticsearch)
- Fast full-text indexing
- Supports complex queries
- Integrates with SQLAlchemy

**Homepage**: https://whoosh.readthedocs.io/
**Our Implementation**: Search engine in `src/advanced_memory/services/search_service.py`

### Configuration

#### Pydantic
**What**: Data validation using Python type hints
**Why**:
- Type-safe configuration
- Automatic validation
- Clear error messages
- JSON schema generation

**Docs**: https://docs.pydantic.dev/

### Markdown Processing

#### Python-Frontmatter
**What**: YAML frontmatter parser
**Why**: Standard way to embed metadata in markdown
**Docs**: https://python-frontmatter.readthedocs.io/

**Our Frontmatter Format**:
```yaml
---
title: Note Title
type: note
permalink: note-title
tags: [tag1, tag2]
created: 2024-12-21T14:00:00Z
modified: 2024-12-21T14:00:00Z
---
```

---

## Integration Technologies

### Pandoc (Export Engine)

**What**: Universal document converter
**Homepage**: https://pandoc.org/
**Install**: https://pandoc.org/installing.html

**Why We Use Pandoc**:
- **40+ output formats**: PDF, DOCX, HTML, EPUB, LaTeX, and more
- **Industry standard**: Used by academia, publishing, documentation
- **Highly customizable**: Templates, filters, extensions
- **Active development**: Regular updates, strong community
- **Command-line**: Easy to integrate programmatically

**Our Integration**:
- File: `src/advanced_memory/mcp/tools/adn_export.py`
- Operation: `pandoc`
- Wrapper: Python subprocess to `pandoc` binary

**Supported Formats**:
```python
# PDF (requires LaTeX)
adn_export("pandoc", export_path="output.pdf", format_type="pdf")

# Word
adn_export("pandoc", export_path="output.docx", format_type="docx")

# HTML
adn_export("pandoc", export_path="output.html", format_type="html")

# EPUB
adn_export("pandoc", export_path="output.epub", format_type="epub")

# LaTeX
adn_export("pandoc", export_path="output.tex", format_type="tex")
```

**For PDF Export**:
- Requires LaTeX distribution
- Windows: [MiKTeX](https://miktex.org/) (full) or [TinyTeX](https://yihui.org/tinytex/) (minimal)
- macOS: [MacTeX](https://tug.org/mactex/)
- Linux: `texlive-full` or TinyTeX

**Configuration**:
- PDF engine: `pdflatex`, `xelatex`, `lualatex`, `wkhtmltopdf`
- Templates: Custom Pandoc templates supported
- Filters: Lua filters for custom processing

**Documentation**: [docs/integrations/pandoc.md](docs/integrations/pandoc.md) (to be created)

### External Tool Integrations

**Obsidian**: https://obsidian.md/
- Import WikiLinks, frontmatter, vaults
- Docs: [docs/integrations/obsidian.md](docs/integrations/obsidian.md)

**Notion**: https://notion.so/
- Import HTML/Markdown exports
- Docs: [docs/integrations/notion.md](docs/integrations/notion.md)

**Joplin**: https://joplinapp.org/
- Import/export notes, notebooks
- Docs: [docs/integrations/joplin.md](docs/integrations/joplin.md)

**Evernote**: https://evernote.com/
- Import ENEX files
- Docs: [docs/integrations/evernote.md](docs/integrations/evernote.md)

**Claude Skills**: https://github.com/anthropics/anthropic-skills
- Bidirectional conversion
- Docs: [docs/user-guide/claude-skills.md](docs/user-guide/claude-skills.md)

### Voice Stack (Audio Soul 2026)

**STT Engine**: `faster-whisper` (Replaced `openai-whisper`)
- **Implementation**: CTranslate2-based implementation for 4x+ speedup.
- **Format**: int8/float16 quantization supported.

**TTS Engine**: `Kokoro` (Replaced `pyttsx3`)
- **Implementation**: PyTorch-based high-fidelity synthesis.
- **Features**: Expressive, soulful voices (e.g., af_heart, am_adam).

**Inference Engine**: `onnxruntime-gpu`
- **Performance**: Zero-copy GPU memory access on RTX 409X.
- **Execution**: CUDA Provider with float16 precision.

---

## Build System

### Package Management: UV

**What**: Fast Python package installer (Rust-based)
**Homepage**: https://github.com/astral-sh/uv
**Why**: 10-100x faster than pip

**Installation**:
```bash
# Windows (PowerShell)
irm https://astral.sh/uv/install.ps1 | iex

# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Usage**:
```bash
# Install dependencies
uv sync

# Install with dev dependencies
uv sync --dev

# Run Python
uv run python script.py

# Run tests
uv run pytest
```

### Project Configuration: pyproject.toml

**Standard**: PEP 518, PEP 621
**File**: [pyproject.toml](pyproject.toml)

**Key Sections**:
```toml
[project]
name = "advanced-memory-mcp"
version = "1.0.0b3"
requires-python = ">=3.11"
dependencies = [
    "fastmcp>=0.4.0",
    "sqlalchemy>=2.0.0",
    # ... see pyproject.toml for full list
]

[project.optional-dependencies]
dev = ["pytest", "pytest-asyncio", "ruff", "mypy"]

[tool.ruff]
# Linting configuration

[tool.pytest.ini_options]
# Test configuration
```

### Lock File: uv.lock

**Purpose**: Reproducible builds
**Contains**: Exact versions of all dependencies (including transitive)
**Commit**: Yes (ensures consistent environments)

---

## CI/CD Pipeline

### GitHub Actions

**Workflows**: `.github/workflows/`

#### 1. CI Workflow (`.github/workflows/ci.yml`)

**Triggers**: Push, Pull Request to `master`

**Jobs**:
```yaml
lint:
  - Setup Python 3.12
  - Install dependencies
  - Run ruff (linting)

test:
  matrix:
    python-version: [3.11, 3.12, 3.13]
  steps:
    - Run pytest
    - Upload coverage reports

security:
  - Run Bandit (security scanning)
  - Check dependencies for vulnerabilities
```

**Status**: Public repo, free GitHub Actions

**Documentation**: [docs/github/github-actions.md](docs/github/github-actions.md)

#### 2. Release Workflow (`.github/workflows/release.yml`)

**Triggers**: Tag push (`v*`)

**Jobs**:
```yaml
build-python:
  - Build wheel (.whl)
  - Build source distribution (.tar.gz)
  - Upload to GitHub Release

build-mcpb:
  - Build MCPB package (.mcpb)
  - Validate manifest
  - Upload to GitHub Release
```

**Manual Trigger**: `workflow_dispatch` for manual releases

**Documentation**: [docs/development/release-process.md](docs/development/release-process.md)

### Quality Gates

**Pre-commit** (recommended):
```bash
# Install pre-commit hooks
pre-commit install

# Run manually
pre-commit run --all-files
```

**Checks**:
- Ruff linting (zero errors required)
- Pytest (all tests pass)
- Type checking (mypy)
- Security scanning (Bandit)

**Standards**:
- Code coverage: Aiming for >70%
- Type hints: Required for new code
- Documentation: Required for public APIs

---

## Development Setup

### Quick Start

```bash
# 1. Clone repository
git clone https://github.com/sandraschi/advanced-memory-mcp.git
cd advanced-memory-mcp

# 2. Install UV (if not installed)
curl -LsSf https://astral.sh/uv/install.sh | sh  # macOS/Linux
# or
irm https://astral.sh/uv/install.ps1 | iex  # Windows

# 3. Create virtual environment and install dependencies
uv sync --dev

# 4. Run tests
uv run pytest

# 5. Run MCP server (for testing)
uv run python -m advanced_memory.mcp.server --transport stdio
```

### Project Structure

```
advanced-memory-mcp/
├── src/
│   └── advanced_memory/
│       ├── mcp/
│       │   ├── server.py          # MCP server entry point
│       │   └── tools/             # MCP tools (portmanteau)
│       ├── services/
│       │   ├── content_service.py
│       │   ├── search_service.py
│       │   └── sync_service.py
│       ├── repository/            # Database layer
│       ├── schemas/               # Pydantic models
│       └── config.py              # Configuration
├── mcpb/                          # MCPB package source
│   ├── src/                       # Copied from src/
│   └── manifest.json              # MCPB configuration
├── tests/                         # Test suite
├── docs/                          # Documentation
├── zettelkasten/                  # Template library
├── pyproject.toml                 # Project config
└── uv.lock                        # Dependency lock
```

### Running from Source

**Option 1: Direct Python**:
```bash
cd src
python -m advanced_memory.mcp.server --transport stdio
```

**Option 2: UV**:
```bash
uv run python -m advanced_memory.mcp.server --transport stdio
```

**Option 3: Installed Package**:
```bash
pip install -e .
advanced-memory mcp
```

### Claude Desktop Configuration

**For development** (run from source):
```json
{
  "mcpServers": {
    "advanced-memory-dev": {
      "command": "python",
      "args": ["-m", "advanced_memory.mcp.server", "--transport", "stdio"],
      "cwd": "D:/Dev/repos/advanced-memory-mcp/src",
      "env": {
        "PYTHONPATH": "D:/Dev/repos/advanced-memory-mcp/src",
        "PYTHONUNBUFFERED": "1"
      }
    }
  }
}
```

---

## Testing

### Test Suite

**Framework**: pytest + pytest-asyncio
**Location**: `tests/`
**Count**: 1113 tests (v1.0.0b3)

**Test Structure**:
```
tests/
├── api/              # API tests
├── cli/              # CLI tests
├── integration/      # Integration tests
├── mcp/              # MCP tool tests
├── repository/       # Database tests
├── services/         # Service layer tests
└── conftest.py       # Shared fixtures
```

### Running Tests

```bash
# All tests
uv run pytest

# Specific file
uv run pytest tests/mcp/test_tool_sync_status.py

# With coverage
uv run pytest --cov=advanced_memory --cov-report=html

# Verbose
uv run pytest -v

# Stop on first failure
uv run pytest -x
```

### Test Coverage

**Current**: ~54% (growing)
**Target**: >70%

**View Coverage**:
```bash
uv run pytest --cov=advanced_memory --cov-report=html
open htmlcov/index.html
```

### Real-World Testing

**Checklist**: [docs/testing/REAL_WORLD_TESTING_CHECKLIST.md](docs/testing/REAL_WORLD_TESTING_CHECKLIST.md)

**Priority areas**:
- Core content management ✅
- Project operations ✅
- Claude Skills export/import ✅
- External imports (Obsidian, Notion) ⏳
- Pandoc exports ⏳

---

## Deployment

### Python Package (PyPI)

**Build**:
```bash
# Using build
python -m build

# Using UV
uv build

# Outputs:
# dist/advanced_memory-1.0.0b3-py3-none-any.whl
# dist/advanced_memory-1.0.0b3.tar.gz
```

**Install**:
```bash
pip install advanced-memory-mcp
```

### MCPB Package (Claude Desktop Extension)

**Build**:
```bash
# Using scripts
python scripts/build_mcpb.py

# Or manually
cd mcpb
mcpb build

# Output:
# mcpb/advanced-memory-mcp.mcpb
```

**Install**:
1. Download `.mcpb` file
2. Open Claude Desktop → Settings → Extensions
3. Drag `.mcpb` file to Extensions page
4. Configure via UI

**Documentation**: [mcpb/MCPB_BUILDING_GUIDE.md](mcpb/MCPB_BUILDING_GUIDE.md)

### Docker (Optional)

**Dockerfile**: [Dockerfile](Dockerfile)

```bash
# Build
docker build -t advanced-memory-mcp .

# Run
docker run -v ~/.advanced-memory:/root/.advanced-memory advanced-memory-mcp
```

---

## Performance Considerations

### Database

**Optimization**:
- Indexes on frequently queried columns
- Async queries for responsiveness
- Connection pooling
- Query result caching

**Scaling**:
- SQLite handles 2000+ notes efficiently
- For >10,000 notes, consider PostgreSQL migration
- Full-text search via Whoosh scales to 100k+ documents

### File Sync

**Strategy**:
- Incremental sync (only changed files)
- Debouncing (wait for burst of changes)
- Background processing
- Archive pattern skipping

**Configuration**:
```json
{
  "index_all_files": false,  // .md only for faster sync
  "sync_changes": true        // Auto-sync on file changes
}
```

### Memory Usage

**Typical**:
- Idle: ~50MB
- Active sync: ~100-200MB
- Large exports: ~500MB

**Optimization**:
- Streaming for large files
- Generator-based processing
- Cleanup after operations

---

## Contributing

### Development Workflow

1. **Fork** repository
2. **Create branch**: `git checkout -b feature/my-feature`
3. **Make changes**
4. **Add tests**: Maintain >70% coverage
5. **Run quality checks**:
   ```bash
   uv run ruff check .
   uv run pytest
   uv run mypy src/
   ```
6. **Commit**: Follow conventional commits
7. **Push**: `git push origin feature/my-feature`
8. **Pull Request**: Target `master` branch

**Guidelines**: [CONTRIBUTING.md](CONTRIBUTING.md)

### Code Style

**Formatter**: Ruff (configured in `pyproject.toml`)
**Linter**: Ruff
**Type Checker**: mypy

**Rules**:
- PEP 8 compliance
- Type hints for all public APIs
- Docstrings for all public functions
- Maximum line length: 100 characters

---

## Related Documentation

### Architecture
- [Architecture Deep Dive](docs/ARCHITECTURE_DEEP_DIVE.md)
- [Database Architecture](docs/architecture/DATABASE_ARCHITECTURE.md)
- [Portmanteau Tools Design](docs/PORTMANTEAU_TOOLS_REFERENCE.md)

### Development
- [Developer Guide](docs/DEVELOPER_GUIDE.md)
- [Release Process](docs/development/release-process.md)
- [Testing Strategy](docs/testing/)

### CI/CD
- [GitHub Actions](docs/github/github-actions.md)
- [CI Configuration](CI_CONFIGURATION.md)
- [Release Workflow](docs/development/release-process.md)

### Integrations
- [FastMCP Integration](docs/integrations/fastmcp.md)
- [Pandoc Integration](docs/integrations/pandoc.md) (to be created)
- [External Tools](docs/integrations/)

---

## Technical Support

### For Developers

**Issues**: https://github.com/sandraschi/advanced-memory-mcp/issues
**Discussions**: https://github.com/sandraschi/advanced-memory-mcp/discussions
**Pull Requests**: https://github.com/sandraschi/advanced-memory-mcp/pulls

### For System Administrators

**Installation**: [INSTALLATION.md](INSTALLATION.md)
**Troubleshooting**: [docs/TROUBLESHOOTING_GUIDE.md](docs/TROUBLESHOOTING_GUIDE.md)
**Configuration**: [docs/user-guide/](docs/user-guide/)

---

**Last Updated**: October 20, 2025
**Version**: 1.0.0b3
**Maintainer**: Sandra Schipal
