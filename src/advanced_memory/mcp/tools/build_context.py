"""Build context tool for Advanced Memory MCP server."""

from typing import Annotated

from loguru import logger
from pydantic import Field

from advanced_memory.mcp.async_client import client
from advanced_memory.mcp.mcp_instance import mcp
from advanced_memory.mcp.project_session import get_active_project
from advanced_memory.mcp.tools.utils import call_get
from advanced_memory.schemas.base import TimeFrame
from advanced_memory.schemas.memory import (
    GraphContext,
    MemoryUrl,
    memory_url_path,
)


@mcp.tool
async def build_context(
    url: Annotated[MemoryUrl, Field(description="memory:// URI to follow")],
    depth: Annotated[int | None, Field(description="Relation hops (1-3 recommended)")] = 1,
    timeframe: Annotated[
        TimeFrame | None, Field(description="Lookback window (e.g. 'today', '2 days ago')")
    ] = "7d",
    page: Annotated[int, Field(description="Results page number")] = 1,
    page_size: Annotated[int, Field(description="Results per page")] = 10,
    max_related: Annotated[int, Field(description="Max related results")] = 10,
    project: Annotated[str | None, Field(description="Optional project override")] = None,
) -> GraphContext:
    """Get context needed to continue a discussion via memory:// URIs."""
    logger.info(f"Building context from {url}")
    # URL is already validated and normalized by MemoryUrl type annotation

    # Get the active project first to check project-specific sync status
    active_project = get_active_project(project)

    # Check migration status and wait briefly if needed
    from advanced_memory.mcp.tools.utils import wait_for_migration_or_return_status

    migration_status = await wait_for_migration_or_return_status(
        timeout=5.0, project_name=active_project.name
    )
    if migration_status:  # pragma: no cover
        # Return a proper GraphContext with status message
        from datetime import datetime

        from advanced_memory.schemas.memory import MemoryMetadata

        return GraphContext(
            results=[],
            metadata=MemoryMetadata(
                depth=depth or 1,
                timeframe=timeframe,
                generated_at=datetime.now(),
                primary_count=0,
                related_count=0,
                uri=migration_status,  # Include status in metadata
            ),
        )
    project_url = active_project.project_url

    response = await call_get(
        client,
        f"{project_url}/memory/{memory_url_path(url)}",
        params={
            "depth": depth,
            "timeframe": timeframe,
            "page": page,
            "page_size": page_size,
            "max_related": max_related,
        },
    )
    return GraphContext.model_validate(response.json())
