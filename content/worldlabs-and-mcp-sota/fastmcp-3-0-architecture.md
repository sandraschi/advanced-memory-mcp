# FastMCP 3.0.0 Architecture

**Timestamp**: 2026-01-23
**Status**: SOTA Standard

- [primitives] Introduces **Providers** (component sources) and **Transforms** (middleware).
- [providers] Includes `FileSystemProvider`, `ProxyProvider`, `OpenAPIProvider`, and `SkillsProvider`.
- [transforms] Enables `NamespaceTransform`, `RenameTransform`, and `ArgTransform` for component modification during import.
- [startup] SOTA servers should use `mcp.run_stdio_async()` for better async handling.
- [protocol] Targets MCP Protocol version `2025-11-25`.

- relation_type [[MCP Standards]]
- relation_type [[FastMCP]]
- relation_type [[Domain Hub Architecture]]
