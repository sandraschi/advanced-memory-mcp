"""Recent activity tool for Advanced Memory MCP server."""

# UTC is available in Python 3.11+, for older versions use timezone.utc
try:
    from datetime import UTC
except ImportError:
    UTC = UTC
from typing import Annotated, Any

from loguru import logger
from pydantic import Field

from advanced_memory.config import ConfigManager
from advanced_memory.mcp.async_client import client
from advanced_memory.mcp.mcp_instance import mcp
from advanced_memory.mcp.project_session import get_active_project
from advanced_memory.mcp.tools.utils import call_get
from advanced_memory.schemas.base import TimeFrame
from advanced_memory.schemas.memory import GraphContext
from advanced_memory.schemas.search import SearchItemType


@mcp.tool
async def recent_activity(
    type_filter: Annotated[
        str | list[str], Field(description="Filter by 'entity', 'relation', 'observation'")
    ] = "",
    depth: Annotated[int, Field(description="Relation hops (1-3 recommended)")] = 1,
    timeframe: Annotated[
        TimeFrame,
        Field(
            description=(
                "Floor for **created or last-edited** items: 'yesterday' (calendar), 'today', "
                "'recent' (~7d), '7d', ISO date, etc. Results are newest-first."
            )
        ),
    ] = "7d",
    page: Annotated[int, Field(description="Page number for results")] = 1,
    page_size: Annotated[int, Field(description="Results per page")] = 10,
    max_related: Annotated[int, Field(description="Max related results per primary item")] = 10,
    project: Annotated[str | None, Field(description="Optional project override")] = None,
) -> Any:
    """Get recent activity across the knowledge base."""
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
    context = GraphContext.model_validate(response.json())

    return _format_activity_as_markdown(
        context, str(timeframe), active_project=active_project
    )


def _format_activity_as_markdown(
    context: GraphContext,
    timeframe: str,
    *,
    active_project,
) -> str:
    """Helper to format activity as markdown for fallback."""
    md = [f"## Recent Activity ({timeframe})\n"]
    if not context.results:
        md.append("No recent activity found in the **search index** for this project.")
        md.append("")
        md.append(
            "That usually means one of: (1) edits were made under a **different** Advanced Memory "
            "project than the active one, (2) the vault was edited **only on disk** and sync/index has "
            "not picked it up yet, or (3) `api_url` in `~/.advanced-memory/config.json` points at a "
            "**remote** API whose database is empty or stale while you edited files locally."
        )
        md.append("")
        md.append(f"- **Active project:** `{active_project.name}`")
        md.append(f"- **Vault root:** `{active_project.home}`")
        cfg = ConfigManager().config
        if cfg.api_url:
            md.append(f"- **api_url (remote backend):** `{cfg.api_url}`")
        else:
            md.append("- **api_url:** not set (in-process ASGI — same DB as this machine)")
        md.append("")
        md.append(
            "**Try:** `project_list` / `project_switch` (or pass `project=` on this tool), "
            "then `nav_sync` if sync is enabled, or open the correct project in config."
        )
        return "\n".join(md)

    for item in context.results:
        res = item.primary_result
        res_type = getattr(res, "type", None)
        if hasattr(res_type, "value"):
            res_type = res_type.value
        res_type = res_type or "unknown"
        created = getattr(res, "created_at", "N/A") or "N/A"

        if res_type == "note":
            title = getattr(res, "title", None) or "Untitled Note"
            md.append(f"### [Note] {title}")
            md.append(f"- Created: {created}")
            content_preview = getattr(res, "content", None)
            if content_preview:
                md.append(f"- Content: {content_preview[:200]}...")
        elif res_type == "observation":
            cat = getattr(res, "category", None) or "general"
            content = getattr(res, "content", None) or ""
            md.append(f"### [Observation] {cat}")
            md.append(f"- Created: {created}")
            md.append(f"- {content}")
        elif res_type == "relation":
            rel = getattr(res, "relation_type", None) or "related_to"
            from_e = getattr(res, "from_entity", None) or "Unknown"
            to_e = getattr(res, "to_entity", None) or "Unknown"
            md.append(f"### [Relation] {rel}")
            md.append(f"- Created: {created}")
            md.append(f"- {from_e} -> {to_e}")
        md.append("")

    return "\n".join(md)
