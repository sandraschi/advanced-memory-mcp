"""
Combined PDF export with clickable TOC - Multiple notes in one PDF.

This tool creates a single PDF from multiple notes with:
- Search query support (e.g., "docker")
- Table of contents (clickable)
- Bookmarks for navigation
- Combined content from all matching notes
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

    class CombinedMarkdownPDF(FPDF):
        """PDF generator that combines multiple notes with TOC."""

        def __init__(self, title: str = "Advanced Memory Combined Export"):
            super().__init__()
            self.title = title
            self.set_auto_page_break(auto=True, margin=15)
            self._section_links = {}  # Store links for TOC

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
                    bullet_text = line.strip()[2:].replace("**", "").replace("__", "")
                    self.cell(0, 6, "• " + bullet_text, ln=1)
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
                    text = line.strip().replace("**", "").replace("__", "")
                    self.multi_cell(0, 6, text, align="L")
                    self.ln(1)
                else:
                    self.ln(2)

        def add_note_section(self, note_title: str, note_content: str):
            """Add a note as a section with bookmark."""
            # Create bookmark for this note
            self.start_section(note_title, level=0)

            # Add note title as H1
            self.ln(10)
            self.set_font("Arial", "B", 20)
            self.cell(0, 12, note_title, ln=1)
            self.ln(5)

            # Add note content
            self.add_markdown(note_content)

            # Add page break between notes
            self.ln(10)


# @mcp.tool
async def export_pdf_combined(
    export_path: str,
    search_query: str | None = None,
    source_folder: str | None = None,
    pdf_title: str | None = None,
    include_subfolders: bool = True,
    project: str | None = None,
) -> str:
    """
    Export multiple notes into a single PDF with clickable table of contents.

    Perfect for creating comprehensive documents from related notes.
    Example: Search for "docker" notes and combine into one PDF book.

    Args:
        export_path: File path where the combined PDF will be saved
        search_query: Search query to find notes (e.g., "docker", "python")
        source_folder: Optional folder to search within (overrides search_query)
        pdf_title: Title for the combined PDF (default: auto-generated)
        include_subfolders: Include subfolders when using source_folder
        project: Specific Advanced Memory project to export from

    Returns:
        Summary of export operation with PDF details.
    """
    if not FPDF_AVAILABLE:
        return """# fpdf2 Not Installed

The PDF export requires fpdf2 to be installed in the server's Python environment.

**Installation:**
```powershell
pip install fpdf2
```

After installing, restart the MCP server.
"""

    try:
        # Get notes based on search query or folder
        if source_folder:
            notes_data = await _get_notes_from_folder(source_folder, include_subfolders, project)
        elif search_query:
            notes_data = await _search_notes(search_query, project)
        else:
            return "Error: Either 'search_query' or 'source_folder' must be provided."

        if not notes_data:
            query_desc = f"query '{search_query}'" if search_query else f"folder '{source_folder}'"
            return f"No notes found matching {query_desc}."

        # Generate PDF title if not provided
        if not pdf_title:
            if search_query:
                pdf_title = f"Notes: {search_query.title()}"
            elif source_folder:
                folder_name = source_folder.strip("/").split("/")[-1] or "All Notes"
                pdf_title = f"Notes: {folder_name.title()}"
            else:
                pdf_title = "Advanced Memory Combined Export"

        # Create PDF with TOC
        pdf = CombinedMarkdownPDF(title=pdf_title)

        # Add title page
        pdf.add_page()
        pdf.set_font("Arial", "B", 24)
        pdf.cell(0, 40, pdf_title, 0, 1, "C")
        pdf.ln(20)
        pdf.set_font("Arial", "", 12)
        pdf.cell(0, 8, f"Generated from {len(notes_data)} notes", 0, 1, "C")
        pdf.ln(10)

        # Insert TOC placeholder (will be populated after all sections)
        from fpdf.outline import TableOfContents

        toc = TableOfContents()
        pdf.insert_toc_placeholder(toc.render_toc, pages=1)

        # Add each note as a section
        for note_info in notes_data:
            note_title = note_info.get("title", "Untitled")
            note_content = note_info.get("content", "")
            pdf.add_note_section(note_title, note_content)

        # Save PDF
        export_path_obj = Path(export_path)
        export_path_obj.parent.mkdir(parents=True, exist_ok=True)

        # Ensure .pdf extension
        if not export_path_obj.suffix.lower() == ".pdf":
            export_path_obj = export_path_obj.with_suffix(".pdf")

        pdf.output(str(export_path_obj))

        if export_path_obj.exists():
            file_size = export_path_obj.stat().st_size
            return f"""# Combined PDF Export Complete ✅

**PDF Created:** `{export_path_obj}`
**Title:** {pdf_title}
**Notes Combined:** {len(notes_data)}
**File Size:** {file_size:,} bytes ({file_size / 1024:.1f} KB)

## Features:
- ✅ Clickable table of contents
- ✅ Bookmarks for navigation
- ✅ All notes in single PDF
- ✅ Professional formatting

**Ready to use!** Open the PDF to see the clickable TOC."""
        else:
            return f"Error: PDF file was not created at {export_path_obj}"

    except Exception as e:
        logger.error(f"Combined PDF export failed: {e}")
        return f"PDF export failed: {e!s}"


async def _search_notes(query: str, project: str | None = None) -> list[dict[str, Any]]:
    """Search for notes by query."""
    try:
        search_query = SearchQuery(
            query=query,
            search_type="text",
            page=1,
            page_size=1000,  # Large limit for comprehensive export
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


async def _get_notes_from_folder(
    source_folder: str,
    include_subfolders: bool,
    project: str | None = None,
) -> list[dict[str, Any]]:
    """Get all notes from a folder."""
    try:
        folder_path = source_folder.rstrip("/")
        if folder_path == "/":
            folder_path = ""

        query = SearchQuery(
            query=f'folder:"{folder_path}"' if folder_path else "*",
            search_type="text",
            page=1,
            page_size=1000,
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
                    rel_path = permalink[len(folder_path) :].lstrip("/")
                    if "/" not in rel_path:
                        filtered_notes.append(note)
            notes = filtered_notes

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
        logger.error(f"Error getting notes from folder: {e}")
        return []
