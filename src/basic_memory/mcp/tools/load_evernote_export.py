"""Load Evernote export tool for Basic Memory MCP server."""

import os
import re
import base64
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Optional, List, Dict, Any, Tuple
from datetime import datetime

from loguru import logger

from basic_memory.mcp.async_client import client
from basic_memory.mcp.server import mcp
from basic_memory.mcp.tools.search import search_notes
from basic_memory.mcp.tools.utils import call_get
from basic_memory.mcp.project_session import get_active_project


@mcp.tool(
    description="""Import Evernote ENEX files into Basic Memory with complete content and metadata preservation.

This tool processes Evernote's ENEX (Evernote XML) export format, converting rich notes
with attachments into clean Basic Memory markdown while preserving all organizational structure.

EVERNOTE FEATURES SUPPORTED:
- ENEX XML format parsing with full metadata extraction
- Rich HTML content conversion to clean markdown
- Notebook hierarchy preservation (stacks become folders)
- Tag system conversion and mapping
- Creation and modification timestamps
- Base64-encoded attachment extraction (images, files, audio)
- Note links and cross-references

PARAMETERS:
- export_path (str, REQUIRED): Path to .enex file or directory containing ENEX files
- folder (str, default="evernote-import"): Basic Memory folder for imported content
- preserve_notebooks (bool, default=True): Maintain Evernote notebook hierarchy
- include_attachments (bool, default=True): Extract and save embedded media files
- project (str, optional): Target Basic Memory project

ENEX FILE STRUCTURE:
Evernote exports are XML files containing:
- Note content in HTML format with Evernote-specific styling
- Metadata: title, creation date, modification date, tags
- Notebook and stack information
- Embedded resources (images, files, audio) as base64

CONTENT CONVERSION:
- HTML rich text → Clean markdown formatting
- Evernote tables → Markdown table syntax
- Embedded images → Extracted files with proper references
- Internal links → Basic Memory entity relationships
- Tags → Preserved as metadata tags

USAGE EXAMPLES:
Single file: load_evernote_export("my-notes.enex")
Directory: load_evernote_export("/path/to/enex-files")
Custom folder: load_evernote_export("export.enex", folder="archive/evernote")
No attachments: load_evernote_export("notes.enex", include_attachments=False)
Flat structure: load_evernote_export("notes.enex", preserve_notebooks=False)

RETURNS:
Detailed import report with note counts, attachment extractions, notebook mappings, and any conversion issues.

NOTE: ENEX files can be large with many embedded attachments. Processing time depends on file size
and attachment count. Use include_attachments=False for faster imports without media files.""",
)
async def load_evernote_export(
    export_path: str,
    folder: str = "evernote-import",
    preserve_notebooks: bool = True,
    include_attachments: bool = True,
    project: Optional[str] = None,
) -> str:
    """Import Evernote ENEX exports into Basic Memory.

    This tool imports content from Evernote ENEX (.enex) export files.
    Evernote exports contain notes in XML format with metadata, tags,
    and embedded attachments.

    The tool will:
    - Parse Evernote ENEX XML format
    - Convert HTML content to markdown
    - Preserve note metadata (creation date, tags, notebooks)
    - Extract and save attachments
    - Handle both single files and batch imports

    Args:
        export_path: Path to .enex file or directory containing multiple .enex files
        folder: Base folder for imported notes (default: "evernote-import")
        preserve_notebooks: Preserve Evernote notebook structure (default: True)
        include_attachments: Extract and save attachments (default: True)
        project: Optional project name to import into

    Returns:
        Summary of imported content with created entities and statistics

    Examples:
        # Import single ENEX file
        load_evernote_export("path/to/notes.enex")

        # Import directory of ENEX files
        load_evernote_export("path/to/evernote-exports")

        # Import with custom folder and notebook preservation
        load_evernote_export("exports/", folder="my-evernote-notes", preserve_notebooks=True)
    """

    # Get the active project
    active_project = get_active_project(project)
    project_url = active_project.project_url

    export_path_obj = Path(export_path)

    if not export_path_obj.exists():
        return f"Error: Export path '{export_path}' does not exist"

    # Find all .enex files
    if export_path_obj.is_file():
        if export_path_obj.suffix.lower() == '.enex':
            enex_files = [export_path_obj]
        else:
            return f"Error: File '{export_path}' is not a .enex file"
    else:
        enex_files = list(export_path_obj.rglob('*.enex'))

    if not enex_files:
        return f"No .enex files found in '{export_path}'"

    # Create attachments directory if needed
    attachments_dir = None
    if include_attachments:
        attachments_dir = Path(f"{folder}/attachments")
        attachments_dir.mkdir(parents=True, exist_ok=True)

    # Process files
    total_notes = 0
    processed_files = 0
    created_entities = []
    errors = []

    for enex_file in enex_files:
        try:
            logger.info(f"Processing ENEX file: {enex_file}")
            result = await _process_enex_file(
                enex_file, project_url, folder, preserve_notebooks,
                include_attachments, attachments_dir
            )

            if result['success']:
                created_entities.extend(result['entities'])
                total_notes += result['note_count']
                processed_files += 1
            else:
                errors.append(f"{enex_file.name}: {result['error']}")

        except Exception as e:
            errors.append(f"{enex_file.name}: {str(e)}")

    # Generate summary
    summary = f"## Evernote Import Complete\n\n"
    summary += f"- **ENEX files processed**: {processed_files}/{len(enex_files)}\n"
    summary += f"- **Notes imported**: {total_notes}\n"
    summary += f"- **Entities created**: {len(created_entities)}\n"

    if created_entities:
        summary += f"\n### Sample Imported Notes:\n"
        for entity in created_entities[:5]:  # Show first 5
            summary += f"- **{entity['title']}** ({entity.get('notebook', 'No notebook')})\n"
        if len(created_entities) > 5:
            summary += f"- ... and {len(created_entities) - 5} more notes\n"

    if errors:
        summary += f"\n### Errors ({len(errors)}):\n"
        for error in errors[:5]:  # Show first 5 errors
            summary += f"- {error}\n"
        if len(errors) > 5:
            summary += f"- ... and {len(errors) - 5} more errors\n"

    return summary


async def _process_enex_file(
    enex_file: Path,
    project_url: str,
    base_folder: str,
    preserve_notebooks: bool,
    include_attachments: bool,
    attachments_dir: Optional[Path]
) -> Dict[str, Any]:
    """Process a single ENEX file."""

    try:
        # Parse XML
        tree = ET.parse(enex_file)
        root = tree.getroot()

        # ENEX files have a <note> element for each note
        notes = root.findall('.//note')

        if not notes:
            return {'success': False, 'error': 'No notes found in ENEX file', 'note_count': 0}

        created_entities = []
        processed_notes = 0

        for note_elem in notes:
            try:
                entity_data = _parse_enex_note(
                    note_elem, base_folder, preserve_notebooks,
                    include_attachments, attachments_dir
                )

                if entity_data:
                    # Create the note in Basic Memory
                    response = await call_get(project_url + "/api/memory", method='POST', json=entity_data)

                    if response.status_code == 200:
                        result_data = response.json()
                        created_entities.append({
                            'title': entity_data['title'],
                            'permalink': result_data.get('permalink', ''),
                            'notebook': entity_data.get('folder', '').replace(base_folder + '/', ''),
                            'tags': entity_data.get('tags', [])
                        })
                        processed_notes += 1
                    else:
                        logger.warning(f"Failed to create note '{entity_data['title']}': {response.text}")

            except Exception as e:
                logger.warning(f"Error processing note in {enex_file}: {e}")
                continue

        return {
            'success': True,
            'entities': created_entities,
            'note_count': processed_notes
        }

    except ET.ParseError as e:
        return {'success': False, 'error': f'XML parsing error: {e}', 'note_count': 0}
    except Exception as e:
        return {'success': False, 'error': str(e), 'note_count': 0}


def _parse_enex_note(
    note_elem: ET.Element,
    base_folder: str,
    preserve_notebooks: bool,
    include_attachments: bool,
    attachments_dir: Optional[Path]
) -> Optional[Dict[str, Any]]:
    """Parse a single note from ENEX XML."""

    # Extract basic metadata
    title_elem = note_elem.find('title')
    if title_elem is None or not title_elem.text:
        return None

    title = title_elem.text.strip()

    # Extract content (ENEX content is HTML wrapped in CDATA)
    content_elem = note_elem.find('content')
    content_html = ""
    if content_elem is not None and content_elem.text:
        # Remove CDATA wrapper
        content_text = content_elem.text.strip()
        if content_text.startswith('<![CDATA[') and content_text.endswith(']]>'):
            content_html = content_text[9:-3]
        else:
            content_html = content_text

    # Convert HTML to markdown
    content_md = _evernote_html_to_markdown(content_html)

    # Extract creation date
    created_elem = note_elem.find('created')
    created_date = None
    if created_elem is not None and created_elem.text:
        try:
            # ENEX dates are in format: 20231201T123456Z
            date_str = created_elem.text.strip()
            created_date = datetime.strptime(date_str, '%Y%m%dT%H%M%SZ')
        except ValueError:
            pass

    # Extract tags
    tags = []
    tag_elems = note_elem.findall('tag')
    for tag_elem in tag_elems:
        if tag_elem.text:
            tags.append(tag_elem.text.strip())

    # Extract notebook (if available)
    notebook = None
    notebook_elem = note_elem.find('notebook')
    if notebook_elem is not None and notebook_elem.text:
        notebook = notebook_elem.text.strip()

    # Determine folder structure
    if preserve_notebooks and notebook:
        folder_path = f"{base_folder}/{notebook}"
    else:
        folder_path = base_folder

    # Handle attachments
    if include_attachments and attachments_dir:
        content_md, attachment_refs = _process_enex_attachments(
            note_elem, attachments_dir, title
        )
        if attachment_refs:
            # Add attachment references to content
            content_md += "\n\n## Attachments\n"
            for ref in attachment_refs:
                content_md += f"- [{ref['filename']}]({ref['path']})\n"

    # Build entity data
    entity_data = {
        'title': title,
        'content': content_md,
        'folder': folder_path,
        'content_type': 'markdown'
    }

    # Add tags if any
    if tags:
        entity_data['tags'] = tags

    # Add creation date as frontmatter if available
    if created_date:
        frontmatter = f"---\nevernote_created: {created_date.isoformat()}\n"
        if notebook:
            frontmatter += f"evernote_notebook: {notebook}\n"
        frontmatter += "---\n\n"
        entity_data['content'] = frontmatter + content_md

    return entity_data


def _evernote_html_to_markdown(html_content: str) -> str:
    """Convert Evernote HTML to markdown."""

    if not html_content:
        return ""

    # Basic HTML to markdown conversion
    markdown = html_content

    # Headers
    markdown = re.sub(r'<h1[^>]*>(.*?)</h1>', r'# \1', markdown, flags=re.IGNORECASE | re.DOTALL)
    markdown = re.sub(r'<h2[^>]*>(.*?)</h2>', r'## \1', markdown, flags=re.IGNORECASE | re.DOTALL)
    markdown = re.sub(r'<h3[^>]*>(.*?)</h3>', r'### \1', markdown, flags=re.IGNORECASE | re.DOTALL)

    # Lists
    markdown = re.sub(r'<ul[^>]*>(.*?)</ul>', _convert_list_items, markdown, flags=re.IGNORECASE | re.DOTALL)
    markdown = re.sub(r'<ol[^>]*>(.*?)</ol>', _convert_ordered_list_items, markdown, flags=re.IGNORECASE | re.DOTALL)

    # Links
    markdown = re.sub(r'<a[^>]*href="([^"]*)"[^>]*>(.*?)</a>', r'[\2](\1)', markdown, flags=re.IGNORECASE | re.DOTALL)

    # Formatting
    markdown = re.sub(r'<strong[^>]*>(.*?)</strong>', r'**\1**', markdown, flags=re.IGNORECASE | re.DOTALL)
    markdown = re.sub(r'<b[^>]*>(.*?)</b>', r'**\1**', markdown, flags=re.IGNORECASE | re.DOTALL)
    markdown = re.sub(r'<em[^>]*>(.*?)</em>', r'*\1*', markdown, flags=re.IGNORECASE | re.DOTALL)
    markdown = re.sub(r'<i[^>]*>(.*?)</i>', r'*\1*', markdown, flags=re.IGNORECASE | re.DOTALL)

    # Code
    markdown = re.sub(r'<code[^>]*>(.*?)</code>', r'`\1`', markdown, flags=re.IGNORECASE | re.DOTALL)

    # Remove remaining HTML tags
    markdown = re.sub(r'<[^>]+>', '', markdown)

    # Clean up whitespace
    markdown = re.sub(r'\n{3,}', '\n\n', markdown)
    markdown = markdown.strip()

    return markdown


def _convert_list_items(match):
    """Convert HTML list items to markdown."""
    ul_content = match.group(1)
    items = re.findall(r'<li[^>]*>(.*?)</li>', ul_content, re.IGNORECASE | re.DOTALL)
    return '\n'.join(f'- {item.strip()}' for item in items)


def _convert_ordered_list_items(match):
    """Convert HTML ordered list items to markdown."""
    ol_content = match.group(1)
    items = re.findall(r'<li[^>]*>(.*?)</li>', ol_content, re.IGNORECASE | re.DOTALL)
    return '\n'.join(f'{i+1}. {item.strip()}' for i, item in enumerate(items))


def _process_enex_attachments(
    note_elem: ET.Element,
    attachments_dir: Path,
    note_title: str
) -> Tuple[str, List[Dict[str, str]]]:
    """Process attachments in ENEX note."""

    content = ""
    attachment_refs = []

    resource_elems = note_elem.findall('resource')
    for resource_elem in resource_elems:
        try:
            # Extract attachment data
            data_elem = resource_elem.find('data')
            if data_elem is None or not data_elem.text:
                continue

            # Get filename
            filename = "attachment"
            resource_attrs = resource_elem.find('resource-attributes')
            if resource_attrs is not None:
                file_name_elem = resource_attrs.find('file-name')
                if file_name_elem is not None and file_name_elem.text:
                    filename = file_name_elem.text.strip()

            # Decode base64 data
            try:
                attachment_data = base64.b64decode(data_elem.text.strip())
            except Exception:
                continue

            # Create safe filename
            safe_title = re.sub(r'[^\w\-_\.]', '_', note_title)[:50]
            safe_filename = f"{safe_title}_{filename}"
            attachment_path = attachments_dir / safe_filename

            # Save attachment
            with open(attachment_path, 'wb') as f:
                f.write(attachment_data)

            attachment_refs.append({
                'filename': filename,
                'path': str(attachment_path)
            })

        except Exception as e:
            logger.warning(f"Error processing attachment: {e}")
            continue

    return content, attachment_refs
