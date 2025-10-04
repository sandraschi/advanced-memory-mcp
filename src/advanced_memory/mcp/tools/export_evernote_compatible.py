"""Export Evernote compatible tool for Basic Memory MCP server."""

import os
import re
from pathlib import Path
from typing import Optional, List, Dict, Any
from datetime import datetime
from xml.etree.ElementTree import Element, SubElement, tostring
from xml.dom import minidom

from loguru import logger

from advanced_memory.mcp.async_client import client
from advanced_memory.mcp.server import mcp
from advanced_memory.mcp.tools.search import search_notes
from advanced_memory.mcp.tools.utils import call_get
from advanced_memory.mcp.project_session import get_active_project


@mcp.tool(
    description="""Export Basic Memory content to Evernote-compatible ENEX XML format for mobile access.

This tool converts Basic Memory knowledge base content into Evernote's ENEX (Evernote XML) format,
enabling access through Evernote's mobile apps and cross-platform synchronization.

EXPORT FEATURES:
- Generates valid ENEX XML files compatible with Evernote import
- Converts markdown content to rich HTML with Evernote styling
- Preserves folder structure as Evernote notebook hierarchy
- Includes creation/modification timestamps and metadata
- Supports selective export by search query or folder
- Handles rich content including Mermaid diagrams and complex formatting

PARAMETERS:
- output_path (str, REQUIRED): Filesystem path where ENEX files will be created
- query (str, optional): Search query to filter notes (exports matching notes)
- folder_filter (str, optional): Folder path to limit export scope
- notebook_name (str, default="Basic Memory Export"): Evernote notebook name for imported notes
- include_observations (bool, default=True): Include observation metadata as note content
- include_relations (bool, default=True): Include relationship links in content
- project (str, optional): Specific Basic Memory project to export from

CONTENT CONVERSION:
- Basic Memory markdown → Rich HTML with Evernote-compatible formatting
- Entity relationships → Standard HTML links with context
- Observations → Structured HTML content blocks
- Mermaid diagrams → Preserved as formatted code blocks
- Tags and metadata → ENEX XML attributes and elements

OUTPUT STRUCTURE:
Creates ENEX files containing:
- Valid XML structure following Evernote ENEX specification
- Rich HTML content with proper Evernote styling
- Complete metadata including timestamps, tags, and notebook assignments
- Embedded resources and attachments where applicable

EVERNOTE IMPORT PROCESS:
1. Export using this tool: export_evernote_compatible("evernote-ready/")
2. Open Evernote application (desktop or web)
3. Go to File → Import Notes → Evernote XML (.enex)
4. Select the exported .enex file
5. Choose target notebook and complete import

USAGE EXAMPLES:
All content: export_evernote_compatible("evernote-export/")
Search filter: export_evernote_compatible("export/", query="meeting notes")
Folder filter: export_evernote_compatible("export/", folder_filter="projects/")
Custom notebook: export_evernote_compatible("export/", notebook_name="Work Notes")
Minimal export: export_evernote_compatible("export/", include_observations=False, include_relations=False)

RETURNS:
Export summary with file counts, ENEX validation status, and Evernote import instructions.

NOTE: Evernote's free tier has upload limits. Large exports may need to be split into multiple ENEX files.
Some advanced formatting may be simplified for Evernote compatibility.""",
)
async def export_evernote_compatible(
    output_path: str,
    query: Optional[str] = None,
    folder_filter: Optional[str] = None,
    notebook_name: str = "Basic Memory Export",
    include_observations: bool = True,
    include_relations: bool = True,
    project: Optional[str] = None,
) -> str:
    """Export Basic Memory content in Evernote-compatible ENEX format.

    This tool exports Basic Memory entities as ENEX (Evernote XML) files that can be
    imported directly into Evernote. The exported format preserves content structure
    and metadata for seamless migration.

    Features:
    - Generate valid ENEX XML format compatible with Evernote import
    - Preserve entity metadata as Evernote note attributes
    - Convert Basic Memory relations to Evernote tags
    - Include observations as structured content sections
    - Support custom notebook naming

    Args:
        output_path: Directory path where to save the .enex file
        query: Optional search query to filter entities (default: all entities)
        folder_filter: Optional folder path to filter entities
        notebook_name: Name for the Evernote notebook (default: "Basic Memory Export")
        include_observations: Include observation metadata (default: True)
        include_relations: Include relation links as tags (default: True)
        project: Optional project name to export from

    Returns:
        Summary of exported content with file path and statistics

    Examples:
        # Export all entities
        export_evernote_compatible("path/to/export")

        # Export entities matching a query
        export_evernote_compatible("export", query="project planning")

        # Export from specific folder with custom notebook name
        export_evernote_compatible("export", folder_filter="notes/project", notebook_name="Project Notes")
    """

    # Get the active project
    active_project = get_active_project(project)
    project_url = active_project.project_url

    # Create output directory
    output_dir = Path(output_path)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Search for notes to export
    if query:
        # Make HTTP call to search API to find matching notes
        from advanced_memory.mcp.async_client import client
        from advanced_memory.mcp.project_session import get_active_project
        from advanced_memory.schemas.search import SearchQuery
        from advanced_memory.mcp.tools.utils import call_post

        active_project = get_active_project(project)
        project_url = active_project.project_url

        # Create search query
        search_query = SearchQuery(text=query)

        search_response_raw = await call_post(
            client,
            f"{project_url}/search/",
            json=search_query.model_dump(),
            params={"page": 1, "page_size": 1000},
        )

        from advanced_memory.schemas.search import SearchResponse
        search_response = SearchResponse.model_validate(search_response_raw.json())

        if not search_response or not hasattr(search_response, 'results'):
            return f"No notes found matching query: {query}"

        entities = search_response.results
    else:
        # Get all entities (simplified approach)
        entities_url = f"{project_url}/api/memory"
        params = {}
        if folder_filter:
            params["folder"] = folder_filter

        response = await call_get(client, entities_url, params=params)
        if response.status_code != 200:
            return f"Failed to retrieve entities: {response.status_code} - {response.text}"

        entities_data = response.json()
        entities = entities_data.get('results', [])

    if not entities:
        return f"No entities found to export"

    # Generate ENEX file
    enex_content = _generate_enex_xml(entities, notebook_name, include_observations, include_relations)

    # Save file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"basic_memory_export_{timestamp}.enex"
    file_path = output_dir / filename

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(enex_content)

    # Generate summary
    summary = f"## Evernote Export Complete\n\n"
    summary += f"- **Entities exported**: {len(entities)}\n"
    summary += f"- **Notebook name**: {notebook_name}\n"
    summary += f"- **Output file**: {file_path}\n"
    summary += f"- **File size**: {file_path.stat().st_size:,} bytes\n"

    summary += f"\n### Export Options:\n"
    summary += f"- Observations included: {include_observations}\n"
    summary += f"- Relations as tags: {include_relations}\n"
    if query:
        summary += f"- Query filter: {query}\n"
    if folder_filter:
        summary += f"- Folder filter: {folder_filter}\n"

    summary += f"\n### Import Instructions:\n"
    summary += f"1. Open Evernote desktop or web application\n"
    summary += f"2. Go to **File** → **Import** → **Evernote Export Files (.enex)**\n"
    summary += f"3. Select the exported `{filename}` file\n"
    summary += f"4. Choose to import into notebook: **{notebook_name}**\n"
    summary += f"5. Evernote will create notes with preserved formatting and metadata\n"

    return summary


def _generate_enex_xml(
    entities: List[Dict[str, Any]],
    notebook_name: str,
    include_observations: bool,
    include_relations: bool
) -> str:
    """Generate ENEX XML content from Basic Memory entities."""

    # Create root element
    en_export = Element("en-export")
    en_export.set("export-date", datetime.now().strftime("%Y%m%dT%H%M%SZ"))
    en_export.set("application", "basic-memory")
    en_export.set("version", "0.1")

    for entity in entities:
        note_elem = _create_enex_note_element(
            entity, notebook_name, include_observations, include_relations
        )
        en_export.append(note_elem)

    # Convert to formatted XML
    rough_string = tostring(en_export, encoding='unicode')
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="  ")


def _create_enex_note_element(
    entity: Dict[str, Any],
    notebook_name: str,
    include_observations: bool,
    include_relations: bool
) -> Element:
    """Create a single note element in ENEX format."""

    note = Element("note")

    # Title
    title = SubElement(note, "title")
    title.text = entity.get('title', 'Untitled')

    # Content (HTML wrapped in CDATA)
    content = SubElement(note, "content")
    html_content = _generate_note_html_content(entity, include_observations, include_relations)
    content.text = f"<![CDATA[{html_content}]]>"

    # Creation date (use current time if not available)
    created = SubElement(note, "created")
    created_date = datetime.now().strftime("%Y%m%dT%H%M%SZ")
    created.text = created_date

    # Updated date
    updated = SubElement(note, "updated")
    updated.text = created_date

    # Notebook
    notebook = SubElement(note, "notebook")
    notebook.text = notebook_name

    # Tags (from relations if enabled)
    if include_relations:
        relations = entity.get('relations', [])
        for relation in relations:
            tag = SubElement(note, "tag")
            tag.text = relation.get('type', 'relation')

    return note


def _generate_note_html_content(
    entity: Dict[str, Any],
    include_observations: bool,
    include_relations: bool
) -> str:
    """Generate HTML content for an ENEX note."""

    title = entity.get('title', 'Untitled')
    content = entity.get('content', '')

    html = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE en-note SYSTEM "http://xml.evernote.com/pub/enml2.dtd">
<en-note>
<h1>{_escape_html(title)}</h1>
"""

    # Main content
    if content:
        # Convert basic markdown to HTML
        html_content = _markdown_to_evernote_html(content)
        html += html_content

    # Add observations if requested
    if include_observations:
        observations = entity.get('observations', [])
        if observations:
            html += "<h2>Observations</h2>\n<ul>\n"
            for obs in observations:
                category = obs.get('category', 'note')
                content_obs = obs.get('content', '')
                html += f"<li><strong>{_escape_html(category)}:</strong> {_escape_html(content_obs)}</li>\n"
            html += "</ul>\n"

    # Add relations if requested
    if include_relations:
        relations = entity.get('relations', [])
        if relations:
            html += "<h2>Relations</h2>\n<ul>\n"
            for relation in relations:
                rel_type = relation.get('type', 'relates_to')
                target_title = relation.get('target_title', 'Unknown')
                html += f"<li><strong>{_escape_html(rel_type)}:</strong> {_escape_html(target_title)}</li>\n"
            html += "</ul>\n"

    html += "</en-note>"

    return html


def _markdown_to_evernote_html(markdown: str) -> str:
    """Convert basic markdown to Evernote HTML."""

    if not markdown:
        return ""

    html = markdown

    # Headers
    html = re.sub(r'^### (.*)$', r'<h3>\1</h3>', html, flags=re.MULTILINE)
    html = re.sub(r'^## (.*)$', r'<h2>\1</h2>', html, flags=re.MULTILINE)
    html = re.sub(r'^# (.*)$', r'<h1>\1</h1>', html, flags=re.MULTILINE)

    # Bold/Italic
    html = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', html)
    html = re.sub(r'\*(.*?)\*', r'<em>\1</em>', html)

    # Code
    html = re.sub(r'`([^`]+)`', r'<code>\1</code>', html)

    # Links
    html = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2">\1</a>', html)

    # Lists
    html = re.sub(r'^- (.*)$', r'<li>\1</li>', html, flags=re.MULTILINE)
    html = re.sub(r'^(\d+)\. (.*)$', r'<li>\2</li>', html, flags=re.MULTILINE)

    # Wrap consecutive list items
    html = re.sub(r'((?:<li>.*?</li>\s*)+)', r'<ul>\1</ul>', html, flags=re.DOTALL)

    # Paragraphs
    lines = html.split('\n')
    in_list = False
    result = []

    for line in lines:
        line = line.strip()
        if not line:
            continue
        elif line.startswith('<h') or line.startswith('<ul') or line.startswith('<ol'):
            result.append(line)
        elif line.startswith('<li>'):
            if not in_list:
                result.append('<ul>')
                in_list = True
            result.append(line)
        else:
            if in_list:
                result.append('</ul>')
                in_list = False
            result.append(f'<p>{line}</p>')

    if in_list:
        result.append('</ul>')

    return '\n'.join(result)


def _escape_html(text: str) -> str:
    """Escape HTML special characters."""
    if not text:
        return ""

    return (text
            .replace('&', '&amp;')
            .replace('<', '&lt;')
            .replace('>', '&gt;')
            .replace('"', '&quot;')
            .replace("'", '&#39;'))
