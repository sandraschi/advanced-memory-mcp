"""Portmanteau tool for import and export operations.

PORTMANTEAU PATTERN RATIONALE: Consolidates 20+ import/export operations across
different formats (Obsidian, Notion, Joplin, Evernote, HTML, PDF, etc.) into a single
tool with format and operation parameters. This maintains format-specific functionality
while reducing tool count significantly.
"""

from typing import Annotated, Literal

from loguru import logger
from pydantic import Field

from advanced_memory.mcp.mcp_instance import mcp
from advanced_memory.mcp.tools.utils import build_error_response, build_success_response


@mcp.tool
async def adn_import_export(
    operation: Annotated[
        Literal["import", "export", "load", "search"],
        Field(description="Import/export operation type"),
    ],
    format: Annotated[
        Literal[
            "obsidian",
            "notion",
            "joplin",
            "evernote",
            "onenote",
            "html",
            "pdf",
            "pandoc",
            "docsify",
            "archive",
            "canvas",
        ],
        Field(description="Data format for operation"),
    ],
    path: Annotated[str | None, Field(description="File/directory path")] = None,
    query: Annotated[str | None, Field(description="Search query (for search operations)")] = None,
    destination: Annotated[str | None, Field(description="Export destination path")] = None,
    options: Annotated[dict | None, Field(description="Format-specific options")] = None,
) -> dict:
    """Unified portmanteau tool for all import and export operations.

    This tool consolidates all data import/export functionality across multiple formats:
    - External app imports (Obsidian, Notion, Joplin, Evernote, OneNote)
    - Export formats (HTML, PDF, Pandoc, Docsify)
    - Archive operations
    - Canvas loading
    - Format-specific search

    Args:
        operation: The import/export operation to perform
        format: Data format (obsidian, notion, joplin, evernote, html, pdf, etc.)
        path: Source file/directory path
        query: Search query for vault searches
        destination: Export destination path
        options: Format-specific configuration options

    Returns:
        Operation result with import/export data

    Examples:
        # Import Obsidian vault
        adn_import_export("import", "obsidian", path="/path/to/vault")

        # Import Notion export
        adn_import_export("import", "notion", path="/path/to/notion-export.html")

        # Export to HTML
        adn_import_export("export", "html", destination="/output/folder")

        # Export to PDF
        adn_import_export("export", "pdf", destination="/output/file.pdf")

        # Load Obsidian canvas
        adn_import_export("load", "canvas", path="/path/to/canvas.canvas")

        # Search Evernote vault
        adn_import_export("search", "evernote", query="machine learning")
    """
    try:
        options = options or {}

        if operation == "import":
            if not path:
                return build_error_response(
                    "VALIDATION_ERROR", "MISSING_PARAMETER", "Path required for import operations"
                )

            # Route to appropriate import tool based on format
            if format == "obsidian":
                from advanced_memory.mcp.tools.load_obsidian_vault import load_obsidian_vault

                result = await load_obsidian_vault.fn(path, **options)
            elif format == "notion":
                from advanced_memory.mcp.tools.load_notion_export import load_notion_export

                result = await load_notion_export.fn(path, **options)
            elif format == "joplin":
                from advanced_memory.mcp.tools.load_joplin_vault import load_joplin_vault

                result = await load_joplin_vault.fn(path, **options)
            elif format == "evernote":
                from advanced_memory.mcp.tools.load_evernote_export import load_evernote_export

                result = await load_evernote_export.fn(path, **options)
            elif format == "onenote":
                from advanced_memory.mcp.tools.load_onenote_html import load_onenote_html

                result = await load_onenote_html.fn(path, **options)
            elif format == "archive":
                from advanced_memory.mcp.tools.import_from_archive import import_from_archive

                result = await import_from_archive.fn(path, **options)
            else:
                return build_error_response(
                    "VALIDATION_ERROR", "VALIDATION_ERROR", f"Unsupported import format: {format}"
                )

            return build_success_response("import", result)

        elif operation == "export":
            if not destination:
                return build_error_response(
                    "VALIDATION_ERROR",
                    "MISSING_PARAMETER",
                    "Destination required for export operations",
                )

            # Route to appropriate export tool based on format
            if format == "html":
                from advanced_memory.mcp.tools.export_html_notes import export_html_notes

                result = await export_html_notes.fn(destination, **options)
            elif format == "pdf":
                # Choose appropriate PDF export based on options
                if options.get("combined", False):
                    from advanced_memory.mcp.tools.export_pdf_combined import export_pdf_combined

                    result = await export_pdf_combined.fn(destination, **options)
                else:
                    from advanced_memory.mcp.tools.export_pdf_native import export_pdf_native

                    result = await export_pdf_native.fn(destination, **options)
            elif format == "pandoc":
                from advanced_memory.mcp.tools.export_pandoc import export_pandoc

                result = await export_pandoc.fn(destination, **options)
            elif format == "docsify":
                from advanced_memory.mcp.tools.export_docsify import export_docsify

                result = await export_docsify.fn(destination, **options)
            elif format == "archive":
                from advanced_memory.mcp.tools.export_to_archive import export_to_archive

                result = await export_to_archive.fn(destination, **options)
            else:
                return build_error_response(
                    "VALIDATION_ERROR", "VALIDATION_ERROR", f"Unsupported export format: {format}"
                )

            return build_success_response("export", result)

        elif operation == "load":
            if not path:
                return build_error_response(
                    "VALIDATION_ERROR", "MISSING_PARAMETER", "Path required for load operations"
                )

            if format == "canvas":
                from advanced_memory.mcp.tools.load_canvas import load_obsidian_canvas

                result = await load_obsidian_canvas.fn(path, **options)
            else:
                return build_error_response(
                    "VALIDATION_ERROR", "VALIDATION_ERROR", f"Unsupported load format: {format}"
                )

            return build_success_response("load", result)

        elif operation == "search":
            if not query:
                return build_error_response(
                    "VALIDATION_ERROR", "MISSING_PARAMETER", "Query required for search operations"
                )

            # Route to appropriate search tool based on format
            if format == "obsidian":
                from advanced_memory.mcp.tools.search_obsidian_vault import search_obsidian_vault

                result = await search_obsidian_vault.fn(query, **options)
            elif format == "notion":
                from advanced_memory.mcp.tools.search_notion_vault import search_notion_vault

                result = await search_notion_vault.fn(query, **options)
            elif format == "joplin":
                from advanced_memory.mcp.tools.search_joplin_vault import search_joplin_vault

                result = await search_joplin_vault.fn(query, **options)
            elif format == "evernote":
                from advanced_memory.mcp.tools.search_evernote_vault import search_evernote_vault

                result = await search_evernote_vault.fn(query, **options)
            else:
                return build_error_response(
                    "VALIDATION_ERROR", "VALIDATION_ERROR", f"Unsupported search format: {format}"
                )

            return build_success_response("search", result)

        else:
            return build_error_response(
                "VALIDATION_ERROR", "VALIDATION_ERROR", f"Unknown operation: {operation}"
            )

    except Exception as e:
        logger.error(f"Import/export operation '{operation}' for format '{format}' failed: {e}")
        return build_error_response(
            "VALIDATION_ERROR", "VALIDATION_ERROR", f"Operation failed: {str(e)}"
        )
