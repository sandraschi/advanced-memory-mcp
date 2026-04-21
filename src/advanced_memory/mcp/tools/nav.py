"""Navigation namespaced app for Advanced Memory MCP.

Decomposed from the legacy adn_navigation portmanteau.
Follows FastMCP 3.2 GA Managed Namespace standards.
"""

from typing import Annotated, Any

from fastmcp import FastMCP
from pydantic import Field

# Initialize the namespaced app
nav_app = FastMCP("nav")


@nav_app.tool(task=True)
async def build_context(
    url: Annotated[str, Field(description="Memory URI (memory://project/permalink) to explore")],
    depth: Annotated[int, Field(description="Relation traversal depth (1-3)", ge=1, le=3)] = 1,
    max_related: Annotated[int, Field(description="Limit of related notes per level")] = 10,
    project: Annotated[str | None, Field(description="Project context override")] = None,
) -> Any:
    """Graph Exploration Engine
    
    Traverses semantic relations from a starting node to build a comprehensive contextual map.
    """
    from advanced_memory.mcp.tools.adn_navigation import adn_navigation
    return await adn_navigation(
        operation="build_context",
        url=url,
        depth=depth,
        max_related=max_related,
        project=project
    )


@nav_app.tool()
async def recent(
    timeframe: Annotated[str, Field(description="ISO date or shorthand (e.g., '1d', '7d', 'yesterday')")] = "24h",
    page: Annotated[int, Field(description="Results page number", ge=1)] = 1,
    page_size: Annotated[int, Field(description="Items per page", ge=1, le=50)] = 20,
    project: Annotated[str | None, Field(description="Project context override")] = None,
) -> Any:
    """Discovery Feed Tool
    
    Returns a chronologically sorted list of recent additions and modifications across the knowledge base.
    """
    from advanced_memory.mcp.tools.adn_navigation import adn_navigation
    return await adn_navigation(
        operation="recent_activity",
        timeframe=timeframe,
        page=page,
        page_size=page_size,
        project=project
    )


@nav_app.tool()
async def ls(
    path: Annotated[str | None, Field(description="Relative folder path to list (defaults to project root)")] = None,
    project: Annotated[str | None, Field(description="Project context override")] = None,
) -> Any:
    """Structural Discovery Tool
    
    Provides a directory-style listing of files and folders within the knowledge base.
    """
    from advanced_memory.mcp.tools.adn_navigation import adn_navigation
    return await adn_navigation(
        operation="list_directory",
        dir_name=path,
        project=project
    )


@nav_app.tool(task=True)
async def backlinks(
    identifier: Annotated[str, Field(description="Title or permalink of the target note")],
    project: Annotated[str | None, Field(description="Project context override")] = None,
) -> Any:
    """Relational Discovery Tool
    
    Identifies and lists all notes that reference or link to a specific target node.
    """
    from advanced_memory.mcp.tools.adn_navigation import adn_navigation
    return await adn_navigation(
        operation="backlinks",
        identifier=identifier,
        project=project
    )


@nav_app.tool()
async def status() -> Any:
    """Graph Health Tool
    
    Reports the current state of the knowledge graph, node counts, and relationship density.
    """
    from advanced_memory.mcp.tools.adn_navigation import adn_navigation
    return await adn_navigation(operation="status")


@nav_app.tool()
async def sync() -> Any:
    """Synchronization Status Tool
    
    Displays the health and progress of the background file synchronization and indexing engine.
    """
    from advanced_memory.mcp.tools.adn_navigation import adn_navigation
    return await adn_navigation(operation="sync_status")
