[![License: AGPL v3](https://img.shields.io/badge/License-AGPL_v3-blue.svg)](https://www.gnu.org/licenses/agpl-3.0)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Tests](https://img.shields.io/badge/tests-1244%20passing-brightgreen)](https://github.com/sandraschi/advanced-memory-mcp/actions)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
![MCP Server](https://badge.mcpx.dev?type=server 'MCP Server')
![Research Powered](https://img.shields.io/badge/research--powered-🔍-blue)](https://github.com/sandraschi/advanced-memory-mcp)

# Advanced Memory MCP

**Research-Driven Knowledge Platform** - Transform AI assistants into comprehensive research tools with multi-source intelligence gathering, academic literature access, and intelligent skill creation.

Advanced Memory MCP builds upon the foundational work of [Basic Memory MCP](https://github.com/sandraschi/basic-memory-mcp), evolving it into an enterprise-grade research platform with expanded capabilities and improved reliability.

## Core Capabilities

- **Multi-Source Research**: Web search, academic papers (arXiv), code repositories (GitHub), narrative patterns (TV Tropes)
- **Document Intelligence**: PDF/EPUB processing with RAG vector search for large document analysis
- **Skill Synthesis**: Research-driven expert skill generation using FastMCP sampling
- **Knowledge Management**: Zettelkasten-based note system with Claude Skills export/import
- **Cross-Platform Support**: Compatible with Claude Desktop, Cursor IDE, Windsurf, and other MCP clients
- **Web Interface**: Standalone React application for direct usage without MCP client requirements

## Architecture

```
advanced-memory-mcp/
├── src/                    # MCP server source code
├── webapp/                 # React web application
├── docs/                   # Documentation
├── tests/                  # Test suite
└── scripts/                # Build and utility scripts
```

## Quick Start

### MCP Server Installation
```bash
pip install advanced-memory-mcp
advanced-memory setup  # Interactive configuration
```

### Web Application
```bash
cd webapp
npm install && npm run dev  # http://localhost:3000
```

## Documentation

| Document | Description |
|----------|-------------|
| [**Installation**](docs/INSTALLATION.md) | Setup and configuration guides |
| [**Features**](docs/FEATURES.md) | Comprehensive capabilities overview |
| [**Research Guide**](docs/RESEARCH_DRIVEN_SKILLS.md) | Multi-source research capabilities |
| [**API Reference**](docs/PORTMANTEAU_TOOLS_REFERENCE.md) | MCP tools and parameters |
| [**Web Interface**](webapp/README.md) | React application documentation |
| [**Evolution**](docs/EVOLUTION.md) | Development from Basic Memory MCP |
| [**Architecture**](docs/ARCHITECTURE_DEEP_DIVE.md) | System design and data flow |
| [**Troubleshooting**](docs/TROUBLESHOOTING_GUIDE.md) | Common issues and solutions |

## Development Status

**Version**: 1.3.0
**Status**: Production Ready
**MCP Compatibility**: FastMCP 2.14.3+
**Test Coverage**: 98% pass rate (1,136/1,161 tests)
**Glama Rating**: Silver Tier (80/100)
**Web Interface**: React application included

## Requirements

- Python 3.11+
- Node.js 18+ (for web interface)
- Compatible MCP client (Claude Desktop, Cursor, etc.)

## License

AGPL-3.0-or-later

---

**Advanced Memory MCP** - Enterprise-grade research platform for AI assistants, evolved from Basic Memory MCP with expanded research capabilities and production reliability.
