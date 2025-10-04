"""Export Manager portmanteau tool for Advanced Memory MCP server.

This tool consolidates all export operations: pandoc, docsify, html, joplin, pdf_book, archive, evernote, notion.
It reduces the number of MCP tools while maintaining full functionality.
"""

from typing import Optional, List, Dict, Any

from loguru import logger

from advanced_memory.mcp.server import mcp


@mcp.tool(
    description="""Comprehensive export management tool for Advanced Memory knowledge base.

This portmanteau tool consolidates all export operations into a single interface,
reducing MCP tool count while maintaining full functionality for Cursor IDE compatibility.

SUPPORTED OPERATIONS:
- **pandoc**: Export to PDF, Word, HTML, and 40+ formats using Pandoc
- **docsify**: Export to Docsify documentation website with navigation
- **html**: Export to standalone HTML website with Mermaid diagram rendering
- **joplin**: Export to Joplin-compatible format for cross-platform access
- **pdf_book**: Create professional PDF books with title pages and chapters
- **archive**: Export complete Advanced Memory archive for migration/backup
- **evernote**: Export to Evernote-compatible format
- **notion**: Export to Notion-compatible format

EXPORT FEATURES:
- Multiple format support (PDF, HTML, DOCX, EPUB, etc.)
- Professional document generation with templates
- Mermaid diagram rendering in HTML exports
- Cross-platform compatibility for various note-taking apps
- Complete archive creation for backup/migration

PARAMETERS:
- operation (str, REQUIRED): Export operation type (pandoc, docsify, html, joplin, pdf_book, archive, evernote, notion)
- export_path (str, REQUIRED): Path where exported files will be saved
- format_type (str, default="pdf"): Output format for pandoc operations
- source_folder (str, default="/"): Source folder to export from
- include_subfolders (bool, default=True): Include subfolders recursively
- site_title (str, optional): Title for docsify/html exports
- site_description (str, optional): Description for docsify/html exports
- book_title (str, optional): Title for PDF book exports
- tag_filter (str, optional): Filter notes by tag for exports
- pdf_engine (str, default="pdflatex"): PDF generation engine
- project (str, optional): Specific project to export from

USAGE EXAMPLES:
Pandoc export: adn_export("pandoc", export_path="output.pdf", format_type="pdf", source_folder="/notes")
Docsify export: adn_export("docsify", export_path="website/", site_title="My Knowledge Base")
HTML export: adn_export("html", export_path="static-site/", include_index=True)
PDF book: adn_export("pdf_book", export_path="book.pdf", book_title="My Research", tag_filter="research")
Archive export: adn_export("archive", export_path="backup.zip", include_projects=["work", "personal"])

RETURNS:
Operation-specific results with export details, file counts, and processing information.

NOTE: This tool provides all export functionality in a single interface for better MCP client compatibility.""",
)
async def adn_export(
    operation: str,
    export_path: str,
    format_type: str = "pdf",
    source_folder: str = "/",
    include_subfolders: bool = True,
    site_title: Optional[str] = None,
    site_description: Optional[str] = None,
    book_title: Optional[str] = None,
    tag_filter: Optional[str] = None,
    pdf_engine: str = "pdflatex",
    project: Optional[str] = None,
) -> str:
    """Comprehensive export management for Advanced Memory knowledge base.

    This portmanteau tool consolidates all export operations:
    - pandoc: Export to various formats using Pandoc
    - docsify: Export to Docsify documentation website
    - html: Export to standalone HTML website
    - joplin: Export to Joplin-compatible format
    - pdf_book: Create professional PDF books
    - archive: Export complete system archive
    - evernote: Export to Evernote-compatible format
    - notion: Export to Notion-compatible format

    Args:
        operation: The export operation to perform
        export_path: Path where exported files will be saved
        format_type: Output format for pandoc operations
        source_folder: Source folder to export from
        include_subfolders: Include subfolders recursively
        site_title: Title for docsify/html exports
        site_description: Description for docsify/html exports
        book_title: Title for PDF book exports
        tag_filter: Filter notes by tag for exports
        pdf_engine: PDF generation engine
        project: Optional project name

    Returns:
        Operation-specific result with export details and file counts

    Examples:
        # Export to PDF using Pandoc
        adn_export("pandoc", export_path="output.pdf", format_type="pdf", source_folder="/notes")

        # Export to Docsify website
        adn_export("docsify", export_path="website/", site_title="My Knowledge Base")

        # Create PDF book
        adn_export("pdf_book", export_path="book.pdf", book_title="Research Papers", tag_filter="research")

        # Export complete archive
        adn_export("archive", export_path="backup.zip")
    """
    logger.info(f"MCP tool call tool=adn_export operation={operation} export_path={export_path}")

    # Route to appropriate operation
    if operation == "pandoc":
        return await _pandoc_export(export_path, format_type, source_folder, include_subfolders, pdf_engine, project)
    elif operation == "docsify":
        return await _docsify_export(export_path, source_folder, include_subfolders, site_title, site_description, project)
    elif operation == "html":
        return await _html_export(export_path, source_folder, include_subfolders, project)
    elif operation == "joplin":
        return await _joplin_export(export_path, source_folder, include_subfolders, project)
    elif operation == "pdf_book":
        return await _pdf_book_export(export_path, source_folder, include_subfolders, book_title, tag_filter, project)
    elif operation == "archive":
        return await _archive_export(export_path, project)
    elif operation == "evernote":
        return await _evernote_export(export_path, source_folder, include_subfolders, project)
    elif operation == "notion":
        return await _notion_export(export_path, source_folder, include_subfolders, project)
    else:
        return f"# Error\n\nInvalid operation '{operation}'. Supported operations: pandoc, docsify, html, joplin, pdf_book, archive, evernote, notion"


async def _pandoc_export(export_path: str, format_type: str, source_folder: str, include_subfolders: bool, pdf_engine: str, project: Optional[str]) -> str:
    """Handle Pandoc export operation."""
    from advanced_memory.mcp.tools.export_pandoc import export_pandoc
    return await export_pandoc(export_path, format_type, source_folder, include_subfolders, pdf_engine, None, None, False, "tango", True, False, project)


async def _docsify_export(export_path: str, source_folder: str, include_subfolders: bool, site_title: Optional[str], site_description: Optional[str], project: Optional[str]) -> str:
    """Handle Docsify export operation."""
    from advanced_memory.mcp.tools.export_docsify import export_docsify
    return await export_docsify(export_path, source_folder, include_subfolders, site_title or "Knowledge Base", site_description or "Documentation generated from Advanced Memory", project)


async def _html_export(export_path: str, source_folder: str, include_subfolders: bool, project: Optional[str]) -> str:
    """Handle HTML export operation."""
    from advanced_memory.mcp.tools.export_html_notes import export_html_notes
    return await export_html_notes(export_path, source_folder, include_subfolders, True, project)


async def _joplin_export(export_path: str, source_folder: str, include_subfolders: bool, project: Optional[str]) -> str:
    """Handle Joplin export operation."""
    from advanced_memory.mcp.tools.export_joplin_notes import export_joplin_notes
    return await export_joplin_notes(export_path, source_folder, include_subfolders, True, project)


async def _pdf_book_export(export_path: str, source_folder: str, include_subfolders: bool, book_title: Optional[str], tag_filter: Optional[str], project: Optional[str]) -> str:
    """Handle PDF book export operation."""
    if not book_title:
        return "# Error\n\nPDF book export requires: book_title parameter"
    
    from advanced_memory.mcp.tools.make_pdf_book import make_pdf_book
    return await make_pdf_book(book_title, source_folder, tag_filter, export_path, "Advanced Memory", include_subfolders, 2, "a4", project)


async def _archive_export(export_path: str, project: Optional[str]) -> str:
    """Handle archive export operation."""
    from advanced_memory.mcp.tools.export_to_archive import export_to_archive
    return await export_to_archive(export_path, None, None, None, None, True, project)


async def _evernote_export(export_path: str, source_folder: str, include_subfolders: bool, project: Optional[str]) -> str:
    """Handle Evernote export operation."""
    from advanced_memory.mcp.tools.export_evernote_compatible import export_evernote_compatible
    return await export_evernote_compatible(export_path, source_folder, include_subfolders, project)


async def _notion_export(export_path: str, source_folder: str, include_subfolders: bool, project: Optional[str]) -> str:
    """Handle Notion export operation."""
    from advanced_memory.mcp.tools.export_notion_compatible import export_notion_compatible
    return await export_notion_compatible(export_path, source_folder, include_subfolders, project)
