"""
Pandoc-based export tool for Advanced Memory.

This tool replaces Typora export functionality with reliable, automated
Pandoc-based document conversion supporting multiple output formats.

Supports: PDF, HTML, DOCX, ODT, RTF, LaTeX, EPUB, and more.

Pandoc is auto-installed on first use via pypandoc.
"""

import asyncio
from pathlib import Path
from typing import Any

from loguru import logger

from advanced_memory.mcp.async_client import client
from advanced_memory.mcp.mcp_instance import mcp
from advanced_memory.mcp.tools.utils import call_post
from advanced_memory.schemas.search import SearchQuery
from advanced_memory.utils.pandoc_installer import get_pandoc_command


# @mcp.tool
async def export_pandoc(
    export_path: str,
    format_type: str = "pdf",
    source_folder: str = "/",
    include_subfolders: bool = True,
    pdf_engine: str = "none",
    template_path: str | None = None,
    css_path: str | None = None,
    toc: bool = False,
    highlight_style: str = "tango",
    standalone: bool = True,
    self_contained: bool = True,
    project: str | None = None,
    show_after_export: bool = True,
) -> str:
    """
    Export Advanced Memory notes to various formats using Pandoc.

    This tool provides automated, batch document export capabilities
    that surpass Typora's GUI-only limitations with full CLI automation.

    Parameters:
    - export_path: Directory path where exported files will be saved
    - format_type: Output format (pdf, html, docx, odt, rtf, tex, epub, etc.)
    - source_folder: Advanced Memory folder to export from (default: "/")
    - include_subfolders: Include notes from subfolders (default: True)
    - pdf_engine: DEPRECATED - PDF not supported, use adn_export("pdf") instead
    - template_path: Path to custom Pandoc template file
    - css_path: Path to custom CSS file (defaults to water.css dark mode)
    - toc: Generate table of contents (default: False)
    - highlight_style: Syntax highlighting style (tango, pygments, kate, etc.)
    - standalone: Generate standalone document with headers (default: True)
    - self_contained: Embed resources in output (default: True for HTML)
    - project: Specific Advanced Memory project to export from
    - show_after_export: Open exported file/folder when done (default: True)

    Supported Formats:
    - pdf: NOT SUPPORTED - Use adn_export("pdf") instead (fpdf2, no LaTeX!)
    - html: HTML page (with embedded resources and dark CSS by default)
    - docx: Microsoft Word document
    - odt: OpenDocument Text
    - rtf: Rich Text Format
    - tex: LaTeX source
    - epub: EPUB ebook
    - txt: Plain text

    PDF Export Notes:
    - Default engine is weasyprint (pure Python, already installed!)
    - No external dependencies required
    - Alternative: wkhtmltopdf (needs separate install)
    - Alternative: LaTeX engines for advanced typography

    HTML Export Notes:
    - Uses --embed-resources for self-contained files
    - Default CSS: water.css dark mode (beautiful, minimal)
    - Custom CSS path supported

    Examples:
    - Export all notes as PDF: export_pandoc("/exports", "pdf")
    - Export as HTML with TOC: export_pandoc("/exports", "html", toc=True)
    - Export as Word: export_pandoc("/exports", "docx")
    - Use wkhtmltopdf: export_pandoc("/exports", "pdf", pdf_engine="wkhtmltopdf")
    - Use LaTeX: export_pandoc("/exports", "pdf", pdf_engine="xelatex")

    Returns:
    Summary of export operation with file counts and any errors encountered.
    """
    try:
        # Reject PDF format - use native PDF export instead (fpdf2, no LaTeX!)
        if format_type == "pdf":
            return """# PDF Export Not Supported via Pandoc

PDF export has been moved to the native PDF export tool using **fpdf2** - pure Python, no LaTeX needed!

**Use this instead:**
```python
adn_export("pdf", export_path="...", source_folder="...")
```

**Why?**
- ✅ No 2GB LaTeX installation required
- ✅ No weasyprint dependencies
- ✅ Pure Python - works immediately
- ✅ Lightweight and fast

**Pandoc still supports these formats:**
- docx: Word documents
- html: HTML pages
- epub: eBooks
- odt: OpenDocument Text
- rtf: Rich Text Format
- And 40+ other formats (but NOT PDF)
"""

        # Create export directory
        export_dir = Path(export_path)
        export_dir.mkdir(parents=True, exist_ok=True)

        # Find all notes in the specified folder
        notes_data = await _get_notes_from_folder(source_folder, include_subfolders, project)

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
                    self_contained,
                )
                if output_file:
                    exported_files.append(output_file)
                else:
                    errors.append(f"Failed to export: {note_info['title']}")
            except Exception as e:
                errors.append(f"Error exporting {note_info['title']}: {e!s}")

        # Generate summary
        summary = _generate_export_summary(exported_files, errors, format_type, export_path)

        # Open exported files if requested
        if show_after_export and exported_files:
            from advanced_memory.utils.file_opener import format_open_result, open_file_or_folder

            export_dir = Path(export_path)
            # Open the first file (or the folder if multiple)
            if len(exported_files) == 1:
                success, msg = open_file_or_folder(exported_files[0])
                summary += "\n\n" + format_open_result(success, msg, exported_files[0])
            else:
                # Multiple files - open the folder
                success, msg = open_file_or_folder(export_dir)
                summary += (
                    f"\n\n## 🚀 Opened Folder\n\n✅ Opened {len(exported_files)} files in file explorer: {export_dir}"
                )

        return summary

    except Exception as e:
        return f"Pandoc export failed: {e!s}"


async def _get_notes_from_folder(
    source_folder: str, include_subfolders: bool, project: str | None = None
) -> list[dict[str, Any]]:
    """
    Retrieve all notes from the specified folder using the search API.
    """
    try:
        # Use same working pattern as export_html_notes
        from advanced_memory.mcp.project_session import get_active_project
        from advanced_memory.schemas.search import SearchResponse

        active_project = get_active_project(project)
        project_url = active_project.project_url

        # Use wildcard search to get all notes (same as HTML export)
        query = SearchQuery(text="*")  # Use wildcard instead of empty string

        response = await call_post(
            client,
            f"{project_url}/search/",  # Use project URL endpoint
            params={"page": 1, "page_size": 1000},
            json=query.model_dump(),
        )

        if not response:
            return []

        search_result = SearchResponse.model_validate(response.json())

        notes_data = []
        for note in search_result.results:
            # Filter by folder path
            note_path = note.file_path

            # Check if note is in the requested folder
            if include_subfolders:
                # Include notes in subfolders
                folder_matches = note_path.startswith(source_folder.lstrip("/"))
            else:
                # Only notes directly in the folder
                note_folder = "/".join(note_path.split("/")[:-1])
                folder_matches = note_folder == source_folder.lstrip("/")

            if folder_matches and note_path.endswith(".md"):
                # Get full note content
                content = await _get_note_content(note)
                if content:
                    notes_data.append(
                        {
                            "id": note.id if hasattr(note, "id") else "",
                            "title": note.title,
                            "file_path": note_path,
                            "content": content,
                        }
                    )

        return notes_data

    except Exception as e:
        logger.error(f"Error retrieving notes: {e}")
        return []


async def _get_note_content(note) -> str | None:
    """
    Retrieve the full content of a note.
    """
    try:
        # Use the read_note tool to get content
        from advanced_memory.mcp.tools.read_note import read_note

        # Get the identifier (prefer permalink, fallback to title)
        identifier = getattr(note, "permalink", None) or getattr(note, "title", "")

        if not identifier:
            return None

        content = await (read_note.fn if hasattr(read_note, "fn") else read_note)(identifier)
        return content if content else None

    except Exception as e:
        logger.error(f"Error reading note content: {e}")
        return None


async def _export_single_note(
    note_info: dict[str, Any],
    export_dir: Path,
    format_type: str,
    pdf_engine: str,
    template_path: str | None,
    css_path: str | None,
    toc: bool,
    highlight_style: str,
    standalone: bool,
    self_contained: bool,
) -> str | None:
    """
    Export a single note using Pandoc.
    """
    try:
        # Create safe filename
        safe_title = _sanitize_filename(note_info["title"])
        output_filename = f"{safe_title}.{format_type}"
        output_path = export_dir / output_filename

        # Create temporary markdown file
        temp_md_path = export_dir / f"{safe_title}_temp.md"
        with open(temp_md_path, "w", encoding="utf-8") as f:
            f.write(note_info["content"])

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
            self_contained,
        )

        # Execute Pandoc
        result = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=str(export_dir),
        )

        stdout, stderr = await result.communicate()

        # Clean up temporary file
        temp_md_path.unlink(missing_ok=True)

        if result.returncode == 0:
            return str(output_path)
        else:
            error_msg = stderr.decode("utf-8", errors="ignore")
            logger.error(f"Pandoc error for {note_info['title']}: {error_msg}")
            return None

    except Exception as e:
        logger.error(f"Error exporting note {note_info['title']}: {e}")
        return None


def _build_pandoc_command(
    input_path: str,
    output_path: str,
    format_type: str,
    pdf_engine: str,
    template_path: str | None,
    css_path: str | None,
    toc: bool,
    highlight_style: str,
    standalone: bool,
    self_contained: bool,
) -> list[str]:
    """
    Build the Pandoc command with all specified options.

    Pandoc is auto-installed on first use if not found.

    PDF Export Strategy:
    - Default: weasyprint (pure Python, already installed as dependency)
    - Alternative: wkhtmltopdf (needs separate install)
    - Alternative: LaTeX engines (pdflatex, xelatex, lualatex) for advanced typography

    HTML Export Strategy:
    - Uses --embed-resources for self-contained output (replaces deprecated --self-contained)
    - Default dark-mode CSS from water.css CDN if no custom CSS specified
    """
    import shutil

    # Get pandoc executable (auto-installs if needed)
    try:
        cmd = get_pandoc_command()
        cmd.extend([input_path, "-o", output_path])
    except Exception as e:
        logger.error(f"Failed to get Pandoc: {e}")
        raise RuntimeError(
            f"Pandoc is required for export but could not be installed: {e}\n\n"
            "Please install manually from: https://pandoc.org/installing.html"
        )

    # Format specification
    if format_type == "pdf":
        if pdf_engine == "weasyprint":
            # weasyprint is pure Python, already in our dependencies
            # Pandoc calls it directly - no path lookup needed
            cmd.extend(["--pdf-engine", "weasyprint"])
        elif pdf_engine == "wkhtmltopdf":
            # wkhtmltopdf needs to be found in PATH or standard locations
            wkhtmltopdf_path = shutil.which("wkhtmltopdf")
            if not wkhtmltopdf_path:
                # Try common install locations on Windows
                import os

                program_files = os.environ.get("ProgramFiles", "C:\\Program Files")
                wkhtmltopdf_bin = Path(program_files) / "wkhtmltopdf" / "bin" / "wkhtmltopdf.exe"
                if wkhtmltopdf_bin.exists():
                    wkhtmltopdf_path = str(wkhtmltopdf_bin)
                else:
                    raise RuntimeError(
                        "wkhtmltopdf not found. Install from: https://wkhtmltopdf.org/downloads.html\n"
                        "Or use pdf_engine='weasyprint' (default, pure Python)"
                    )
            cmd.extend(["--pdf-engine", wkhtmltopdf_path])
        else:
            # LaTeX-based engines (pdflatex, xelatex, lualatex)
            cmd.extend(["--pdf-engine", pdf_engine])

        # Add sensible margin defaults for HTML-based engines
        if pdf_engine in ("weasyprint", "wkhtmltopdf"):
            cmd.extend(["-V", "margin-top=15mm"])
            cmd.extend(["-V", "margin-bottom=15mm"])
            cmd.extend(["-V", "margin-left=15mm"])
            cmd.extend(["-V", "margin-right=15mm"])
    else:
        cmd.extend(["-t", format_type])

    # Standalone document
    if standalone:
        cmd.append("-s")

    # Table of contents
    if toc:
        if format_type == "docx":
            # Use Lua filter for native Word TOC (clickable, no "external files" popup)
            import importlib.resources

            try:
                # Python 3.9+
                with importlib.resources.files("advanced_memory.resources.pandoc") as pandoc_res:
                    lua_filter = pandoc_res / "word-toc.lua"
                    if lua_filter.exists():
                        cmd.extend(["--lua-filter", str(lua_filter)])
                    else:
                        # Fallback to Pandoc's built-in TOC (may cause popup)
                        cmd.append("--toc")
                        cmd.extend(["--toc-depth", "3"])
            except Exception:
                # Fallback
                cmd.append("--toc")
                cmd.extend(["--toc-depth", "3"])
        else:
            cmd.append("--toc")
            cmd.extend(["--toc-depth", "3"])

    # Syntax highlighting
    if highlight_style:
        cmd.extend(["--highlight-style", highlight_style])

    # Custom template
    if template_path and Path(template_path).exists():
        cmd.extend(["--template", template_path])

    # CSS for HTML output (or PDF via HTML-based engines)
    if format_type == "html" or (format_type == "pdf" and pdf_engine in ("weasyprint", "wkhtmltopdf")):
        if css_path and Path(css_path).exists():
            cmd.extend(["--css", css_path])
        else:
            # Default to water.css dark mode for nice styling
            cmd.extend(["--css", "https://cdn.jsdelivr.net/npm/water.css@2/out/dark.min.css"])

    # Self-contained / embedded resources for HTML
    if self_contained and format_type == "html":
        # Use --embed-resources (Pandoc 2.19+) instead of deprecated --self-contained
        cmd.append("--embed-resources")

    return cmd


def _sanitize_filename(title: str) -> str:
    """
    Create a safe filename from note title.
    """
    import re
    import unicodedata

    # Normalize unicode characters
    title = unicodedata.normalize("NFKD", title)

    # Replace problematic characters
    title = title.replace(":", "-").replace(".", "_").replace("/", "-")

    # Remove or replace other unsafe characters
    title = re.sub(r'[<>:"|?*\\]', "_", title)

    # Collapse multiple underscores/spaces
    title = re.sub(r"[_ ]+", "_", title)

    # Trim underscores and spaces
    title = title.strip("_ ")

    # Limit length
    if len(title) > 100:
        title = title[:100].rstrip("_ ")

    # Ensure not empty
    if not title:
        title = "untitled"

    return title


def _generate_export_summary(exported_files: list[str], errors: list[str], format_type: str, export_path: str) -> str:
    """
    Generate a summary of the export operation.
    """
    lines = [
        "# Pandoc Export Summary",
        "",
        f"**Format:** {format_type.upper()}",
        f"**Output Directory:** {export_path}",
        f"**Files Exported:** {len(exported_files)}",
        f"**Errors:** {len(errors)}",
        "",
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

    lines.extend(
        [
            "## Next Steps:",
            f"- Check the `{export_path}` directory for exported files",
            f"- Open {format_type.upper()} files with appropriate applications",
            "- For PDF: Requires PDF viewer (Adobe Reader, etc.)",
            "- For DOCX: Requires Word or compatible viewer",
            "- For HTML: Open in any web browser",
            "",
        ]
    )

    return "\n".join(lines)
