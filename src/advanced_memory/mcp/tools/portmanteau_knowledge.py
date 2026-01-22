"""Portmanteau tool for core knowledge management operations.

PORTMANTEAU PATTERN RATIONALE: Consolidates 25+ individual CRUD operations for notes,
content management, editing, and basic knowledge operations into a single tool with
operation parameters. This reduces tool count while maintaining clear conceptual boundaries
for basic knowledge management tasks.
"""

from typing import Annotated, Literal

from loguru import logger
from pydantic import Field

from advanced_memory.mcp.mcp_instance import mcp
from advanced_memory.mcp.tools.utils import build_error_response, build_success_response


@mcp.tool
async def adn_knowledge(
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
    try:
        if operation == "create":
            if not title:
                return build_error_response(
                    "VALIDATION_ERROR", "MISSING_PARAMETER", "Title required for note creation"
                )
            if not content:
                return build_error_response(
                    "VALIDATION_ERROR", "MISSING_PARAMETER", "Content required for note creation"
                )

            # Import here to avoid circular imports
            from advanced_memory.mcp.tools.write_note import write_note

            result = await write_note(
                title=title,
                content=content,
                folder=folder or "",
                tags=tags or [],
                entity_type=entity_type or "note",
            )
            return build_success_response("create", result)

        elif operation == "read":
            if not identifier:
                return build_error_response(
                    "VALIDATION_ERROR", "MISSING_PARAMETER", "Identifier required for note reading"
                )

            from advanced_memory.mcp.tools.read_note import read_note

            result = await read_note(identifier)
            return build_success_response("read", result)

        elif operation == "update":
            if not identifier:
                return build_error_response(
                    "VALIDATION_ERROR", "MISSING_PARAMETER", "Identifier required for note update"
                )

            from advanced_memory.mcp.tools.edit_note import edit_note

            result = await edit_note(identifier, "replace", content or "")
            return build_success_response("update", result)

        elif operation == "delete":
            if not identifier:
                return build_error_response(
                    "VALIDATION_ERROR", "MISSING_PARAMETER", "Identifier required for note deletion"
                )

            from advanced_memory.mcp.tools.delete_note import delete_note

            result = await delete_note(identifier)
            return build_success_response("delete", result)

        elif operation == "move":
            if not identifier or not folder:
                return build_error_response(
                    "VALIDATION_ERROR",
                    "MISSING_PARAMETER",
                    "Identifier and folder required for move operation",
                )

            from advanced_memory.mcp.tools.move_note import move_note

            result = await move_note(identifier, folder)
            return build_success_response("move", result)

        elif operation == "search":
            if not query:
                return build_error_response(
                    "VALIDATION_ERROR", "MISSING_PARAMETER", "Query required for search operation"
                )

            from advanced_memory.mcp.tools.search import search_notes

            result = await search_notes(query, page=1, page_size=20)
            return build_success_response("search", result)

        elif operation == "list":
            from advanced_memory.mcp.tools.list_directory import list_directory

            result = await list_directory(path or "", depth=depth or 1)
            return build_success_response("list", result)

        elif operation == "navigate":
            if not identifier:
                return build_error_response(
                    "VALIDATION_ERROR", "MISSING_PARAMETER", "Identifier required for navigation"
                )

            from advanced_memory.mcp.tools.build_context import build_context

            result = await build_context(identifier, depth=depth or 2)
            return build_success_response("navigate", result)

        elif operation == "context":
            if not identifier:
                return build_error_response(
                    "VALIDATION_ERROR",
                    "MISSING_PARAMETER",
                    "Identifier required for context building",
                )

            from advanced_memory.mcp.tools.build_context import build_context

            result = await build_context(identifier, depth=depth or 2)
            return build_success_response("context", result)

        elif operation == "activity":
            from advanced_memory.mcp.tools.recent_activity import recent_activity

            result = await recent_activity("all", depth=10, timeframe=timeframe or "1d")
            return build_success_response("activity", result)

        elif operation == "status":
            from advanced_memory.mcp.tools.status import status

            result = await status("basic")
            return build_success_response("status", result)

        else:
            return build_error_response(
                "VALIDATION_ERROR", "VALIDATION_ERROR", f"Unknown operation: {operation}"
            )

    except Exception as e:
        logger.error(f"Knowledge operation '{operation}' failed: {e}")
        return build_error_response(
            "VALIDATION_ERROR", "VALIDATION_ERROR", f"Operation failed: {str(e)}"
        )
