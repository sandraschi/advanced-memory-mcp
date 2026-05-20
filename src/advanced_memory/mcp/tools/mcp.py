"""MCP namespaced app for Advanced Memory MCP.

Decomposed from the legacy adn_import_export and canvas tools.
Follows FastMCP 3.2 GA Managed Namespace standards for data portability.
"""

from typing import Annotated, Any, Literal

from fastmcp import FastMCP
from pydantic import Field

# Initialize the namespaced app
mcp_app = FastMCP("mcp")


@mcp_app.tool(task=True)
async def ingest(
    format: Annotated[Literal["obsidian", "notion", "joplin", "evernote", "onenote", "archive"], Field(description="Source data format")],
    path: Annotated[str, Field(description="Absolute path to the vault, export, or notebook file")],
    options: Annotated[dict | None, Field(description="Format-specific ingestion settings")] = None,
) -> Any:
    """External Data Ingestion

    Imports knowledge from external silos into the native Advanced Memory ecosystem.
    """
    from advanced_memory.mcp.tools.portmanteau_import_export import adn_import_export
    return await adn_import_export(
        operation="import",
        format=format,
        path=path,
        options=options
    )


@mcp_app.tool(task=True)
async def export(
    format: Annotated[Literal["html", "pdf", "pandoc", "docsify", "archive"], Field(description="Target output format")],
    destination: Annotated[str, Field(description="Absolute path to the output file or directory")],
    options: Annotated[dict | None, Field(description="Format-specific export settings")] = None,
) -> Any:
    """Knowledge Portability Engine

    Synthesizes and exports knowledge from Advanced Memory into professional formats like PDF, HTML, or Docsify.
    """
    from advanced_memory.mcp.tools.portmanteau_import_export import adn_import_export
    return await adn_import_export(
        operation="export",
        format=format,
        destination=destination,
        options=options
    )


@mcp_app.tool()
async def canvas(
    title: Annotated[str, Field(description="Title of the canvas file")],
    nodes: Annotated[list[dict], Field(description="List of node objects (file, text, link, group)")],
    edges: Annotated[list[dict], Field(description="List of edge objects (connections)")],
    folder: Annotated[str, Field(description="Target folder path relative to project root")],
    project: Annotated[str | None, Field(description="Project context override")] = None,
) -> Any:
    """Obsidian Canvas Engine

    Generates an Obsidian-compatible .canvas file to visualize relationships between notes.
    """
    from advanced_memory.mcp.tools.canvas import canvas as _canvas_fn
    return await _canvas_fn(nodes=nodes, edges=edges, title=title, folder=folder, project=project)


@mcp_app.tool(task=True)
async def load(
    path: Annotated[str, Field(description="Absolute path to the resource to load (e.g., .canvas)")],
    format: Annotated[Literal["canvas"], Field(description="Type of resource to load")] = "canvas",
) -> Any:
    """Resource Loading Tool

    Loads non-markdown knowledge resources like Obsidian Canvas files into the active context.
    """
    from advanced_memory.mcp.tools.portmanteau_import_export import adn_import_export
    return await adn_import_export(
        operation="load",
        format=format,
        path=path
    )
