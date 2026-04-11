"""Edit in Notepad++ tool for Advanced Memory MCP server.

[UNICODE] FREE & Open Source Alternative to Typora!
This tool enables editing Advanced Memory notes in Notepad++, a powerful free code editor
with excellent markdown support through plugins.

Notepad++ Features:
- Completely FREE (no licensing costs)
- Open Source (GPL license)
- Lightweight and fast
- Markdown syntax highlighting
- Plugin ecosystem for enhanced markdown editing
- Cross-platform (Windows, with alternatives for other OS)

For document export, use export_pandoc (FREE) instead of this editing tool.
"""

import os
import shutil
from datetime import datetime
from pathlib import Path

from loguru import logger

from advanced_memory.mcp.mcp_instance import mcp
from advanced_memory.mcp.tools import read_note as mcp_read_note
from advanced_memory.mcp.tools import write_note as mcp_write_note


@mcp.tool
async def edit_in_notepadpp(
    note_identifier: str, workspace_path: str | None = None, create_backup: bool = True
) -> str:
    """
    Export an Advanced Memory note to Notepad++ for editing.

    This creates a temporary workspace where the note can be edited with
    Notepad++'s professional markdown editing features, then imported back.

    Args:
        note_identifier: Title or permalink of the note to edit
        workspace_path: Custom workspace directory path
        create_backup: Whether to create a backup of the original content

    Returns:
        Success message with workspace information

    Errors:
        - "Note not found": The provided note_identifier could not be found or returned empty content.
        - "Notepad++ not found": The Notepad++ executable could not be located in common installation paths or PATH.
        - "Failed to open Notepad++": An error occurred while launching the Notepad++ process.
    """
    try:
        # Get the note content
        original_content = await (
            mcp_read_note.fn if hasattr(mcp_read_note, "fn") else mcp_read_note
        )(note_identifier)
        if not original_content:
            return f"[UNICODE] Note '{note_identifier}' not found or empty."

        # Setup workspace
        workspace_dir = Path(workspace_path) if workspace_path else Path("notepadpp-workspace")
        workspace_dir.mkdir(parents=True, exist_ok=True)

        # Create safe filename
        safe_title = _sanitize_filename(note_identifier)
        md_file = workspace_dir / f"{safe_title}.md"
        backup_file = (
            workspace_dir / f"{safe_title}_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        )

        # Create backup if requested
        if create_backup:
            backup_file.write_text(original_content, encoding="utf-8")
            logger.info(f"Backup created: {backup_file}")

        # Write current content to workspace
        md_file.write_text(original_content, encoding="utf-8")

        # Open in Notepad++
        notepadpp_path = _find_notepadpp_executable()
        if not notepadpp_path:
            return "[UNICODE] Notepad++ not found. Please install Notepad++ from https://notepad-plus-plus.org/"

        # Launch Notepad++ with the file
        import subprocess

        try:
            subprocess.Popen([str(notepadpp_path), str(md_file)])
            logger.info(f"Opened {md_file} in Notepad++")
        except Exception as e:
            return f"[UNICODE] Failed to open Notepad++: {e!s}"

        return f"""[UNICODE] **Note exported to Notepad++ workspace!**

**Workspace:** `{workspace_dir}`
**File:** `{md_file.name}`
{f"**Backup:** `{backup_file.name}`" if create_backup else ""}

**Next Steps:**
1. **Edit the file** in Notepad++ using its markdown features
2. **Save your changes** in Notepad++
3. **Import back** using: `import_from_notepadpp("{note_identifier}")`

**Notepad++ Tips:**
- Install "MarkdownViewer" plugin for live preview
- Use "PreviewHTML" plugin for HTML preview
- Enable markdown syntax highlighting in Language menu

**Note:** Notepad++ is completely FREE and open source! [SUCCESS]"""

    except Exception as e:
        logger.error(f"Error in edit_in_notepadpp: {e}")
        return f"[UNICODE] Error exporting note to Notepad++: {e!s}"


@mcp.tool
async def import_from_notepadpp(
    note_identifier: str,
    workspace_path: str | None = None,
    keep_workspace: bool = False,
) -> str:
    """
    Import an edited note back from Notepad++ workspace.

    This completes the round-trip workflow by reading the edited content
    and updating the original note in Advanced Memory.

    Args:
        note_identifier: Original note title or permalink
        workspace_path: Workspace directory path
        keep_workspace: Whether to keep workspace files

    Returns:
        Success message with import details

    Errors:
        - "Workspace directory not found": The provided workspace_path does not exist.
        - "Edited file not found": The markdown file matching the note_identifier was not found in the workspace directory.
        - "Original note not found": The original note could not be retrieved from the knowledge base for comparison.
        - "Failed to update the note": An error occurred while writing the edited content back to the knowledge base.
    """
    try:
        # Setup workspace
        workspace_dir = Path(workspace_path) if workspace_path else Path("notepadpp-workspace")
        if not workspace_dir.exists():
            return f"[UNICODE] Workspace directory not found: {workspace_dir}"

        # Find the edited file
        safe_title = _sanitize_filename(note_identifier)
        md_file = workspace_dir / f"{safe_title}.md"

        if not md_file.exists():
            return f"[UNICODE] Edited file not found: {md_file}"

        # Read edited content
        edited_content = md_file.read_text(encoding="utf-8")

        # Get original content for comparison
        original_content = await (
            mcp_read_note.fn if hasattr(mcp_read_note, "fn") else mcp_read_note
        )(note_identifier)
        if not original_content:
            return f"[UNICODE] Original note '{note_identifier}' not found."

        # Check if content changed
        if edited_content.strip() == original_content.strip():
            # Clean up workspace if requested
            if not keep_workspace:
                shutil.rmtree(workspace_dir, ignore_errors=True)

            return f"""[UNICODE][UNICODE] **No changes detected**

The content in Notepad++ workspace is identical to the original note.
{f"Workspace preserved at: {workspace_dir}" if keep_workspace else "Workspace cleaned up."}"""

        # Update the note
        success = await (mcp_write_note.fn if hasattr(mcp_write_note, "fn") else mcp_write_note)(
            title=note_identifier,
            content=edited_content,
            folder="",
            tags=None,
            entity_type="note",
        )
        if not success:
            return "[UNICODE] Failed to update the note with edited content."

        # Clean up workspace
        if not keep_workspace:
            shutil.rmtree(workspace_dir, ignore_errors=True)

        # Calculate some stats
        original_lines = len(original_content.split("\n"))
        edited_lines = len(edited_content.split("\n"))
        line_diff = edited_lines - original_lines

        return f"""[UNICODE] **Note successfully imported from Notepad++!**

**Updated:** `{note_identifier}`
**Lines:** {original_lines} [UNICODE] {edited_lines} ({"+" if line_diff > 0 else ""}{line_diff})
{f"**Workspace preserved:** `{workspace_dir}`" if keep_workspace else "**Workspace cleaned up**"}

**Your edits have been saved to Advanced Memory!** [NOTE][UNICODE]"""

    except Exception as e:
        logger.error(f"Error in import_from_notepadpp: {e}")
        return f"[UNICODE] Error importing note from Notepad++: {e!s}"


def _find_notepadpp_executable() -> Path | None:
    """
    Find Notepad++ executable in common installation locations.
    """
    common_paths = [
        Path("C:/Program Files/Notepad++/notepad++.exe"),
        Path("C:/Program Files (x86)/Notepad++/notepad++.exe"),
        Path(os.environ.get("LOCALAPPDATA", "")) / "Programs" / "Notepad++" / "notepad++.exe",
        Path(os.environ.get("PROGRAMFILES", "")) / "Notepad++" / "notepad++.exe",
        Path(os.environ.get("PROGRAMFILES(X86)", "")) / "Notepad++" / "notepad++.exe",
    ]

    for path in common_paths:
        if path.exists():
            return path

    # Try to find in PATH
    import shutil

    notepadpp_exe = shutil.which("notepad++")
    if notepadpp_exe:
        return Path(notepadpp_exe)

    return None


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
