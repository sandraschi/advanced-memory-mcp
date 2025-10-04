"""Import Manager portmanteau tool for Advanced Memory MCP server.

This tool consolidates all import operations: obsidian, joplin, notion, evernote, archive, canvas.
It reduces the number of MCP tools while maintaining full functionality.
"""

from typing import Optional, List, Dict, Any

from loguru import logger

from advanced_memory.mcp.server import mcp


@mcp.tool(
    description="""Comprehensive import management tool for Advanced Memory knowledge base.

This portmanteau tool consolidates all import operations into a single interface,
reducing MCP tool count while maintaining full functionality for Cursor IDE compatibility.

SUPPORTED OPERATIONS:
- **obsidian**: Import complete Obsidian vaults with full feature preservation
- **joplin**: Import Joplin knowledge bases with metadata preservation
- **notion**: Import Notion workspaces and pages with intelligent conversion
- **evernote**: Import Evernote ENEX files with complete content preservation
- **archive**: Import complete Advanced Memory archive from migration/backup
- **canvas**: Import Obsidian Canvas visual mind maps as structured knowledge

IMPORT FEATURES:
- Full metadata preservation (tags, timestamps, relationships)
- Intelligent content conversion (HTML to Markdown, etc.)
- Folder hierarchy preservation and conversion
- Entity relationship extraction and linking
- Attachment and media file handling
- Cross-platform compatibility

PARAMETERS:
- operation (str, REQUIRED): Import operation type (obsidian, joplin, notion, evernote, archive, canvas)
- source_path (str, REQUIRED): Path to source files (vault, export, archive, etc.)
- destination_folder (str, default="imported/[type]"): Advanced Memory folder for imported content
- preserve_structure (bool, default=True): Maintain original folder hierarchy
- convert_links (bool, default=True): Convert internal links to entity references
- include_attachments (bool, default=True): Import images and media files
- skip_existing (bool, default=True): Skip notes that already exist
- create_missing_files (bool, default=False): Create placeholder notes for missing references
- restore_mode (str, default="overwrite"): Archive restore mode (overwrite, merge, skip_existing)
- backup_existing (bool, default=True): Backup current data before restore
- project (str, optional): Target Advanced Memory project

USAGE EXAMPLES:
Obsidian import: adn_import("obsidian", source_path="/path/to/vault", destination_folder="imported/obsidian")
Joplin import: adn_import("joplin", source_path="/path/to/export", destination_folder="imported/joplin")
Notion import: adn_import("notion", source_path="Notion-Export.zip", destination_folder="imported/notion")
Evernote import: adn_import("evernote", source_path="notes.enex", destination_folder="imported/evernote")
Archive import: adn_import("archive", source_path="backup.zip", restore_mode="merge")
Canvas import: adn_import("canvas", source_path="mindmap.canvas", destination_folder="imported/canvases")

RETURNS:
Operation-specific results with import details, file counts, and processing information.

NOTE: This tool provides all import functionality in a single interface for better MCP client compatibility.""",
)
async def adn_import(
    operation: str,
    source_path: str,
    destination_folder: Optional[str] = None,
    preserve_structure: bool = True,
    convert_links: bool = True,
    include_attachments: bool = True,
    skip_existing: bool = True,
    create_missing_files: bool = False,
    restore_mode: str = "overwrite",
    backup_existing: bool = True,
    project: Optional[str] = None,
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
        return await _obsidian_import(source_path, destination_folder, preserve_structure, convert_links, include_attachments, skip_existing, project)
    elif operation == "joplin":
        return await _joplin_import(source_path, destination_folder, preserve_structure, convert_links, skip_existing, project)
    elif operation == "notion":
        return await _notion_import(source_path, destination_folder, preserve_structure, project)
    elif operation == "evernote":
        return await _evernote_import(source_path, destination_folder, preserve_structure, include_attachments, project)
    elif operation == "archive":
        return await _archive_import(source_path, restore_mode, backup_existing, project)
    elif operation == "canvas":
        return await _canvas_import(source_path, destination_folder, create_missing_files, project)
    else:
        return f"# Error\n\nInvalid operation '{operation}'. Supported operations: obsidian, joplin, notion, evernote, archive, canvas"


async def _obsidian_import(source_path: str, destination_folder: str, preserve_structure: bool, convert_links: bool, include_attachments: bool, skip_existing: bool, project: Optional[str]) -> str:
    """Handle Obsidian import operation."""
    from advanced_memory.mcp.tools.load_obsidian_vault import load_obsidian_vault
    return await load_obsidian_vault(source_path, destination_folder, preserve_structure, convert_links, include_attachments, skip_existing, project)


async def _joplin_import(source_path: str, destination_folder: str, preserve_structure: bool, convert_links: bool, skip_existing: bool, project: Optional[str]) -> str:
    """Handle Joplin import operation."""
    from advanced_memory.mcp.tools.load_joplin_vault import load_joplin_vault
    return await load_joplin_vault(source_path, destination_folder, preserve_structure, convert_links, skip_existing, project)


async def _notion_import(source_path: str, destination_folder: str, preserve_structure: bool, project: Optional[str]) -> str:
    """Handle Notion import operation."""
    from advanced_memory.mcp.tools.load_notion_export import load_notion_export
    return await load_notion_export(source_path, destination_folder, preserve_structure, project)


async def _evernote_import(source_path: str, destination_folder: str, preserve_structure: bool, include_attachments: bool, project: Optional[str]) -> str:
    """Handle Evernote import operation."""
    from advanced_memory.mcp.tools.load_evernote_export import load_evernote_export
    return await load_evernote_export(source_path, destination_folder, preserve_structure, include_attachments, project)


async def _archive_import(source_path: str, restore_mode: str, backup_existing: bool, project: Optional[str]) -> str:
    """Handle archive import operation."""
    from advanced_memory.mcp.tools.import_from_archive import import_from_archive
    return await import_from_archive(source_path, restore_mode, backup_existing, False, project)


async def _canvas_import(source_path: str, destination_folder: str, create_missing_files: bool, project: Optional[str]) -> str:
    """Handle Canvas import operation."""
    from advanced_memory.mcp.tools.load_obsidian_canvas import load_obsidian_canvas
    return await load_obsidian_canvas(source_path, destination_folder, create_missing_files, project)
