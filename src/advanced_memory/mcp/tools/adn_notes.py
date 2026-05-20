"""Notes Manager portmanteau tool for Advanced Memory MCP server.

This tool consolidates note operations: write, read, edit, delete, move, quick, daily.
It reduces the number of MCP tools while maintaining full functionality.
"""

from typing import Any

from loguru import logger

from advanced_memory.mcp.mcp_instance import mcp
from advanced_memory.mcp.models.portmanteau import NotesOperation


@mcp.tool(name="adn_notes")
async def adn_notes(op: NotesOperation) -> Any:
    """
    Comprehensive note management for the Advanced Memory knowledge base.

    This tool consolidates all primary note operations into a single entry point,
    providing a unified interface for writing, reading, editing, and organizing
    markdown notes with semantic metadata.

    ---------------------------------------------------------------------------
    [RATIONALE]
    By unifying note operations, we reduce the total tool count to stay within
    IDE limits (Cursor/Antigravity) while ensuring that all note mutations
    follow consistent semantic rules, tagging patterns, and folder structures.

    ---------------------------------------------------------------------------
    [SUPPORTED OPERATIONS]
    - write: Create a new markdown note with metadata (Observations/Relations).
    - read: Retrieve the full content of a note by title or permalink.
    - edit: Perform surgical modifications (append, prepend, find-replace).
    - delete: Permanently remove a note from the active project.
    - move: Reorganize notes by changing their relative folder path.
    - quick: Capture rapid, off-the-cuff thoughts with auto-titling.
    - daily: Append logs to today's periodic note (chronological stream).

    ---------------------------------------------------------------------------
    [PARAMETERS]
    - operation (str): The task to perform (write, read, edit, delete, move, quick, daily).
    - identifier (str, optional): Title, permalink, or relative path of the note.
    - content (str, optional): Markdown body content or replacement text.
    - title (str, optional): Unique title for a new note (used in 'write').
    - folder (str, optional): Target vault folder (e.g., 'projects', 'meetings').
    - tags (str/list, optional): Categorization metadata.
    - mode (str, optional): Edit strategy (append, prepend, replace_section, find_replace).
    - section (str, optional): Target header for 'replace_section' edits.
    - find_text (str, optional): String to locate for 'find_replace' edits.
    - destination (str, optional): New folder path for 'move' operations.
    - project (str, optional): Override the current active project context.

    ---------------------------------------------------------------------------
    [EXAMPLES]
    ```python
    # Rapidly capture a thought
    adn_notes(operation="quick", content="Idea: Use quantum-resistant encryption for the vault.")

    # Surgically edit a specific section
    adn_notes(
        operation="edit",
        identifier="Project Glenn",
        mode="replace_section",
        section="Current Status",
        content="## Current Status\nRefactoring portmanteau tools for FastMCP 3.2 compliance."
    )
    ```
    """
    operation = op.operation
    logger.info(f"MCP tool call tool=adn_notes operation={operation}")

    from advanced_memory.mcp.tools.content_manager import _dispatch_content_operations

    if operation == "write":
        return await _dispatch_content_operations(
            operation="write",
            identifier=op.title,
            content=op.content,
            folder=op.folder,
            tags=op.tags,
            project=op.project,
            mcp_tool="adn_notes:write"
        )
    elif operation == "read":
        return await _dispatch_content_operations(
            operation="read",
            identifier=op.identifier,
            page=op.page,
            page_size=op.page_size,
            project=op.project,
            mcp_tool="adn_notes:read"
        )
    elif operation == "edit":
        return await _dispatch_content_operations(
            operation="edit",
            identifier=op.identifier,
            edit_operation=op.mode,
            content=op.content,
            section=op.section,
            find_text=op.find_text,
            project=op.project,
            mcp_tool="adn_notes:edit"
        )
    elif operation == "delete":
        return await _dispatch_content_operations(
            operation="delete",
            identifier=op.identifier,
            project=op.project,
            mcp_tool="adn_notes:delete"
        )
    elif operation == "move":
        return await _dispatch_content_operations(
            operation="move",
            identifier=op.identifier,
            destination_path=op.destination,
            project=op.project,
            mcp_tool="adn_notes:move"
        )
    elif operation == "quick":
        return await _dispatch_content_operations(
            operation="quick",
            content=op.content,
            tags=op.tags,
            project=op.project,
            mcp_tool="adn_notes:quick"
        )
    elif operation == "daily":
        return await _dispatch_content_operations(
            operation="daily",
            content=op.content,
            tags=op.tags,
            project=op.project,
            mcp_tool="adn_notes:daily"
        )
    else:
        return f"Error: Unsupported operation {operation}"
