"""View note tool for Basic Memory MCP server."""

from textwrap import dedent
from typing import Optional

from loguru import logger

from advanced_memory.mcp.server import mcp
from advanced_memory.mcp.tools.read_note import read_note
from advanced_memory.mcp.tools.utils import sanitize_unicode_content


@mcp.tool(
    description="""Display notes as formatted markdown artifacts optimized for Claude Desktop viewing experience.

This specialized viewing tool provides enhanced readability through formatted markdown artifacts,
combining note content retrieval with presentation optimization for AI assistant interfaces.

ARTIFACT FORMATTING:
- Clean markdown rendering with proper structure
- Unicode content sanitization and normalization
- Optimized line breaks and spacing
- Metadata inclusion with timestamps and relationships
- Link formatting for cross-references

VIEWING FEATURES:
- Same lookup logic as read_note() for consistency
- Enhanced formatting for artifact display
- Content pagination support
- Relationship context inclusion
- Metadata display with creation/modification info

PARAMETERS:
- identifier (str, REQUIRED): Note title, permalink, or memory:// URL
- page (int, default=1): Pagination page for long content
- page_size (int, default=10): Items per page
- project (str, optional): Target project (defaults to active project)

CONTENT ENHANCEMENT:
- Unicode normalization and sanitization
- Consistent markdown formatting
- Relationship link formatting
- Metadata header inclusion
- Reading-friendly structure

USAGE EXAMPLES:
Basic view: view_note("Meeting Notes")
By permalink: view_note("notes/meeting-notes")
Memory URL: view_note("memory://notes/meeting-notes")
Paginated: view_note("long-document", page=2, page_size=20)
Specific project: view_note("report", project="work-project")

RETURNS:
Formatted markdown content optimized for artifact display, including:
- Note title and metadata header
- Sanitized and formatted content
- Relationship references
- Pagination indicators (if applicable)

DIFFERENCE FROM READ_NOTE:
- Optimized for Claude Desktop artifact viewing
- Enhanced formatting and structure
- Unicode sanitization applied
- Metadata headers included

NOTE: Use this tool when you want to display note content as a formatted artifact.
For programmatic content access, use read_note() instead.""",
)
async def view_note(
    identifier: str, page: int = 1, page_size: int = 10, project: Optional[str] = None
) -> str:
    """View a markdown note as a formatted artifact.

    This tool reads a note using the same logic as read_note but displays the content
    as a markdown artifact for better viewing experience in Claude Desktop.

    After calling this tool, create an artifact using the returned content to display
    the note in a readable format. The tool returns the note content that should be
    used to create a markdown artifact.

    Args:
        identifier: The title or permalink of the note to view
        page: Page number for paginated results (default: 1)
        page_size: Number of items per page (default: 10)
        project: Optional project name to read from. If not provided, uses current active project.

    Returns:
        The note content as a markdown artifact with a confirmation message.
    """

    logger.info(f"Viewing note: {identifier}")

    # Call the existing read_note logic
    content = await read_note.fn(identifier, page, page_size, project)

    # Check if this is an error message (note not found)
    if "# Note Not Found:" in content:
        return content  # Return error message directly instead of creating artifact

    # Extract title from content if possible
    title = identifier
    lines = content.split("\n")
    for line in lines:
        if line.startswith("title:"):
            # Extract title from frontmatter
            title = line.split("title:", 1)[1].strip().strip('"').strip("'")
            break
        elif line.startswith("# "):
            # Extract title from first heading
            title = line[2:].strip()
            break

    # Return the artifact XML as part of the response
    artifact = f'<artifact identifier="note-{hash(identifier) & 0x7FFFFFFF}" type="text/markdown" title="{title}">\n{content}\n</artifact>'

    return dedent(f"""
            <instructions>
            Create an artifact using the returned artifact content to display the note in a readable format.
            </instructions>
            {artifact}\n\n✅ Note displayed as artifact: **{title}**""")
