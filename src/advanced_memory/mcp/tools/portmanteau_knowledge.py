"""Portmanteau tool for core knowledge management operations.

PORTMANTEAU PATTERN RATIONALE: Consolidates 25+ individual CRUD operations for notes,
content management, editing, and basic knowledge operations into a single tool with
operation parameters. This reduces tool count while maintaining clear conceptual boundaries
for basic knowledge management tasks.
"""

from typing import Annotated, Literal

from pydantic import Field

from advanced_memory.mcp.tools.utils import build_error_response, build_success_response


async def adn_knowledge_portmanteau(
    operation: Annotated[
        Literal[
            "create",
            "read",
            "update",
            "delete",
            "move",
            "list",
            "search",
            "navigate",
            "context",
            "activity",
            "status",
        ],
        Field(description="Knowledge operation to perform"),
    ],
    identifier: Annotated[
        str | None,
        Field(description="Note/entity identifier (required for read/update/delete/move)"),
    ] = None,
    title: Annotated[str | None, Field(description="Note title (required for create)")] = None,
    content: Annotated[str | None, Field(description="Note content (for create/update)")] = None,
    folder: Annotated[str | None, Field(description="Target folder (for create/move)")] = None,
    tags: Annotated[
        list[str] | None, Field(description="Tags to assign (for create/update)")
    ] = None,
    query: Annotated[str | None, Field(description="Search query (for search operation)")] = None,
    path: Annotated[
        str | None, Field(description="File/directory path (for list/navigation)")
    ] = None,
    depth: Annotated[
        int | None, Field(description="Navigation depth (for context/navigation)")
    ] = None,
    timeframe: Annotated[str | None, Field(description="Time filter (for activity)")] = None,
    entity_type: Annotated[str | None, Field(description="Entity type filter")] = None,
    search_type: Annotated[
        str | None, Field(description='Search type: "text", "title", "permalink" (for search)')
    ] = None,
    page: Annotated[int | None, Field(description="Page number for results")] = None,
    results_per_page: Annotated[int | None, Field(description="Number of results per page")] = None,
    projects: Annotated[
        str | None, Field(description="Project filter (e.g. 'work', 'personal', 'ALL')")
    ] = None,
) -> dict:
    """Unified portmanteau tool for all core knowledge management operations.

    This tool consolidates basic CRUD operations for knowledge management:
    - Note creation, reading, updating, deletion
    - Content navigation and exploration
    - Basic search functionality
    - Activity monitoring
    - Directory listing

    Args:
        operation: The specific knowledge operation to perform
        identifier: Note/entity identifier for targeted operations
        title: Note title for creation
        content: Note content for creation/updates
        folder: Target folder for organization
        tags: Tags for categorization
        query: Search terms
        path: File/directory path for navigation
        depth: Navigation depth for context building
        timeframe: Time-based filtering
        entity_type: Entity type filtering

    Returns:
        Operation result with appropriate data structure

    Examples:
        # Create a new note
        adn_knowledge("create", title="My Note", content="Note content", folder="research")

        # Read existing note
        adn_knowledge("read", identifier="note-id")

        # Update note content
        adn_knowledge("update", identifier="note-id", content="Updated content")

        # Search notes
        adn_knowledge("search", query="machine learning")

        # List directory
        adn_knowledge("list", path="research/")

        # Get recent activity
        adn_knowledge("activity", timeframe="1 week")
    """
    if operation == "create":
        if not title:
            return build_error_response(
                "VALIDATION_ERROR", "MISSING_PARAMETER", "Title required for note creation"
            )
        if not content:
            return build_error_response(
                "VALIDATION_ERROR", "MISSING_PARAMETER", "Content required for note creation"
            )

        from advanced_memory.mcp.tools.write_note import write_note

        result = await write_note.fn(
            title=title,
            content=content,
            folder=folder or "",
            tags=tags or [],
            entity_type=entity_type or "note",
        )
        return build_success_response("create", result, result=result)

    elif operation == "read":
        if not identifier:
            return build_error_response(
                "VALIDATION_ERROR", "MISSING_PARAMETER", "Identifier required for note reading"
            )

        from advanced_memory.mcp.tools.read_note import read_note

        result = await read_note.fn(identifier)
        # result is already likely a dict or model from read_note
        return build_success_response("read", "Note read successfully", result=result)

    elif operation == "update":
        if not identifier:
            return build_error_response(
                "VALIDATION_ERROR", "MISSING_PARAMETER", "Identifier required for note update"
            )

        from advanced_memory.mcp.tools.edit_note import edit_note

        result = await edit_note.fn(identifier, "replace", content or "")
        return build_success_response("update", result)

    elif operation == "delete":
        if not identifier:
            return build_error_response(
                "VALIDATION_ERROR", "MISSING_PARAMETER", "Identifier required for note deletion"
            )

        from advanced_memory.mcp.tools.delete_note import delete_note

        result = await delete_note.fn(identifier)
        return build_success_response("delete", result)

    elif operation == "move":
        if not identifier or not folder:
            return build_error_response(
                "VALIDATION_ERROR",
                "MISSING_PARAMETER",
                "Identifier and folder required for move operation",
            )

        from advanced_memory.mcp.tools.move_note import move_note

        result = await move_note.fn(identifier, folder)
        return build_success_response("move", result)

    elif operation == "search":
        if not query:
            return build_error_response(
                "VALIDATION_ERROR", "MISSING_PARAMETER", "Query required for search operation"
            )

        from advanced_memory.mcp.tools.search import search_notes

        result = await search_notes.fn(
            query,
            page=page or 1,
            results_per_page=results_per_page or 20,
            search_type=search_type or "text",
            projects=projects,
            entity_types=[entity_type] if entity_type else None,
        )
        # search_notes returns SearchResponse object
        return build_success_response(
            "search",
            "Search completed",
            result=result.model_dump() if hasattr(result, "model_dump") else result,
        )

    elif operation == "list":
        try:
            from advanced_memory.mcp.tools.list_directory import (
                call_get,
                client,
                get_active_project,
                list_directory,
            )

            # Fetch raw nodes for programmatic use
            active_project = get_active_project(None)
            params = {"dir_name": path or "", "depth": str(depth or 1)}
            response = await call_get(
                client, f"{active_project.project_url}/directory/list", params=params
            )
            raw_nodes = response.json()

            formatted_result = await list_directory.fn(path or "", depth=depth or 1)
            return build_success_response("list", formatted_result, result=raw_nodes)
        except Exception as e:
            return build_error_response(
                "LIST_FAILED",
                "LIST_FAILED",
                f"List operation failed internal: {type(e).__name__}: {str(e)}",
            )

    elif operation == "navigate":
        if not identifier:
            return build_error_response(
                "VALIDATION_ERROR", "MISSING_PARAMETER", "Identifier required for navigation"
            )

        from advanced_memory.mcp.tools.build_context import build_context

        result = await build_context.fn(identifier, depth=depth or 2)
        return build_success_response("navigate", result)

    elif operation == "context":
        if not identifier:
            return build_error_response(
                "VALIDATION_ERROR",
                "MISSING_PARAMETER",
                "Identifier required for context building",
            )

        from advanced_memory.mcp.tools.build_context import build_context

        result = await build_context.fn(identifier, depth=depth or 2)
        return build_success_response("context", result)

    elif operation == "activity":
        from advanced_memory.mcp.tools.recent_activity import recent_activity

        result = await recent_activity.fn(
            entity_type or "entity", depth=depth or 1, timeframe=timeframe or "1d"
        )
        # recent_activity might return a string or object depending on implementation
        return build_success_response("activity", "Recent activity fetched", result=result)

    elif operation == "status":
        from advanced_memory.mcp.tools.status import status

        result = await status.fn("basic")
        return build_success_response("status", result)

    else:
        return build_error_response(
            "VALIDATION_ERROR", "VALIDATION_ERROR", f"Unknown operation: {operation}"
        )
