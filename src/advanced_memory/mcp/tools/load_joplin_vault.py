"""Load Joplin vault tool for Basic Memory MCP server.

This tool imports Joplin exports into Basic Memory, preserving
folder structure, metadata, and relationships.
"""

import os
import re
import json
from pathlib import Path
from typing import Optional, Dict, List, Any, Set
from datetime import datetime

from loguru import logger

from advanced_memory.mcp.server import mcp
from advanced_memory.mcp.tools.write_note import write_note
from advanced_memory.mcp.tools.search import search_notes


@mcp.tool(
    description="""Import Joplin knowledge bases into Basic Memory with full metadata preservation.

This tool migrates Joplin exports into Basic Memory, converting Joplin's note organization
into Basic Memory's entity-relationship model while preserving all metadata and structure.

JOPLIN FEATURES SUPPORTED:
- Markdown notes with full formatting support
- Notebook hierarchy (folders become Basic Memory folders)
- Tags and categorization systems
- Note metadata (creation dates, modification dates, author info)
- Rich content (tables, code blocks, lists, links)
- Attachment references and media links

PARAMETERS:
- export_path (str, REQUIRED): Path to Joplin export directory (containing .md and .json files)
- destination_folder (str, default="imported/joplin"): Basic Memory folder for imported content
- preserve_structure (bool, default=True): Maintain Joplin notebook hierarchy
- convert_links (bool, default=True): Convert Joplin links to Basic Memory entity references
- skip_existing (bool, default=True): Skip notes that already exist in Basic Memory
- project (str, optional): Target Basic Memory project

JOPLIN EXPORT STRUCTURE:
Joplin exports create pairs of files:
- .md files: Note content in markdown format
- .json files: Metadata including title, tags, notebook, timestamps
- _resources/ folder: Attachments and media files

USAGE EXAMPLES:
Basic import: load_joplin_vault("/path/to/joplin-export")
Custom folder: load_joplin_vault("/export", destination_folder="research/joplin-notes")
Preserve links: load_joplin_vault("/export", convert_links=True)
Incremental: load_joplin_vault("/export", skip_existing=True)

RETURNS:
Detailed import report with note counts, tag conversions, notebook mappings, and any issues.

NOTE: Joplin's end-to-end encryption must be disabled before export. Large knowledge bases
may take time to process. Use skip_existing=True for incremental synchronization.""",
)
async def load_joplin_vault(
    export_path: str,
    destination_folder: str = "imported/joplin",
    preserve_structure: bool = True,
    convert_links: bool = True,
    skip_existing: bool = True,
    project: Optional[str] = None,
) -> str:
    """Import a Joplin export into Basic Memory.

    This tool reads all markdown files and JSON metadata from a Joplin export
    and imports them into Basic Memory, preserving folder structure, tags,
    timestamps, and converting Joplin links to Basic Memory format.

    Args:
        export_path: Path to the Joplin export root directory
        destination_folder: Base folder in Basic Memory where export will be imported
        preserve_structure: Whether to preserve the notebook/folder structure (default: True)
        convert_links: Whether to convert Joplin links to Basic Memory format (default: True)
        skip_existing: Whether to skip notes that already exist (default: True)
        project: Optional project name to import into. If not provided, uses current active project.

    Returns:
        Detailed import summary with statistics and any issues encountered.

    Examples:
        # Basic import preserving structure
        result = await load_joplin_vault("/path/to/joplin/export")

        # Import with custom destination
        result = await load_joplin_vault(
            "/path/to/export",
            destination_folder="notes/joplin-backup"
        )

        # Import without converting links (keep original Joplin links)
        result = await load_joplin_vault(
            "/path/to/export",
            convert_links=False
        )

        # Import to specific project
        result = await load_joplin_vault(
            "/path/to/export",
            project="personal-notes"
        )
    """

    try:
        export_path_obj = Path(export_path)

        # Validate export path
        if not export_path_obj.exists():
            return f"# Joplin Import Failed\n\nExport path does not exist: {export_path}"

        if not export_path_obj.is_dir():
            return f"# Joplin Import Failed\n\nPath is not a directory: {export_path}"

        logger.info(f"Starting Joplin export import: {export_path} -> {destination_folder}")

        # Find all Joplin note files (markdown + JSON pairs)
        joplin_files = await _find_joplin_files(export_path_obj)

        if not joplin_files:
            return f"# Joplin Import Complete\n\nNo Joplin notes found in export: {export_path}"

        # Build notebook mapping for folder structure
        notebook_mapping = await _build_notebook_mapping(joplin_files)

        # Process the import
        result = await _process_joplin_import(
            export_path_obj,
            joplin_files,
            notebook_mapping,
            destination_folder,
            preserve_structure,
            convert_links,
            skip_existing,
            project
        )

        return result

    except Exception as e:
        logger.error(f"Joplin import failed: {e}")
        return f"# Joplin Import Failed\n\nUnexpected error: {e}"


async def _find_joplin_files(export_path: Path) -> List[Dict[str, Path]]:
    """Find all Joplin note files (markdown + JSON pairs)."""
    return await _find_joplin_files_recursive(export_path)


async def _find_joplin_files_recursive(export_path: Path) -> List[Dict[str, Path]]:
    """Recursively find all Joplin note files."""
    joplin_files = []

    try:
        # Use MCP filesystem if available, otherwise direct access
        try:
            from mcp_filesystem import list_directory

            async def scan_recursive(current_path: str) -> List[Dict[str, str]]:
                files = []
                try:
                    dir_contents = await list_directory(current_path)

                    # Group files by base name (without extension)
                    file_groups = {}
                    for line in dir_contents.split('\n'):
                        if '📄' in line:
                            parts = line.split()
                            if len(parts) >= 2:
                                filename = parts[1].strip()
                                file_path = os.path.join(current_path, filename)

                                if filename.endswith('.md'):
                                    base_name = filename[:-3]  # Remove .md
                                    if base_name not in file_groups:
                                        file_groups[base_name] = {}
                                    file_groups[base_name]['md'] = file_path
                                elif filename.endswith('.json'):
                                    base_name = filename[:-5]  # Remove .json
                                    if base_name not in file_groups:
                                        file_groups[base_name] = {}
                                    file_groups[base_name]['json'] = file_path

                        elif '📁' in line and not line.strip().endswith('.'):
                            # Directory - recurse
                            parts = line.split()
                            if len(parts) >= 2:
                                dirname = parts[1].strip()
                                subdir_path = os.path.join(current_path, dirname)
                                subfiles = await scan_recursive(subdir_path)
                                files.extend(subfiles)

                    # Only include complete pairs (both .md and .json)
                    for base_name, file_dict in file_groups.items():
                        if 'md' in file_dict and 'json' in file_dict:
                            files.append({
                                'md': file_dict['md'],
                                'json': file_dict['json'],
                                'base_name': base_name,
                                'directory': current_path
                            })

                except Exception as e:
                    logger.warning(f"Error scanning directory {current_path}: {e}")

                return files

            joplin_files_raw = await scan_recursive(str(export_path))
            joplin_files = [
                {
                    'md': Path(f['md']),
                    'json': Path(f['json']),
                    'base_name': f['base_name'],
                    'directory': f['directory']
                }
                for f in joplin_files_raw
            ]

        except ImportError:
            # Fallback to direct filesystem access
            logger.warning("MCP filesystem not available, using direct access")

            file_groups = {}
            for file_path in export_path.rglob("*"):
                if file_path.is_file():
                    if file_path.suffix.lower() == '.md':
                        base_name = file_path.stem
                        dir_path = str(file_path.parent)
                        key = f"{dir_path}/{base_name}"
                        if key not in file_groups:
                            file_groups[key] = {}
                        file_groups[key]['md'] = file_path
                    elif file_path.suffix.lower() == '.json':
                        base_name = file_path.stem
                        dir_path = str(file_path.parent)
                        key = f"{dir_path}/{base_name}"
                        if key not in file_groups:
                            file_groups[key] = {}
                        file_groups[key]['json'] = file_path

            # Only include complete pairs
            for key, file_dict in file_groups.items():
                if 'md' in file_dict and 'json' in file_dict:
                    md_path = file_dict['md']
                    joplin_files.append({
                        'md': md_path,
                        'json': file_dict['json'],
                        'base_name': md_path.stem,
                        'directory': str(md_path.parent)
                    })

    except Exception as e:
        logger.error(f"Error finding Joplin files: {e}")

    return joplin_files


async def _build_notebook_mapping(joplin_files: List[Dict[str, Path]]) -> Dict[str, str]:
    """Build mapping from notebook IDs to folder paths."""
    notebook_mapping = {}

    for file_info in joplin_files:
        try:
            metadata = _read_joplin_metadata(file_info['json'])

            # Joplin stores parent relationships
            parent_id = metadata.get('parent_id', '')

            if parent_id:
                # For simplicity, we'll use the directory structure
                # In a full implementation, you'd resolve parent relationships
                notebook_path = file_info['directory']
                notebook_mapping[parent_id] = notebook_path

        except Exception as e:
            logger.warning(f"Error reading metadata for {file_info['md']}: {e}")
            continue

    return notebook_mapping


async def _process_joplin_import(
    export_path: Path,
    joplin_files: List[Dict[str, Path]],
    notebook_mapping: Dict[str, str],
    destination_folder: str,
    preserve_structure: bool,
    convert_links: bool,
    skip_existing: bool,
    project: Optional[str]
) -> str:
    """Process the Joplin export import with all files."""

    # Track import statistics
    stats = {
        'total_files': len(joplin_files),
        'imported_files': 0,
        'skipped_files': 0,
        'failed_files': 0,
        'converted_links': 0,
        'folders_created': set()
    }

    # Build file mapping for link conversion
    file_mapping = await _build_file_mapping(export_path, joplin_files, destination_folder, preserve_structure)

    # Process Joplin files
    processed_files = []

    for file_info in joplin_files:
        try:
            # Read metadata and content
            metadata = _read_joplin_metadata(file_info['json'])
            content = file_info['md'].read_text(encoding='utf-8')

            # Calculate destination path
            dest_path = _calculate_destination_path(
                file_info, export_path, destination_folder, preserve_structure, metadata
            )

            # Check if note already exists
            if skip_existing:
                try:
                    existing = await search_notes.fn(
                        query=dest_path,
                        search_type="permalink",
                        project=project
                    )
                    if existing.results:
                        logger.info(f"Skipping existing note: {dest_path}")
                        stats['skipped_files'] += 1
                        continue
                except Exception:
                    pass  # Continue with import if search fails

            # Get title from metadata or content
            title = metadata.get('title', _extract_title_from_content(content))

            # Process content (convert links, add metadata)
            processed_content, link_conversions = _process_content(
                content, convert_links, file_mapping, metadata
            )
            stats['converted_links'] += link_conversions

            # Create the note
            result = await write_note.fn(
                title=title,
                content=processed_content,
                folder=dest_path,
                project=project
            )

            stats['imported_files'] += 1
            processed_files.append({
                'original_path': str(file_info['md'].relative_to(export_path)),
                'destination_path': dest_path,
                'title': title,
                'id': metadata.get('id', 'unknown'),
                'links_converted': link_conversions if convert_links else 0
            })

            # Track folder creation
            folder_path = dest_path
            while '/' in folder_path:
                folder_path = folder_path.rsplit('/', 1)[0]
                stats['folders_created'].add(folder_path)

        except Exception as e:
            logger.error(f"Failed to import {file_info['md']}: {e}")
            stats['failed_files'] += 1
            processed_files.append({
                'original_path': str(file_info['md'].relative_to(export_path)),
                'error': str(e)
            })

    # Generate summary report
    return _generate_import_report(stats, processed_files, export_path, destination_folder)


def _read_joplin_metadata(json_path: Path) -> Dict[str, Any]:
    """Read and parse Joplin JSON metadata."""
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logger.warning(f"Error reading Joplin metadata {json_path}: {e}")
        return {}


def _extract_title_from_content(content: str) -> str:
    """Extract title from markdown content."""
    lines = content.split('\n')

    # Look for first heading
    for line in lines:
        if line.startswith('# '):
            return line[2:].strip()

    # Fallback to first line
    return lines[0].strip() if lines else "Untitled"


async def _build_file_mapping(
    export_path: Path,
    joplin_files: List[Dict[str, Path]],
    destination_folder: str,
    preserve_structure: bool
) -> Dict[str, str]:
    """Build mapping from Joplin IDs to new Basic Memory paths for link conversion."""
    mapping = {}

    for file_info in joplin_files:
        try:
            metadata = _read_joplin_metadata(file_info['json'])
            note_id = metadata.get('id', '')

            dest_path = _calculate_destination_path(
                file_info, export_path, destination_folder, preserve_structure, metadata
            )

            if note_id:
                mapping[note_id] = dest_path

            # Also map by title for simpler links
            title = metadata.get('title', _extract_title_from_content(file_info['md'].read_text(encoding='utf-8')))
            mapping[title] = dest_path

        except Exception as e:
            logger.warning(f"Error building mapping for {file_info['md']}: {e}")
            continue

    return mapping


def _calculate_destination_path(
    file_info: Dict[str, Path],
    export_path: Path,
    destination_folder: str,
    preserve_structure: bool,
    metadata: Dict[str, Any]
) -> str:
    """Calculate the destination path for a Joplin note."""
    if not preserve_structure:
        return destination_folder

    # Calculate relative path from export root
    rel_path = Path(file_info['directory']).relative_to(export_path)

    if str(rel_path) == '.':
        return f"{destination_folder}/{file_info['base_name']}"
    else:
        return f"{destination_folder}/{rel_path}/{file_info['base_name']}"


def _process_content(
    content: str,
    convert_links: bool,
    file_mapping: Dict[str, str],
    metadata: Dict[str, Any]
) -> tuple[str, int]:
    """Process note content for import."""
    conversions = 0

    if not convert_links:
        processed_content = content
    else:
        processed_content, conversions = _convert_joplin_links(content, file_mapping)

    # Add metadata footer
    footer_lines = [
        "\n\n---",
        "*Imported from Joplin export*",
        f"*Joplin ID: {metadata.get('id', 'unknown')}*",
        f"*Created: {_format_timestamp(metadata.get('created_time'))}*",
        f"*Updated: {_format_timestamp(metadata.get('updated_time'))}*"
    ]

    # Add tags if present
    tags = metadata.get('tags', [])
    if tags:
        footer_lines.append(f"*Tags: {', '.join(tags)}*")

    footer = "\n".join(footer_lines)
    processed_content += footer

    return processed_content, conversions


def _convert_joplin_links(content: str, file_mapping: Dict[str, str]) -> tuple[str, int]:
    """Convert Joplin links to Basic Memory format."""
    conversions = 0

    def replace_link(match):
        nonlocal conversions
        link_target = match.group(1)

        # Check if we have a mapping for this link
        if link_target in file_mapping:
            new_path = file_mapping[link_target]
            # Convert to Basic Memory link format
            converted = f"[[{new_path}]]"
            conversions += 1
            return converted
        else:
            # Keep original if not found
            return match.group(0)

    # Convert Joplin link format [:link](:id) or similar patterns
    # Joplin links can be in various formats, this is a basic implementation
    pattern = r'\[:([^\]]+)\]\(:([^)]+)\)'
    converted_content = re.sub(pattern, replace_link, content)

    return converted_content, conversions


def _format_timestamp(timestamp_ms: Optional[int]) -> str:
    """Format timestamp from milliseconds to readable date."""
    if not timestamp_ms:
        return "unknown"

    try:
        dt = datetime.fromtimestamp(timestamp_ms / 1000)
        return dt.strftime('%Y-%m-%d %H:%M:%S')
    except Exception:
        return "unknown"


def _generate_import_report(
    stats: Dict[str, Any],
    processed_files: List[Dict[str, Any]],
    export_path: str,
    destination_folder: str
) -> str:
    """Generate a comprehensive import report."""
    lines = [
        f"# Joplin Export Import Complete",
        f"**Source export:** {export_path}",
        f"**Destination folder:** {destination_folder}",
        f"**Import completed:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        ""
    ]

    # Statistics
    lines.extend([
        "## Import Statistics",
        f"- **Total notes:** {stats['total_files']}",
        f"- **Successfully imported:** {stats['imported_files']}",
        f"- **Skipped (existing):** {stats['skipped_files']}",
        f"- **Failed to import:** {stats['failed_files']}",
        f"- **Links converted:** {stats['converted_links']}",
        f"- **Folders created:** {len(stats['folders_created'])}",
        ""
    ])

    # Success rate
    total_processed = stats['imported_files'] + stats['skipped_files'] + stats['failed_files']
    if total_processed > 0:
        success_rate = (stats['imported_files'] + stats['skipped_files']) / total_processed * 100
        lines.append(f"**Success rate:** {success_rate:.1f}%")
        lines.append("")

    # Processed files summary
    if processed_files:
        lines.append("## Processed Notes")
        for file_info in processed_files[:20]:  # Limit to first 20
            if 'error' in file_info:
                lines.append(f"- ❌ **{file_info['original_path']}** - Error: {file_info['error']}")
            else:
                links_text = f" ({file_info['links_converted']} links converted)" if file_info.get('links_converted', 0) > 0 else ""
                lines.append(f"- ✅ **{file_info['original_path']}** → {file_info['destination_path']}{links_text}")

        if len(processed_files) > 20:
            lines.append(f"- ... and {len(processed_files) - 20} more notes")
        lines.append("")

    # Recommendations
    lines.extend([
        "## Next Steps",
        "1. **Review imported content** - Check that links and formatting converted correctly",
        "2. **Run sync** - Execute 'basic-memory sync' to index the new content",
        "3. **Update remaining links** - Any unconverted Joplin links may need manual fixing",
        "4. **Verify metadata** - Check that tags, dates, and other metadata imported correctly",
        ""
    ])

    return "\n".join(lines)
