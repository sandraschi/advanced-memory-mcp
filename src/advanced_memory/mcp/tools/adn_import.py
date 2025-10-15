"""Import Manager portmanteau tool for Advanced Memory MCP server.

This tool consolidates all import operations: obsidian, joplin, notion, evernote, archive, canvas.
It reduces the number of MCP tools while maintaining full functionality.
"""

from loguru import logger

from advanced_memory.mcp.mcp_instance import mcp


@mcp.tool
async def adn_import(
    operation: str,
    source_path: str,
    destination_folder: str | None = None,
    preserve_structure: bool = True,
    convert_links: bool = True,
    include_attachments: bool = True,
    skip_existing: bool = True,
    create_missing_files: bool = False,
    restore_mode: str = "overwrite",
    backup_existing: bool = True,
    project: str | None = None,
) -> str:
    """Comprehensive import management for Advanced Memory knowledge base.

    This portmanteau tool consolidates all import operations:
    - obsidian: Import complete Obsidian vaults
    - joplin: Import Joplin knowledge bases
    - notion: Import Notion workspaces
    - evernote: Import Evernote ENEX files
    - archive: Import complete system archive
    - canvas: Import Obsidian Canvas files

    Args:
        operation: The import operation to perform
        source_path: Path to source files
        destination_folder: Advanced Memory folder for imported content
        preserve_structure: Maintain original folder hierarchy
        convert_links: Convert internal links to entity references
        include_attachments: Import images and media files
        skip_existing: Skip notes that already exist
        create_missing_files: Create placeholder notes for missing references
        restore_mode: Archive restore mode
        backup_existing: Backup current data before restore
        project: Optional project name

    Returns:
        Operation-specific result with import details and file counts

    Examples:
        # Import Obsidian vault
        adn_import("obsidian", source_path="/path/to/vault", destination_folder="imported/obsidian")

        # Import Joplin export
        adn_import("joplin", source_path="/path/to/export", destination_folder="imported/joplin")

        # Import Notion workspace
        adn_import("notion", source_path="Notion-Export.zip", destination_folder="imported/notion")

        # Import from archive
        adn_import("archive", source_path="backup.zip", restore_mode="merge")
    """
    logger.info(f"MCP tool call tool=adn_import operation={operation} source_path={source_path}")

    # Set default destination folder based on operation
    if not destination_folder:
        destination_folder = f"imported/{operation}"

    # Route to appropriate operation
    if operation == "obsidian":
        return await _obsidian_import(
            source_path,
            destination_folder,
            preserve_structure,
            convert_links,
            include_attachments,
            skip_existing,
            project,
        )
    elif operation == "joplin":
        return await _joplin_import(
            source_path,
            destination_folder,
            preserve_structure,
            convert_links,
            skip_existing,
            project,
        )
    elif operation == "notion":
        return await _notion_import(source_path, destination_folder, preserve_structure, project)
    elif operation == "evernote":
        return await _evernote_import(
            source_path, destination_folder, preserve_structure, include_attachments, project
        )
    elif operation == "archive":
        return await _archive_import(source_path, restore_mode, backup_existing, project)
    elif operation == "canvas":
        return await _canvas_import(source_path, destination_folder, create_missing_files, project)
    else:
        return f"# Error\n\nInvalid operation '{operation}'. Supported operations: obsidian, joplin, notion, evernote, archive, canvas"


async def _obsidian_import(
    source_path: str,
    destination_folder: str,
    preserve_structure: bool,
    convert_links: bool,
    include_attachments: bool,
    skip_existing: bool,
    project: str | None,
) -> str:
    """Handle Obsidian import operation."""
    from advanced_memory.mcp.tools.load_obsidian_vault import load_obsidian_vault

    return await load_obsidian_vault(
        source_path,
        destination_folder,
        preserve_structure,
        convert_links,
        include_attachments,
        skip_existing,
        project,
    )  # type: ignore[operator,no-any-return]


async def _joplin_import(
    source_path: str,
    destination_folder: str,
    preserve_structure: bool,
    convert_links: bool,
    skip_existing: bool,
    project: str | None,
) -> str:
    """Handle Joplin import operation."""
    from advanced_memory.mcp.tools.load_joplin_vault import load_joplin_vault

    return await load_joplin_vault(
        source_path, destination_folder, preserve_structure, convert_links, skip_existing, project
    )  # type: ignore[operator,no-any-return]


async def _notion_import(
    source_path: str, destination_folder: str, preserve_structure: bool, project: str | None
) -> str:
    """Handle Notion import operation."""
    from advanced_memory.mcp.tools.load_notion_export import load_notion_export

    return await load_notion_export(source_path, destination_folder, preserve_structure, project)  # type: ignore[operator,no-any-return]


async def _evernote_import(
    source_path: str,
    destination_folder: str,
    preserve_structure: bool,
    include_attachments: bool,
    project: str | None,
) -> str:
    """Handle Evernote import operation."""
    from advanced_memory.mcp.tools.load_evernote_export import load_evernote_export

    return await load_evernote_export(
        source_path, destination_folder, preserve_structure, include_attachments, project
    )  # type: ignore[operator,no-any-return]


async def _archive_import(
    source_path: str, restore_mode: str, backup_existing: bool, project: str | None
) -> str:
    """Handle archive import operation."""
    from advanced_memory.mcp.tools.import_from_archive import import_from_archive

    return await import_from_archive(source_path, restore_mode, backup_existing, False, project)  # type: ignore[operator,no-any-return]


async def _canvas_import(
    source_path: str, destination_folder: str, create_missing_files: bool, project: str | None
) -> str:
    """Handle Canvas import operation."""
    return f"[UNICODE] **Canvas Import**\n\nCanvas import functionality requires the full load_canvas tool.\n\n**Requested**: {source_path} → {destination_folder}\n**Create missing files**: {create_missing_files}\n\nUse the individual load_canvas tool for complete functionality."
