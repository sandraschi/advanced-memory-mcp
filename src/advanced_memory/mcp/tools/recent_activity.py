"""Recent activity tool for Advanced Memory MCP server."""

import datetime
from typing import Any

from loguru import logger

from advanced_memory.mcp.async_client import client
from advanced_memory.mcp.mcp_instance import mcp
from advanced_memory.mcp.project_session import get_active_project
from advanced_memory.mcp.tools.utils import call_get
from advanced_memory.schemas.base import TimeFrame
from advanced_memory.schemas.memory import GraphContext
from advanced_memory.schemas.search import SearchItemType

# Python 3.10 compatibility - UTC was added in 3.11
try:
    UTC = datetime.UTC
except AttributeError:
    from datetime import timedelta, timezone

    # Fallback for Python < 3.11
    UTC = timezone(timedelta(0))


@mcp.tool
async def recent_activity(
    type_filter: str | list[str] = "",
    depth: int = 1,
    timeframe: TimeFrame = "7d",
    page: int = 1,
    page_size: int = 10,
    max_related: int = 10,
    project: str | None = None,
) -> dict[str, Any]:
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
        Dictionary containing:
            - results: Latest activities matching the filters
            - metadata: Query details and statistics
            - page/page_size: Pagination info (when available)

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

    Errors:
        - "Invalid timeframe": Returned if the provided 'timeframe' natural language format is not recognized.
        - "Project not found": Returned if the specified 'project' name does not exist.

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
                logger.warning(
                    f"Invalid type_filter value: '{t}'. Ignoring and continuing with valid types."
                )

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
    raw_data = response.json()

    def normalize_timestamp(value: Any) -> str | None:
        if value is None:
            return None
        if isinstance(value, str):
            try:
                # Handle timestamps with or without timezone info
                ts = value.replace("Z", "+00:00")
                dt = datetime.fromisoformat(ts)
            except ValueError:
                return value
        elif isinstance(value, datetime):
            dt = value
        else:
            return str(value)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=UTC)
        return dt.astimezone(UTC).strftime("%Y-%m-%dT%H:%M:%S+00:00")

    def normalize_summary(summary: dict[str, Any]) -> dict[str, Any]:
        summary_type = summary.get("type")

        if summary_type == "relation":
            summary["relation_type"] = summary.get("relation_type") or "related_to"
            summary["from_entity"] = summary.get("from_entity")
            summary["to_entity"] = summary.get("to_entity")
        elif summary_type == "observation":
            summary["category"] = summary.get("category") or "general"
            summary["content"] = summary.get("content") or ""

        summary["created_at"] = normalize_timestamp(summary.get("created_at"))
        return summary

    results = raw_data.get("results", [])
    for item in results:
        if "primary_result" in item and isinstance(item["primary_result"], dict):
            item["primary_result"] = normalize_summary(item["primary_result"])

        observations = item.get("observations", [])
        item["observations"] = [
            normalize_summary(obs) for obs in observations if isinstance(obs, dict)
        ]

        related = item.get("related_results", [])
        item["related_results"] = [
            normalize_summary(rel) for rel in related if isinstance(rel, dict)
        ]

    metadata = raw_data.get("metadata", {})
    metadata["generated_at"] = normalize_timestamp(metadata.get("generated_at"))
    metadata["timeframe"] = metadata.get("timeframe")
    raw_data["metadata"] = metadata

    raw_data["results"] = results

    context = GraphContext.model_validate(raw_data)
    return context.model_dump(mode="json")
