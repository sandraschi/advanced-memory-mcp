"""Navigation Manager portmanteau tool for Advanced Memory MCP server.

This tool consolidates navigation operations: build_context, recent_activity, list_directory, status, sync_status.
It reduces the number of MCP tools while maintaining full functionality.
"""

import re
from typing import Literal

from loguru import logger

from advanced_memory.mcp.mcp_instance import mcp
from advanced_memory.mcp.tools.utils import build_error_response, build_success_response
from advanced_memory.schemas.memory import GraphContext


@mcp.tool
async def adn_navigation(
    operation: Literal[
        "build_context",
        "recent_activity",
        "list_directory",
        "backlinks",
        "status",
        "sync_status",
    ],
    identifier: str | None = None,
    url: str | None = None,
    dir_name: str = "/",
    depth: int = 1,
    timeframe: str = "30d",
    page: int = 1,
    page_size: int = 10,
    max_related: int = 10,
    file_name_glob: str | None = None,
    type_filter: Literal["entity", "observation", "relation", ""] | None = "",
    level: Literal["basic", "intermediate", "advanced"] | None = "basic",
    focus: str | None = None,
    project: str | None = None,
) -> dict:
    """Comprehensive navigation management tool for Advanced Memory.

    Operations: build_context, recent_activity, list_directory, backlinks, status, sync_status.

    For full documentation on parameters and usage examples, call:
    `help(topic="adn_navigation")`
    """
    logger.info(f"MCP tool call tool=adn_navigation operation={operation}")

    original_operation = operation
    normalized_operation = re.sub(r"(?<!^)(?=[A-Z])", "_", operation)
    normalized_operation = normalized_operation.replace("-", "_").replace(" ", "_").lower()
    alias_map = {
        "last_activity": "recent_activity",
        "latest_activity": "recent_activity",
        "lastactivity": "recent_activity",
        "latestactivity": "recent_activity",
        "recentactivity": "recent_activity",
        "listdirectory": "list_directory",
        "syncstatus": "sync_status",
    }
    operation = alias_map.get(normalized_operation, normalized_operation)

    # Route to appropriate operation
    if operation == "build_context":
        if not url:
            return build_error_response(
                error="Missing required parameter",
                error_code="MISSING_URL",
                message="build_context operation requires a url parameter with memory:// URL",
                recovery_options=[
                    "Provide url parameter starting with memory://",
                    "Use memory://projects/project-name or memory://notes/note-name",
                    "Check URL format and try again",
                ],
                example={
                    "operation": "build_context",
                    "url": "memory://projects/my-project",
                    "depth": 2,
                },
                urgency="medium",
            )
        return await _build_context_operation(
            url, depth, timeframe, page, page_size, max_related, project
        )
    elif operation == "recent_activity":
        # Pass type_filter to recent_activity operation
        return await _recent_activity_operation(
            type_filter, depth, timeframe, page, page_size, max_related, project
        )
    elif operation == "list_directory":
        return await _list_directory_operation(dir_name, depth, file_name_glob, project)
    elif operation == "backlinks":
        if not identifier:
            return build_error_response(
                error="Missing required parameter",
                error_code="MISSING_IDENTIFIER",
                message="backlinks operation requires an identifier parameter (note title, permalink, or memory:// URL)",
                recovery_options=[
                    "Provide identifier parameter with note title or permalink",
                    "Use adn_content('read') to find the correct identifier first",
                    "Check identifier spelling and try again",
                ],
                example={"operation": "backlinks", "identifier": "Python Basics"},
                urgency="medium",
            )
        return await _backlinks_operation(identifier, max_related, project)
    elif operation == "status":
        return await _status_operation(level, focus)
    elif operation == "sync_status":
        return await _sync_status_operation(project)
    else:
        return f"""# Error: Invalid operation parameter

**Received:** `{original_operation}` -> normalized to `{operation}`

**Valid operations are:**
- `build_context` - Navigate knowledge graph via memory:// URLs
- `recent_activity` - Get recently updated notes (use this for "latest notes")
- `list_directory` - Browse directory contents
- `backlinks` - Find notes that reference a specific note
- `status` - System status and diagnostics
- `sync_status` - File sync monitoring

**Example for "latest notes":**
```
adn_navigation(
    operation="recent_activity",
    timeframe="1d"
)
```

Please adjust the `operation` parameter and try again."""


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
    # URL validation already done in main function

    from advanced_memory.mcp.tools.build_context import build_context

    result = await (build_context.fn if hasattr(build_context, "fn") else build_context)(url, depth, timeframe, page, page_size, max_related, project)

    # Convert GraphContext to markdown string
    output = [f"# Context: {url}\n"]

    if hasattr(result, "results") and result.results:
        output.append(f"**Found {len(result.results)} matching items**\n")
        for ctx_result in result.results:
            # Each result has a primary_result nested inside
            item = (
                ctx_result.primary_result if hasattr(ctx_result, "primary_result") else ctx_result
            )
            title = getattr(item, "title", getattr(item, "name", "Unknown"))
            item_type = getattr(item, "type", "item")
            permalink = getattr(item, "permalink", "")
            output.append(f"- **{title}** ({item_type}) - `{permalink}`")

            # Show related results if any
            if hasattr(ctx_result, "related_results") and ctx_result.related_results:
                for related in ctx_result.related_results[:3]:
                    rel_item = (
                        related.primary_result if hasattr(related, "primary_result") else related
                    )
                    rel_title = getattr(rel_item, "title", "Unknown")
                    output.append(f"  - Related: {rel_title}")
    else:
        output.append("No matching items found.\n")

    if hasattr(result, "metadata"):
        metadata = result.metadata
        if hasattr(metadata, "total_results"):
            output.append(f"\n**Total results**: {metadata.total_results}")

    return "\n".join(output)


async def _recent_activity_operation(
    type_param: str | list[str] | None,  # Can be type_filter or type
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
        # Fallback: attempt to convert from json-like (list, etc.)
        try:
            result = GraphContext.model_validate(raw_result)  # type: ignore[arg-type]
        except Exception:  # pragma: no cover
            logger.error(
                "adn_navigation_recent_activity_invalid_payload",
                payload_type=type(raw_result),
            )
            return build_error_response(
                error="Invalid response format",
                error_code="INVALID_RESPONSE_FORMAT",
                message="recent_activity returned data in an unexpected format",
                recovery_options=[
                    "Try the operation again",
                    "Check server logs for more details",
                    "Contact support if the issue persists",
                ],
                diagnostic_info={
                    "payload_type": str(type(raw_result)),
                    "operation": "recent_activity",
                },
                urgency="low",
            )

    # Prepare structured recent activity results
    activity_items = []
    if hasattr(result, "results") and result.results:
        for ctx_result in result.results:
            # Each result has a primary_result nested inside
            item = (
                ctx_result.primary_result if hasattr(ctx_result, "primary_result") else ctx_result
            )
            activity_items.append(
                {
                    "title": getattr(item, "title", getattr(item, "name", "Unknown")),
                    "type": getattr(item, "type", "item"),
                    "permalink": getattr(item, "permalink", ""),
                    "timestamp": getattr(item, "timestamp", None),
                    "content_preview": getattr(item, "content", "")[:100]
                    if getattr(item, "content", "")
                    else None,
                }
            )

    metadata = {}
    if hasattr(result, "metadata"):
        result_metadata = result.metadata
        metadata = {
            "timeframe": getattr(result_metadata, "timeframe", "N/A"),
            "total_results": getattr(result_metadata, "total_results", len(activity_items)),
            "query_time": getattr(result_metadata, "query_time", None),
        }

    if not activity_items:
        return build_success_response(
            operation="recent_activity",
            summary="No recent activity found",
            result={
                "timeframe": timeframe,
                "total_results": 0,
                "items": [],
                "metadata": metadata,
            },
            next_steps=[
                "Try a different timeframe",
                "Check if there are any notes in the project",
                "Use adn_content() to add some content first",
            ],
        )

    return build_success_response(
        operation="recent_activity",
        summary=f"Found {len(activity_items)} recent items",
        result={
            "timeframe": timeframe,
            "total_results": len(activity_items),
            "items": activity_items,
            "metadata": metadata,
        },
        next_steps=[
            "Use adn_content('read', identifier='permalink') to read specific items",
            "Use adn_navigation() with different parameters to explore more",
            "Consider using adn_search() for content-based queries",
        ],
    )


async def _list_directory_operation(
    dir_name: str, depth: int, file_name_glob: str | None, project: str | None
) -> str:
    """Handle list directory operation."""
    from advanced_memory.mcp.tools.list_directory import list_directory

    return await (list_directory.fn if hasattr(list_directory, "fn") else list_directory)(dir_name, depth, file_name_glob, project)


async def _status_operation(level: str, focus: str | None) -> str:
    """Handle status operation."""
    from advanced_memory.mcp.tools.status import status

    return await (status.fn if hasattr(status, "fn") else status)(level, focus)


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
        return f"""# Error: Backlinks Search Failed

**Operation:** backlinks

**Identifier:** {identifier}

**Problem:** {str(e)}

**Possible causes:**
1. The note identifier doesn't exist
2. Database connection issue
3. Project sync needed

**How to fix:**
1. Verify the note exists: Use `adn_content("read", identifier="{identifier}")`
2. Check project status: Use `adn_navigation("status", level="basic")`
3. Try searching for the note first: Use `adn_search("notes", query="{identifier}")`

**Try again after verifying the note exists.**"""


async def _sync_status_operation(project: str | None) -> str:
    """Handle sync status operation."""
    from advanced_memory.mcp.tools.sync_status import sync_status

    return await (sync_status.fn if hasattr(sync_status, "fn") else sync_status)(project)
