"""Typora namespaced app for Advanced Memory MCP.

Decomposed from the legacy typora_control tool.
Follows FastMCP 3.2 GA Managed Namespace standards for remote editor control.
"""

from typing import Annotated, Any, Literal

from fastmcp import FastMCP
from pydantic import Field

# Initialize the namespaced app
typora_app = FastMCP("typora")


@typora_app.tool()
async def open(
    file_path: Annotated[str, Field(description="Absolute path to the markdown file to open in Typora")],
) -> Any:
    """Editor Induction Tool

    Opens a specific markdown file in Typora for rich manual editing.
    """
    from advanced_memory.mcp.tools.typora_control import typora_control

    return await typora_control(operation="open_file", file_path=file_path)


@typora_app.tool()
async def save() -> Any:
    """Editor Persistence Tool

    Triggers the save operation in the active Typora instance to persist current changes.
    """
    from advanced_memory.mcp.tools.typora_control import typora_control

    return await typora_control(operation="save_file")


@typora_app.tool(task=True)
async def export(
    format: Annotated[Literal["pdf", "html", "docx", "odt"], Field(description="Target export format")],
    path: Annotated[str, Field(description="Absolute destination path for the exported file")],
    options: Annotated[dict | None, Field(description="Format-specific export parameters")] = None,
) -> Any:
    """Editor Synthesis Tool

    Leverages Typora's rendering engine to export the current document into professional formats.
    """
    from advanced_memory.mcp.tools.typora_control import typora_control

    return await typora_control(operation="export", format=format, output_path=path, options=options)


@typora_app.tool()
async def get_content() -> Any:
    """Editor Inspection Tool

    Reads the full markdown content of the document currently active in Typora.
    """
    from advanced_memory.mcp.tools.typora_control import typora_control

    return await typora_control(operation="get_content")


@typora_app.tool()
async def set_content(
    content: Annotated[str, Field(description="New markdown body to replace the current document")],
) -> Any:
    """Editor Modification Engine

    Replaces the entire content of the active Typora document with the provided markdown string.
    """
    from advanced_memory.mcp.tools.typora_control import typora_control

    return await typora_control(operation="set_content", content=content)


@typora_app.tool()
async def insert(
    text: Annotated[str, Field(description="Text or markdown to insert")],
    position: Annotated[str | None, Field(description="Target location anchor or 'current cursor'")] = None,
) -> Any:
    """Editor Mutation Tool

    Injects text at the current cursor position or a specified anchor within the active Typora document.
    """
    from advanced_memory.mcp.tools.typora_control import typora_control

    return await typora_control(operation="insert_text", text=text, position=position)


@typora_app.tool()
async def cursor() -> Any:
    """Editor Telemetry Tool

    Retrieves the current cursor position, selection range, and line/column metrics from Typora.
    """
    from advanced_memory.mcp.tools.typora_control import typora_control

    return await typora_control(operation="get_cursor")


@typora_app.tool()
async def analyze() -> Any:
    """Editor Intelligence Tool

    Performs structural and metric analysis on the active document, reporting headings, links, and health.
    """
    from advanced_memory.mcp.tools.typora_control import typora_control

    return await typora_control(operation="content_analysis")
