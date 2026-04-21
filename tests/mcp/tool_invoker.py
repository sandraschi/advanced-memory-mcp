"""Helpers for MCP tests: direct imports may be plain callables; FastMCP also exposes `.fn`."""

from typing import Any


def mcp_fn(tool: Any) -> Any:
    return getattr(tool, "fn", tool)
