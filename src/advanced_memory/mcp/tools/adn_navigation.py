"""Navigation Manager portmanteau tool for Advanced Memory MCP server.

This tool consolidates navigation operations: build_context, recent_activity, list_directory, status, sync_status.
It reduces the number of MCP tools while maintaining full functionality.
"""

from loguru import logger

from advanced_memory.mcp.mcp_instance import mcp


@mcp.tool
async def adn_navigation(
    operation: str,
    identifier: str | None = None,
    url: str | None = None,
    dir_name: str = "/",
    depth: int = 1,
    timeframe: str = "7d",
    page: int = 1,
    page_size: int = 10,
    max_related: int = 10,
    file_name_glob: str | None = None,
    type_filter: str | None = "",
    level: str = "basic",
    focus: str | None = None,
    project: str | None = None,
) -> str:
    """Comprehensive navigation management tool for Advanced Memory knowledge base.

    This portmanteau tool consolidates all navigation operations into a single interface,
    reducing MCP tool count while maintaining full functionality for Cursor IDE compatibility.

    SUPPORTED OPERATIONS:
    - build_context: Navigate the knowledge graph via memory:// URLs for conversation continuity
    - recent_activity: Get recently updated information with specified timeframe
    - list_directory: List directory contents with filtering and depth control
    - backlinks: Find all notes that reference a specific note (reverse links)
    - status: Comprehensive system status and diagnostic monitoring
    - sync_status: Monitor file synchronization status and background operations

    NAVIGATION FEATURES:
    - Knowledge graph traversal with relationship exploration
    - Recent activity filtering by type and timeframe
    - Directory listing with recursive depth control
    - System health monitoring and diagnostics
    - File synchronization status tracking
    - Background process monitoring

    Args:
        operation: The navigation operation to perform
        identifier: Note identifier for backlinks operation
        url: Memory URL or pattern for context building
        dir_name: Directory path to list
        depth: Relationship exploration depth or directory recursion depth
        timeframe: Time window for activity filtering
        page: Pagination page for results
        page_size: Results per page
        max_related: Maximum related items to include
        file_name_glob: Glob pattern for file filtering
        type_filter: Type filter for recent activity
        level: Status detail level
        focus: Specific area to focus on
        project: Optional project name

    Returns:
        Operation-specific result with navigation details and system information

    Examples:
        # Build context from memory URL
        adn_navigation("build_context", url="memory://projects/ai", depth=2, timeframe="7d")

        # Get recent activity
        adn_navigation("recent_activity", timeframe="today", type_filter="notes")

        # List directory contents
        adn_navigation("list_directory", dir_name="/projects", depth=2)

        # Find backlinks to a note
        adn_navigation("backlinks", identifier="Python Basics", max_related=20)

        # Check system status
        adn_navigation("status", level="intermediate", focus="sync")

        # Monitor sync status
        adn_navigation("sync_status", project="work")
    """
    logger.info(f"MCP tool call tool=adn_navigation operation={operation}")

    # Route to appropriate operation
    if operation == "build_context":
        return await _build_context_operation(
            url, depth, timeframe, page, page_size, max_related, project
        )
    elif operation == "recent_activity":
        return await _recent_activity_operation(
            type_filter, depth, timeframe, page, page_size, max_related, project
        )
    elif operation == "list_directory":
        return await _list_directory_operation(dir_name, depth, file_name_glob, project)
    elif operation == "backlinks":
        if not identifier:
            return "# Error\n\nBacklinks operation requires: identifier parameter"
        return await _backlinks_operation(identifier, max_related, project)
    elif operation == "status":
        return await _status_operation(level, focus)
    elif operation == "sync_status":
        return await _sync_status_operation(project)
    else:
        return f"# Error\n\nInvalid operation '{operation}'. Supported operations: build_context, recent_activity, list_directory, backlinks, status, sync_status"


async def _build_context_operation(
    url: str | None,
    depth: int,
    timeframe: str,
    page: int,
    page_size: int,
    max_related: int,
    project: str | None,
) -> str:
    """Handle build context operation."""
    if not url:
        return "# Error\n\nBuild context requires: url parameter"

    from advanced_memory.mcp.tools.build_context import build_context

    return await build_context.fn(url, depth, timeframe, page, page_size, max_related, project)


async def _recent_activity_operation(
    type_filter: str | None,
    depth: int,
    timeframe: str,
    page: int,
    page_size: int,
    max_related: int,
    project: str | None,
) -> str:
    """Handle recent activity operation."""
    from advanced_memory.mcp.tools.recent_activity import recent_activity

    return await recent_activity.fn(
        type_filter, depth, timeframe, page, page_size, max_related, project
    )


async def _list_directory_operation(
    dir_name: str, depth: int, file_name_glob: str | None, project: str | None
) -> str:
    """Handle list directory operation."""
    from advanced_memory.mcp.tools.list_directory import list_directory

    return await list_directory.fn(dir_name, depth, file_name_glob, project)


async def _status_operation(level: str, focus: str | None) -> str:
    """Handle status operation."""
    from advanced_memory.mcp.tools.status import status

    return await status.fn(level, focus)


async def _backlinks_operation(identifier: str, max_related: int, project: str | None) -> str:
    """Handle backlinks operation - find notes that reference this note."""
    from advanced_memory.mcp.async_client import client
    from advanced_memory.mcp.project_session import get_active_project
    from advanced_memory.mcp.tools.utils import call_post

    active_project = get_active_project(project)
    project_url = active_project.project_url

    # Search for wikilink references to this note
    # Use the identifier as search term with special handling for wikilinks
    search_query = f"[[{identifier}]]"

    try:
        # Search for content containing the wikilink
        response = await call_post(
            client,
            f"{project_url}/search/",
            json={"text": search_query, "types": ["entity"]},
            params={"page": 1, "page_size": max_related},
        )

        if response.status_code != 200:
            return f"# Backlinks: {identifier}\n\nNo backlinks found or search failed."

        results = response.json().get("results", [])

        if not results:
            return f"""# Backlinks: {identifier}

No backlinks found.

This note is not referenced by any other notes in your knowledge base.

SUGGESTIONS:
- This might be an orphan note (isolated knowledge)
- Consider linking it from related notes
- Or this is a foundational note that others should reference
"""

        # Format backlinks response
        response_lines = [
            f"# Backlinks: {identifier}",
            "",
            f"Found {len(results)} note(s) that reference this note:",
            "",
        ]

        for idx, result in enumerate(results, 1):
            title = result.get("title", "Unknown")
            permalink = result.get("permalink", "")
            content_snippet = result.get("content", "")[:200]

            response_lines.append(f"## {idx}. {title}")
            response_lines.append(f"**Permalink:** {permalink}")
            response_lines.append(f"**Preview:** {content_snippet}...")
            response_lines.append("")

        response_lines.append(f"**Total backlinks:** {len(results)}")
        response_lines.append(
            f"**Status:** {'Well-connected' if len(results) > 3 else 'Some connections' if len(results) > 0 else 'Orphan (no connections)'}"
        )

        logger.info(
            f"MCP tool response: tool=adn_navigation operation=backlinks identifier={identifier} backlinks_count={len(results)}"
        )

        return "\n".join(response_lines)

    except Exception as e:
        logger.error(f"Error finding backlinks: {e}")
        return f"# Error\n\nFailed to find backlinks for '{identifier}': {str(e)}"


async def _sync_status_operation(project: str | None) -> str:
    """Handle sync status operation."""
    from advanced_memory.mcp.tools.sync_status import sync_status

    return await sync_status.fn(project)
