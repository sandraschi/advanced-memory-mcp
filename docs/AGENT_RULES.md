# Advanced Memory MCP — Agent / IDE Rules

These rules apply to ALL AI agents and IDEs (Antigravity, Windsurf, Cursor, etc.)
working in this repository. They encode hard-won lessons from production breakage.

---

## CRITICAL: Tool Registration Architecture

FastMCP registers tools **at import time** via the `@mcp.tool` decorator.
If a file is not imported, its tools do not exist. There is no magic auto-discovery.

### The single source of truth for tool registration:
```
src/advanced_memory/mcp/tools/__init__.py
```

**NEVER gut this file.** The portmanteau imports must always be present:
- `portmanteau_knowledge`  → `adn_knowledge`
- `portmanteau_research`   → `adn_research`
- `portmanteau_skills`     → `adn_skills`
- `portmanteau_system`     → `adn_system`
- `portmanteau_external`   → `adn_external`
- `portmanteau_import_export` → `adn_import_export`
- `help`                   → `help`

If you remove these imports, the server starts but has zero tools. This looks like
a broken server from the user's perspective and is very hard to debug.

---

## CRITICAL: CodeMode

`CodeMode` is a FastMCP 3.2 transform that replaces ALL registered tools with
two meta-tools: `search` and `execute`. This is useful for agents that prefer
BM25 tool discovery over explicit tool lists.

### Where CodeMode is applied: `cli/commands/mcp.py` ONLY
```python
if agentic:
    from fastmcp.experimental.transforms.code_mode import CodeMode
    mcp_server.add_transform(CodeMode())
```

### Where CodeMode must NEVER appear:
- `src/advanced_memory/mcp/server.py` — module scope, affects all users
- `src/advanced_memory/mcp/tools/__init__.py` — import time, wrong layer

### How to use agentic mode:
```
# In claude_desktop_config.json for an agent entry:
"args": ["run", "python", "-m", "advanced_memory.cli.main", "mcp",
         "--transport", "stdio", "--agentic"]

# Interactive mode (default, no --agentic):
"args": ["run", "python", "-m", "advanced_memory.cli.main", "mcp",
         "--transport", "stdio"]
```

### CodeMode API (fastmcp 3.2):
```python
CodeMode()        # CORRECT — zero arguments
CodeMode(mcp)     # WRONG — was valid in 3.1, TypeError in 3.2
```

---

## CRITICAL: FileSystemProvider

`FileSystemProvider` scans a directory for tool *definition files* (YAML/JSON/Markdown
schemas). It does **not** discover or register Python `@mcp.tool` decorated functions.

**NEVER add FileSystemProvider to server.py pointing at the tools/ directory.**
It does not work for this codebase and will silently register zero tools.

---

## fastmcp Version Compatibility

Before any fastmcp upgrade, check CHANGELOG for API breaks.
Known breaking changes:
- 3.1 → 3.2: `CodeMode(mcp)` → `CodeMode()` (constructor arg removed)

Current SOTA: `fastmcp>=3.2.0`

---

## Pre-commit Hooks

The `.git/hooks/pre-commit` and `.git/hooks/commit-msg` files must have LF line
endings (not CRLF). Windows tools that write these files will corrupt them.
If commits start failing with `$'\\r': command not found`, delete the hook files —
git will skip them and they can be reinstalled via `pre-commit install`.

---

## Two-Mode Server Summary

| Mode | Flag | Tools visible | Use case |
|------|------|--------------|----------|
| Interactive | (none) | 7 portmanteau tools | Claude Desktop, humans |
| Agentic | `--agentic` | `search` + `execute` | Cowork, pipelines, agents |

The interactive mode is the default and must always work correctly.
Agentic mode is opt-in and applied only in `cli/commands/mcp.py`.
