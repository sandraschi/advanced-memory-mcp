"""PDF Book Creation Tool for Basic Memory MCP server.

Creates professional PDF books from Basic Memory notes with title pages,
table of contents, and chapter organization using Pandoc.
"""

import asyncio
import tempfile
from pathlib import Path
from typing import List, Optional, Dict, Any
from datetime import datetime

from advanced_memory.mcp.server import mcp
from advanced_memory.mcp.tools.utils import call_post
from advanced_memory.schemas.search import SearchQuery, SearchResponse


@mcp.tool(
    description="""📖 Create Professional PDF Books from Basic Memory Notes

Generates a complete PDF book with title page, table of contents, and chapters
from your Basic Memory notes. Perfect for creating documentation, research papers,
or knowledge base books.

BOOK FEATURES:
- Title page with book metadata (title, author, date)
- Automatic table of contents
- Chapter organization from notes
- Professional book formatting
- Custom styling and templates

WORKFLOW:
1. Select notes by folder, tags, or search criteria
2. Generate book structure with chapters
3. Create PDF with Pandoc (requires LaTeX)
4. Professional book-quality output

PARAMETERS:
- book_title (str, REQUIRED): Title for the PDF book
- source_folder (str, optional): Folder to get notes from (default: "/")
- tag_filter (str, optional): Filter notes by tag (e.g., "standards", "research")
- output_path (str, optional): Where to save the PDF (default: "pdf-books/")
- author (str, optional): Book author (default: "Basic Memory")
- include_subfolders (bool, optional): Include notes from subfolders (default: True)
- toc_depth (int, optional): TOC depth (1-3, default: 2)
- paper_size (str, optional): Paper size (a4, letter, default: a4)
- project (str, optional): Specific project to export from

RETURNS:
Success message with PDF location and book statistics.

EXAMPLES:
- Book from folder: make_pdf_book("My Notes", source_folder="/research")
- Book from tags: make_pdf_book("Standards Guide", tag_filter="standards")
- Combined: make_pdf_book("Research Standards", source_folder="/research", tag_filter="standards")

NOTE: Requires Pandoc and LaTeX (MiKTeX/TinyTeX) for PDF generation.
"""
)
async def make_pdf_book(
    book_title: str,
    source_folder: str = "/",
    tag_filter: Optional[str] = None,
    output_path: Optional[str] = None,
    author: str = "Basic Memory",
    include_subfolders: bool = True,
    toc_depth: int = 2,
    paper_size: str = "a4",
    project: Optional[str] = None
) -> str:
    """
    Create a professional PDF book from Basic Memory notes.

    Args:
        book_title: Title for the PDF book
        source_folder: Folder to get notes from
        tag_filter: Filter notes by tag (optional)
        output_path: Output directory for PDF
        author: Book author
        include_subfolders: Include subfolder notes
        toc_depth: Table of contents depth
        paper_size: Paper size (a4, letter)
        project: Specific project

    Returns:
        Success message with PDF details
    """
    try:
        # Setup output directory
        output_dir = Path(output_path) if output_path else Path("pdf-books")
        output_dir.mkdir(parents=True, exist_ok=True)

        # Create safe filename
        safe_title = _sanitize_filename(book_title)
        pdf_filename = f"{safe_title}.pdf"
        pdf_path = output_dir / pdf_filename

        # Get notes for the book
        notes_data = await _get_book_notes(source_folder, tag_filter, include_subfolders, project)
        if not notes_data:
            return f"❌ No notes found in folder '{source_folder}' for book creation."

        # Create temporary book markdown file
        book_md_path = await _create_book_markdown(
            notes_data, book_title, author, output_dir
        )

        # Generate PDF book with Pandoc
        success = await _generate_pdf_book(
            book_md_path, pdf_path, toc_depth, paper_size
        )

        # Clean up temporary file
        book_md_path.unlink(missing_ok=True)

        if success:
            # Calculate book statistics
            total_pages = _estimate_page_count(notes_data)
            total_words = sum(len(note['content'].split()) for note in notes_data)

            return f"""✅ **PDF Book Created Successfully!**

📖 **Book Details:**
- **Title:** {book_title}
- **Author:** {author}
- **Chapters:** {len(notes_data)}
- **Estimated Pages:** {total_pages}
- **Word Count:** {total_words:,}
- **Paper Size:** {paper_size.upper()}

📁 **Files:**
- **PDF Location:** `{pdf_path}`
- **Size:** {_get_file_size(pdf_path)}

📚 **Book Features:**
- ✅ Professional title page
- ✅ Table of contents (depth: {toc_depth})
- ✅ Chapter-based organization
- ✅ Proper page formatting
- ✅ Book-style layout

**Ready to share your knowledge book!** 🎉📖"""
        else:
            return "❌ PDF book creation failed. Check that Pandoc and LaTeX are installed."

    except Exception as e:
        return f"❌ Error creating PDF book: {str(e)}"


async def _get_book_notes(
    source_folder: str,
    tag_filter: Optional[str],
    include_subfolders: bool,
    project: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Get notes for the book, sorted by title for chapter order.
    """
    try:
        # Get all notes from the folder (with optional tag filtering)
        notes_data = await _get_notes_from_folder(source_folder, tag_filter, include_subfolders, project)

        if not notes_data:
            return []

        # Sort notes by title for consistent chapter order
        notes_data.sort(key=lambda x: x['title'].lower())

        return notes_data

    except Exception as e:
        print(f"Error getting book notes: {e}")
        return []


async def _get_notes_from_folder(
    source_folder: str,
    tag_filter: Optional[str],
    include_subfolders: bool,
    project: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Retrieve all notes from the specified folder using the search API.
    """
    try:
        # Use search API to find notes (exclude entities for book chapters)
        if tag_filter:
            # Search for notes with specific tag
            query = SearchQuery(
                text=f"tag:{tag_filter}",  # Search for notes tagged with the specified tag
                types=["note"],  # Only notes, not entities
                page=1,
                page_size=1000  # Large limit for book creation
            )
        else:
            # Search all notes (will be filtered by folder below)
            query = SearchQuery(
                query="",  # Empty query to get all notes
                types=["note"],  # Only notes, not entities
                page=1,
                page_size=1000  # Large limit for book creation
            )

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
        from advanced_memory.mcp.tools.read_note import read_note

        # Get the identifier (prefer permalink, fallback to title)
        identifier = getattr(note, 'permalink', None) or getattr(note, 'title', '')

        if not identifier:
            return None

        content = await read_note(identifier)
        return content if content else None

    except Exception as e:
        print(f"Error reading note content: {e}")
        return None


async def _create_book_markdown(
    notes_data: List[Dict[str, Any]],
    book_title: str,
    author: str,
    output_dir: Path
) -> Path:
    """
    Create a temporary markdown file with book structure.
    """
    book_md_path = output_dir / "temp_book.md"

    with open(book_md_path, 'w', encoding='utf-8') as f:
        # Write YAML metadata for title page
        f.write("---\n")
        f.write(f"title: {book_title}\n")
        f.write(f"author: {author}\n")
        f.write(f"date: {datetime.now().strftime('%B %d, %Y')}\n")
        f.write("geometry: margin=1in\n")
        f.write("documentclass: book\n")
        f.write("fontsize: 11pt\n")
        f.write("linestretch: 1.2\n")
        f.write("colorlinks: true\n")
        f.write("linkcolor: blue\n")
        f.write("urlcolor: blue\n")
        f.write("citecolor: green\n")
        f.write("---\n\n")

        # Add title page content
        f.write("\\frontmatter\n\n")
        f.write("# Title Page\n\n")
        f.write(f"## {book_title}\n\n")
        f.write(f"**Author:** {author}\n\n")
        f.write(f"**Generated:** {datetime.now().strftime('%B %d, %Y')}\n\n")
        f.write("**Created with Basic Memory & Pandoc**\n\n")
        f.write("\\newpage\n\n")

        # Table of contents
        f.write("# Table of Contents\n\n")
        f.write("\\tableofcontents\n\n")
        f.write("\\newpage\n\n")

        # Main content
        f.write("\\mainmatter\n\n")

        # Add each note as a chapter
        for i, note in enumerate(notes_data, 1):
            f.write(f"# Chapter {i}: {note['title']}\n\n")

            # Clean up the content for book format
            content = _prepare_chapter_content(note['content'])

            f.write(content)
            f.write("\n\n\\newpage\n\n")

        # Back matter
        f.write("\\backmatter\n\n")
        f.write("# About\n\n")
        f.write("This book was generated from Basic Memory notes using Pandoc.\n\n")
        f.write("**Basic Memory** - Knowledge management for AI conversations.\n\n")
        f.write("**Pandoc** - Universal document converter.\n\n")

    return book_md_path


def _prepare_chapter_content(content: str) -> str:
    """
    Prepare note content for book chapter format.
    """
    # Remove any existing title headers (we add our own chapter titles)
    lines = content.split('\n')
    cleaned_lines = []

    for line in lines:
        # Skip level 1 headers (we use them as chapter titles)
        if line.startswith('# '):
            continue
        cleaned_lines.append(line)

    content = '\n'.join(cleaned_lines)

    # Ensure content doesn't start with excessive whitespace
    content = content.strip()

    # Add some formatting if content is empty
    if not content:
        content = "*No content available for this chapter.*"

    return content


async def _generate_pdf_book(
    book_md_path: Path,
    pdf_path: Path,
    toc_depth: int,
    paper_size: str
) -> bool:
    """
    Generate PDF book using Pandoc.
    """
    try:
        # Build Pandoc command for book creation
        cmd = [
            "C:\\Program Files\\Pandoc\\pandoc.exe",
            str(book_md_path),
            "-o", str(pdf_path),
            "--pdf-engine=pdflatex",  # Use pdflatex for PDF generation
            f"--toc-depth={toc_depth}",
            "--toc",
            f"--variable=geometry:{paper_size}paper",
            "--variable=documentclass=book",
            "--variable=fontsize=11pt",
            "--variable=linestretch=1.2",
            "--variable=colorlinks=true",
            "--variable=linkcolor=blue",
            "--variable=urlcolor=blue",
            "--variable=citecolor=green",
        ]

        # Execute Pandoc
        result = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )

        stdout, stderr = await result.communicate()

        if result.returncode == 0:
            return True
        else:
            error_msg = stderr.decode('utf-8', errors='ignore')
            print(f"Pandoc PDF book error: {error_msg}")
            return False

    except Exception as e:
        print(f"Error generating PDF book: {e}")
        return False


def _estimate_page_count(notes_data: List[Dict[str, Any]]) -> int:
    """
    Estimate the number of pages based on content length.
    Rough estimate: ~500 words per page.
    """
    total_words = sum(len(note['content'].split()) for note in notes_data)
    return max(1, round(total_words / 500))


def _get_file_size(file_path: Path) -> str:
    """
    Get human-readable file size.
    """
    if not file_path.exists():
        return "Unknown"

    size_bytes = file_path.stat().st_size
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} TB"


def _sanitize_filename(title: str) -> str:
    """
    Create a safe filename from book title.
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
        title = "book"

    return title
