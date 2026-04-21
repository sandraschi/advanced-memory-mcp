"""Inbox namespaced app for Advanced Memory MCP.

Decomposed from the legacy adn_inbox portmanteau.
Follows FastMCP 3.2 GA Managed Namespace standards.
"""

from typing import Annotated, Any

from fastmcp import FastMCP
from pydantic import Field

# Initialize the namespaced app
inbox_app = FastMCP("inbox")


@inbox_app.tool()
async def status() -> Any:
    """Inbox Diagnostic Tool
    
    Provides a real-time overview of pending documents, supported formats, and directory health.
    """
    from advanced_memory.mcp.tools.adn_inbox import _status_operation
    return await _status_operation(ctx=None)


@inbox_app.tool(task=True)
async def process(
    file_name: Annotated[str | None, Field(description="Optional specific file to process (relative to inbox root)")] = None,
) -> Any:
    """Ingestion Engine
    
    Batch converts and imports pending documents (PDF, DOCX, HTML) into the active project.
    """
    from advanced_memory.mcp.tools.adn_inbox import _process_operation
    return await _process_operation(file_name, ctx=None)


@inbox_app.tool()
async def info() -> Any:
    """Infrastructure Status Tool
    
    Returns detailed configuration data, dependency versions (Pandoc/pypdf), and system paths.
    """
    from advanced_memory.mcp.tools.adn_inbox import _info_operation
    return await _info_operation(ctx=None)


@inbox_app.tool()
async def watch() -> Any:
    """Real-time Monitor Status
    
    Check background watcher availability and active ingestion monitoring state.
    """
    from advanced_memory.mcp.tools.adn_inbox import _watch_operation
    return await _watch_operation(ctx=None)
