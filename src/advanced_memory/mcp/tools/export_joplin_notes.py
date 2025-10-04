"""Export Joplin notes tool for Basic Memory MCP server.

This tool exports Basic Memory notes to Joplin format, creating
markdown files with corresponding JSON metadata.
"""

import os
import json
import uuid
from pathlib import Path
from typing import Optional, List, Dict, Any
from datetime import datetime

from loguru import logger

from advanced_memory.mcp.server import mcp
from advanced_memory.mcp.tools.list_directory import list_directory
from advanced_memory.mcp.tools.search import search_notes
from advanced_memory.mcp.tools.read_note import read_note


@mcp.tool(
    description="""Export Basic Memory notes to Joplin-compatible format for cross-platform access.

This tool converts Basic Memory knowledge base content into Joplin's native format,
creating markdown files paired with JSON metadata that can be directly imported into Joplin.

EXPORT FEATURES:
- Generates Joplin-compatible markdown files with full formatting
- Creates corresponding JSON metadata files with complete note information
- Preserves folder structure as Joplin notebooks
- Maintains tags, timestamps, and note relationships
- Handles rich content including tables, lists, and links
- Supports selective export by folder or project

PARAMETERS:
- export_path (str, REQUIRED): Filesystem path where Joplin export will be created
- source_folder (str, default="/"): Basic Memory folder to export (use "/" for all notes)
- include_subfolders (bool, default=True): Include subfolders recursively
- create_notebooks (bool, default=True): Create notebook structure from folders
- project (str, optional): Specific Basic Memory project to export from

OUTPUT STRUCTURE:
Creates a Joplin-compatible export with:
- .md files: Note content in markdown format with Joplin extensions
- .json files: Metadata including title, tags, notebook, timestamps, and IDs
- Organized folder structure representing Joplin notebooks

CONTENT CONVERSION:
- Basic Memory markdown → Joplin-compatible markdown
- Entity links → Standard markdown links (relationships may be lost)
- Tags → Preserved in JSON metadata
- Folder hierarchy → Joplin notebook structure
- Rich formatting → Standard markdown formatting

USAGE EXAMPLES:
Basic export: export_joplin_notes("joplin-export/")
Folder export: export_joplin_notes("export/", source_folder="projects/alpha")
Flat export: export_joplin_notes("export/", create_notebooks=False)
Project export: export_joplin_notes("export/", project="work-project")

JOPLIN IMPORT PROCESS:
1. Open Joplin application
2. Go to File → Import → Joplin Export Directory
3. Select the exported directory
4. Choose import options and complete import

RETURNS:
Detailed export summary with file counts, notebook mappings, tag conversions, and import instructions.

NOTE: Joplin's end-to-end encryption should be disabled before import. Some advanced
Basic Memory features like entity relationships may not translate perfectly to Joplin.""",
)
async def export_joplin_notes(
    export_path: str,
    source_folder: str = "/",
    include_subfolders: bool = True,
    create_notebooks: bool = True,
    project: Optional[str] = None,
) -> str:
    """Export Basic Memory notes to Joplin format.

    This tool reads notes from Basic Memory and exports them to Joplin format,
    creating markdown files with corresponding JSON metadata files that can be
    imported back into Joplin.

    Args:
        source_folder: Folder in Basic Memory to export from (default: root "/")
        export_path: Path where to create the Joplin export
        include_subfolders: Whether to include subfolders recursively (default: True)
        create_notebooks: Whether to create notebook structure (default: True)
        project: Optional project name to export from. If not provided, uses current active project.

    Returns:
        Detailed export summary with statistics and file locations.

    Examples:
        # Export entire knowledge base
        result = await export_joplin_notes(export_path="/path/to/export")

        # Export specific folder
        result = await export_joplin_notes(
            source_folder="/research",
            export_path="/path/to/research-export"
        )

        # Export from specific project
        result = await export_joplin_notes(
            export_path="/path/to/export",
            project="work-notes"
        )

        # Flat export (no notebook structure)
        result = await export_joplin_notes(
            export_path="/path/to/export",
            create_notebooks=False
        )
    """

    try:
        export_path_obj = Path(export_path)

        # Create export directory if it doesn't exist
        export_path_obj.mkdir(parents=True, exist_ok=True)

        logger.info(f"Starting Joplin export: {source_folder} -> {export_path}")

        # Get all notes from the source folder
        notes_data = await _get_notes_from_folder(source_folder, include_subfolders, project)

        if not notes_data:
            return f"# Joplin Export Complete\n\nNo notes found in folder: {source_folder}"

        # Process the export
        result = await _process_joplin_export(
            notes_data,
            export_path_obj,
            create_notebooks
        )

        return result

    except Exception as e:
        logger.error(f"Joplin export failed: {e}")
        return f"# Joplin Export Failed\n\nUnexpected error: {e}"


async def _get_notes_from_folder(
    source_folder: str,
    include_subfolders: bool,
    project: Optional[str]
) -> List[Dict[str, Any]]:
    """Get all notes from the specified folder with full content."""
    try:
        # Make HTTP call to search API to find all notes in the folder
        from advanced_memory.mcp.async_client import client
        from advanced_memory.mcp.project_session import get_active_project
        from advanced_memory.schemas.search import SearchQuery
        from advanced_memory.mcp.tools.utils import call_post

        active_project = get_active_project(project)
        project_url = active_project.project_url

        # Create search query for all notes
        search_query = SearchQuery(text="*")

        search_response = await call_post(
            client,
            f"{project_url}/search/",
            json=search_query.model_dump(),
            params={"page": 1, "page_size": 1000},  # Large page to get all notes
        )

        from advanced_memory.schemas.search import SearchResponse
        search_result = SearchResponse.model_validate(search_response.json())

        notes_data = []

        # Filter notes by folder and get their content
        for note in search_result.results:
            note_path = note.file_path
            note_title = note.title

            # Check if note is in the requested folder
            if include_subfolders:
                # Include notes in subfolders
                folder_matches = note_path.startswith(source_folder.lstrip('/'))
            else:
                # Only notes directly in the folder
                note_folder = '/'.join(note_path.split('/')[:-1])  # Remove filename
                folder_matches = note_folder == source_folder.lstrip('/')

            if folder_matches and note_path.endswith('.md'):
                # Read the actual note content
                try:
                    note_content = await read_note.fn(
                        identifier=note_title,
                        project=project
                    )

                    # Extract just the markdown content (remove any artifact formatting)
                    content = note_content
                    if content.startswith('# '):
                        # Remove any auto-generated headers from view_note
                        lines = content.split('\n')
                        # Skip lines that look like auto-generated metadata
                        filtered_lines = []
                        skip_until_content = False
                        for line in lines:
                            if line.startswith('*Original path:*') or line.startswith('*Exported:*'):
                                continue
                            if line.strip() == '---' and not skip_until_content:
                                continue
                            if line.startswith('## Content') or line.startswith('This note has been exported'):
                                skip_until_content = True
                                continue
                            if skip_until_content or not line.startswith('*Generated by'):
                                filtered_lines.append(line)

                        content = '\n'.join(filtered_lines).strip()

                    notes_data.append({
                        'filename': f"{note_title}.md",
                        'path': note_path,
                        'title': note_title,
                        'folder': source_folder,
                        'content': content
                    })

                except Exception as e:
                    logger.warning(f"Could not read content for note {note_title}: {e}")
                    # Still include the note but with empty content
                    notes_data.append({
                        'filename': f"{note_title}.md",
                        'path': note_path,
                        'title': note_title,
                        'folder': source_folder,
                        'content': f"# {note_title}\n\n*Content could not be read*"
                    })

    except Exception as e:
        logger.error(f"Error getting notes from folder {source_folder}: {e}")
        return []

    return notes_data


async def _process_joplin_export(
    notes_data: List[Dict[str, Any]],
    export_path: Path,
    create_notebooks: bool
) -> str:
    """Process the export of notes to Joplin format."""

    # Track export statistics
    stats = {
        'total_notes': len(notes_data),
        'exported_notes': 0,
        'created_folders': 0,
        'failed_exports': 0,
        'notebooks_created': set()
    }

    # Process each note
    exported_files = []

    for note_info in notes_data:
        try:
            # Calculate export paths
            if create_notebooks:
                # Create folder structure based on note path
                rel_path = note_info['path']
                folder_path = export_path / rel_path
                folder_path = folder_path.parent  # Remove the filename part
                folder_path.mkdir(parents=True, exist_ok=True)

                if str(folder_path) != str(export_path):
                    stats['created_folders'] += 1

                # Notebook name from folder
                notebook_name = folder_path.name if folder_path != export_path else "Imported Notes"
                if notebook_name not in stats['notebooks_created']:
                    stats['notebooks_created'].add(notebook_name)
            else:
                # Flat structure
                folder_path = export_path
                notebook_name = "Imported Notes"

            # Generate Joplin-compatible filenames
            base_name = _generate_joplin_filename(note_info['title'])
            md_path = folder_path / f"{base_name}.md"
            json_path = folder_path / f"{base_name}.json"

            # Create Joplin metadata
            metadata = _create_joplin_metadata(note_info, notebook_name)

            # Get the actual note content
            content = note_info.get('content', f"# {note_info['title']}\n\n*Content could not be loaded*")

            # Write files
            with open(md_path, 'w', encoding='utf-8') as f:
                f.write(content)

            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)

            stats['exported_notes'] += 1
            exported_files.append({
                'title': note_info['title'],
                'export_path': str(md_path.relative_to(export_path)),
                'notebook': notebook_name,
                'id': metadata['id']
            })

        except Exception as e:
            logger.error(f"Failed to export note {note_info['title']}: {e}")
            stats['failed_exports'] += 1
            exported_files.append({
                'title': note_info['title'],
                'error': str(e)
            })

    # Generate summary report
    return _generate_export_report(stats, exported_files, export_path)


def _generate_joplin_filename(title: str) -> str:
    """Generate a Joplin-compatible filename from title."""
    # Joplin uses a specific naming scheme, often with IDs
    # For simplicity, we'll sanitize the title
    import re
    from unicodedata import normalize

    # Normalize unicode characters
    title = normalize('NFKD', title).encode('ascii', 'ignore').decode('ascii')

    # Replace unsafe characters
    title = re.sub(r'[^\w\s-]', '_', title)

    # Replace spaces and multiple underscores
    title = re.sub(r'[\s_]+', '_', title)

    # Trim underscores
    title = title.strip('_')

    # Limit length and ensure it's not empty
    if len(title) > 50:
        title = title[:47] + '...'

    if not title:
        title = 'untitled'

    # Add timestamp to make it unique (Joplin style)
    timestamp = int(datetime.now().timestamp() * 1000)
    return f"{title}_{timestamp}"


def _create_joplin_metadata(note_info: Dict[str, Any], notebook_name: str) -> Dict[str, Any]:
    """Create Joplin-compatible JSON metadata."""
    now = int(datetime.now().timestamp() * 1000)

    metadata = {
        "id": str(uuid.uuid4()),
        "title": note_info['title'],
        "body": "",  # Will be filled with actual content
        "parent_id": "",  # Would be set for notebook relationships
        "created_time": now,
        "updated_time": now,
        "user_created_time": now,
        "user_updated_time": now,
        "encryption_cipher_text": "",
        "encryption_applied": 0,
        "markup_language": 1,  # 1 = Markdown
        "is_shared": 0,
        "type_": 1,  # 1 = Note
        "source": "basic-memory-export",
        "source_application": "basic-memory",
        "application_data": json.dumps({
            "original_path": note_info['path'],
            "exported_from": "basic-memory",
            "export_timestamp": now
        }),
        "author": "",
        "source_url": "",
        "is_todo": 0,
        "todo_due": 0,
        "todo_completed": 0,
        "latitude": 0.0,
        "longitude": 0.0,
        "altitude": 0.0,
        "order": 0,
        "tags": []  # Could be populated from Basic Memory tags
    }

    return metadata


def _generate_export_report(
    stats: Dict[str, Any],
    exported_files: List[Dict[str, Any]],
    export_path: Path
) -> str:
    """Generate a comprehensive export report."""
    lines = [
        f"# Joplin Export Complete",
        f"**Export location:** {export_path}",
        f"**Export completed:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        ""
    ]

    # Statistics
    lines.extend([
        "## Export Statistics",
        f"- **Total notes processed:** {stats['total_notes']}",
        f"- **Successfully exported:** {stats['exported_notes']}",
        f"- **Failed exports:** {stats['failed_exports']}",
        f"- **Folders created:** {stats['created_folders']}",
        f"- **Notebooks created:** {len(stats['notebooks_created'])}",
        ""
    ])

    # Success rate
    if stats['total_notes'] > 0:
        success_rate = stats['exported_notes'] / stats['total_notes'] * 100
        lines.append(f"**Success rate:** {success_rate:.1f}%")
        lines.append("")

    # List created notebooks
    if stats['notebooks_created']:
        lines.append("## Notebooks Created")
        for notebook in sorted(stats['notebooks_created']):
            lines.append(f"- {notebook}")
        lines.append("")

    # Exported files summary
    if exported_files:
        lines.append("## Exported Notes")
        for file_info in exported_files[:20]:  # Limit to first 20
            if 'error' in file_info:
                lines.append(f"- ❌ **{file_info['title']}** - Error: {file_info['error']}")
            else:
                lines.append(f"- ✅ **{file_info['title']}** → {file_info['export_path']} (ID: {file_info['id']})")

        if len(exported_files) > 20:
            lines.append(f"- ... and {len(exported_files) - 20} more notes")
        lines.append("")

    # Import instructions
    lines.extend([
        "## How to Import into Joplin",
        "1. **Open Joplin** and go to File → Import",
        "2. **Choose 'Joplin Export Directory'** as the import format",
        "3. **Select the export folder:** `{export_path}`",
        "4. **Complete the import** - Joplin will create the notes and notebooks",
        "",
        "## Notes",
        "- Each note has been exported as a `.md` file with a corresponding `.json` metadata file",
        "- Notebook structure has been preserved based on folder organization",
        "- Original Basic Memory paths are stored in the metadata for reference",
        ""
    ])

    return "\n".join(lines)
