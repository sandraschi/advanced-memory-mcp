"""System namespaced app for Advanced Memory MCP.

Decomposed from the legacy adn_system portmanteau.
Follows FastMCP 3.2 GA Managed Namespace standards for system orchestration.
"""

from typing import Annotated, Any, Literal

from fastmcp import Context, FastMCP
from pydantic import Field

# Initialize the namespaced app
system_app = FastMCP("system")


@system_app.tool()
async def status(
    level: Annotated[Literal["basic", "detailed", "expert"], Field(description="Depth of the status report")] = "basic",
    focus: Annotated[str | None, Field(description="Specific area of focus (e.g., 'db', 'audio', 'memory')")] = None,
) -> Any:
    """Environment Status Tool

    Provides a comprehensive report on the health and configuration of the Advanced Memory environment.
    """
    from advanced_memory.mcp.tools.portmanteau_system import adn_system

    return await adn_system(operation="status", level=level, focus=focus)


@system_app.tool()
async def sync() -> Any:
    """Global Synchronization Tool

    Reports the real-time status of the background file synchronization and indexing engine.
    """
    from advanced_memory.mcp.tools.portmanteau_system import adn_system

    return await adn_system(operation="sync_status")


@system_app.tool(task=True)
async def workflow(
    goal: Annotated[str, Field(description="Directly articulated goal for the autonomous agent to solve")],
    ctx: Context,
) -> Any:
    """Agentic Execution Engine

    Triggers an autonomous workflow where the agent orchestrates multiple tools to achieve a complex goal.
    """
    from advanced_memory.mcp.tools.portmanteau_system import adn_system

    return await adn_system(operation="workflow", topic=goal, ctx=ctx)


@system_app.tool(task=True)
async def external(
    server: Annotated[str, Field(description="Target MCP server name (e.g., 'speech-mcp')")],
    tool: Annotated[str, Field(description="Target tool within the external server")],
    args: Annotated[dict | None, Field(description="JSON parameters for the tool call")] = None,
) -> Any:
    """External MCP Bridge

    Allows Advanced Memory to act as a control plane by calling tools on other registered MCP servers.
    """
    from advanced_memory.mcp.tools.portmanteau_system import adn_system

    return await adn_system(operation="external_call", server_name=server, tool_name=tool, parameters=args or {})


@system_app.tool()
async def help(
    topic: Annotated[str | None, Field(description="Specific feature or tool to get help on")] = None,
    level: Annotated[
        Literal["basic", "intermediate", "expert"], Field(description="Detail level of the documentation")
    ] = "basic",
) -> Any:
    """Documentation Library

    Retrieves high-fidelity guidance and usage examples for the Advanced Memory platform.
    """
    from advanced_memory.mcp.tools.portmanteau_system import adn_system

    return await adn_system(operation="help", topic=topic, level=level)
