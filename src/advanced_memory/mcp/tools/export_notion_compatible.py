"""Export Notion compatible tool for Basic Memory MCP server."""

import json
import os
import re
from pathlib import Path
from typing import Optional, List, Dict, Any
from urllib.parse import urljoin

from loguru import logger

from advanced_memory.mcp.async_client import client
from advanced_memory.mcp.server import mcp
from advanced_memory.mcp.tools.search import search_notes
from advanced_memory.mcp.tools.utils import call_get
from advanced_memory.mcp.project_session import get_active_project


@mcp.tool(
    description="""Export Basic Memory content to Notion-compatible markdown for team collaboration.

This tool converts Basic Memory knowledge base content into clean markdown format
optimized for Notion import, enabling enhanced team collaboration and database features.

EXPORT FEATURES:
- Generates Notion-importable markdown files with proper formatting
- Preserves content structure and relationships as standard links
- Includes frontmatter metadata for Notion properties
- Supports selective export by search query or folder
- Handles rich content including Mermaid diagrams and complex formatting
- Maintains folder hierarchy as importable structure

PARAMETERS:
- output_path (str, REQUIRED): Filesystem path where Notion-compatible files will be created
- query (str, optional): Search query to filter notes (exports matching notes)
- folder_filter (str, optional): Folder path to limit export scope
- include_observations (bool, default=True): Include observation metadata in frontmatter
- include_relations (bool, default=True): Include relationship links in content
- project (str, optional): Specific Basic Memory project to export from

CONTENT CONVERSION:
- Basic Memory markdown → Notion-compatible markdown
- Entity relationships → Standard markdown links with context
- Observations → YAML frontmatter for Notion properties
- Mermaid diagrams → Preserved as code blocks (Notion renders some diagram types)
- Rich formatting → Standard markdown formatting

OUTPUT STRUCTURE:
Creates import-ready files with:
- Clean markdown content optimized for Notion
- YAML frontmatter with metadata and properties
- Folder structure preserved for logical organization
- Relationship links as standard markdown references

NOTION IMPORT PROCESS:
1. Export using this tool: export_notion_compatible("notion-ready/")
2. Open Notion workspace
3. Click "Import" → "Markdown & CSV"
4. Select the exported directory
5. Choose import settings and complete

USAGE EXAMPLES:
All content: export_notion_compatible("notion-export/")
Search filter: export_notion_compatible("export/", query="project alpha")
Folder filter: export_notion_compatible("export/", folder_filter="docs/")
Minimal export: export_notion_compatible("export/", include_observations=False, include_relations=False)

RETURNS:
Export summary with file counts, content statistics, and Notion import instructions.

NOTE: Notion's import capabilities may vary by plan type. Some advanced formatting
may be simplified. For best results, use Notion's "Markdown & CSV" import option.""",
)
async def export_notion_compatible(
    output_path: str,
    query: Optional[str] = None,
    folder_filter: Optional[str] = None,
    include_observations: bool = True,
    include_relations: bool = True,
    project: Optional[str] = None,
) -> str:
    """Export Basic Memory content in Notion-compatible markdown format.

    This tool exports Basic Memory entities as clean markdown files that can be
    imported into Notion. The exported format preserves content structure while
    being optimized for Notion's import capabilities.

    Features:
    - Clean markdown formatting compatible with Notion
    - Optional inclusion of observations and relations
    - Folder structure preservation
    - Frontmatter metadata for Notion properties

    Args:
        output_path: Directory path where to export the files
        query: Optional search query to filter entities (default: all entities)
        folder_filter: Optional folder path to filter entities
        include_observations: Include observation metadata (default: True)
        include_relations: Include relation links (default: True)
        project: Optional project name to export from

    Returns:
        Summary of exported content with file paths and statistics

    Examples:
        # Export all entities
        export_notion_compatible("path/to/export")

        # Export entities matching a query
        export_notion_compatible("export", query="project planning")

        # Export from specific folder
        export_notion_compatible("export", folder_filter="notes/project-alpha")

        # Export without observations
        export_notion_compatible("export", include_observations=False)
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
        # Get all entities (this is a simplified approach - in practice you'd want pagination)
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

    # Export each entity
    exported_files = []
    errors = []

    for entity in entities:
        try:
            file_path = await _export_entity_to_notion_markdown(
                entity, output_dir, project_url, include_observations, include_relations
            )
            exported_files.append({
                'title': entity.get('title', 'Unknown'),
                'file_path': str(file_path),
                'permalink': entity.get('permalink', '')
            })
        except Exception as e:
            errors.append(f"{entity.get('title', 'Unknown')}: {str(e)}")

    # Generate summary
    summary = f"## Notion Export Complete\n\n"
    summary += f"- **Entities processed**: {len(entities)}\n"
    summary += f"- **Files exported**: {len(exported_files)}\n"
    summary += f"- **Errors**: {len(errors)}\n"
    summary += f"- **Output directory**: {output_path}\n"

    if exported_files:
        summary += f"\n### Exported Files:\n"
        for export_info in exported_files[:10]:  # Show first 10
            summary += f"- **{export_info['title']}** → {export_info['file_path']}\n"
        if len(exported_files) > 10:
            summary += f"- ... and {len(exported_files) - 10} more files\n"

    if errors:
        summary += f"\n### Errors ({len(errors)}):\n"
        for error in errors[:5]:  # Show first 5 errors
            summary += f"- {error}\n"
        if len(errors) > 5:
            summary += f"- ... and {len(errors) - 5} more errors\n"

    summary += f"\n### Import Instructions:\n"
    summary += f"1. Open Notion and create a new page\n"
    summary += f"2. Use **Import** → **Markdown & CSV**\n"
    summary += f"3. Select the exported markdown files\n"
    summary += f"4. Notion will create pages from the markdown files\n"

    return summary


async def _export_entity_to_notion_markdown(
    entity: Dict[str, Any],
    output_dir: Path,
    project_url: str,
    include_observations: bool,
    include_relations: bool
) -> Path:
    """Export a single entity to Notion-compatible markdown."""

    title = entity.get('title', 'Untitled')
    permalink = entity.get('permalink', '')
    content = entity.get('content', '')
    folder = entity.get('folder', '')

    # Create filename from title (Notion-safe)
    safe_filename = _sanitize_notion_filename(title)
    file_path = output_dir / f"{safe_filename}.md"

    # Handle folder structure
    if folder:
        folder_path = output_dir / folder
        folder_path.mkdir(parents=True, exist_ok=True)
        file_path = folder_path / f"{safe_filename}.md"

    # Build markdown content
    markdown_lines = []

    # Title (Notion will use the first heading)
    markdown_lines.append(f"# {title}")
    markdown_lines.append("")

    # Frontmatter-like metadata (Notion will treat as regular text)
    markdown_lines.append("---")
    if permalink:
        markdown_lines.append(f"permalink: {permalink}")
    if folder:
        markdown_lines.append(f"folder: {folder}")
    markdown_lines.append("---")
    markdown_lines.append("")

    # Main content
    if content:
        markdown_lines.append(content)
        markdown_lines.append("")

    # Add observations if requested
    if include_observations:
        observations = entity.get('observations', [])
        if observations:
            markdown_lines.append("## Observations")
            markdown_lines.append("")
            for obs in observations:
                category = obs.get('category', 'note')
                content_obs = obs.get('content', '')
                markdown_lines.append(f"- **{category}**: {content_obs}")
            markdown_lines.append("")

    # Add relations if requested
    if include_relations:
        relations = entity.get('relations', [])
        if relations:
            markdown_lines.append("## Relations")
            markdown_lines.append("")
            for relation in relations:
                rel_type = relation.get('type', 'relates_to')
                target_title = relation.get('target_title', 'Unknown')
                target_permalink = relation.get('target_permalink', '')
                if target_permalink:
                    markdown_lines.append(f"- **{rel_type}**: [{target_title}]({target_permalink})")
                else:
                    markdown_lines.append(f"- **{rel_type}**: {target_title}")
            markdown_lines.append("")

    # Write file
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(markdown_lines))

    return file_path


def _sanitize_notion_filename(filename: str) -> str:
    """Create a Notion-safe filename from a title."""

    # Replace characters that Notion doesn't like in filenames
    safe_name = filename

    # Replace slashes and backslashes with dashes
    safe_name = safe_name.replace('/', '-').replace('\\', '-')

    # Replace other problematic characters
    safe_name = re.sub(r'[<>:"|?*]', '-', safe_name)

    # Replace multiple spaces/dashes with single dash
    safe_name = re.sub(r'[-_\s]+', '-', safe_name)

    # Remove leading/trailing dashes
    safe_name = safe_name.strip('-')

    # Limit length
    if len(safe_name) > 100:
        safe_name = safe_name[:100].rstrip('-')

    # Ensure not empty
    if not safe_name:
        safe_name = 'untitled'

    return safe_name
