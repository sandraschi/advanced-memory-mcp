"""Edit in Notepad++ tool for Basic Memory MCP server.

✅ FREE & Open Source Alternative to Typora!
This tool enables editing Basic Memory notes in Notepad++, a powerful free code editor
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
import tempfile
import shutil
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime

from loguru import logger

from advanced_memory.mcp.server import mcp
from advanced_memory.mcp.tools.read_note import read_note
from advanced_memory.mcp.tools.write_note import write_note


@mcp.tool(
    description="""✅ FREE & Open Source Markdown Editing with Notepad++
Export Basic Memory notes to Notepad++ for professional code-style editing.

This tool provides a FREE alternative to paid editors like Typora, using Notepad++
(a powerful, lightweight code editor) with excellent markdown support.

NOTEPAD++ FEATURES (All FREE):
- Syntax highlighting for Markdown
- Plugin ecosystem (MarkdownViewer, PreviewHTML, etc.)
- Lightweight and fast startup
- Professional code editing features
- Completely open source (GPL)

WORKFLOW:
1. Export note from Basic Memory to Notepad++ workspace
2. Edit with full markdown syntax highlighting and features
3. Import edited content back to Basic Memory
4. Preserve all metadata and relationships

PARAMETERS:
- note_identifier (str, REQUIRED): Note title or permalink to edit
- workspace_path (str, optional): Custom workspace directory (defaults to "notepadpp-workspace")
- create_backup (bool, optional): Create backup of original content (default: True)

RETURNS:
Confirmation with workspace location and editing instructions.

NOTE: This is for EDITING only. For exporting documents to PDF/HTML/DOCX, use export_pandoc (FREE).
"""
)
async def edit_in_notepadpp(
    note_identifier: str,
    workspace_path: Optional[str] = None,
    create_backup: bool = True
) -> str:
    """
    Export a Basic Memory note to Notepad++ for editing.

    This creates a temporary workspace where the note can be edited with
    Notepad++'s professional markdown editing features, then imported back.

    Args:
        note_identifier: Title or permalink of the note to edit
        workspace_path: Custom workspace directory path
        create_backup: Whether to create a backup of the original content

    Returns:
        Success message with workspace information
    """
    try:
        # Get the note content
        original_content = await read_note(note_identifier)
        if not original_content:
            return f"❌ Note '{note_identifier}' not found or empty."

        # Setup workspace
        workspace_dir = Path(workspace_path) if workspace_path else Path("notepadpp-workspace")
        workspace_dir.mkdir(parents=True, exist_ok=True)

        # Create safe filename
        safe_title = _sanitize_filename(note_identifier)
        md_file = workspace_dir / f"{safe_title}.md"
        backup_file = workspace_dir / f"{safe_title}_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"

        # Create backup if requested
        if create_backup:
            backup_file.write_text(original_content, encoding='utf-8')
            logger.info(f"Backup created: {backup_file}")

        # Write current content to workspace
        md_file.write_text(original_content, encoding='utf-8')

        # Open in Notepad++
        notepadpp_path = _find_notepadpp_executable()
        if not notepadpp_path:
            return "❌ Notepad++ not found. Please install Notepad++ from https://notepad-plus-plus.org/"

        # Launch Notepad++ with the file
        import subprocess
        try:
            subprocess.Popen([str(notepadpp_path), str(md_file)])
            logger.info(f"Opened {md_file} in Notepad++")
        except Exception as e:
            return f"❌ Failed to open Notepad++: {str(e)}"

        return f"""✅ **Note exported to Notepad++ workspace!**

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

**Note:** Notepad++ is completely FREE and open source! 🎉"""

    except Exception as e:
        logger.error(f"Error in edit_in_notepadpp: {e}")
        return f"❌ Error exporting note to Notepad++: {str(e)}"


@mcp.tool(
    description="""✅ Import edited note back from Notepad++ workspace
Complete the round-trip editing workflow by importing your edited markdown back into Basic Memory.

This tool reads the edited content from the Notepad++ workspace and updates the original note,
preserving all metadata and relationships.

PARAMETERS:
- note_identifier (str, REQUIRED): Original note title or permalink
- workspace_path (str, optional): Workspace directory (defaults to "notepadpp-workspace")
- keep_workspace (bool, optional): Keep workspace files after import (default: False)

RETURNS:
Confirmation of successful import with change summary.
"""
)
async def import_from_notepadpp(
    note_identifier: str,
    workspace_path: Optional[str] = None,
    keep_workspace: bool = False
) -> str:
    """
    Import an edited note back from Notepad++ workspace.

    This completes the round-trip workflow by reading the edited content
    and updating the original note in Basic Memory.

    Args:
        note_identifier: Original note title or permalink
        workspace_path: Workspace directory path
        keep_workspace: Whether to keep workspace files

    Returns:
        Success message with import details
    """
    try:
        # Setup workspace
        workspace_dir = Path(workspace_path) if workspace_path else Path("notepadpp-workspace")
        if not workspace_dir.exists():
            return f"❌ Workspace directory not found: {workspace_dir}"

        # Find the edited file
        safe_title = _sanitize_filename(note_identifier)
        md_file = workspace_dir / f"{safe_title}.md"

        if not md_file.exists():
            return f"❌ Edited file not found: {md_file}"

        # Read edited content
        edited_content = md_file.read_text(encoding='utf-8')

        # Get original content for comparison
        original_content = await read_note(note_identifier)
        if not original_content:
            return f"❌ Original note '{note_identifier}' not found."

        # Check if content changed
        if edited_content.strip() == original_content.strip():
            # Clean up workspace if requested
            if not keep_workspace:
                shutil.rmtree(workspace_dir, ignore_errors=True)

            return f"""ℹ️ **No changes detected**

The content in Notepad++ workspace is identical to the original note.
{f"Workspace preserved at: {workspace_dir}" if keep_workspace else "Workspace cleaned up."}"""

        # Update the note
        success = await write_note(note_identifier, edited_content)
        if not success:
            return "❌ Failed to update the note with edited content."

        # Clean up workspace
        if not keep_workspace:
            shutil.rmtree(workspace_dir, ignore_errors=True)

        # Calculate some stats
        original_lines = len(original_content.split('\n'))
        edited_lines = len(edited_content.split('\n'))
        line_diff = edited_lines - original_lines

        return f"""✅ **Note successfully imported from Notepad++!**

**Updated:** `{note_identifier}`
**Lines:** {original_lines} → {edited_lines} ({'+' if line_diff > 0 else ''}{line_diff})
{f"**Workspace preserved:** `{workspace_dir}`" if keep_workspace else "**Workspace cleaned up**"}

**Your edits have been saved to Basic Memory!** 📝✨"""

    except Exception as e:
        logger.error(f"Error in import_from_notepadpp: {e}")
        return f"❌ Error importing note from Notepad++: {str(e)}"


def _find_notepadpp_executable() -> Optional[Path]:
    """
    Find Notepad++ executable in common installation locations.
    """
    common_paths = [
        Path("C:/Program Files/Notepad++/notepad++.exe"),
        Path("C:/Program Files (x86)/Notepad++/notepad++.exe"),
        Path(os.environ.get('LOCALAPPDATA', '')) / "Programs" / "Notepad++" / "notepad++.exe",
        Path(os.environ.get('PROGRAMFILES', '')) / "Notepad++" / "notepad++.exe",
        Path(os.environ.get('PROGRAMFILES(X86)', '')) / "Notepad++" / "notepad++.exe",
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

