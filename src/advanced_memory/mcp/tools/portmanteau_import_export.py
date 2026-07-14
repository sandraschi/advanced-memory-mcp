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


# @mcp.tool  # Decommissioned in favor of namespaced mcp app (FastMCP 3.2 GA)
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
    """Unified portmanteau for all import and export operations.

    Operations: import, export, load, search.
    Formats: obsidian, notion, joplin, evernote, onenote, html, pdf, pandoc, docsify, archive, canvas.

    For full documentation on parameters and usage examples, call:
    `help(topic="adn_import_export")`
    """
    try:
        options = options or {}

        if operation == "import":
            if not path:
                return build_error_response(
                    "VALIDATION_ERROR",
                    "MISSING_PARAMETER",
                    "Path required for import operations",
                )

            if format == "obsidian":
                from advanced_memory.mcp.tools.load_obsidian_vault import (
                    load_obsidian_vault,
                )

                result = await load_obsidian_vault(path, **options)
            elif format == "notion":
                from advanced_memory.mcp.tools.load_notion_export import (
                    load_notion_export,
                )

                result = await load_notion_export(path, **options)
            elif format == "joplin":
                from advanced_memory.mcp.tools.load_joplin_vault import (
                    load_joplin_vault,
                )

                result = await load_joplin_vault(path, **options)
            elif format == "evernote":
                from advanced_memory.mcp.tools.load_evernote_export import (
                    load_evernote_export,
                )

                result = await load_evernote_export(path, **options)
            elif format == "onenote":
                from advanced_memory.mcp.tools.load_onenote_html import (
                    load_onenote_html,
                )

                result = await load_onenote_html(path, **options)
            elif format == "archive":
                from advanced_memory.mcp.tools.import_from_archive import (
                    import_from_archive,
                )

                result = await import_from_archive(path, **options)
            else:
                return build_error_response(
                    "VALIDATION_ERROR",
                    "VALIDATION_ERROR",
                    f"Unsupported import format: {format}",
                )

            return build_success_response("import", result)

        elif operation == "export":
            if not destination:
                return build_error_response(
                    "VALIDATION_ERROR",
                    "MISSING_PARAMETER",
                    "Destination required for export operations",
                )

            if format == "html":
                from advanced_memory.mcp.tools.export_html_notes import (
                    export_html_notes,
                )

                result = await export_html_notes(destination, **options)
            elif format == "pdf":
                if options.get("combined", False):
                    from advanced_memory.mcp.tools.export_pdf_combined import (
                        export_pdf_combined,
                    )

                    result = await export_pdf_combined(destination, **options)
                else:
                    from advanced_memory.mcp.tools.export_pdf_native import (
                        export_pdf_native,
                    )

                    result = await export_pdf_native(destination, **options)
            elif format == "pandoc":
                from advanced_memory.mcp.tools.export_pandoc import export_pandoc

                result = await export_pandoc(destination, **options)
            elif format == "docsify":
                from advanced_memory.mcp.tools.export_docsify import export_docsify

                result = await export_docsify(destination, **options)
            elif format == "archive":
                from advanced_memory.mcp.tools.export_to_archive import (
                    export_to_archive,
                )

                result = await export_to_archive(destination, **options)
            else:
                return build_error_response(
                    "VALIDATION_ERROR",
                    "VALIDATION_ERROR",
                    f"Unsupported export format: {format}",
                )

            return build_success_response("export", result)

        elif operation == "load":
            if not path:
                return build_error_response(
                    "VALIDATION_ERROR",
                    "MISSING_PARAMETER",
                    "Path required for load operations",
                )

            if format == "canvas":
                from advanced_memory.mcp.tools.load_canvas import load_obsidian_canvas

                result = await load_obsidian_canvas(path, **options)
            else:
                return build_error_response(
                    "VALIDATION_ERROR",
                    "VALIDATION_ERROR",
                    f"Unsupported load format: {format}",
                )

            return build_success_response("load", result)

        elif operation == "search":
            if not query:
                return build_error_response(
                    "VALIDATION_ERROR",
                    "MISSING_PARAMETER",
                    "Query required for search operations",
                )

            if format == "obsidian":
                from advanced_memory.mcp.tools.search_obsidian_vault import (
                    search_obsidian_vault,
                )

                result = await search_obsidian_vault(query, **options)
            elif format == "notion":
                from advanced_memory.mcp.tools.search_notion_vault import (
                    search_notion_vault,
                )

                result = await search_notion_vault(query, **options)
            elif format == "joplin":
                from advanced_memory.mcp.tools.search_joplin_vault import (
                    search_joplin_vault,
                )

                result = await search_joplin_vault(query, **options)
            elif format == "evernote":
                from advanced_memory.mcp.tools.search_evernote_vault import (
                    search_evernote_vault,
                )

                result = await search_evernote_vault(query, **options)
            else:
                return build_error_response(
                    "VALIDATION_ERROR",
                    "VALIDATION_ERROR",
                    f"Unsupported search format: {format}",
                )

            return build_success_response("search", result)

        else:
            return build_error_response(
                "VALIDATION_ERROR",
                "VALIDATION_ERROR",
                f"Unknown operation: {operation}",
            )

    except Exception as e:
        logger.error(f"Import/export operation '{operation}' for format '{format}' failed: {e}")
        return build_error_response("VALIDATION_ERROR", "VALIDATION_ERROR", f"Operation failed: {e!s}")
