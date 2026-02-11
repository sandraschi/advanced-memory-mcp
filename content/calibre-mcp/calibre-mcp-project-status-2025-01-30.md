# CalibreMCP Project Status

**Timestamp**: 2025-01-30
**Type**: status-report
**Status**: operational

---

## Executive Summary

- [status] CalibreMCP operational. Database auto-initialization complete. Webapp full UI functional. #calibre-mcp #fastmcp

- [architecture] 18 portmanteau tools, 55% reduction from ~40 individual tools. FastMCP 2.14.3+, Python 3.11+, Calibre 6.0+. #portmanteau-pattern

- [webapp] Books, authors, series, tags, publishers, chat, logs, import, export all operational. Backend FastAPI 13000; frontend Next.js 15 on 13001. #webapp

## Core Metrics

- [quality] Zero ruff errors. All portmanteau tools standardized with docstrings. #code-quality

- [reliability] First-try search reliability. Intelligent query parsing for author, tag, pubdate, rating, series. #library-management

- [logging] logs/calibremcp.log (MCP stdio), logs/webapp.log (backend). RotatingFileHandler 10MB, 5 backups. #observability

## Architecture Decisions (ADN)

- [decision] MCP_USE_HTTP=false for webapp. Direct Python import of tool functions; HTTP mount has no tools (main() runs only in stdio). #adn

- [decision] get_book uses direct BookService.get_by_id for full metadata (rating, publisher, identifiers, comments). Fallback to MCP manage_books. #adn

- [decision] Logs page: backend /api/logs; tail, filter, level; live tail with exponential backoff. #adn

## Portmanteau Tools (18)

- [tools] manage_libraries, manage_books, query_books, manage_tags, manage_authors, manage_comments, manage_metadata, manage_files, manage_system, manage_analysis, analyze_library, manage_bulk_operations, manage_content_sync, manage_smart_collections, manage_users, export_books, manage_viewer, manage_specialized. #mcp-tools

## Known Limitations

- [limitation] HTTP MCP mount has no tool registration at module load; stdio mode only registers tools in main(). #architecture

- [debt] Triple initiatives: Great Doc Bash, GitHub Dash, Release Flash at 5-7/10 baseline. #technical-debt

---

- relates_to [[webapp-adn-session-2025-01-30]]
