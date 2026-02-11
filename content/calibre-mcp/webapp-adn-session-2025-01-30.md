# CalibreMCP Webapp ADN Session 2025-01-30

**Timestamp**: 2025-01-30
**Type**: adn
**Scope**: webapp fixes and enhancements

---

## Summary

- [adn] Session addressed broken webapp: logs URL parse error, book modal missing metadata, chat undefined variables. Added logs API with tail/filter/live tail. #adn

## Decisions

- [decision] MCP_USE_HTTP=false. Webapp uses direct Python import; HTTP mount has no tools. Circular import blocked HTTP path fix. #architecture

- [decision] Direct BookService for get_book. Guarantees full metadata; _to_response includes publisher, rating, identifiers. #api

- [decision] Logs page: getBaseUrl() fix, /api/logs, toggle Log file / System status, live tail with exponential backoff. #observability

- [decision] Chat personalities: Default, Librarian, Casual. PERSONALITIES constant and personality state. #chat

## Implemented

- [implementation] webapp/backend/app/api/logs.py, webapp/frontend/app/logs/page.tsx, getSystemStatus fix, get_book direct path, chat personalities, Books publisher param, webapp file logging. #implementation

---

- relates_to [[CalibreMCP Project Status 2025-01-30]]
