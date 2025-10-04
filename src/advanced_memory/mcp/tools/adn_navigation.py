"""Navigation Manager portmanteau tool for Advanced Memory MCP server.

This tool consolidates navigation operations: build_context, recent_activity, list_directory, status, sync_status.
It reduces the number of MCP tools while maintaining full functionality.
"""

from typing import Optional, List, Dict, Any

from loguru import logger

from advanced_memory.mcp.server import mcp


@mcp.tool(
    description="""Comprehensive navigation management tool for Advanced Memory knowledge base.

This portmanteau tool consolidates all navigation operations into a single interface,
reducing MCP tool count while maintaining full functionality for Cursor IDE compatibility.

SUPPORTED OPERATIONS:
- **build_context**: Navigate the knowledge graph via memory:// URLs for conversation continuity
- **recent_activity**: Get recently updated information with specified timeframe
- **list_directory**: List directory contents with filtering and depth control
- **status**: Comprehensive system status and diagnostic monitoring
- **sync_status**: Monitor file synchronization status and background operations

NAVIGATION FEATURES:
- Knowledge graph traversal with relationship exploration
- Recent activity filtering by type and timeframe
- Directory listing with recursive depth control
- System health monitoring and diagnostics
- File synchronization status tracking
- Background process monitoring

PARAMETERS:
- operation (str, REQUIRED): Navigation operation type (build_context, recent_activity, list_directory, status, sync_status)
- url (str, optional): Memory URL or pattern for context building
- dir_name (str, default="/"): Directory path to list
- depth (int, default=1): Relationship exploration depth or directory recursion depth
- timeframe (str, default="7d"): Time window for activity filtering
- page (int, default=1): Pagination page for results
- page_size (int, default=10): Results per page
- max_related (int, default=10): Maximum related items to include
- file_name_glob (str, optional): Glob pattern for file filtering
- type_filter (str, optional): Type filter for recent activity
- level (str, default="basic"): Status detail level (basic/intermediate/advanced/diagnostic)
- focus (str, optional): Specific area to focus on (sync/tools/system/projects)
- project (str, optional): Target project for operations

USAGE EXAMPLES:
Build context: adn_navigation("build_context", url="memory://projects/ai", depth=2, timeframe="7d")
Recent activity: adn_navigation("recent_activity", timeframe="today", type_filter="notes")
List directory: adn_navigation("list_directory", dir_name="/projects", depth=2)
System status: adn_navigation("status", level="intermediate", focus="sync")
Sync status: adn_navigation("sync_status", project="work")

RETURNS:
Operation-specific results with navigation details, activity information, and system status.

NOTE: This tool provides all navigation functionality in a single interface for better MCP client compatibility.""",
)
async def adn_navigation(
    operation: str,
    url: Optional[str] = None,
    dir_name: str = "/",
    depth: int = 1,
    timeframe: str = "7d",
    page: int = 1,
    page_size: int = 10,
    max_related: int = 10,
    file_name_glob: Optional[str] = None,
    type_filter: Optional[str] = "",
    level: str = "basic",
    focus: Optional[str] = None,
    project: Optional[str] = None,
) -> str:
    """Comprehensive navigation management for Advanced Memory knowledge base.

    This portmanteau tool consolidates all navigation operations:
    - build_context: Navigate the knowledge graph via memory:// URLs
    - recent_activity: Get recently updated information
    - list_directory: List directory contents with filtering
    - status: System status and diagnostic monitoring
    - sync_status: File synchronization status tracking

    Args:
        operation: The navigation operation to perform
        url: Memory URL or pattern for context building
        dir_name: Directory path to list
        depth: Relationship exploration depth or directory recursion depth
        timeframe: Time window for activity filtering
        page: Pagination page for results
        page_size: Results per page
        max_related: Maximum related items to include
        file_name_glob: Glob pattern for file filtering
        type_filter: Type filter for recent activity
        level: Status detail level
        focus: Specific area to focus on
        project: Optional project name

    Returns:
        Operation-specific result with navigation details and system information

    Examples:
        # Build context from memory URL
        adn_navigation("build_context", url="memory://projects/ai", depth=2, timeframe="7d")

        # Get recent activity
        adn_navigation("recent_activity", timeframe="today", type_filter="notes")

        # List directory contents
        adn_navigation("list_directory", dir_name="/projects", depth=2)

        # Check system status
        adn_navigation("status", level="intermediate", focus="sync")

        # Monitor sync status
        adn_navigation("sync_status", project="work")
    """
    logger.info(f"MCP tool call tool=adn_navigation operation={operation}")

    # Route to appropriate operation
    if operation == "build_context":
        return await _build_context_operation(url, depth, timeframe, page, page_size, max_related, project)
    elif operation == "recent_activity":
        return await _recent_activity_operation(type_filter, depth, timeframe, page, page_size, max_related, project)
    elif operation == "list_directory":
        return await _list_directory_operation(dir_name, depth, file_name_glob, project)
    elif operation == "status":
        return await _status_operation(level, focus)
    elif operation == "sync_status":
        return await _sync_status_operation(project)
    else:
        return f"# Error\n\nInvalid operation '{operation}'. Supported operations: build_context, recent_activity, list_directory, status, sync_status"


async def _build_context_operation(url: Optional[str], depth: int, timeframe: str, page: int, page_size: int, max_related: int, project: Optional[str]) -> str:
    """Handle build context operation."""
    if not url:
        return "# Error\n\nBuild context requires: url parameter"
    
    from advanced_memory.mcp.tools.build_context import build_context
    return await build_context(url, depth, timeframe, page, page_size, max_related, project)


async def _recent_activity_operation(type_filter: Optional[str], depth: int, timeframe: str, page: int, page_size: int, max_related: int, project: Optional[str]) -> str:
    """Handle recent activity operation."""
    from advanced_memory.mcp.tools.recent_activity import recent_activity
    return await recent_activity(type_filter, depth, timeframe, page, page_size, max_related, project)


async def _list_directory_operation(dir_name: str, depth: int, file_name_glob: Optional[str], project: Optional[str]) -> str:
    """Handle list directory operation."""
    from advanced_memory.mcp.tools.list_directory import list_directory
    return await list_directory(dir_name, depth, file_name_glob, project)


async def _status_operation(level: str, focus: Optional[str]) -> str:
    """Handle status operation."""
    from advanced_memory.mcp.tools.status import status
    return await status(level, focus)


async def _sync_status_operation(project: Optional[str]) -> str:
    """Handle sync status operation."""
    from advanced_memory.mcp.tools.sync_status import sync_status
    return await sync_status(project)
