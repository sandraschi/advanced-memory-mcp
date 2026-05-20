"""Load OneNote HTML content tool for Advanced Memory MCP server.

This tool imports OneNote pages from HTML content (typically from office-365-mcp
or other OneNote API sources) and converts them to readable notes in Advanced Memory.
"""

import json
from pathlib import Path
from typing import Any

from loguru import logger

from advanced_memory.mcp.mcp_instance import mcp
from advanced_memory.mcp.project_session import get_active_project
from advanced_memory.mcp.tools.content_manager import adn_content
from advanced_memory.utils.onenote_text_extractor import extract_readable_text


# @mcp.tool
async def load_onenote_html(
    source_path: str | None = None,
    html_content: str | None = None,
    page_title: str | None = None,
    folder: str = "onenote-import",
    project: str | None = None,
) -> str:
    """Import OneNote pages from HTML content into Advanced Memory.

    This tool converts OneNote's idiosyncratic HTML output (from office-365-mcp
    or other sources) into clean, readable notes that Claude/Cursor/Sandra can
    easily parse and understand.

    The tool accepts HTML content in multiple formats:
    - Direct HTML string (from office-365-mcp API calls)
    - JSON file with page data (title, html_content fields)
    - Directory of HTML files
    - Single HTML file

    Args:
        source_path: Path to HTML file, JSON file, or directory containing HTML files.
                     If None, html_content must be provided.
        html_content: Direct HTML content string. If None, source_path must be provided.
        page_title: Title for the note (if not provided, extracted from HTML or filename).
        folder: Base folder for imported notes (default: "onenote-import").
        project: Optional project name to import into.

    Returns:
        Summary of imported content with created entities and statistics.

    Examples:
        # Import from HTML file
        load_onenote_html(source_path="page.html", page_title="My Note")

        # Import from JSON file (with title and html_content fields)
        load_onenote_html(source_path="onenote-pages.json")

        # Import direct HTML content
        load_onenote_html(html_content="<html>...", page_title="Meeting Notes")

        # Import directory of HTML files
        load_onenote_html(source_path="onenote-export/", folder="imported/onenote")
    """
    get_active_project(project)

    # Validate inputs
    if not source_path and not html_content:
        return "# Error\n\nEither source_path or html_content must be provided."

    pages_to_import: list[dict[str, Any]] = []

    # Case 1: Direct HTML content
    if html_content:
        pages_to_import.append(
            {
                "title": page_title or "OneNote Page",
                "html_content": html_content,
            }
        )

    # Case 2: Source path provided
    elif source_path:
        source_path_obj = Path(source_path).expanduser()

        if not source_path_obj.exists():
            return f"# Error\n\nSource path not found: {source_path}"

        # Case 2a: JSON file (array of pages with title and html_content)
        if source_path_obj.is_file() and source_path_obj.suffix.lower() == ".json":
            try:
                json_data = json.loads(source_path_obj.read_text(encoding="utf-8"))
                if isinstance(json_data, list):
                    pages_to_import = json_data
                elif isinstance(json_data, dict):
                    # Single page object
                    pages_to_import = [json_data]
                else:
                    return (
                        "# Error\n\nInvalid JSON format. Expected array or object with page data."
                    )
            except json.JSONDecodeError as e:
                return f"# Error\n\nFailed to parse JSON: {e}"

        # Case 2b: Single HTML file
        elif source_path_obj.is_file() and source_path_obj.suffix.lower() in [".html", ".htm"]:
            html_content = source_path_obj.read_text(encoding="utf-8")
            pages_to_import.append(
                {
                    "title": page_title or source_path_obj.stem,
                    "html_content": html_content,
                }
            )

        # Case 2c: Directory of HTML files
        elif source_path_obj.is_dir():
            html_files = list(source_path_obj.rglob("*.html")) + list(
                source_path_obj.rglob("*.htm")
            )
            if not html_files:
                return f"# Error\n\nNo HTML files found in directory: {source_path}"

            for html_file in html_files:
                html_content = html_file.read_text(encoding="utf-8")
                pages_to_import.append(
                    {
                        "title": html_file.stem,
                        "html_content": html_content,
                    }
                )

        else:
            return "# Error\n\nUnsupported file type. Expected .html, .htm, or .json file, or directory."

    if not pages_to_import:
        return "# Error\n\nNo pages to import."

    # Process pages
    total_notes = 0
    created_entities = []
    errors = []

    for page_data in pages_to_import:
        try:
            page_title = page_data.get("title", "Untitled OneNote Page")
            html_content = page_data.get("html_content") or page_data.get("html")

            if not html_content:
                errors.append(f"{page_title}: No HTML content found")
                continue

            # Extract readable text from HTML
            readable_text = extract_readable_text(html_content)

            if not readable_text.strip():
                logger.warning(f"Empty text extracted from {page_title}")
                readable_text = f"# {page_title}\n\n(Content extraction resulted in empty text)"

            # Create note in Advanced Memory
            await adn_content(
                operation="write",
                identifier=page_title,
                content=readable_text,
                folder=folder,
                tags=["onenote", "imported"],
                entity_type="note",
                project=project,
            )

            total_notes += 1
            created_entities.append(page_title)
            logger.info(f"Imported OneNote page: {page_title}")

        except Exception as e:
            error_msg = f"{page_data.get('title', 'Unknown')}: {e!s}"
            errors.append(error_msg)
            logger.error(f"Failed to import page: {error_msg}")

    # Generate summary
    summary_lines = [
        "# 📝 OneNote Import Complete",
        "",
        f"**Imported**: {total_notes} pages",
        f"**To**: {folder}",
        "",
    ]

    if errors:
        summary_lines.append(f"⚠️ **Errors**: {len(errors)}")
        summary_lines.append("")
        for error in errors[:10]:  # Show first 10
            summary_lines.append(f"  - {error}")
        summary_lines.append("")

    summary_lines.extend(
        [
            "## ✅ What's Imported",
            "",
            f"- {total_notes} OneNote pages converted to readable notes",
            "- HTML content extracted to clean, readable text",
            "- Tagged with `onenote` and `imported` for filtering",
            "- Searchable via Advanced Memory search",
            "",
            "## 🔍 Next Steps",
            "",
            "**Search Imported Notes**:",
            f'  search_notes("keyword", folder="{folder}")',
            "",
            "**View Imported Notes**:",
            f'  adn_navigation("list_directory", dir_name="{folder}")',
            "",
            f"**Total Notes Imported**: {total_notes}",
        ]
    )

    return "\n".join(summary_lines)
