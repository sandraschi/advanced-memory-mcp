"""List directory tool for Advanced Memory MCP server."""

from loguru import logger

from advanced_memory.mcp.async_client import client
from advanced_memory.mcp.mcp_instance import mcp
from advanced_memory.mcp.project_session import get_active_project
from advanced_memory.mcp.tools.utils import call_get

_MAX_PAGE = 5000
_DEFAULT_LIMIT = 200


# @mcp.tool
async def list_directory(
    dir_name: str = "/",
    depth: int = 1,
    file_name_glob: str | None = None,
    limit: int = _DEFAULT_LIMIT,
    offset: int = 0,
    project: str | None = None,
) -> str:
    """Browse vault folders/files with bounded pages (avoids huge context dumps).

    PORTMANTEAU RATIONALE: Same as filesystem `ls` — agents need structure without loading
    thousands of paths at once. Use ``limit``/``offset`` or narrow ``dir_name``/``file_name_glob``.

    Args:
        dir_name: Directory path to list (default root ``/``). Examples: ``/``, ``/projects``.
        depth: Recursion depth 1–10 (default 1 = immediate children only).
        file_name_glob: Optional glob for file names (e.g. ``*.md``, ``*meeting*``).
        limit: Max nodes in this response (default 200, max 5000). Same ``dir_name``/depth/glob with
            higher ``offset`` returns the next page.
        offset: Skip this many nodes after stable sort; use ``offset = previous_offset + limit``
            when ``has_more`` is true.
        project: Project name; defaults to active project.

    Returns:
        Markdown-style text listing directories and files for this page, plus a pagination line:
        ``total``, ``has_more``, and hint for the next ``offset``.

    Examples:
        list_directory()  # first page of root, depth 1
        list_directory(dir_name="/projects", limit=50, offset=0)
        list_directory(dir_name="/", depth=2, limit=100, offset=100)  # next page

    Errors:
        Depth outside 1–10 or invalid project: surfaced via API/MCP error handling.
    """
    active_project = get_active_project(project)
    project_url = active_project.project_url

    if depth < 1 or depth > 10:
        return (
            f"Invalid depth={depth}: must be between 1 and 10. "
            "Use a lower depth or narrow dir_name/file_name_glob."
        )

    limit = max(1, min(int(limit), _MAX_PAGE))
    offset = max(0, int(offset))

    params: dict[str, str] = {
        "dir_name": dir_name,
        "depth": str(depth),
        "limit": str(limit),
        "offset": str(offset),
    }
    if file_name_glob:
        params["file_name_glob"] = file_name_glob

    logger.debug(
        f"Listing directory '{dir_name}' depth={depth} glob='{file_name_glob}' "
        f"limit={limit} offset={offset}"
    )

    response = await call_get(
        client,
        f"{project_url}/directory/list",
        params=params,
    )

    payload = response.json()
    if not isinstance(payload, dict) or "nodes" not in payload:
        return "Unexpected directory/list response shape. Retry or narrow dir_name."

    nodes = payload.get("nodes") or []
    total = int(payload.get("total", 0))
    has_more = bool(payload.get("has_more", False))
    ret_limit = int(payload.get("limit", limit))
    ret_offset = int(payload.get("offset", offset))

    if not nodes:
        filter_desc = ""
        if file_name_glob:
            filter_desc = f" matching '{file_name_glob}'"
        base = f"No files found in directory '{dir_name}'{filter_desc}"
        if total == 0:
            return base
        return (
            f"{base}\n\n"
            f"Pagination: total_matching={total}, offset={ret_offset}, limit={ret_limit} "
            f"(empty page — try offset=0 or smaller limit)."
        )

    output_lines: list[str] = []
    if file_name_glob:
        output_lines.append(
            f"Files in '{dir_name}' matching '{file_name_glob}' (depth {depth}) "
            f"[page offset={ret_offset}, limit={ret_limit}]:"
        )
    else:
        output_lines.append(
            f"Contents of '{dir_name}' (depth {depth}) "
            f"[page offset={ret_offset}, limit={ret_limit}]:"
        )
    output_lines.append("")

    directories = [n for n in nodes if n.get("type") == "directory"]
    files = [n for n in nodes if n.get("type") == "file"]

    directories.sort(key=lambda x: x.get("name") or "")
    files.sort(key=lambda x: x.get("name") or "")

    for node in directories:
        path_display = node.get("directory_path", "")
        output_lines.append(f"[FOLDER] {node.get('name', ''):<30} {path_display}")

    if directories and files:
        output_lines.append("")

    for node in files:
        path_display = node.get("directory_path", "")
        title = node.get("title", "")
        updated = node.get("updated_at", "")

        if path_display.startswith("/"):
            path_display = path_display[1:]

        date_str = ""
        if updated:
            try:
                from datetime import datetime

                dt = datetime.fromisoformat(str(updated).replace("Z", "+00:00"))
                date_str = dt.strftime("%Y-%m-%d")
            except Exception:  # pragma: no cover
                date_str = str(updated)[:10] if len(str(updated)) >= 10 else ""

        file_line = f"[DOC] {node.get('name', ''):<30} {path_display}"
        if title and title != node.get("name"):
            file_line += f" | {title}"
        if date_str:
            file_line += f" | {date_str}"

        output_lines.append(file_line)

    output_lines.append("")
    dir_count = len(directories)
    file_count = len(files)
    page_count = dir_count + file_count
    summary_parts = []
    if dir_count:
        summary_parts.append(f"{dir_count} director{'y' if dir_count == 1 else 'ies'}")
    if file_count:
        summary_parts.append(f"{file_count} file{'s' if file_count != 1 else ''}")

    output_lines.append(
        f"This page: {page_count} items ({', '.join(summary_parts) if summary_parts else 'none'})"
    )
    output_lines.append(
        f"Pagination: total_matching={total}, offset={ret_offset}, limit={ret_limit}, "
        f"has_more={str(has_more).lower()}"
    )
    if has_more:
        next_off = ret_offset + ret_limit
        output_lines.append(
            f"Next page: call list_directory with the same dir_name/depth/file_name_glob "
            f"and offset={next_off}, limit={ret_limit}"
        )

    return "\n".join(output_lines)
