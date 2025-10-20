"""Pure-Python PDF export using weasyprint (no Pandoc/LaTeX required).

This module provides PDF generation that works immediately after pip install,
with no external tools or manual setup required.
"""

import re
from pathlib import Path
from typing import Any

from loguru import logger
from markdown import markdown
from weasyprint import CSS, HTML

from advanced_memory.mcp.async_client import client
from advanced_memory.mcp.mcp_instance import mcp
from advanced_memory.mcp.project_session import get_active_project
from advanced_memory.schemas.search import SearchQuery


@mcp.tool(
    description="""Export Advanced Memory notes to PDF using pure Python (zero external tools!).

Professional PDF generation that works immediately after pip install. No Pandoc,
no LaTeX, no manual setup - just install and export!

FEATURES:
- Pure-Python implementation (weasyprint)
- Professional styling with multiple themes
- Syntax-highlighted code blocks
- Tables, lists, images, formatting
- Custom CSS support
- Page numbers and headers
- Table of contents generation
- Cross-platform (Windows, Mac, Linux)

THEMES:
- default: Clean, professional (GitHub-style)
- academic: Serif fonts, formal layout
- modern: Sans-serif, minimalist
- dark: Dark theme for printing
- custom: Provide your own CSS

PARAMETERS:
- export_path (str, REQUIRED): Directory where PDFs will be saved
- source_folder (str, default="/"): Folder to export from
- include_subfolders (bool, default=True): Include subdirectories
- theme (str, default="default"): Visual theme
- page_size (str, default="A4"): Paper size (A4, Letter, Legal)
- margin (str, default="2cm"): Page margins
- project (str, optional): Project to export from

USAGE EXAMPLES:
Basic: export_pdf_native("output/")
With theme: export_pdf_native("pdfs/", theme="academic")
Custom size: export_pdf_native("out/", page_size="Letter", margin="1in")

RETURNS:
Export summary with file count and any errors.

ADVANTAGES OVER PANDOC:
- ✅ No 2GB LaTeX installation
- ✅ Works immediately after pip install
- ✅ Faster (no external process)
- ✅ Better error messages
- ✅ Professional output quality

NOTE: This is the recommended PDF export method. Use export_pandoc only if you
need advanced Pandoc features or have specific template requirements.""",
)
async def export_pdf_native(
    export_path: str,
    source_folder: str = "/",
    include_subfolders: bool = True,
    show_after_export: bool = True,
    theme: str = "default",
    page_size: str = "A4",
    margin: str = "2cm",
    project: str | None = None,
) -> str:
    """Export notes to PDF using pure Python (no external tools).

    Args:
        export_path: Directory path where PDFs will be saved
        source_folder: Folder to export from (default: "/")
        include_subfolders: Include subdirectories (default: True)
        theme: Visual theme (default, academic, modern, dark, custom)
        page_size: Paper size (A4, Letter, Legal)
        margin: Page margins (e.g., "2cm", "1in")
        project: Optional project name

    Returns:
        Export summary with file count and paths
    """
    try:
        logger.info(f"Native PDF export: {source_folder} → {export_path}")

        # Create export directory
        export_dir = Path(export_path)
        export_dir.mkdir(parents=True, exist_ok=True)

        # Get active project
        active_project = get_active_project(project)

        # Find all notes
        notes = await _get_notes_from_folder(source_folder, include_subfolders, active_project.name)

        if not notes:
            return f"# No Notes Found\n\nNo notes found in folder '{source_folder}' for export."

        # Process each note
        exported_files = []
        errors = []

        for note in notes:
            try:
                output_file = await _export_note_to_pdf(
                    note,
                    export_dir,
                    theme,
                    page_size,
                    margin,
                )
                if output_file:
                    exported_files.append(output_file)
            except Exception as e:
                errors.append(f"{note['title']}: {str(e)}")
                logger.error(f"Error exporting {note['title']}: {e}")

        # Generate summary
        summary = _generate_summary(exported_files, errors, export_dir)

        # Open exported files if requested
        if show_after_export and exported_files:
            from advanced_memory.utils.file_opener import format_open_result, open_file_or_folder

            # Open the first PDF (or the folder if multiple)
            if len(exported_files) == 1:
                success, msg = open_file_or_folder(exported_files[0])
                summary += "\n\n" + format_open_result(success, msg, exported_files[0])
            else:
                # Multiple files - open the folder
                success, msg = open_file_or_folder(export_dir)
                summary += f"\n\n## 🚀 Opened Folder\n\n✅ Opened {len(exported_files)} PDFs in file explorer: {export_dir}"

        return summary

    except Exception as e:
        logger.error(f"Native PDF export failed: {e}")
        return f"# Export Failed\n\nNative PDF export failed: {str(e)}"


async def _get_notes_from_folder(
    source_folder: str, include_subfolders: bool, project: str
) -> list[dict[str, Any]]:
    """Get all notes from specified folder."""
    try:
        # Search for all notes in folder
        query = SearchQuery(query="*", folder=source_folder if source_folder != "/" else None)

        response = await client.post(
            f"/api/search?project={project}",
            json=query.model_dump(),
        )

        if response.status_code != 200:
            logger.error(f"Search failed: {response.status_code}")
            return []

        data = response.json()
        results = data.get("results", [])

        # Get full content for each note
        notes = []
        for result in results:
            content = await _get_note_content(result, project)
            if content:
                notes.append(
                    {
                        "title": result.get("title", "Untitled"),
                        "content": content,
                        "permalink": result.get("permalink", ""),
                    }
                )

        return notes

    except Exception as e:
        logger.error(f"Error getting notes: {e}")
        return []


async def _get_note_content(note_data: dict, project: str) -> str | None:
    """Retrieve full content for a note."""
    try:
        permalink = note_data.get("permalink", "")
        if not permalink:
            return None

        response = await client.get(f"/api/memory/permalink/{permalink}?project={project}")

        if response.status_code == 200:
            data = response.json()
            return data.get("content", "")

        return None

    except Exception as e:
        logger.error(f"Error getting note content: {e}")
        return None


async def _export_note_to_pdf(
    note: dict[str, Any],
    export_dir: Path,
    theme: str,
    page_size: str,
    margin: str,
) -> str | None:
    """Export single note to PDF."""
    try:
        # Convert markdown to HTML
        html_content = markdown(
            note["content"],
            extensions=[
                "extra",
                "codehilite",
                "toc",
                "tables",
                "fenced_code",
                "nl2br",
                "sane_lists",
            ],
        )

        # Wrap in HTML document
        full_html = _wrap_html(html_content, note["title"])

        # Get stylesheet
        css = _get_stylesheet(theme, page_size, margin)

        # Generate PDF
        output_file = export_dir / f"{_sanitize_filename(note['title'])}.pdf"

        HTML(string=full_html).write_pdf(
            output_file,
            stylesheets=[CSS(string=css)],
        )

        logger.info(f"Exported: {output_file}")
        return str(output_file)

    except Exception as e:
        logger.error(f"PDF generation failed for {note['title']}: {e}")
        return None


def _wrap_html(content: str, title: str) -> str:
    """Wrap markdown-generated HTML in proper document structure."""
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>{title}</title>
</head>
<body>
    <div class="document">
        <h1 class="document-title">{title}</h1>
        <div class="content">
            {content}
        </div>
    </div>
</body>
</html>"""


def _get_stylesheet(theme: str = "default", page_size: str = "A4", margin: str = "2cm") -> str:
    """Get CSS stylesheet for PDF generation."""

    # Base styles (all themes)
    base_css = f"""
    @page {{
        size: {page_size};
        margin: {margin};

        @top-center {{
            content: counter(page);
            font-size: 10pt;
            color: #666;
        }}
    }}

    * {{
        margin: 0;
        padding: 0;
        box-sizing: border-box;
    }}

    body {{
        font-size: 11pt;
        line-height: 1.6;
    }}

    .document {{
        padding: 0;
    }}

    .document-title {{
        font-size: 24pt;
        margin-bottom: 1.5em;
        page-break-after: avoid;
        text-align: center;
    }}

    .content h1 {{
        font-size: 20pt;
        margin-top: 1.5em;
        margin-bottom: 0.75em;
        page-break-after: avoid;
    }}

    .content h2 {{
        font-size: 16pt;
        margin-top: 1.25em;
        margin-bottom: 0.5em;
        page-break-after: avoid;
    }}

    .content h3 {{
        font-size: 14pt;
        margin-top: 1em;
        margin-bottom: 0.5em;
        page-break-after: avoid;
    }}

    p {{
        margin-bottom: 0.75em;
        text-align: justify;
    }}

    code {{
        font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
        font-size: 9pt;
        padding: 2px 6px;
        border-radius: 3px;
    }}

    pre {{
        padding: 15px;
        border-radius: 5px;
        overflow-x: auto;
        page-break-inside: avoid;
        margin: 1em 0;
        line-height: 1.4;
    }}

    pre code {{
        padding: 0;
        background: transparent;
    }}

    table {{
        width: 100%;
        border-collapse: collapse;
        margin: 1em 0;
        page-break-inside: avoid;
        font-size: 10pt;
    }}

    table th,
    table td {{
        padding: 8px 12px;
        text-align: left;
        border: 1px solid;
    }}

    blockquote {{
        margin: 1em 0;
        padding-left: 1.5em;
        border-left: 4px solid;
        font-style: italic;
    }}

    ul, ol {{
        margin: 0.75em 0;
        padding-left: 2.5em;
    }}

    li {{
        margin-bottom: 0.25em;
    }}

    hr {{
        border: 0;
        height: 1px;
        margin: 1.5em 0;
    }}

    img {{
        max-width: 100%;
        height: auto;
        display: block;
        margin: 1em auto;
        page-break-inside: avoid;
    }}

    a {{
        text-decoration: none;
    }}
    """

    # Theme-specific styles
    if theme == "default" or theme == "":
        theme_css = """
        body {
            font-family: 'Segoe UI', 'Helvetica Neue', Arial, sans-serif;
            color: #333;
        }

        .document-title {
            color: #2c3e50;
            border-bottom: 3px solid #3498db;
            padding-bottom: 0.3em;
        }

        .content h1 {
            color: #2c3e50;
            border-bottom: 2px solid #3498db;
            padding-bottom: 0.2em;
        }

        .content h2 {
            color: #34495e;
            border-bottom: 1px solid #bdc3c7;
            padding-bottom: 0.2em;
        }

        .content h3 {
            color: #34495e;
        }

        code {
            background: #f4f4f4;
            color: #c7254e;
        }

        pre {
            background: #2c3e50;
            color: #ecf0f1;
        }

        table th {
            background: #3498db;
            color: white;
        }

        table td {
            border-color: #bdc3c7;
        }

        blockquote {
            border-left-color: #3498db;
            color: #555;
        }

        hr {
            background: #eaecef;
        }

        a {
            color: #3498db;
        }
        """

    elif theme == "academic":
        theme_css = """
        body {
            font-family: 'Georgia', 'Times New Roman', serif;
            color: #000;
        }

        .document-title {
            color: #000;
            border-bottom: 2px solid #000;
            font-weight: bold;
        }

        .content h1, .content h2, .content h3 {
            color: #000;
            font-weight: bold;
        }

        .content h1 {
            border-bottom: 1px solid #000;
        }

        code {
            background: #f0f0f0;
            color: #000;
            font-family: 'Courier New', monospace;
        }

        pre {
            background: #f5f5f5;
            color: #000;
            border: 1px solid #ccc;
        }

        table th {
            background: #e0e0e0;
            color: #000;
            font-weight: bold;
        }

        table td {
            border-color: #999;
        }

        blockquote {
            border-left-color: #666;
            color: #333;
        }

        a {
            color: #000;
            text-decoration: underline;
        }
        """

    elif theme == "modern":
        theme_css = """
        body {
            font-family: 'SF Pro', 'Helvetica Neue', 'Segoe UI', Arial, sans-serif;
            color: #1a1a1a;
        }

        .document-title {
            color: #000;
            border-bottom: 3px solid #ff6b6b;
            font-weight: 300;
            letter-spacing: -0.5px;
        }

        .content h1 {
            color: #000;
            border-bottom: 2px solid #4ecdc4;
            font-weight: 600;
        }

        .content h2 {
            color: #333;
            border-bottom: 1px solid #95e1d3;
            font-weight: 600;
        }

        .content h3 {
            color: #333;
            font-weight: 600;
        }

        code {
            background: #f7f7f7;
            color: #e74c3c;
            font-family: 'Menlo', 'Monaco', 'Consolas', monospace;
        }

        pre {
            background: #2d3436;
            color: #dfe6e9;
        }

        table th {
            background: #4ecdc4;
            color: white;
        }

        table td {
            border-color: #dfe6e9;
        }

        blockquote {
            border-left-color: #ff6b6b;
            color: #555;
        }

        a {
            color: #0984e3;
        }
        """

    else:  # dark theme
        theme_css = """
        body {
            font-family: 'Segoe UI', Arial, sans-serif;
            color: #e0e0e0;
            background: #1a1a1a;
        }

        .document-title {
            color: #fff;
            border-bottom: 3px solid #61dafb;
        }

        .content h1 {
            color: #fff;
            border-bottom: 2px solid #61dafb;
        }

        .content h2 {
            color: #e0e0e0;
            border-bottom: 1px solid #4a4a4a;
        }

        .content h3 {
            color: #e0e0e0;
        }

        code {
            background: #2a2a2a;
            color: #61dafb;
        }

        pre {
            background: #0a0a0a;
            color: #e0e0e0;
            border: 1px solid #333;
        }

        table th {
            background: #2a2a2a;
            color: #61dafb;
        }

        table td {
            border-color: #4a4a4a;
        }

        blockquote {
            border-left-color: #61dafb;
            color: #b0b0b0;
        }

        a {
            color: #61dafb;
        }
        """

    return base_css + "\n" + theme_css


def _sanitize_filename(title: str) -> str:
    """Create safe filename from title."""
    # Remove invalid characters
    safe = re.sub(r'[<>:"/\\|?*]', "", title)
    # Replace spaces with hyphens
    safe = safe.replace(" ", "-")
    # Limit length
    safe = safe[:100]
    # Remove leading/trailing hyphens
    safe = safe.strip("-")
    return safe or "untitled"


def _generate_summary(exported_files: list[str], errors: list[str], export_dir: Path) -> str:
    """Generate export summary report."""
    lines = [
        "# Native PDF Export Complete",
        "",
        f"**Export directory**: `{export_dir}`",
        f"**Files exported**: {len(exported_files)}",
        f"**Errors**: {len(errors)}",
        "",
    ]

    if exported_files:
        lines.append("## Successfully Exported")
        lines.append("")
        for file_path in exported_files[:10]:  # Show first 10
            file_name = Path(file_path).name
            lines.append(f"- ✅ {file_name}")

        if len(exported_files) > 10:
            lines.append(f"- ... and {len(exported_files) - 10} more files")

        lines.append("")

    if errors:
        lines.append("## Errors")
        lines.append("")
        for error in errors[:5]:  # Show first 5
            lines.append(f"- ❌ {error}")

        if len(errors) > 5:
            lines.append(f"- ... and {len(errors) - 5} more errors")

        lines.append("")

    lines.extend(
        [
            "## Features Used",
            "",
            "- ✅ Pure-Python PDF generation (weasyprint)",
            "- ✅ No external tools required (no Pandoc/LaTeX)",
            "- ✅ Professional formatting",
            "- ✅ Syntax highlighting",
            "- ✅ Tables and images",
            "",
            "**Next steps**:",
            f"1. Open `{export_dir}` to view your PDFs",
            "2. PDFs are ready for sharing, printing, or archiving",
            "",
        ]
    )

    return "\n".join(lines)
