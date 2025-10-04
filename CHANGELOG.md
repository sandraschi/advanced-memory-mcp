# Changelog

All notable changes to Advanced Memory MCP will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Comprehensive CI/CD pipeline with automated testing
- GitHub issue and PR templates for better community interaction
- Security scanning and vulnerability detection
- Automated dependency updates with Dependabot
- Release automation with GitHub Actions
- CODEOWNERS file for code review assignments
- SECURITY.md for vulnerability reporting
- CONTRIBUTING.md with detailed contribution guidelines
- Performance and compatibility issue templates

### Changed
- Enhanced project documentation and guidelines

## [1.0.0] - 2024-10-04

### Added
- **Portmanteau Tools**: Consolidated 40+ individual tools into 8 comprehensive tools
  - `adn_content`: Content management (write, read, edit, move, delete)
  - `adn_project`: Project management (create, switch, list, etc.)
  - `adn_export`: Export to various formats (PDF, HTML, Docsify, etc.)
  - `adn_import`: Import from external systems (Obsidian, Notion, etc.)
  - `adn_search`: Search across knowledge base and external systems
  - `adn_knowledge`: Advanced knowledge operations and analytics
  - `adn_navigation`: Navigate and explore your knowledge base
  - `adn_editor`: Editor integration (Typora, Notepad++, etc.)
- **MCPB Package**: Complete package for Claude Desktop installation
- **Extensive Prompt Templates**: 
  - Advanced Memory Guide (12.4KB comprehensive guide)
  - Quick Start Guide (5-minute getting started)
  - Examples (comprehensive usage patterns)
  - Troubleshooting (common issues and solutions)
- **Cursor IDE Compatibility**: Reduced tool count to stay within 50-tool limit
- **Backward Compatibility**: Legacy individual tools still available
- **Cross-Platform Support**: Windows, macOS, and Linux compatibility

### Features
- **Content Management**: Full CRUD operations for notes and entities
- **Project Management**: Multi-project support with switching capabilities
- **Export Capabilities**: Multiple format support (PDF, HTML, Docsify, Joplin, etc.)
- **Import Capabilities**: Support for Obsidian, Notion, Evernote, Joplin vaults
- **Search Functionality**: Full-text search across knowledge base and external systems
- **Knowledge Operations**: Bulk operations, tag analytics, research orchestration
- **Navigation Tools**: Context building, recent activity, directory listing
- **Editor Integration**: Typora automation, Notepad++ integration, canvas creation

### Technical
- **FastMCP Framework**: Built on FastMCP 2.12+ for optimal performance
- **Async/Await**: Full asynchronous support for better responsiveness
- **Pydantic Schemas**: Robust data validation and serialization
- **SQLAlchemy ORM**: Modern database operations with async support
- **Comprehensive Testing**: Unit, integration, and MCP tool tests
- **Type Safety**: Full type hints throughout the codebase

### Documentation
- **README.md**: Comprehensive project overview and usage examples
- **Gold Status Assessment**: Current status against quality standards
- **API Documentation**: Detailed tool descriptions and parameters
- **Installation Guides**: Multiple installation methods and platforms

## [0.1.0] - 2024-09-XX

### Added
- Initial fork from Basic Memory MCP
- Core MCP server implementation
- Basic tool structure
- Project setup and configuration

---

## Legend

- **Added** for new features
- **Changed** for changes in existing functionality
- **Deprecated** for soon-to-be removed features
- **Removed** for now removed features
- **Fixed** for any bug fixes
- **Security** for vulnerability fixes