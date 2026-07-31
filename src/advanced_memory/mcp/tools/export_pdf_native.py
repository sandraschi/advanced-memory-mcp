"""
Native PDF export using fpdf2 - Pure Python, NO LaTeX!

This tool provides lightweight PDF generation from Markdown without requiring
LaTeX, weasyprint, or any heavy dependencies.
"""

from pathlib import Path
from typing import Any

from loguru import logger

from advanced_memory.mcp.mcp_instance import mcp
from advanced_memory.mcp.tools.utils import call_post
from advanced_memory.schemas.search import SearchQuery

# Try to import fpdf2
try:
    from fpdf import FPDF

    FPDF_AVAILABLE = True
except ImportError as e:
    logger.error(f"fpdf2 not installed: {e}")
    FPDF = None
    FPDF_AVAILABLE = False

if FPDF_AVAILABLE:

    class MarkdownPDF(FPDF):
        """PDF generator that handles markdown content."""

        def __init__(self, title: str = "Advanced Memory Export"):
            super().__init__()
            self.title = title
            self.set_auto_page_break(auto=True, margin=15)

        @staticmethod
        def _sanitize(text: object) -> str:
            """Replace characters the core fonts (latin-1) cannot encode."""
            s = str(text)
            try:
                s.encode("latin-1")
                return s
            except UnicodeEncodeError:
                return "".join(c if ord(c) < 256 else "?" for c in s)

        def cell(self, *args, **kwargs):
            if "text" in kwargs:
                kwargs["text"] = self._sanitize(kwargs["text"])
            elif len(args) >= 3 and isinstance(args[2], str):
                args = (*args[:2], self._sanitize(args[2]), *args[3:])
            return super().cell(*args, **kwargs)

        def multi_cell(self, *args, **kwargs):
            if "text" in kwargs:
                kwargs["text"] = self._sanitize(kwargs["text"])
            elif len(args) >= 3 and isinstance(args[2], str):
                args = (*args[:2], self._sanitize(args[2]), *args[3:])
            return super().multi_cell(*args, **kwargs)

        def header(self):
            """Add header to each page."""
            self.set_font("Arial", "B", 15)
            self.cell(0, 10, self.title, 0, 1, "C")
            self.ln(5)

        def footer(self):
            """Add footer with page numbers."""
            self.set_y(-15)
            self.set_font("Arial", "I", 8)
            self.cell(0, 10, f"Page {self.page_no()}", 0, 0, "C")

        def add_markdown(self, md_content: str):
            """Add markdown content to PDF."""
            lines = md_content.split("\n")
            in_code_block = False
            code_lines = []

            for line in lines:
                # Code blocks
                if line.strip().startswith("```"):
                    if in_code_block:
                        # End code block
                        self.set_font("Courier", "", 9)
                        self.set_fill_color(240, 240, 240)
                        code_text = "\n".join(code_lines)
                        self.multi_cell(0, 5, code_text, border=0, fill=True)
                        code_lines = []
                        in_code_block = False
                        self.ln(2)
                    else:
                        # Start code block
                        in_code_block = True
                    continue

                if in_code_block:
                    code_lines.append(line)
                    continue

                # Headers
                if line.startswith("# "):
                    self.set_font("Arial", "B", 24)
                    self.cell(0, 12, line[2:].strip(), ln=1)
                    self.ln(2)
                elif line.startswith("## "):
                    self.set_font("Arial", "B", 18)
                    self.cell(0, 10, line[3:].strip(), ln=1)
                    self.ln(2)
                elif line.startswith("### "):
                    self.set_font("Arial", "B", 14)
                    self.cell(0, 8, line[4:].strip(), ln=1)
                    self.ln(1)
                elif line.startswith("#### "):
                    self.set_font("Arial", "B", 12)
                    self.cell(0, 7, line[5:].strip(), ln=1)
                    self.ln(1)
                # Lists
                elif line.strip().startswith("- ") or line.strip().startswith("* "):
                    self.set_font("Arial", "", 12)
                    self.cell(10)
                    bullet_text = line.strip()[2:]
                    # Remove markdown formatting for now
                    bullet_text = bullet_text.replace("**", "").replace("__", "")
                    self.cell(0, 6, "- " + bullet_text, ln=1)
                # Numbered lists
                elif line.strip() and line.strip()[0].isdigit() and ". " in line[:5]:
                    self.set_font("Arial", "", 12)
                    self.cell(10)
                    list_text = line.strip().split(". ", 1)[1] if ". " in line else line.strip()
                    list_text = list_text.replace("**", "").replace("__", "")
                    self.cell(0, 6, list_text, ln=1)
                # Horizontal rule
                elif line.strip() in ("---", "***", "___"):
                    self.ln(3)
                    self.line(10, self.get_y(), 200, self.get_y())
                    self.ln(3)
                # Regular text
                elif line.strip():
                    self.set_font("Arial", "", 12)
                    # Handle basic formatting
                    text = line.strip()
                    text = text.replace("**", "").replace("__", "")  # Remove formatting for now
                    self.multi_cell(0, 6, text, align="L")
                    self.ln(1)
                else:
                    # Empty line
                    self.ln(2)
else:
    # Dummy class when fpdf2 is not available
    class MarkdownPDF:
        def __init__(self, *args, **kwargs):
            raise ImportError("fpdf2 is not installed. Run: pip install fpdf2")


# @mcp.tool
async def export_pdf_native(
    export_path: str,
    source_folder: str = "/",
    include_subfolders: bool = True,
    project: str | None = None,
    search_query: str | None = None,
    combine_into_one: bool = False,
    pdf_title: str | None = None,
    make_toc: bool = True,
) -> str:
    """
    Export Advanced Memory notes to PDF using fpdf2 (pure Python, no LaTeX!).

    This tool provides lightweight PDF generation without requiring LaTeX,
    weasyprint, or any heavy dependencies. Perfect for quick PDF exports.

    Args:
        export_path: Directory path where exported PDFs will be saved (or file path if combine_into_one=True)
        source_folder: Advanced Memory folder to export from (default: "/")
        include_subfolders: Include notes from subfolders (default: True)
        project: Specific Advanced Memory project to export from
        search_query: Optional search query to find notes (e.g., "docker", "python")
        combine_into_one: If True, combine all notes into a single PDF with TOC
        pdf_title: Title for combined PDF (only used when combine_into_one=True)
        make_toc: If True, add clickable table of contents page to combined PDF (default: True).
                  Bookmarks are always added for navigation regardless of this setting.

    Returns:
        Summary of export operation with file counts and any errors encountered.
    """
    # Check if fpdf2 is available
    if not FPDF_AVAILABLE:
        return """# fpdf2 Not Installed

The PDF export requires fpdf2 to be installed in the server's Python environment.

**Installation:**
```powershell
pip install fpdf2
```

**Or if using a specific Python:**
```powershell
py -3.13 -m pip install fpdf2
python -m pip install fpdf2
```

After installing, restart the MCP server.

**Note:** fpdf2 has been added to requirements.txt, but you may need to install it manually if the server uses a different Python environment.
"""

    try:
        # Get notes based on search query or folder
        if search_query:
            notes_data = await _search_notes(search_query, project)
        else:
            notes_data = await _get_notes_from_folder(source_folder, include_subfolders, project)

        if not notes_data:
            query_desc = f"query '{search_query}'" if search_query else f"folder '{source_folder}'"
            return f"No notes found matching {query_desc} for export."

        # Combine into one PDF with TOC if requested
        if combine_into_one:
            return await _export_combined_pdf(notes_data, export_path, pdf_title or "Combined Notes", make_toc)

        # Otherwise, export each note as separate PDF
        export_dir = Path(export_path)
        export_dir.mkdir(parents=True, exist_ok=True)

        exported_files = []
        errors = []

        for note_info in notes_data:
            try:
                output_file = await _export_single_note_pdf(note_info, export_dir)
                if output_file:
                    exported_files.append(output_file)
                else:
                    errors.append(f"Failed to export: {note_info['title']}")
            except Exception as e:
                logger.error(f"Error exporting {note_info['title']}: {e}")
                errors.append(f"Error exporting {note_info['title']}: {e!s}")

        # Generate summary
        summary = "# PDF Export Summary\n\n"
        summary += "**Format:** PDF (fpdf2 - pure Python, no LaTeX!)\n"
        summary += f"**Output Directory:** {export_path}\n"
        summary += f"**Files Exported:** {len(exported_files)}\n"

        if errors:
            summary += f"**Errors:** {len(errors)}\n\n"
            summary += "## Errors:\n"
            for error in errors:
                summary += f"- {error}\n"

        if exported_files:
            summary += "\n## Exported Files:\n"
            for file_path in exported_files[:10]:  # Show first 10
                summary += f"- {Path(file_path).name}\n"
            if len(exported_files) > 10:
                summary += f"\n... and {len(exported_files) - 10} more files\n"

        summary += "\n## Next Steps:\n"
        summary += "- Check the export directory for PDF files\n"
        summary += "- Open PDF files with any PDF viewer\n"

        return summary

    except Exception as e:
        logger.error(f"PDF export failed: {e}")
        return f"PDF export failed: {e!s}"


async def _export_single_note_pdf(note_info: dict[str, Any], export_dir: Path) -> str | None:
    """Export a single note to PDF."""
    try:
        # Get note content
        note_content = note_info.get("content", "")
        note_title = note_info.get("title", "Untitled")

        # Create PDF
        pdf = MarkdownPDF(title=note_title)
        pdf.add_page()
        pdf.add_markdown(note_content)

        # Sanitize filename
        safe_title = "".join(c for c in note_title if c.isalnum() or c in (" ", "-", "_")).strip()
        safe_title = safe_title.replace(" ", "_")
        if not safe_title:
            safe_title = "untitled"
        # Truncate to stay within Windows path limits
        safe_title = safe_title[:80].rstrip("._ ")

        output_path = export_dir / f"{safe_title}.pdf"
        pdf.output(str(output_path))

        if output_path.exists():
            logger.info(f"Exported PDF: {output_path}")
            return str(output_path)
        else:
            logger.error(f"PDF file not created: {output_path}")
            return None

    except Exception as e:
        logger.error(f"Error exporting note to PDF: {e}")
        return None


async def _search_notes(query: str, project: str | None = None) -> list[dict[str, Any]]:
    """Search for notes by query."""
    try:
        search_query = SearchQuery(
            query=query,
            search_type="text",
            page=1,
            page_size=1000,  # Large limit
        )

        response = await call_post("/search/notes", search_query.model_dump(mode="json"))
        notes = response.get("results", [])

        # Convert to expected format
        notes_data = []
        for note in notes:
            notes_data.append(
                {
                    "title": note.get("title", "Untitled"),
                    "content": note.get("content", ""),
                    "permalink": note.get("permalink", ""),
                }
            )

        return notes_data

    except Exception as e:
        logger.error(f"Error searching notes: {e}")
        return []


async def _export_combined_pdf(
    notes_data: list[dict[str, Any]],
    export_path: str,
    pdf_title: str,
    make_toc: bool = True,
) -> str:
    """Export multiple notes into a single PDF with optional clickable TOC."""
    try:
        from fpdf.outline import TableOfContents

        # Create combined PDF class with TOC support
        class CombinedPDF(FPDF):
            def __init__(self, title: str):
                super().__init__()
                self.title = title
                self.set_auto_page_break(auto=True, margin=15)

            def header(self):
                """Add header to each page."""
                self.set_font("Arial", "B", 15)
                self.cell(0, 10, self.title, 0, 1, "C")
                self.ln(5)

            def footer(self):
                """Add footer with page numbers."""
                self.set_y(-15)
                self.set_font("Arial", "I", 8)
                self.cell(0, 10, f"Page {self.page_no()}", 0, 0, "C")

            def add_markdown(self, md_content: str):
                """Add markdown content to PDF."""
                lines = md_content.split("\n")
                in_code_block = False
                code_lines = []

                for line in lines:
                    if line.strip().startswith("```"):
                        if in_code_block:
                            self.set_font("Courier", "", 9)
                            self.set_fill_color(240, 240, 240)
                            code_text = "\n".join(code_lines)
                            self.multi_cell(0, 5, code_text, border=0, fill=True)
                            code_lines = []
                            in_code_block = False
                            self.ln(2)
                        else:
                            in_code_block = True
                        continue

                    if in_code_block:
                        code_lines.append(line)
                        continue

                    if line.startswith("# "):
                        self.set_font("Arial", "B", 24)
                        self.cell(0, 12, line[2:].strip(), ln=1)
                        self.ln(2)
                    elif line.startswith("## "):
                        self.set_font("Arial", "B", 18)
                        self.cell(0, 10, line[3:].strip(), ln=1)
                        self.ln(2)
                    elif line.startswith("### "):
                        self.set_font("Arial", "B", 14)
                        self.cell(0, 8, line[4:].strip(), ln=1)
                        self.ln(1)
                    elif line.strip().startswith("- ") or line.strip().startswith("* "):
                        self.set_font("Arial", "", 12)
                        self.cell(10)
                        bullet_text = line.strip()[2:].replace("**", "").replace("__", "")
                        self.cell(0, 6, "- " + bullet_text, ln=1)
                    elif line.strip():
                        self.set_font("Arial", "", 12)
                        text = line.strip().replace("**", "").replace("__", "")
                        self.multi_cell(0, 6, text, align="L")
                        self.ln(1)
                    else:
                        self.ln(2)

        pdf = CombinedPDF(title=pdf_title)

        # Add title page
        pdf.add_page()
        pdf.set_font("Arial", "B", 24)
        pdf.cell(0, 40, pdf_title, 0, 1, "C")
        pdf.ln(20)
        pdf.set_font("Arial", "", 12)
        pdf.cell(0, 8, f"Generated from {len(notes_data)} notes", 0, 1, "C")
        pdf.ln(20)

        # Insert TOC placeholder if requested (will be populated after sections are added)
        if make_toc:
            toc = TableOfContents()
            pdf.page_no()
            pdf.insert_toc_placeholder(toc.render_toc, pages=1)

        # Add each note as a section with bookmark
        for note_info in notes_data:
            note_title = note_info.get("title", "Untitled")
            note_content = note_info.get("content", "")

            # Start section for bookmark/TOC
            pdf.start_section(note_title, level=0)

            # Add note title as H1
            pdf.ln(10)
            pdf.set_font("Arial", "B", 20)
            pdf.cell(0, 12, note_title, ln=1)
            pdf.ln(5)

            # Add note content
            pdf.add_markdown(note_content)

            # Add separator between notes
            pdf.ln(10)

        # Save PDF
        export_path_obj = Path(export_path)
        export_path_obj.parent.mkdir(parents=True, exist_ok=True)

        # Ensure .pdf extension
        if not export_path_obj.suffix.lower() == ".pdf":
            export_path_obj = export_path_obj.with_suffix(".pdf")

        pdf.output(str(export_path_obj))

        if export_path_obj.exists():
            file_size = export_path_obj.stat().st_size
            toc_status = "✅ Clickable table of contents\n" if make_toc else ""
            return f"""# Combined PDF Export Complete ✅

**PDF Created:** `{export_path_obj}`
**Title:** {pdf_title}
**Notes Combined:** {len(notes_data)}
**File Size:** {file_size:,} bytes ({file_size / 1024:.1f} KB)

## Features:
{toc_status}- ✅ Bookmarks for navigation
- ✅ All notes in single PDF
- ✅ Professional formatting

**Ready to use!**{" Open the PDF to see the clickable TOC." if make_toc else ""}"""
        else:
            return f"Error: PDF file was not created at {export_path_obj}"

    except Exception as e:
        logger.error(f"Combined PDF export failed: {e}")
        import traceback

        logger.error(traceback.format_exc())
        return f"Combined PDF export failed: {e!s}"


async def _get_notes_from_folder(
    source_folder: str,
    include_subfolders: bool,
    project: str | None = None,
) -> list[dict[str, Any]]:
    """Get all notes from a folder."""
    try:
        # Build search query for folder
        folder_path = source_folder.rstrip("/")
        if folder_path == "/":
            folder_path = ""

        # Use search to find notes in folder
        query = SearchQuery(
            query=f'folder:"{folder_path}"' if folder_path else "*",
            search_type="text",
            page=1,
            page_size=1000,  # Large limit
        )

        response = await call_post("/search/notes", query.model_dump(mode="json"))
        notes = response.get("results", [])

        # Filter by folder if needed
        if folder_path:
            filtered_notes = []
            for note in notes:
                permalink = note.get("permalink", "")
                if include_subfolders:
                    if permalink.startswith(folder_path):
                        filtered_notes.append(note)
                else:
                    # Only direct children
                    rel_path = permalink[len(folder_path) :].lstrip("/")
                    if "/" not in rel_path:  # No subfolder in path
                        filtered_notes.append(note)
            notes = filtered_notes

        # Convert to format expected by export
        notes_data = []
        for note in notes:
            notes_data.append(
                {
                    "title": note.get("title", "Untitled"),
                    "content": note.get("content", ""),
                    "permalink": note.get("permalink", ""),
                }
            )

        return notes_data

    except Exception as e:
        logger.error(f"Error getting notes from folder: {e}")
        return []
