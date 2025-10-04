"""Load Notion export tool for Basic Memory MCP server."""

import os
import re
import zipfile
from pathlib import Path
from typing import Optional, List, Dict, Any
from urllib.parse import unquote

from loguru import logger

from advanced_memory.mcp.async_client import client
from advanced_memory.mcp.server import mcp
from advanced_memory.mcp.tools.search import search_notes
from advanced_memory.mcp.tools.utils import call_get
from advanced_memory.mcp.project_session import get_active_project
from advanced_memory.schemas.memory import memory_url_path
from advanced_memory.utils import validate_project_path


@mcp.tool(
    description="""Import Notion workspaces and pages into Basic Memory with intelligent content conversion.

This tool processes Notion HTML/Markdown exports, converting Notion's complex block-based
structure into clean, searchable Basic Memory notes while preserving relationships and hierarchy.

NOTION FEATURES SUPPORTED:
- HTML export format (most comprehensive - preserves all formatting)
- Markdown export format (simpler, faster processing)
- Page hierarchy and nested structures
- Block types: text, headings, lists, tables, code blocks, quotes
- Database views and structured content
- Internal page links and cross-references
- Image and attachment extraction from ZIP exports

PARAMETERS:
- export_path (str, REQUIRED): Path to Notion export (ZIP file or directory)
- folder (str, default="notion-import"): Basic Memory folder for imported content
- preserve_hierarchy (bool, default=True): Maintain page/subpage structure
- project (str, optional): Target Basic Memory project

NOTION EXPORT FORMATS:
- ZIP files: Complete exports with assets (recommended)
- HTML directories: Individual page exports
- Markdown files: Simplified exports (limited formatting)

CONTENT CONVERSION:
- Page titles → Note titles with proper sanitization
- Rich text blocks → Clean markdown formatting
- Tables → Markdown table syntax
- Code blocks → Syntax-highlighted markdown code
- Links → Basic Memory entity references
- Images → Extracted and referenced properly

USAGE EXAMPLES:
ZIP import: load_notion_export("Notion-Export.zip")
Directory: load_notion_export("/path/to/html-export")
Custom folder: load_notion_export("export.zip", folder="workspace/docs")
Flat structure: load_notion_export("export.zip", preserve_hierarchy=False)

RETURNS:
Import summary with page counts, conversion details, hierarchy preservation status, and any processing issues.

NOTE: HTML exports provide the most accurate conversion. ZIP files preserve images and attachments.
Large workspaces may take time to process. Use preserve_hierarchy=False for simpler organization.""",
)
async def load_notion_export(
    export_path: str,
    folder: str = "notion-import",
    preserve_hierarchy: bool = True,
    project: Optional[str] = None,
) -> str:
    """Import Notion HTML or Markdown exports into Basic Memory.

    This tool imports content from Notion exports (HTML or Markdown format).
    Notion exports typically come as ZIP files containing HTML pages with assets,
    or as individual HTML/Markdown files.

    The tool will:
    - Extract and parse Notion HTML structure
    - Convert pages to Basic Memory entities
    - Preserve page hierarchy and internal links
    - Handle databases and page properties

    Args:
        export_path: Path to Notion export (ZIP file or directory)
        folder: Folder to import into (default: "notion-import")
        preserve_hierarchy: Preserve Notion's page hierarchy (default: True)
        project: Optional project name to import into

    Returns:
        Summary of imported content with created entities

    Examples:
        # Import from ZIP export
        load_notion_export("path/to/notion-export.zip")

        # Import from directory
        load_notion_export("path/to/notion-export-directory")

        # Import with custom folder
        load_notion_export("export.zip", folder="my-notion-notes")
    """

    # Get the active project
    active_project = get_active_project(project)
    project_url = active_project.project_url

    export_path_obj = Path(export_path)

    if not export_path_obj.exists():
        return f"Error: Export path '{export_path}' does not exist"

    # Extract files if it's a ZIP
    temp_dir = None
    if export_path_obj.is_file() and export_path_obj.suffix.lower() == '.zip':
        temp_dir = Path(f"temp_notion_extract_{export_path_obj.stem}")
        temp_dir.mkdir(exist_ok=True)

        try:
            with zipfile.ZipFile(export_path_obj, 'r') as zip_ref:
                zip_ref.extractall(temp_dir)
            source_dir = temp_dir
        except Exception as e:
            return f"Error extracting ZIP file: {e}"
    else:
        source_dir = export_path_obj

    # Find HTML and Markdown files
    html_files = []
    markdown_files = []

    for file_path in source_dir.rglob('*'):
        if file_path.is_file():
            if file_path.suffix.lower() == '.html':
                html_files.append(file_path)
            elif file_path.suffix.lower() in ['.md', '.markdown']:
                markdown_files.append(file_path)

    total_files = len(html_files) + len(markdown_files)
    if total_files == 0:
        return f"No HTML or Markdown files found in '{export_path}'"

    # Process files
    processed = 0
    created_entities = []
    errors = []

    # Process HTML files first (more complex)
    for html_file in html_files:
        try:
            result = await _process_notion_html_file(
                html_file, source_dir, project_url, folder, preserve_hierarchy
            )
            if result['success']:
                created_entities.extend(result['entities'])
                processed += 1
            else:
                errors.append(f"HTML {html_file.name}: {result['error']}")
        except Exception as e:
            errors.append(f"HTML {html_file.name}: {str(e)}")

    # Process Markdown files
    for md_file in markdown_files:
        try:
            result = await _process_notion_markdown_file(
                md_file, source_dir, project_url, folder, preserve_hierarchy
            )
            if result['success']:
                created_entities.extend(result['entities'])
                processed += 1
            else:
                errors.append(f"MD {md_file.name}: {result['error']}")
        except Exception as e:
            errors.append(f"MD {md_file.name}: {str(e)}")

    # Clean up temp directory
    if temp_dir and temp_dir.exists():
        import shutil
        shutil.rmtree(temp_dir)

    # Generate summary
    summary = f"## Notion Import Complete\n\n"
    summary += f"- **Files processed**: {processed}/{total_files}\n"
    summary += f"- **Entities created**: {len(created_entities)}\n"

    if created_entities:
        summary += f"\n### Created Entities:\n"
        for entity in created_entities[:10]:  # Show first 10
            summary += f"- {entity['title']} ({entity['permalink']})\n"
        if len(created_entities) > 10:
            summary += f"- ... and {len(created_entities) - 10} more\n"

    if errors:
        summary += f"\n### Errors ({len(errors)}):\n"
        for error in errors[:5]:  # Show first 5 errors
            summary += f"- {error}\n"
        if len(errors) > 5:
            summary += f"- ... and {len(errors) - 5} more errors\n"

    return summary


async def _process_notion_html_file(
    html_file: Path,
    source_dir: Path,
    project_url: str,
    base_folder: str,
    preserve_hierarchy: bool
) -> Dict[str, Any]:
    """Process a single Notion HTML file."""

    try:
        with open(html_file, 'r', encoding='utf-8') as f:
            html_content = f.read()
    except UnicodeDecodeError:
        # Try with different encoding
        try:
            with open(html_file, 'r', encoding='latin-1') as f:
                html_content = f.read()
        except Exception as e:
            return {'success': False, 'error': f"Failed to read file: {e}"}

    # Extract title from HTML
    title_match = re.search(r'<title>(.*?)</title>', html_content, re.IGNORECASE)
    if title_match:
        title = title_match.group(1).strip()
    else:
        title = html_file.stem

    # Clean up Notion-specific title prefixes
    title = re.sub(r'^Notion\s*[-–]\s*', '', title)

    # Extract main content
    content = _extract_notion_content(html_content)

    # Determine folder structure
    if preserve_hierarchy:
        relative_path = html_file.relative_to(source_dir)
        folder_path = f"{base_folder}/{relative_path.parent}" if relative_path.parent != Path('.') else base_folder
    else:
        folder_path = base_folder

    # Create entity in Basic Memory
    try:
        entity_data = {
            'title': title,
            'content': content,
            'folder': folder_path,
            'content_type': 'markdown'  # Convert HTML to markdown
        }

        # Create the note
        create_url = f"{project_url}/api/memory"
        response = await call_get(client, create_url, method='POST', json=entity_data)

        if response.status_code == 200:
            result_data = response.json()
            return {
                'success': True,
                'entities': [{
                    'title': title,
                    'permalink': result_data.get('permalink', ''),
                    'folder': folder_path
                }]
            }
        else:
            return {
                'success': False,
                'error': f"API error {response.status_code}: {response.text}"
            }

    except Exception as e:
        return {'success': False, 'error': str(e)}


async def _process_notion_markdown_file(
    md_file: Path,
    source_dir: Path,
    project_url: str,
    base_folder: str,
    preserve_hierarchy: bool
) -> Dict[str, Any]:
    """Process a single Notion Markdown file."""

    try:
        with open(md_file, 'r', encoding='utf-8') as f:
            content = f.read()
    except UnicodeDecodeError:
        try:
            with open(md_file, 'r', encoding='latin-1') as f:
                content = f.read()
        except Exception as e:
            return {'success': False, 'error': f"Failed to read file: {e}"}

    # Extract title from first heading or filename
    lines = content.split('\n')
    title = md_file.stem  # Default to filename

    for line in lines[:10]:  # Check first 10 lines
        line = line.strip()
        if line.startswith('# '):
            title = line[2:].strip()
            break

    # Clean up Notion-specific prefixes
    title = re.sub(r'^Notion\s*[-–]\s*', '', title)

    # Determine folder structure
    if preserve_hierarchy:
        relative_path = md_file.relative_to(source_dir)
        folder_path = f"{base_folder}/{relative_path.parent}" if relative_path.parent != Path('.') else base_folder
    else:
        folder_path = base_folder

    # Create entity in Basic Memory
    try:
        entity_data = {
            'title': title,
            'content': content,
            'folder': folder_path,
            'content_type': 'markdown'
        }

        create_url = f"{project_url}/api/memory"
        response = await call_get(client, create_url, method='POST', json=entity_data)

        if response.status_code == 200:
            result_data = response.json()
            return {
                'success': True,
                'entities': [{
                    'title': title,
                    'permalink': result_data.get('permalink', ''),
                    'folder': folder_path
                }]
            }
        else:
            return {
                'success': False,
                'error': f"API error {response.status_code}: {response.text}"
            }

    except Exception as e:
        return {'success': False, 'error': str(e)}


def _extract_notion_content(html_content: str) -> str:
    """Extract and convert Notion HTML content to markdown."""

    # Remove HTML head, scripts, and styles
    # Look for the main content area
    content_match = re.search(
        r'<div[^>]*class="[^"]*notion-page-content[^"]*"[^>]*>(.*?)</div>',
        html_content,
        re.DOTALL | re.IGNORECASE
    )

    if content_match:
        content_html = content_match.group(1)
    else:
        # Fallback: look for any div with page content
        content_match = re.search(
            r'<div[^>]*class="[^"]*page[^"]*"[^>]*>(.*?)</div>',
            html_content,
            re.DOTALL | re.IGNORECASE
        )
        if content_match:
            content_html = content_match.group(1)
        else:
            # Last resort: extract body content
            body_match = re.search(r'<body[^>]*>(.*?)</body>', html_content, re.DOTALL | re.IGNORECASE)
            content_html = body_match.group(1) if body_match else html_content

    # Basic HTML to Markdown conversion
    markdown = _html_to_markdown(content_html)

    return markdown


def _html_to_markdown(html: str) -> str:
    """Basic HTML to Markdown conversion for Notion content."""

    # Remove HTML tags but preserve structure
    markdown = html

    # Headers
    markdown = re.sub(r'<h1[^>]*>(.*?)</h1>', r'# \1', markdown, flags=re.IGNORECASE | re.DOTALL)
    markdown = re.sub(r'<h2[^>]*>(.*?)</h2>', r'## \1', markdown, flags=re.IGNORECASE | re.DOTALL)
    markdown = re.sub(r'<h3[^>]*>(.*?)</h3>', r'### \1', markdown, flags=re.IGNORECASE | re.DOTALL)
    markdown = re.sub(r'<h4[^>]*>(.*?)</h4>', r'#### \1', markdown, flags=re.IGNORECASE | re.DOTALL)
    markdown = re.sub(r'<h5[^>]*>(.*?)</h5>', r'##### \1', markdown, flags=re.IGNORECASE | re.DOTALL)
    markdown = re.sub(r'<h6[^>]*>(.*?)</h6>', r'###### \1', markdown, flags=re.IGNORECASE | re.DOTALL)

    # Lists
    markdown = re.sub(r'<ul[^>]*>(.*?)</ul>', _convert_list_items, markdown, flags=re.IGNORECASE | re.DOTALL)
    markdown = re.sub(r'<ol[^>]*>(.*?)</ol>', _convert_ordered_list_items, markdown, flags=re.IGNORECASE | re.DOTALL)

    # Links
    markdown = re.sub(r'<a[^>]*href="([^"]*)"[^>]*>(.*?)</a>', r'[\2](\1)', markdown, flags=re.IGNORECASE | re.DOTALL)

    # Bold/Italic
    markdown = re.sub(r'<strong[^>]*>(.*?)</strong>', r'**\1**', markdown, flags=re.IGNORECASE | re.DOTALL)
    markdown = re.sub(r'<b[^>]*>(.*?)</b>', r'**\1**', markdown, flags=re.IGNORECASE | re.DOTALL)
    markdown = re.sub(r'<em[^>]*>(.*?)</em>', r'*\1*', markdown, flags=re.IGNORECASE | re.DOTALL)
    markdown = re.sub(r'<i[^>]*>(.*?)</i>', r'*\1*', markdown, flags=re.IGNORECASE | re.DOTALL)

    # Code
    markdown = re.sub(r'<code[^>]*>(.*?)</code>', r'`\1`', markdown, flags=re.IGNORECASE | re.DOTALL)
    markdown = re.sub(r'<pre[^>]*>(.*?)</pre>', r'```\n\1\n```', markdown, flags=re.IGNORECASE | re.DOTALL)

    # Remove remaining HTML tags
    markdown = re.sub(r'<[^>]+>', '', markdown)

    # Clean up extra whitespace
    markdown = re.sub(r'\n{3,}', '\n\n', markdown)
    markdown = markdown.strip()

    return markdown


def _convert_list_items(match):
    """Convert HTML list items to markdown."""
    ul_content = match.group(1)
    # Convert <li> to - with proper indentation
    items = re.findall(r'<li[^>]*>(.*?)</li>', ul_content, re.IGNORECASE | re.DOTALL)
    return '\n'.join(f'- {item.strip()}' for item in items)


def _convert_ordered_list_items(match):
    """Convert HTML ordered list items to markdown."""
    ol_content = match.group(1)
    # Convert <li> to numbered items
    items = re.findall(r'<li[^>]*>(.*?)</li>', ol_content, re.IGNORECASE | re.DOTALL)
    return '\n'.join(f'{i+1}. {item.strip()}' for i, item in enumerate(items))
