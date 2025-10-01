"""
Pandoc-based export tool for Basic Memory.

This tool replaces Typora export functionality with reliable, automated
Pandoc-based document conversion supporting multiple output formats.

Supports: PDF, HTML, DOCX, ODT, RTF, LaTeX, EPUB, and more.
"""

import asyncio
import os
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Any
from urllib.parse import quote

from basic_memory.mcp.server import mcp
from basic_memory.mcp.tools.utils import call_post
from basic_memory.schemas.search import SearchQuery, SearchResponse


@mcp.tool()
async def export_pandoc(
    export_path: str,
    format_type: str = "pdf",
    source_folder: str = "/",
    include_subfolders: bool = True,
    pdf_engine: str = "pdflatex",
    template_path: Optional[str] = None,
    css_path: Optional[str] = None,
    toc: bool = False,
    highlight_style: str = "tango",
    standalone: bool = True,
    self_contained: bool = False,
    project: Optional[str] = None
) -> str:
    """
    Export Basic Memory notes to various formats using Pandoc.

    This tool provides automated, batch document export capabilities
    that surpass Typora's GUI-only limitations with full CLI automation.

    Parameters:
    - export_path: Directory path where exported files will be saved
    - format_type: Output format (pdf, html, docx, odt, rtf, tex, epub, etc.)
    - source_folder: Basic Memory folder to export from (default: "/")
    - include_subfolders: Include notes from subfolders (default: True)
    - pdf_engine: PDF generation engine (pdflatex, xelatex, lualatex, wkhtmltopdf, etc.)
    - template_path: Path to custom Pandoc template file
    - css_path: Path to custom CSS file for HTML output
    - toc: Generate table of contents (default: False)
    - highlight_style: Syntax highlighting style (tango, pygments, kate, etc.)
    - standalone: Generate standalone document with headers (default: True)
    - self_contained: Embed images and styles in output (HTML only, default: False)
    - project: Specific Basic Memory project to export from

    Supported Formats:
    - pdf: PDF document (requires LaTeX)
    - html: HTML page
    - docx: Microsoft Word document
    - odt: OpenDocument Text
    - rtf: Rich Text Format
    - tex: LaTeX source
    - epub: EPUB ebook
    - txt: Plain text
    - And many more...

    Examples:
    - Export all notes as PDF: export_pandoc("/exports", "pdf")
    - Export project docs as HTML: export_pandoc("/exports", "html", source_folder="/projects")
    - Export as Word with TOC: export_pandoc("/exports", "docx", toc=True)
    - Export with custom CSS: export_pandoc("/exports", "html", css_path="/styles/custom.css")

    Returns:
    Summary of export operation with file counts and any errors encountered.
    """
    try:
        # Create export directory
        export_dir = Path(export_path)
        export_dir.mkdir(parents=True, exist_ok=True)

        # Find all notes in the specified folder
        notes_data = await _get_notes_from_folder(
            source_folder, include_subfolders, project
        )

        if not notes_data:
            return f"No notes found in folder '{source_folder}' for export."

        # Process each note
        exported_files = []
        errors = []

        for note_info in notes_data:
            try:
                output_file = await _export_single_note(
                    note_info,
                    export_dir,
                    format_type,
                    pdf_engine,
                    template_path,
                    css_path,
                    toc,
                    highlight_style,
                    standalone,
                    self_contained
                )
                if output_file:
                    exported_files.append(output_file)
                else:
                    errors.append(f"Failed to export: {note_info['title']}")
            except Exception as e:
                errors.append(f"Error exporting {note_info['title']}: {str(e)}")

        # Generate summary
        summary = _generate_export_summary(
            exported_files, errors, format_type, export_path
        )

        return summary

    except Exception as e:
        return f"Pandoc export failed: {str(e)}"


async def _get_notes_from_folder(
    source_folder: str,
    include_subfolders: bool,
    project: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Retrieve all notes from the specified folder using the search API.
    """
    try:
        # Use search API to find notes (exclude entities for now)
        query = SearchQuery(
            query="",  # Empty query to get all notes
            types=["note"],  # Only notes, not entities
            page=1,
            page_size=1000  # Large limit for batch export
        )

        # Add project filter if specified
        if project:
            # Note: This assumes the search API supports project filtering
            # May need adjustment based on actual API
            pass

        response = await call_post(
            "/api/search",
            query.model_dump(),
            SearchResponse
        )

        if not response or not hasattr(response, 'results'):
            return []

        notes_data = []
        for note in response.results:
            # Filter by folder path
            note_path = getattr(note, 'file_path', '')
            if source_folder == "/" or note_path.startswith(source_folder.lstrip("/")):
                # Get full note content
                content = await _get_note_content(note)
                if content:
                    notes_data.append({
                        'id': getattr(note, 'id', ''),
                        'title': getattr(note, 'title', ''),
                        'file_path': note_path,
                        'content': content
                    })

        return notes_data

    except Exception as e:
        print(f"Error retrieving notes: {e}")
        return []


async def _get_note_content(note) -> Optional[str]:
    """
    Retrieve the full content of a note.
    """
    try:
        # Use the read_note tool to get content
        from basic_memory.mcp.tools.read_note import read_note

        # Get the identifier (prefer permalink, fallback to title)
        identifier = getattr(note, 'permalink', None) or getattr(note, 'title', '')

        if not identifier:
            return None

        content = await read_note(identifier)
        return content if content else None

    except Exception as e:
        print(f"Error reading note content: {e}")
        return None


async def _export_single_note(
    note_info: Dict[str, Any],
    export_dir: Path,
    format_type: str,
    pdf_engine: str,
    template_path: Optional[str],
    css_path: Optional[str],
    toc: bool,
    highlight_style: str,
    standalone: bool,
    self_contained: bool
) -> Optional[str]:
    """
    Export a single note using Pandoc.
    """
    try:
        # Create safe filename
        safe_title = _sanitize_filename(note_info['title'])
        output_filename = f"{safe_title}.{format_type}"
        output_path = export_dir / output_filename

        # Create temporary markdown file
        temp_md_path = export_dir / f"{safe_title}_temp.md"
        with open(temp_md_path, 'w', encoding='utf-8') as f:
            f.write(note_info['content'])

        # Build Pandoc command
        cmd = _build_pandoc_command(
            str(temp_md_path),
            str(output_path),
            format_type,
            pdf_engine,
            template_path,
            css_path,
            toc,
            highlight_style,
            standalone,
            self_contained
        )

        # Execute Pandoc
        result = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=str(export_dir)
        )

        stdout, stderr = await result.communicate()

        # Clean up temporary file
        temp_md_path.unlink(missing_ok=True)

        if result.returncode == 0:
            return str(output_path)
        else:
            error_msg = stderr.decode('utf-8', errors='ignore')
            print(f"Pandoc error for {note_info['title']}: {error_msg}")
            return None

    except Exception as e:
        print(f"Error exporting note {note_info['title']}: {e}")
        return None


def _build_pandoc_command(
    input_path: str,
    output_path: str,
    format_type: str,
    pdf_engine: str,
    template_path: Optional[str],
    css_path: Optional[str],
    toc: bool,
    highlight_style: str,
    standalone: bool,
    self_contained: bool
) -> List[str]:
    """
    Build the Pandoc command with all specified options.
    """
    cmd = ["C:\\Program Files\\Pandoc\\pandoc.exe", input_path, "-o", output_path]

    # Format specification
    if format_type == "pdf":
        cmd.extend(["-t", "pdf"])
        cmd.extend(["--pdf-engine", pdf_engine])
    else:
        cmd.extend(["-t", format_type])

    # Standalone document
    if standalone:
        cmd.append("-s")

    # Table of contents
    if toc:
        cmd.append("--toc")

    # Syntax highlighting
    if highlight_style:
        cmd.extend(["--highlight-style", highlight_style])

    # Custom template
    if template_path and Path(template_path).exists():
        cmd.extend(["--template", template_path])

    # CSS for HTML output
    if css_path and format_type == "html" and Path(css_path).exists():
        cmd.extend(["--css", css_path])

    # Self-contained HTML
    if self_contained and format_type == "html":
        cmd.append("--self-contained")

    return cmd


def _sanitize_filename(title: str) -> str:
    """
    Create a safe filename from note title.
    """
    import re
    import unicodedata

    # Normalize unicode characters
    title = unicodedata.normalize('NFKD', title)

    # Replace problematic characters
    title = title.replace(':', '-').replace('.', '_').replace('/', '-')

    # Remove or replace other unsafe characters
    title = re.sub(r'[<>:"|?*\\]', '_', title)

    # Collapse multiple underscores/spaces
    title = re.sub(r'[_ ]+', '_', title)

    # Trim underscores and spaces
    title = title.strip('_ ')

    # Limit length
    if len(title) > 100:
        title = title[:100].rstrip('_ ')

    # Ensure not empty
    if not title:
        title = "untitled"

    return title


def _generate_export_summary(
    exported_files: List[str],
    errors: List[str],
    format_type: str,
    export_path: str
) -> str:
    """
    Generate a summary of the export operation.
    """
    lines = [
        "# Pandoc Export Summary",
        f"",
        f"**Format:** {format_type.upper()}",
        f"**Output Directory:** {export_path}",
        f"**Files Exported:** {len(exported_files)}",
        f"**Errors:** {len(errors)}",
        f""
    ]

    if exported_files:
        lines.append("## Exported Files:")
        for file_path in exported_files:
            lines.append(f"- {Path(file_path).name}")
        lines.append("")

    if errors:
        lines.append("## Errors:")
        for error in errors:
            lines.append(f"- {error}")
        lines.append("")

    lines.extend([
        "## Next Steps:",
        f"- Check the `{export_path}` directory for exported files",
        f"- Open {format_type.upper()} files with appropriate applications",
        f"- For PDF: Requires PDF viewer (Adobe Reader, etc.)",
        f"- For DOCX: Requires Word or compatible viewer",
        f"- For HTML: Open in any web browser",
        f""
    ])

    return "\n".join(lines)
