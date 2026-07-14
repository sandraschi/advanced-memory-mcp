"""Navigation Manager portmanteau tool for Advanced Memory MCP server.

This tool consolidates navigation operations: build_context, recent_activity, list_directory, status, sync_status.
It reduces the number of MCP tools while maintaining full functionality.
"""

from typing import Any

from loguru import logger

from advanced_memory.mcp.mcp_instance import mcp
from advanced_memory.mcp.models.portmanteau import NavOperation
from advanced_memory.schemas.memory import GraphContext


@mcp.tool(name="adn_nav")
async def adn_nav(op: NavOperation) -> Any:
    """
    Semantic graph traversal and relational discovery for Advanced Memory.

    This tool enables high-fidelity navigation through the knowledge base using
    folder-based listings, chronological activity feeds, and graph-based relation
    traversal (backlinks and context maps).

    ---------------------------------------------------------------------------
    [RATIONALE]
    Knowledge in Advanced Memory is not just stored; it is connected. By
    consolidating navigation tasks, we allow the AI to 'surf' the knowledge graph,
    following links and discovering dependencies that would be missed by simple
    keyword search. This provides the 'structural awareness' necessary for complex
    reasoning.

    ---------------------------------------------------------------------------
    [SUPPORTED OPERATIONS]
    - ls: Structural discovery via directory-style listing of files and folders.
    - recent: Chronological feed of new or modified notes across the project.
    - backlinks: Identifies all notes that reference or link to a target node.
    - build_context: Traverses relations from a starting node to build a contextual map.
    - status: Reports on the health and density of the knowledge graph.
    - sync: Displays the progress of background file indexing and sync engine.

    ---------------------------------------------------------------------------
    [PARAMETERS]
    - operation (str): The navigation task (ls, recent, backlinks, build_context, etc.).
    - path (str, optional): Relative folder path to list (defaults to project root).
    - identifier (str, optional): Title or permalink of the target note for backlinks.
    - url (str, optional): Starting memory:// URI for graph traversal.
    - depth (int, optional): Relation traversal depth (1-3 recommended).
    - timeframe (str, optional): Lookback window for recent activity (e.g., '7d', 'today').
    - max_related (int, optional): Limit of related notes per level in context builds.
    - page/page_size (int, optional): Pagination for large result sets.
    - project (str, optional): Override the current active project context.

    ---------------------------------------------------------------------------
    [EXAMPLES]
    ```python
    # Discover all notes that link TO a specific topic
    adn_nav(operation="backlinks", identifier="FastMCP 3.2")

    # Build a 2-hop context map starting from a project note
    adn_nav(operation="build_context", url="memory://project/chrono-glenn", depth=2)
    ```
    """
    operation = op.operation
    logger.info(f"MCP tool call tool=adn_nav operation={operation}")

    # Route to appropriate operation
    if operation == "ls":
        return await _list_directory_operation(op.path or "/", 1, None, op.project)
    elif operation == "recent":
        return await _recent_activity_operation(None, 1, op.timeframe, op.page, op.page_size, 10, op.project)
    elif operation == "sync":
        return await _sync_status_operation(op.project)
    elif operation == "status":
        return await _status_operation("basic", None)
    elif operation == "backlinks":
        return await _backlinks_operation(op.identifier, 10, op.project)
    elif operation == "build_context":
        return await _build_context_operation(op.url, op.depth, "7d", 1, 20, op.max_related, op.project)
    else:
        return f"Error: Unsupported operation {operation}"


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
    from advanced_memory.mcp.tools.build_context import build_context

    result = await (build_context.fn if hasattr(build_context, "fn") else build_context)(
        url, depth, timeframe, page, page_size, max_related, project
    )

    # Convert GraphContext to markdown string
    output = [f"# Context: {url}\n"]

    if hasattr(result, "results") and result.results:
        output.append(f"**Found {len(result.results)} matching items**\n")
        for ctx_result in result.results:
            item = ctx_result.primary_result if hasattr(ctx_result, "primary_result") else ctx_result
            title = getattr(item, "title", getattr(item, "name", "Unknown"))
            item_type = getattr(item, "type", "item")
            permalink = getattr(item, "permalink", "")
            output.append(f"- **{title}** ({item_type}) - `{permalink}`")

            if hasattr(ctx_result, "related_results") and ctx_result.related_results:
                for related in ctx_result.related_results[:3]:
                    rel_item = related.primary_result if hasattr(related, "primary_result") else related
                    rel_title = getattr(rel_item, "title", "Unknown")
                    output.append(f"  - Related: {rel_title}")
    else:
        output.append("No matching items found.\n")

    return "\n".join(output)


async def _recent_activity_operation(
    type_param: str | list[str] | None,
    depth: int,
    timeframe: str,
    page: int,
    page_size: int,
    max_related: int,
    project: str | None,
) -> str:
    """Handle recent activity operation."""
    from advanced_memory.mcp.tools.recent_activity import recent_activity

    raw_result = await (recent_activity.fn if hasattr(recent_activity, "fn") else recent_activity)(
        type_param, depth, timeframe, page, page_size, max_related, project
    )

    if isinstance(raw_result, GraphContext):
        result = raw_result
    elif isinstance(raw_result, dict):
        result = GraphContext.model_validate(raw_result)
    else:
        try:
            result = GraphContext.model_validate(raw_result)
        except Exception:
            return f"Error: Invalid response format from recent_activity: {type(raw_result)}"

    output = [f"# Recent Activity ({timeframe})\n"]
    if hasattr(result, "results") and result.results:
        for ctx_result in result.results:
            item = ctx_result.primary_result if hasattr(ctx_result, "primary_result") else ctx_result
            title = getattr(item, "title", getattr(item, "name", "Unknown"))
            permalink = getattr(item, "permalink", "")
            timestamp = getattr(item, "timestamp", "N/A")
            output.append(f"- **{title}** - `{permalink}` ({timestamp})")
    else:
        output.append("No recent activity found.")

    return "\n".join(output)


async def _list_directory_operation(
    dir_name: str,
    depth: int,
    file_name_glob: str | None,
    project: str | None,
    directory_limit: int = 200,
    directory_offset: int = 0,
) -> str:
    """Handle list directory operation."""
    from advanced_memory.mcp.tools.list_directory import list_directory

    fn = list_directory.fn if hasattr(list_directory, "fn") else list_directory
    return await fn(
        dir_name,
        depth,
        file_name_glob,
        directory_limit,
        directory_offset,
        project,
    )


async def _status_operation(level: str, focus: str | None) -> str:
    """Handle status operation."""
    from advanced_memory.mcp.tools.status import status

    return await (status.fn if hasattr(status, "fn") else status)(level, focus)


async def _backlinks_operation(identifier: str, max_related: int, project: str | None) -> str:
    """Handle backlinks operation."""
    from advanced_memory.mcp.async_client import client
    from advanced_memory.mcp.project_session import get_active_project
    from advanced_memory.mcp.tools.utils import call_post

    active_project = get_active_project(project)
    project_url = active_project.project_url
    search_query = f"[[{identifier}]]"

    try:
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
            return f"# Backlinks: {identifier}\n\nNo backlinks found."

        response_lines = [f"# Backlinks: {identifier}\n", f"Found {len(results)} note(s):\n"]
        for idx, result in enumerate(results, 1):
            title = result.get("title", "Unknown")
            permalink = result.get("permalink", "")
            response_lines.append(f"{idx}. **{title}** (`{permalink}`)")

        return "\n".join(response_lines)
    except Exception as e:
        return f"Error finding backlinks: {e}"


async def _sync_status_operation(project: str | None) -> str:
    """Handle sync status operation."""
    from advanced_memory.mcp.tools.sync_status import sync_status

    return await (sync_status.fn if hasattr(sync_status, "fn") else sync_status)(project)
