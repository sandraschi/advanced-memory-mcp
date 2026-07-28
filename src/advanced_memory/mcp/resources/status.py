"""Status resources for Advanced Memory MCP server."""

import json

from loguru import logger

from advanced_memory.mcp.async_client import client
from advanced_memory.mcp.mcp_instance import mcp
from advanced_memory.mcp.project_session import get_active_project
from advanced_memory.mcp.tools.recent_activity import _format_activity_as_markdown
from advanced_memory.mcp.tools.status import status as mcp_status
from advanced_memory.mcp.tools.utils import call_get
from advanced_memory.schemas.memory import GraphContext


@mcp.resource(
    uri="memory://status",
    description="System status and diagnostics for the active Advanced Memory project.",
)
async def system_status() -> str:
    """Return markdown system status report."""
    logger.info("Loading system status resource")
    result = await (mcp_status.fn if hasattr(mcp_status, "fn") else mcp_status)(level="basic")
    return str(result)


@mcp.resource(
    uri="memory://status/tools",
    description="Catalog of MCP tools registered on this server.",
)
async def tool_catalog() -> str:
    """Return JSON list of available MCP tools."""
    logger.info("Loading tool catalog resource")
    tools = await mcp.list_tools()
    catalog = [
        {
            "name": tool.name,
            "description": (tool.description or "")[:200],
        }
        for tool in tools
    ]
    return json.dumps({"tools": catalog, "count": len(catalog)}, indent=2)


@mcp.resource(
    uri="memory://status/recent_activity",
    description="Recent knowledge-base activity (entities, observations, relations).",
)
async def recent_activity() -> str:
    """Return formatted recent activity markdown."""
    logger.info("Loading recent activity status resource")
    active_project = get_active_project()
    project_url = active_project.project_url
    response = await call_get(
        client,
        f"{project_url}/memory/recent",
        params={"page": 1, "page_size": 10, "timeframe": "7d"},
    )
    context = GraphContext.model_validate(response.json())
    return _format_activity_as_markdown(context, "7d", active_project=active_project)
