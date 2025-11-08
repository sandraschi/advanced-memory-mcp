"""Recent activity tool for Advanced Memory MCP server."""

from loguru import logger

from advanced_memory.mcp.async_client import client
from advanced_memory.mcp.mcp_instance import mcp
from advanced_memory.mcp.project_session import get_active_project
from advanced_memory.mcp.tools.utils import call_get
from advanced_memory.schemas.base import TimeFrame
from advanced_memory.schemas.memory import GraphContext
from advanced_memory.schemas.search import SearchItemType


@mcp.tool
async def recent_activity(
    type_filter: str | list[str] = "",
    depth: int = 1,
    timeframe: TimeFrame = "7d",
    page: int = 1,
    page_size: int = 10,
    max_related: int = 10,
    project: str | None = None,
) -> GraphContext:
    """Get recent activity across the knowledge base.

    Args:
        type_filter: Filter by content type(s). Can be a string or list of strings.
            Valid options:
            - "entity" or ["entity"] for knowledge entities
            - "relation" or ["relation"] for connections between entities
            - "observation" or ["observation"] for notes and observations
            Multiple types can be combined: ["entity", "relation"]
            Case-insensitive: "ENTITY" and "entity" are treated the same.
            Default is an empty string, which returns all types.
            Fallback: Invalid types are ignored. If all types are invalid, falls back to all types with a warning.
        depth: How many relation hops to traverse (1-3 recommended)
        timeframe: Time window to search. Supports natural language:
            - Relative: "2 days ago", "last week", "yesterday"
            - Points in time: "2024-01-01", "January 1st"
            - Standard format: "7d", "24h"
        page: Page number of results to return (default: 1)
        page_size: Number of results to return per page (default: 10)
        max_related: Maximum number of related results to return (default: 10)
        project: Optional project name to get activity from. If not provided, uses current active project.

    Returns:
        GraphContext containing:
            - primary_results: Latest activities matching the filters
            - related_results: Connected content via relations
            - metadata: Query details and statistics

    Examples:
        # Get all entities for the last 10 days (default)
        recent_activity()

        # Get all entities from yesterday (string format)
        recent_activity(type_filter="entity", timeframe="yesterday")

        # Get all entities from yesterday (list format)
        recent_activity(type_filter=["entity"], timeframe="yesterday")

        # Get recent relations and observations
        recent_activity(type_filter=["relation", "observation"], timeframe="today")

        # Look back further with more context
        recent_activity(type_filter="entity", depth=2, timeframe="2 weeks ago")

        # Get activity from specific project
        recent_activity(type_filter="entity", project="work-project")

    Notes:
        - Higher depth values (>3) may impact performance with large result sets
        - For focused queries, consider using build_context with a specific URI
        - Max timeframe is 1 year in the past
    """
    logger.info(
        f"Getting recent activity from type_filter={type_filter}, depth={depth}, timeframe={timeframe}, page={page}, page_size={page_size}, max_related={max_related}"
    )
    params = {
        "page": page,
        "page_size": page_size,
        "max_related": max_related,
    }
    if depth:
        params["depth"] = depth
    if timeframe:
        params["timeframe"] = timeframe  # pyright: ignore

    # Validate and convert type_filter parameter
    invalid_types = []
    if type_filter:
        # Convert single string to list
        if isinstance(type_filter, str):
            type_list = [type_filter]
        else:
            type_list = type_filter

        # Validate each type against SearchItemType enum
        validated_types = []
        for t in type_list:
            try:
                # Try to convert string to enum
                if isinstance(t, str):
                    validated_types.append(SearchItemType(t.lower()))
            except ValueError:
                # Track invalid types but don't fail
                invalid_types.append(t)
                logger.warning(f"Invalid type_filter value: '{t}'. Ignoring and continuing with valid types.")

        # If we have valid types, use them. If all were invalid, fall back to all types
        if validated_types:
            params["type"] = [t.value for t in validated_types]  # pyright: ignore
        elif invalid_types:
            # All types were invalid - fallback to all types with warning
            valid_types = [t.value for t in SearchItemType]
            logger.warning(
                f"All provided types were invalid: {invalid_types}. "
                f"Falling back to all types. Valid options: {valid_types}"
            )

    active_project = get_active_project(project)
    project_url = active_project.project_url

    response = await call_get(
        client,
        f"{project_url}/memory/recent",
        params=params,
    )
    return GraphContext.model_validate(response.json())
