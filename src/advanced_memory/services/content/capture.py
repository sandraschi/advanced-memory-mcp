"""Content capture services — quick capture and daily journal.

Extracted verbatim from content_manager.py (lines 1894-1987) during
Phase 1 of the 2.0 migration (ARCHITECTURE_2_0.md). Pure move, no
behavior changes. Legacy names: _quick_capture_operation,
_daily_note_operation.
"""

from advanced_memory.utils import parse_tags

from advanced_memory.services.content.crud import write_note
from advanced_memory.services.content.tagging import extract_content_tags

TagType = list[str] | str | None


async def quick_capture(active_project, content: str, tags: TagType) -> dict:
    """Handle quick capture operation - ultra-fast note creation with smart defaults."""
    from datetime import datetime

    # Generate smart title from content (first line or timestamp)
    content_lines = content.strip().split("\n")
    first_line = content_lines[0].strip()

    # If first line is a heading, use it as title
    if first_line.startswith("#"):
        title = first_line.lstrip("#").strip()
        # Remove the heading from content since we're using it as title
        content = "\n".join(content_lines[1:]).strip()
    else:
        # Use first few words as title
        words = first_line.split()[:6]
        title = " ".join(words)
        if len(first_line.split()) > 6:
            title += "..."

    # Auto-select folder (inbox or quick-notes)
    folder = "inbox"

    # Start with user-provided tags
    tag_list = parse_tags(tags) if tags else []

    # Auto-extract relevant tags from content
    extracted_tags = extract_content_tags(content, title)
    for tag in extracted_tags:
        if tag not in tag_list:
            tag_list.append(tag)

    # Always add quick-capture and date tags
    tag_list.append("quick-capture")
    tag_list.append(datetime.now().strftime("%Y-%m-%d"))

    # Add timestamp to content
    # Use string concatenation to avoid f-string parsing of JSON curly braces in content
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    formatted_content = f"# {title}\n\n**Captured:** {timestamp}\n\n" + content

    # Create the note
    return await write_note(
        active_project, title, formatted_content, folder, tag_list, "note"
    )


async def daily_note(active_project, content: str, tags: TagType) -> dict:
    """Handle daily note operation - create or append to today's journal."""
    from datetime import datetime

    from advanced_memory.mcp.tools.edit_note import edit_note

    # Generate today's date-based title and folder
    today = datetime.now()
    title = today.strftime("%Y-%m-%d")
    folder = "journal"

    # Auto-add daily tag
    tag_list = parse_tags(tags) if tags else []
    tag_list.extend(["daily", "journal", today.strftime("%Y"), today.strftime("%Y-%m")])

    # Try to read existing daily note
    from advanced_memory.mcp.tools.read_note import read_note

    existing_note = await (read_note.fn if hasattr(read_note, "fn") else read_note)(
        identifier=f"{folder}/{title}",
        page=1,
        page_size=1000,
        project=active_project.name,
    )

    # Check if note exists (not an error message)
    if "# Note Not Found:" in existing_note:
        # Create new daily note
        # Use string concatenation to avoid f-string parsing of JSON curly braces in content
        timestamp = today.strftime("%H:%M")
        formatted_content = f"# Daily Note: {title}\n\n## {timestamp}\n\n" + content + "\n\n---\n\n"
        return await write_note(
            active_project, title, formatted_content, folder, tag_list, "note"
        )
    else:
        # Append to existing daily note
        # Use string concatenation to avoid f-string parsing of JSON curly braces in content
        timestamp = today.strftime("%H:%M")
        append_content = f"\n\n## {timestamp}\n\n" + content + "\n\n---\n"
        return await (edit_note.fn if hasattr(edit_note, "fn") else edit_note)(
            identifier=f"{folder}/{title}",
            operation="append",
            content=append_content,
            project=active_project.name,
        )
