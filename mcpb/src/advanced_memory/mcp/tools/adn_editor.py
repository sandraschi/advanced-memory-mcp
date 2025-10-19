"""Editor Manager portmanteau tool for Advanced Memory MCP server.

This tool consolidates editor operations: notepadpp_edit, notepadpp_import, typora_control, canvas_create, read_content.
It reduces the number of MCP tools while maintaining full functionality.
"""

from typing import Any

from loguru import logger

from advanced_memory.mcp.mcp_instance import mcp


@mcp.tool
async def adn_editor(
    operation: str,
    note_identifier: str | None = None,
    workspace_path: str | None = None,
    create_backup: bool = True,
    keep_workspace: bool = False,
    typora_operation: str | None = None,
    typora_format: str | None = None,
    typora_output_path: str | None = None,
    typora_text: str | None = None,
    typora_file_path: str | None = None,
    typora_content: str | None = None,
    typora_position: str | None = None,
    typora_find_text: str | None = None,
    typora_replace_text: str | None = None,
    typora_files: list[str] | None = None,
    typora_theme: str | None = None,
    typora_visible: bool | None = None,
    typora_template_name: str | None = None,
    typora_options: dict[str, Any] | None = None,
    nodes: list[dict[str, Any]] | None = None,
    edges: list[dict[str, Any]] | None = None,
    canvas_title: str | None = None,
    canvas_folder: str | None = None,
    path: str | None = None,
    project: str | None = None,
) -> str:
    """Comprehensive editor management tool for Advanced Memory knowledge base.

    This portmanteau tool consolidates all editor operations into a single interface,
    reducing MCP tool count while maintaining full functionality for Cursor IDE compatibility.

    SUPPORTED OPERATIONS:
    - notepadpp_edit: Export notes to Notepad++ for professional markdown editing
    - notepadpp_import: Import edited notes back from Notepad++ workspace
    - typora_control: Full Typora API control via json_rpc plugin
    - canvas_create: Create Obsidian canvas files for knowledge graph visualization
    - read_content: Read raw file content (text, images, binaries) without processing

    EDITOR FEATURES:
    - FREE Notepad++ integration with syntax highlighting
    - Professional markdown editing with full feature set
    - Typora automation via plugins (export, import, theme control)
    - Visual knowledge graph creation with Obsidian Canvas
    - Raw file content access for images and binaries
    - Cross-platform compatibility and backup support

    Args:
        operation: The editor operation to perform
        note_identifier: Note title or permalink for Notepad++ operations
        workspace_path: Workspace directory for Notepad++ operations
        create_backup: Create backup of original content
        keep_workspace: Keep workspace files after import
        typora_operation: Typora operation type
        typora_format: Output format for Typora operations
        typora_output_path: Output path for Typora operations
        typora_text: Text content for Typora operations
        typora_file_path: File path for Typora operations
        typora_content: Content for Typora operations
        typora_position: Position for Typora operations
        typora_find_text: Find text for Typora operations
        typora_replace_text: Replace text for Typora operations
        typora_files: File list for Typora operations
        typora_theme: Theme for Typora operations
        typora_visible: Visibility for Typora operations
        typora_template_name: Template name for Typora operations
        typora_options: Additional options for Typora operations
        nodes: Canvas nodes for canvas creation
        edges: Canvas edges for canvas creation
        canvas_title: Title for canvas creation
        canvas_folder: Folder for canvas creation
        path: File path for read_content operation
        project: Optional project name

    Returns:
        Operation-specific result with editing details and file information

    Examples:
        # Edit note in Notepad++
        adn_editor("notepadpp_edit", note_identifier="Meeting Notes", workspace_path="temp/")

        # Import edited note from Notepad++
        adn_editor("notepadpp_import", note_identifier="Meeting Notes", keep_workspace=False)

        # Export from Typora
        adn_editor("typora_control", typora_operation="export", typora_format="pdf", typora_output_path="/exports/doc.pdf")

        # Create Obsidian canvas
        adn_editor("canvas_create", nodes=[...], edges=[...], canvas_title="Project Overview", canvas_folder="visuals")

        # Read image content
        adn_editor("read_content", path="images/diagram.png")
    """
    logger.info(f"MCP tool call tool=adn_editor operation={operation}")

    # Route to appropriate operation
    if operation == "notepadpp_edit":
        return await _notepadpp_edit_operation(note_identifier, workspace_path, create_backup)
    elif operation == "notepadpp_import":
        return await _notepadpp_import_operation(note_identifier, workspace_path, keep_workspace)
    elif operation == "typora_control":
        return await _typora_control_operation(
            typora_operation,
            typora_format,
            typora_output_path,
            typora_text,
            typora_file_path,
            typora_content,
            typora_position,
            typora_find_text,
            typora_replace_text,
            typora_files,
            typora_theme,
            typora_visible,
            typora_template_name,
            typora_options,
        )
    elif operation == "canvas_create":
        return await _canvas_create_operation(nodes, edges, canvas_title, canvas_folder, project)
    elif operation == "read_content":
        return await _read_content_operation(path, project)
    else:
        return f"# Error\n\nInvalid operation '{operation}'. Supported operations: notepadpp_edit, notepadpp_import, typora_control, canvas_create, read_content"


async def _notepadpp_edit_operation(
    note_identifier: str | None, workspace_path: str | None, create_backup: bool
) -> str:
    """Handle Notepad++ edit operation."""
    if not note_identifier:
        return "# Error\n\nNotepad++ edit requires: note_identifier parameter"

    from advanced_memory.mcp.tools.edit_in_notepadpp import edit_in_notepadpp

    return await edit_in_notepadpp(note_identifier, workspace_path, create_backup)


async def _notepadpp_import_operation(
    note_identifier: str | None, workspace_path: str | None, keep_workspace: bool
) -> str:
    """Handle Notepad++ import operation."""
    if not note_identifier:
        return "# Error\n\nNotepad++ import requires: note_identifier parameter"

    from advanced_memory.mcp.tools.import_from_notepadpp import import_from_notepadpp

    return await import_from_notepadpp(note_identifier, workspace_path, keep_workspace)


async def _typora_control_operation(
    typora_operation: str | None,
    typora_format: str | None,
    typora_output_path: str | None,
    typora_text: str | None,
    typora_file_path: str | None,
    typora_content: str | None,
    typora_position: str | None,
    typora_find_text: str | None,
    typora_replace_text: str | None,
    typora_files: list[str] | None,
    typora_theme: str | None,
    typora_visible: bool | None,
    typora_template_name: str | None,
    typora_options: dict[str, Any] | None,
) -> str:
    """Handle Typora control operation."""
    if not typora_operation:
        return "# Error\n\nTypora control requires: typora_operation parameter"

    from advanced_memory.mcp.tools.typora_control import typora_control

    return await typora_control(
        typora_operation,
        typora_format,
        typora_output_path,
        typora_text,
        typora_file_path,
        typora_content,
        typora_position,
        typora_find_text,
        typora_replace_text,
        typora_files,
        typora_theme,
        typora_visible,
        typora_template_name,
        typora_options,
    )


async def _canvas_create_operation(
    nodes: list[dict[str, Any]] | None,
    edges: list[dict[str, Any]] | None,
    canvas_title: str | None,
    canvas_folder: str | None,
    project: str | None,
) -> str:
    """Handle canvas create operation."""
    if not nodes or not edges or not canvas_title or not canvas_folder:
        return "# Error\n\nCanvas create requires: nodes, edges, canvas_title, canvas_folder parameters"

    from advanced_memory.mcp.tools.canvas import canvas

    return await canvas(nodes, edges, canvas_title, canvas_folder, project)


async def _read_content_operation(path: str | None, project: str | None) -> str:
    """Handle read content operation."""
    if not path:
        return "# Error\n\nRead content requires: path parameter"

    from advanced_memory.mcp.tools.read_content import read_content

    return await read_content(path, project)
