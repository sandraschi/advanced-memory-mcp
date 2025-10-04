"""Search Evernote vault tool for Basic Memory MCP server."""

import os
import re
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Optional, List, Dict, Any

from loguru import logger

from advanced_memory.mcp.server import mcp


@mcp.tool(
    description="""Search through external Evernote ENEX and HTML exports without importing them.

This tool enables querying Evernote export files directly from the filesystem,
providing search capabilities across ENEX XML files, HTML exports, and extracted content.

SEARCH CAPABILITIES:
- Full-text search across ENEX XML content and HTML exports
- Case-sensitive or case-insensitive matching
- File type filtering (ENEX, HTML, or all files)
- Notebook-based filtering and organization
- Tag-based filtering and categorization
- Content extraction from complex XML/HTML structures
- Support for large export collections with result limiting

PARAMETERS:
- vault_path (str, REQUIRED): Path to ENEX file or directory containing Evernote exports
- query (str, REQUIRED): Search term or phrase to find
- case_sensitive (bool, default=False): Whether search should be case-sensitive
- file_type (str, optional): Filter by file type ("enex", "html", or None for all)
- notebook_filter (str, optional): Filter results to specific notebook name
- tag_filter (str, optional): Filter results by tag name
- max_results (int, default=20): Maximum number of results to return

EVERNOTE EXPORT FORMATS:
- ENEX files: XML format with rich content and metadata
- HTML exports: Web-viewable notes with Evernote styling
- Directory structures: Organized exports from Evernote

CONTENT PROCESSING:
- ENEX parsing: Extracts content from XML structure with metadata
- HTML parsing: Strips Evernote styling to get clean text content
- Notebook extraction: Preserves organizational hierarchy
- Tag processing: Maintains categorization information
- Date handling: Creation and modification timestamps

RESULT FORMAT:
Returns structured results showing:
- Note titles and content snippets
- Notebook and tag information
- File types and creation dates
- Match locations and context
- Export file paths and metadata

USAGE EXAMPLES:
Basic search: search_evernote_vault("/exports", "meeting notes")
ENEX only: search_evernote_vault("/exports", "project", file_type="enex")
Notebook filter: search_evernote_vault("/exports", "urgent", notebook_filter="Work")
Tag filter: search_evernote_vault("/exports", "review", tag_filter="Important")
Case sensitive: search_evernote_vault("/exports", "API", case_sensitive=True)

RETURNS:
Formatted search results with note details, organizational context, and match statistics.

NOTE: This searches external Evernote exports without importing them. For enhanced search,
relationship discovery, and AI-powered analysis, use load_evernote_export() to import into Basic Memory.""",
)
async def search_evernote_vault(
    vault_path: str,
    query: str,
    case_sensitive: bool = False,
    file_type: Optional[str] = None,
    notebook_filter: Optional[str] = None,
    tag_filter: Optional[str] = None,
    max_results: int = 20,
) -> str:
    """Search through Evernote export files for content matching a query.

    This tool searches through Evernote ENEX (.enex) and HTML export files stored locally.
    It can search across all file types or filter by specific formats, notebooks, or tags.

    Features:
    - Full-text search across ENEX XML and HTML files
    - Filter by notebook, tags, or file type
    - Case-sensitive or insensitive search
    - Result ranking by relevance
    - Content preview with matches highlighted
    - Metadata extraction (creation dates, tags, notebooks)

    Args:
        vault_path: Path to the directory containing Evernote export files
        query: Search query string
        case_sensitive: Whether search should be case sensitive (default: False)
        file_type: Filter by file type ('enex', 'html', or None for all)
        notebook_filter: Filter by notebook name (optional)
        tag_filter: Filter by tag name (optional)
        max_results: Maximum number of results to return (default: 20)

    Returns:
        Search results with matching notes, content snippets, and metadata

    Examples:
        # Search all files in Evernote export
        search_evernote_vault("path/to/evernote-export", "meeting notes")

        # Search only ENEX files
        search_evernote_vault("export", "project plan", file_type="enex")

        # Search specific notebook with tag filter
        search_evernote_vault("export", "budget", notebook_filter="Finance", tag_filter="2024")
    """

    vault_dir = Path(vault_path)

    if not vault_dir.exists():
        return f"Error: Vault path '{vault_path}' does not exist"

    if not vault_dir.is_dir():
        return f"Error: Vault path '{vault_path}' is not a directory"

    # Find all relevant files
    files_to_search = []

    if file_type in ('enex', None):
        files_to_search.extend(vault_dir.rglob('*.enex'))

    if file_type in ('html', None):
        files_to_search.extend(vault_dir.rglob('*.html'))

    if not files_to_search:
        type_desc = f" {file_type}" if file_type else " ENEX or HTML"
        return f"No{type_desc} files found in '{vault_path}'"

    # Search through files
    results = []
    flags = 0 if case_sensitive else re.IGNORECASE

    try:
        query_pattern = re.compile(re.escape(query), flags)
    except re.error as e:
        return f"Invalid search query: {e}"

    for file_path in files_to_search:
        try:
            if file_path.suffix.lower() == '.enex':
                matches = await _search_enex_file(file_path, query_pattern, vault_dir, notebook_filter, tag_filter)
            else:  # HTML files
                matches = await _search_html_file(file_path, query_pattern, vault_dir)

            results.extend(matches)
        except Exception as e:
            logger.warning(f"Error searching file {file_path}: {e}")
            continue

    # Sort by relevance (number of matches, then by file path)
    results.sort(key=lambda x: (-x['match_count'], x['file_path']))

    # Limit results
    results = results[:max_results]

    # Format results
    return _format_evernote_search_results(query, results, len(files_to_search))


async def _search_enex_file(
    file_path: Path,
    query_pattern: re.Pattern,
    vault_dir: Path,
    notebook_filter: Optional[str],
    tag_filter: Optional[str]
) -> List[Dict[str, Any]]:
    """Search a single ENEX file."""

    try:
        # Parse XML
        tree = ET.parse(file_path)
        root = tree.getroot()

        results = []

        # Process each note
        for note_elem in root.findall('.//note'):
            try:
                note_data = _extract_enex_note_data(note_elem)

                # Apply filters
                if notebook_filter and note_data['notebook'] != notebook_filter:
                    continue

                if tag_filter and tag_filter not in note_data['tags']:
                    continue

                # Search in title and content
                search_text = f"{note_data['title']} {note_data['content']}"
                matches = list(query_pattern.finditer(search_text))

                if matches:
                    # Get context around first match
                    first_match = matches[0]
                    start = max(0, first_match.start() - 100)
                    end = min(len(search_text), first_match.end() + 100)
                    context = search_text[start:end]

                    # Highlight the match in context
                    highlighted_context = query_pattern.sub(
                        lambda m: f"**{m.group()}**",
                        context
                    )

                    # Clean up context for display
                    highlighted_context = highlighted_context.replace('\n', ' ').replace('\r', ' ')
                    highlighted_context = re.sub(r'\s+', ' ', highlighted_context)

                    relative_path = file_path.relative_to(vault_dir)

                    results.append({
                        'file_path': str(relative_path),
                        'title': note_data['title'],
                        'file_type': 'enex',
                        'match_count': len(matches),
                        'context': highlighted_context,
                        'notebook': note_data['notebook'],
                        'tags': note_data['tags'],
                        'created': note_data['created'],
                        'line_number': 1  # ENEX doesn't have line numbers
                    })

            except Exception as e:
                logger.warning(f"Error processing note in {file_path}: {e}")
                continue

        return results

    except ET.ParseError:
        logger.warning(f"Invalid XML in {file_path}")
        return []
    except Exception as e:
        logger.warning(f"Error searching ENEX file {file_path}: {e}")
        return []


async def _search_html_file(
    file_path: Path,
    query_pattern: re.Pattern,
    vault_dir: Path
) -> List[Dict[str, Any]]:
    """Search a single HTML file."""

    try:
        # Read file
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except UnicodeDecodeError:
            with open(file_path, 'r', encoding='latin-1') as f:
                content = f.read()

        # Find all matches
        matches = list(query_pattern.finditer(content))

        if not matches:
            return []

        # Extract title
        title_match = re.search(r'<title[^>]*>(.*?)</title>', content, re.IGNORECASE)
        title = title_match.group(1).strip() if title_match else file_path.stem

        # Clean up Evernote-specific title prefixes
        title = re.sub(r'^Evernote\s*[-–]\s*', '', title)

        # Get context around first match
        first_match = matches[0]
        start = max(0, first_match.start() - 100)
        end = min(len(content), first_match.end() + 100)
        context = content[start:end]

        # Remove HTML tags from context for readability
        context = re.sub(r'<[^>]+>', '', context)

        # Highlight the match in context
        highlighted_context = query_pattern.sub(
            lambda m: f"**{m.group()}**",
            context
        )

        # Clean up context for display
        highlighted_context = highlighted_context.replace('\n', ' ').replace('\r', ' ')
        highlighted_context = re.sub(r'\s+', ' ', highlighted_context)

        relative_path = file_path.relative_to(vault_dir)

        return [{
            'file_path': str(relative_path),
            'title': title,
            'file_type': 'html',
            'match_count': len(matches),
            'context': highlighted_context,
            'notebook': 'Unknown',
            'tags': [],
            'created': 'Unknown',
            'line_number': content[:first_match.start()].count('\n') + 1
        }]

    except Exception as e:
        logger.warning(f"Error searching HTML file {file_path}: {e}")
        return []


def _extract_enex_note_data(note_elem: ET.Element) -> Dict[str, Any]:
    """Extract metadata from an ENEX note element."""

    # Title
    title_elem = note_elem.find('title')
    title = title_elem.text.strip() if title_elem is not None and title_elem.text else 'Untitled'

    # Content
    content_elem = note_elem.find('content')
    content = ""
    if content_elem is not None and content_elem.text:
        # Remove CDATA wrapper and basic HTML tags
        content_text = content_elem.text.strip()
        if content_text.startswith('<![CDATA[') and content_text.endswith(']]>'):
            content = content_text[9:-3]
        else:
            content = content_text
        # Remove HTML tags for search
        content = re.sub(r'<[^>]+>', '', content)

    # Created date
    created_elem = note_elem.find('created')
    created = created_elem.text.strip() if created_elem is not None and created_elem.text else 'Unknown'

    # Notebook
    notebook_elem = note_elem.find('notebook')
    notebook = notebook_elem.text.strip() if notebook_elem is not None and notebook_elem.text else 'Default'

    # Tags
    tags = []
    tag_elems = note_elem.findall('tag')
    for tag_elem in tag_elems:
        if tag_elem.text:
            tags.append(tag_elem.text.strip())

    return {
        'title': title,
        'content': content,
        'created': created,
        'notebook': notebook,
        'tags': tags
    }


def _format_evernote_search_results(query: str, results: List[Dict[str, Any]], total_files: int) -> str:
    """Format search results for display."""

    if not results:
        return f"## No Results Found\n\nNo content matching '{query}' found in {total_files} files."

    summary = f"## Evernote Search Results for '{query}'\n\n"
    summary += f"- **Files searched**: {total_files}\n"
    summary += f"- **Matches found**: {len(results)}\n\n"

    summary += "### Results:\n\n"

    for i, result in enumerate(results, 1):
        summary += f"**{i}. {result['title']}**\n"
        summary += f"- **File**: {result['file_path']} ({result['file_type'].upper()})\n"
        summary += f"- **Notebook**: {result['notebook']}\n"
        if result['tags']:
            summary += f"- **Tags**: {', '.join(result['tags'])}\n"
        if result['created'] != 'Unknown':
            summary += f"- **Created**: {result['created']}\n"
        summary += f"- **Matches**: {result['match_count']}\n"
        summary += f"- **Context**: ...{result['context']}...\n\n"

    if len(results) >= 20:
        summary += "*Showing first 20 results. Use more specific search terms for better results.*\n"

    return summary
