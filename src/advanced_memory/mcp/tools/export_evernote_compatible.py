"""Export Evernote compatible tool for Advanced Memory MCP server."""

import re
from datetime import datetime
from pathlib import Path
from typing import Any

import defusedxml.minidom as minidom
from defusedxml.ElementTree import Element, SubElement, tostring

from advanced_memory.mcp.async_client import client
from advanced_memory.mcp.mcp_instance import mcp
from advanced_memory.mcp.project_session import get_active_project
from advanced_memory.mcp.tools.utils import call_get, call_post
from advanced_memory.schemas.search import SearchQuery


# @mcp.tool
async def export_evernote_compatible(
    output_path: str,
    query: str | None = None,
    folder_filter: str | None = None,
    notebook_name: str = "Advanced Memory Export",
    include_observations: bool = True,
    include_relations: bool = True,
    project: str | None = None,
) -> str:
    """Export Advanced Memory content in Evernote-compatible ENEX format.

    This tool exports Advanced Memory entities as ENEX (Evernote XML) files that can be
    imported directly into Evernote. The exported format preserves content structure
    and metadata for seamless migration.

    Features:
    - Generate valid ENEX XML format compatible with Evernote import
    - Preserve entity metadata as Evernote note attributes
    - Convert Advanced Memory relations to Evernote tags
    - Include observations as structured content sections
    - Support custom notebook naming

    Args:
        output_path: Directory path where to save the .enex file
        query: Optional search query to filter entities (default: all entities)
        folder_filter: Optional folder path to filter entities
        notebook_name: Name for the Evernote notebook (default: "Advanced Memory Export")
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

    # Get the active project (imported at module level)
    active_project = get_active_project(project)
    project_url = active_project.project_url

    # Create output directory
    output_dir = Path(output_path)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Search for notes to export
    if query:
        # Make HTTP call to search API to find matching notes
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

        if not search_response or not hasattr(search_response, "results"):
            return f"No notes found matching query: {query}"

        entities = search_response.results
    else:
        # Get all entities (simplified approach)
        entities_url = f"{project_url}/api/memory"
        params = {}
        if folder_filter:
            params["folder"] = folder_filter

        response = await call_get(client, entities_url, params=params)  # type: ignore[possibly-unbound]
        if response.status_code != 200:
            return f"Failed to retrieve entities: {response.status_code} - {response.text}"

        entities_data = response.json()
        entities_raw = entities_data.get("results", [])
        # Convert SearchResult objects to dicts
        entities = [
            entity.model_dump()
            if hasattr(entity, "model_dump")
            else dict(entity)
            if hasattr(entity, "__dict__")
            else entity
            for entity in entities_raw
        ]

    if not entities:
        return "No entities found to export"

    # Generate ENEX file
    enex_content = _generate_enex_xml(
        entities, notebook_name, include_observations, include_relations
    )

    # Save file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"advanced_memory_export_{timestamp}.enex"
    file_path = output_dir / filename

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(enex_content)

    # Generate summary
    summary = "## Evernote Export Complete\n\n"
    summary += f"- **Entities exported**: {len(entities)}\n"
    summary += f"- **Notebook name**: {notebook_name}\n"
    summary += f"- **Output file**: {file_path}\n"
    summary += f"- **File size**: {file_path.stat().st_size:,} bytes\n"

    summary += "\n### Export Options:\n"
    summary += f"- Observations included: {include_observations}\n"
    summary += f"- Relations as tags: {include_relations}\n"
    if query:
        summary += f"- Query filter: {query}\n"
    if folder_filter:
        summary += f"- Folder filter: {folder_filter}\n"

    summary += "\n### Import Instructions:\n"
    summary += "1. Open Evernote desktop or web application\n"
    summary += (
        "2. Go to **File** [UNICODE] **Import** [UNICODE] **Evernote Export Files (.enex)**\n"
    )
    summary += f"3. Select the exported `{filename}` file\n"
    summary += f"4. Choose to import into notebook: **{notebook_name}**\n"
    summary += "5. Evernote will create notes with preserved formatting and metadata\n"

    return summary


def _generate_enex_xml(
    entities: list[dict[str, Any]],
    notebook_name: str,
    include_observations: bool,
    include_relations: bool,
) -> str:
    """Generate ENEX XML content from Advanced Memory entities."""

    # Create root element
    en_export = Element("en-export")
    en_export.set("export-date", datetime.now().strftime("%Y%m%dT%H%M%SZ"))
    en_export.set("application", "advanced-memory")
    en_export.set("version", "0.1")

    for entity in entities:
        note_elem = _create_enex_note_element(
            entity, notebook_name, include_observations, include_relations
        )
        en_export.append(note_elem)

    # Convert to formatted XML
    rough_string = tostring(en_export, encoding="unicode")
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="  ")


def _create_enex_note_element(
    entity: dict[str, Any], notebook_name: str, include_observations: bool, include_relations: bool
) -> Element:
    """Create a single note element in ENEX format."""

    note = Element("note")

    # Title
    title = SubElement(note, "title")
    title.text = entity.get("title", "Untitled")

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
        relations = entity.get("relations", [])
        for relation in relations:
            tag = SubElement(note, "tag")
            tag.text = relation.get("type", "relation")

    return note


def _generate_note_html_content(
    entity: dict[str, Any], include_observations: bool, include_relations: bool
) -> str:
    """Generate HTML content for an ENEX note."""

    title = entity.get("title", "Untitled")
    content = entity.get("content", "")

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
        observations = entity.get("observations", [])
        if observations:
            html += "<h2>Observations</h2>\n<ul>\n"
            for obs in observations:
                category = obs.get("category", "note")
                content_obs = obs.get("content", "")
                html += f"<li><strong>{_escape_html(category)}:</strong> {_escape_html(content_obs)}</li>\n"
            html += "</ul>\n"

    # Add relations if requested
    if include_relations:
        relations = entity.get("relations", [])
        if relations:
            html += "<h2>Relations</h2>\n<ul>\n"
            for relation in relations:
                rel_type = relation.get("type", "relates_to")
                target_title = relation.get("target_title", "Unknown")
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
    html = re.sub(r"^### (.*)$", r"<h3>\1</h3>", html, flags=re.MULTILINE)
    html = re.sub(r"^## (.*)$", r"<h2>\1</h2>", html, flags=re.MULTILINE)
    html = re.sub(r"^# (.*)$", r"<h1>\1</h1>", html, flags=re.MULTILINE)

    # Bold/Italic
    html = re.sub(r"\*\*(.*?)\*\*", r"<strong>\1</strong>", html)
    html = re.sub(r"\*(.*?)\*", r"<em>\1</em>", html)

    # Code
    html = re.sub(r"`([^`]+)`", r"<code>\1</code>", html)

    # Links
    html = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2">\1</a>', html)

    # Lists
    html = re.sub(r"^- (.*)$", r"<li>\1</li>", html, flags=re.MULTILINE)
    html = re.sub(r"^(\d+)\. (.*)$", r"<li>\2</li>", html, flags=re.MULTILINE)

    # Wrap consecutive list items
    html = re.sub(r"((?:<li>.*?</li>\s*)+)", r"<ul>\1</ul>", html, flags=re.DOTALL)

    # Paragraphs
    lines = html.split("\n")
    in_list = False
    result = []

    for line in lines:
        line = line.strip()
        if not line:
            continue
        elif line.startswith("<h") or line.startswith("<ul") or line.startswith("<ol"):
            result.append(line)
        elif line.startswith("<li>"):
            if not in_list:
                result.append("<ul>")
                in_list = True
            result.append(line)
        else:
            if in_list:
                result.append("</ul>")
                in_list = False
            result.append(f"<p>{line}</p>")

    if in_list:
        result.append("</ul>")

    return "\n".join(result)


def _escape_html(text: str) -> str:
    """Escape HTML special characters."""
    if not text:
        return ""

    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&#39;")
    )
