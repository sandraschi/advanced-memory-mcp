# Changelog

All notable changes to Advanced Memory MCP will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Comprehensive CI/CD pipeline with GitHub Actions
- Multi-OS testing (Ubuntu, Windows, macOS)
- Python 3.10-3.13 compatibility testing
- Automated code quality checks (ruff, mypy)
- Security scanning and vulnerability detection
- MCPB package build automation
- Comprehensive documentation for Gold standard compliance
- **Bulletproof sync error handling** - Prevents hangs on corrupted or unusual files
  - File size limits (10MB) to prevent memory issues
  - UTF-8 encoding fallback with replacement characters
  - Markdown parsing error catching and graceful degradation
  - Wikilink parser safety limits (5000 links, 500 char max)
  - Early file validation before processing
  - 7 new error handling tests with 100% pass rate

### Changed
- Migrated from Basic Memory to Advanced Memory branding
- Updated all imports and references from `basic_memory` to `advanced_memory`
- Converted print statements to structured logging
- Improved test infrastructure with proper fixtures
- Enhanced project configuration management
- **Improved sync reliability** - No longer hangs on large/weird files

### Fixed
- Test import errors in integration tests
- Configuration class naming (`BasicMemoryConfig` → `AdvancedMemoryConfig`)
- Missing dependencies in MCP server
- CI workflow trigger conditions
- MCPB package structure and manifest
- **Sync hanging issues** - Large files, encoding errors, malformed markdown no longer cause hangs
- 131 test failures resolved (from 155 failures to 24)

## [0.1.0] - 2025-01-XX (Initial Release)

### Added
- **Portmanteau Tool Architecture**: Revolutionary approach to MCP tool organization
  - 8 comprehensive portmanteau tools consolidating 40+ individual tools
  - `adn_content`, `adn_project`, `adn_export`, `adn_import`, `adn_search`, `adn_knowledge`, `adn_navigation`, `adn_editor`
  - Solves tool-number explosion problem for MCP clients (Cursor IDE 50-tool limit)
  - Zero feature loss through operation-based parameter routing
  
- **Knowledge Management**
  - Multi-project support with project isolation
  - Full-text search with FTS5 indexing
  - Entity relationships and knowledge graphs
  - Semantic search capabilities
  - Tag-based organization
  
- **Import/Export Capabilities**
  - Obsidian vault import
  - Joplin export import
  - Notion HTML/Markdown import
  - Evernote ENEX import
  - Obsidian Canvas support
  - Docsify website export
  - HTML notes export
  - Pandoc multi-format export (PDF, DOCX, HTML, etc.)
  
- **Editor Integrations**
  - Typora control via json_rpc plugin
  - Notepad++ workspace export/import
  - Pandoc batch export automation
  
- **Advanced Features**
  - PDF book creation from notes
  - Knowledge operations (bulk update, consolidate tags)
  - Research orchestrator for guided research
  - Archive export/import for migration
  - Context building for conversation continuity
  
- **MCP Server**
  - FastMCP 2.12+ implementation
  - Stdio transport support
  - Proper tool registration with decorators
  - MCP compliance and best practices
  
- **API**
  - FastAPI REST endpoints
  - Project management API
  - Search API with pagination
  - Import/export API
  - Knowledge graph API
  
- **CLI**
  - Comprehensive command-line interface
  - Project management commands
  - Sync service with watch mode
  - Status monitoring
  - Tool access via CLI
  
- **Documentation**
  - Comprehensive README
  - Architecture documentation
  - GLAMA AI Gold standard tracking
  - Integration guides (Typora, Notepad++, Pandoc)
  - API documentation
  - Development guides
  
- **Infrastructure**
  - GitHub Actions CI/CD
  - Multi-version Python testing
  - Code quality enforcement
  - Security scanning
  - Automated releases
  - MCPB package building

### Technical Details
- Python 3.12+ with full type annotations
- Async/await throughout
- Pydantic v2 for validation
  - SQLAlchemy 2.0 for database
- FastMCP 2.12+ for MCP protocol
- SQLite with FTS5 for search
- Loguru for structured logging

---

## Release Notes

### Version Numbering
This project uses [Semantic Versioning](https://semver.org/):
- MAJOR version for incompatible API changes
- MINOR version for new functionality in a backward compatible manner
- PATCH version for backward compatible bug fixes

### Categories
- **Added**: New features
- **Changed**: Changes in existing functionality
- **Deprecated**: Soon-to-be removed features
- **Removed**: Now removed features
- **Fixed**: Bug fixes
- **Security**: Security vulnerability fixes

---

_For upgrade instructions and migration guides, see [MIGRATION_PLAN.md](MIGRATION_PLAN.md)_
