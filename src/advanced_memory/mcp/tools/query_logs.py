"""MCP tool to query the in-memory log ring buffer."""

from __future__ import annotations

from typing import Any

from advanced_memory.api.log_buffer import _BUFFER, _LOCK
from advanced_memory.mcp.mcp_instance import mcp


@mcp.tool(annotations={"readOnly": True}, version="0.1.0")
async def query_logs(
    source: str | None = None,
    level: str | None = None,
    search: str | None = None,
    limit: int = 50,
) -> dict[str, Any]:
    """Query the in-memory log ring buffer for recent log entries.

    Filter by source (logger name), level (INFO, WARNING, ERROR, DEBUG),
    or free-text search in the message body.

    Returns: dict with filtered log entries, count, total_matching.
    """
    with _LOCK:
        items = list(_BUFFER)

    if source:
        src = source.lower()
        items = [i for i in items if src in i.get("source", "").lower()]
    if level:
        level_upper = level.upper()
        items = [i for i in items if i.get("level", "").upper() == level_upper]
    if search:
        q = search.lower()
        items = [i for i in items if q in i.get("message", "").lower()]

    total = len(items)
    page = items[-limit:] if limit else items
    return {"success": True, "logs": page, "count": len(page), "total_matching": total}
