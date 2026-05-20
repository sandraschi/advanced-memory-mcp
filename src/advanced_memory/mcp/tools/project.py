"""Project namespaced app for Advanced Memory MCP.

Decomposed from the legacy adn_project portmanteau.
Follows FastMCP 3.2 GA Managed Namespace standards for session context management.
"""

from typing import Annotated, Any

from fastmcp import FastMCP
from pydantic import Field

# Initialize the namespaced app
project_app = FastMCP("project")


@project_app.tool(task=True)
async def create(
    name: Annotated[str, Field(description="Unique hyphen-case identifier for the project")],
    path: Annotated[str, Field(description="Absolute file system path to the project root directory")],
    set_default: Annotated[bool, Field(description="If true, loads this project automatically on startup")] = False,
) -> Any:
    """Project Initialization Engine

    Creates a new project configuration and links it to the specified file system directory.
    """
    from advanced_memory.mcp.tools.project_manager import _create_operation
    return await _create_operation(name, path, set_default, ctx=None)


@project_app.tool(task=True)
async def switch(
    name: Annotated[str, Field(description="Name or identifier of the project to activate")],
) -> Any:
    """Context Switch Engine

    Activates a different project context, re-scoping all search and file operations.
    """
    from advanced_memory.mcp.tools.project_manager import _switch_operation
    return await _switch_operation(name, ctx=None)


@project_app.tool()
async def ls() -> Any:
    """Gallery Tool

    Lists all projects registered in the knowledge base with their health and session status.
    """
    from advanced_memory.mcp.tools.project_manager import _list_operation
    return await _list_operation(ctx=None)


@project_app.tool(task=True)
async def rm(
    name: Annotated[str, Field(description="Name of the project to remove from registry")],
) -> Any:
    """Project Deletion Tool

    Permanently removes a project's configuration from the database. Files on disk are preserved.
    """
    from advanced_memory.mcp.tools.project_manager import _delete_operation
    return await _delete_operation(name, ctx=None)


@project_app.tool()
async def status(
    name: Annotated[str | None, Field(description="Project name (defaults to active project)")] = None,
) -> Any:
    """Health Monitoring Tool

    Displays detailed statistics, file counts, and synchronization health for a specific project.
    """
    from advanced_memory.mcp.project_session import session
    from advanced_memory.mcp.tools.project_manager import _status_operation

    target = name or session.get_current_project()
    return await _status_operation(target, ctx=None)


@project_app.tool(task=True)
async def detect() -> Any:
    """AI Context Detector

    Analyzes the conversation history to automatically identify and switch to the most relevant project.
    """
    from advanced_memory.mcp.tools.project_manager import _detect_operation
    return await _detect_operation(ctx=None)
