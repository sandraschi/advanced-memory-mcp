"""Notes namespaced app for Advanced Memory MCP.

Decomposed from the legacy adn_notes and adn_content portmanteaus.
Follows FastMCP 3.2 GA Managed Namespace standards.
"""

from typing import Annotated, Any, Literal

from fastmcp import FastMCP
from pydantic import Field

# Initialize the namespaced app
notes_app = FastMCP("notes")

TagType = list[str] | str | None


@notes_app.tool(task=True)
async def write(
    title: Annotated[str, Field(description="Unique title for the note")],
    content: Annotated[str, Field(description="Markdown body content")],
    folder: Annotated[str | None, Field(description="Target vault folder (e.g., 'projects', 'meetings')")] = "inbox",
    tags: Annotated[TagType, Field(description="Tags string or list")] = None,
    project: Annotated[str | None, Field(description="Project context override")] = None,
) -> Any:
    """Note Creation Engine
    
    Persists a new markdown note to the knowledge base with semantic metadata.
    """
    from advanced_memory.mcp.tools.content_manager import _dispatch_content_operations
    return await _dispatch_content_operations(
        operation="write",
        identifier=title,
        content=content,
        folder=folder,
        tags=tags,
        project=project,
        mcp_tool="notes:write"
    )


@notes_app.tool()
async def read(
    identifier: Annotated[str, Field(description="Title, permalink, or memory:// URL to retrieve")],
    page: Annotated[int, Field(description="Page number for paginated view", ge=1)] = 1,
    page_size: Annotated[int, Field(description="Lines or items per page", ge=1, le=100)] = 20,
    project: Annotated[str | None, Field(description="Project context override")] = None,
) -> Any:
    """Note Retrieval Tool
    
    Reads the content of a specific note from the knowledge base.
    """
    from advanced_memory.mcp.tools.content_manager import _dispatch_content_operations
    return await _dispatch_content_operations(
        operation="read",
        identifier=identifier,
        page=page,
        page_size=page_size,
        project=project,
        mcp_tool="notes:read"
    )


@notes_app.tool(task=True)
async def edit(
    identifier: Annotated[str, Field(description="Title or permalink of the note to modify")],
    mode: Annotated[Literal["append", "prepend", "replace_section", "find_replace"], Field(description="Mutation strategy")],
    content: Annotated[str, Field(description="New content or replacement text")],
    section: Annotated[str | None, Field(description="Target section header for replace_section")] = None,
    find_text: Annotated[str | None, Field(description="Text to search for in find_replace mode")] = None,
    project: Annotated[str | None, Field(description="Project context override")] = None,
) -> Any:
    """Note Mutation Engine
    
    Applies surgical edits to existing notes using various strategies like section replacement or find-replace.
    """
    from advanced_memory.mcp.tools.content_manager import _dispatch_content_operations
    return await _dispatch_content_operations(
        operation="edit",
        identifier=identifier,
        edit_operation=mode,
        content=content,
        section=section,
        find_text=find_text,
        project=project,
        mcp_tool="notes:edit"
    )


@notes_app.tool(task=True)
async def delete(
    identifier: Annotated[str, Field(description="Note title or permalink to permanently remove")],
    project: Annotated[str | None, Field(description="Project context override")] = None,
) -> Any:
    """Note Deletion Tool
    
    Permanently removes a note from the knowledge base. Use with caution.
    """
    from advanced_memory.mcp.tools.content_manager import _dispatch_content_operations
    return await _dispatch_content_operations(
        operation="delete",
        identifier=identifier,
        project=project,
        mcp_tool="notes:delete"
    )


@notes_app.tool(task=True)
async def move(
    identifier: Annotated[str, Field(description="Note title or permalink to move")],
    destination: Annotated[str, Field(description="New folder path relative to project root")],
    project: Annotated[str | None, Field(description="Project context override")] = None,
) -> Any:
    """Vault Reorganization Tool
    
    Relocates a note to a different folder within the project structure.
    """
    from advanced_memory.mcp.tools.content_manager import _dispatch_content_operations
    return await _dispatch_content_operations(
        operation="move",
        identifier=identifier,
        destination_path=destination,
        project=project,
        mcp_tool="notes:move"
    )


@notes_app.tool(task=True)
async def quick(
    content: Annotated[str, Field(description="Thought or content to capture")],
    tags: Annotated[TagType, Field(description="Optional tags")] = None,
    project: Annotated[str | None, Field(description="Project context override")] = None,
) -> Any:
    """Rapid Ingestion Engine
    
    Low-friction capture tool that auto-generates titles and metadata for off-the-cuff insights.
    """
    from advanced_memory.mcp.tools.content_manager import _dispatch_content_operations
    return await _dispatch_content_operations(
        operation="quick",
        content=content,
        tags=tags,
        project=project,
        mcp_tool="notes:quick"
    )


@notes_app.tool(task=True)
async def daily(
    content: Annotated[str, Field(description="Entry content for today's log")],
    tags: Annotated[TagType, Field(description="Optional tags")] = "daily-log",
    project: Annotated[str | None, Field(description="Project context override")] = None,
) -> Any:
    """Chronological Logging Tool
    
    Appends content to the daily periodic note, maintaining a temporal stream of consciousness.
    """
    from advanced_memory.mcp.tools.content_manager import _dispatch_content_operations
    return await _dispatch_content_operations(
        operation="daily",
        content=content,
        tags=tags,
        project=project,
        mcp_tool="notes:daily"
    )
