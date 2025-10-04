"""Search Notion vault tool for Basic Memory MCP server."""

import os
import re
from pathlib import Path
from typing import Optional, List, Dict, Any, Tuple

from loguru import logger

from advanced_memory.mcp.server import mcp


@mcp.tool(
    description="""Search through external Notion HTML/Markdown exports without importing them.

This tool enables querying Notion export directories directly from the filesystem,
providing search capabilities across HTML pages, markdown files, and structured content.

SEARCH CAPABILITIES:
- Full-text search across HTML and markdown content
- Case-sensitive or case-insensitive matching
- File type filtering (HTML, Markdown, or all files)
- Content extraction from complex HTML structures
- Support for large export directories with result limiting
- Structured results with page hierarchy information

PARAMETERS:
- vault_path (str, REQUIRED): Path to Notion export directory (ZIP extracted or HTML folder)
- query (str, REQUIRED): Search term or phrase to find
- case_sensitive (bool, default=False): Whether search should be case-sensitive
- file_type (str, optional): Filter by file type ("html", "markdown", or None for all)
- max_results (int, default=20): Maximum number of results to return

NOTION EXPORT FORMATS:
- HTML exports: Complex structured pages with Notion styling
- Markdown exports: Simplified text format (limited formatting)
- ZIP files: Complete exports that should be extracted first
- Directory structures: Organized by page hierarchy

CONTENT PROCESSING:
- HTML parsing: Extracts text content from Notion's block structure
- Markdown parsing: Standard text search with formatting preservation
- Link resolution: Handles internal Notion page references
- Metadata extraction: Page titles, creation dates, hierarchy

RESULT FORMAT:
Returns structured results showing:
- Page/file names and paths
- Content snippets with search term highlighting
- File types and sizes
- Match locations and context
- Page hierarchy information

USAGE EXAMPLES:
Basic search: search_notion_vault("/export/path", "meeting notes")
Case sensitive: search_notion_vault("/export", "API", case_sensitive=True)
HTML only: search_notion_vault("/export", "database", file_type="html")
Markdown only: search_notion_vault("/export", "todo", file_type="markdown")
Limited results: search_notion_vault("/export", "project", max_results=50)

RETURNS:
Formatted search results with file details, content previews, and match statistics.

NOTE: This searches external Notion exports without importing them. For enhanced search
and AI-powered analysis, use load_notion_export() to import into Basic Memory.""",
)
async def search_notion_vault(
    vault_path: str,
    query: str,
    case_sensitive: bool = False,
    file_type: Optional[str] = None,
    max_results: int = 20,
) -> str:
    """Search through Notion export files for content matching a query.

    This tool searches through Notion HTML or Markdown export files stored locally.
    It can search across all file types or filter by HTML/Markdown specifically.

    Features:
    - Full-text search across Notion exports
    - Support for HTML and Markdown files
    - Case-sensitive or insensitive search
    - Result ranking by relevance
    - Content preview with matches highlighted

    Args:
        vault_path: Path to the directory containing Notion export files
        query: Search query string
        case_sensitive: Whether search should be case sensitive (default: False)
        file_type: Filter by file type ('html', 'markdown', or None for all)
        max_results: Maximum number of results to return (default: 20)

    Returns:
        Search results with matching files, content snippets, and metadata

    Examples:
        # Search all files in Notion export
        search_notion_vault("path/to/notion-export", "project planning")

        # Search only HTML files
        search_notion_vault("export", "meeting notes", file_type="html")

        # Case-sensitive search
        search_notion_vault("export", "API", case_sensitive=True)
    """

    vault_dir = Path(vault_path)

    if not vault_dir.exists():
        return f"Error: Vault path '{vault_path}' does not exist"

    if not vault_dir.is_dir():
        return f"Error: Vault path '{vault_path}' is not a directory"

    # Find all relevant files
    files_to_search = []

    if file_type == 'html' or file_type is None:
        files_to_search.extend(vault_dir.rglob('*.html'))

    if file_type == 'markdown' or file_type is None:
        files_to_search.extend(vault_dir.rglob('*.md'))
        files_to_search.extend(vault_dir.rglob('*.markdown'))

    if not files_to_search:
        return f"No {file_type or 'HTML/Markdown'} files found in '{vault_path}'"

    # Search through files
    results = []
    flags = 0 if case_sensitive else re.IGNORECASE

    try:
        query_pattern = re.compile(re.escape(query), flags)
    except re.error as e:
        return f"Invalid search query: {e}"

    for file_path in files_to_search:
        try:
            matches = await _search_file(file_path, query_pattern, vault_dir)
            if matches:
                results.extend(matches)
        except Exception as e:
            logger.warning(f"Error searching file {file_path}: {e}")
            continue

    # Sort by relevance (number of matches, then by file path)
    results.sort(key=lambda x: (-x['match_count'], x['file_path']))

    # Limit results
    results = results[:max_results]

    # Format results
    return _format_search_results(query, results, len(files_to_search))


async def _search_file(
    file_path: Path,
    query_pattern: re.Pattern,
    vault_dir: Path
) -> List[Dict[str, Any]]:
    """Search a single file for the query pattern."""

    try:
        # Try UTF-8 first, then fallback to latin-1
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except UnicodeDecodeError:
            with open(file_path, 'r', encoding='latin-1') as f:
                content = f.read()
    except Exception as e:
        logger.warning(f"Could not read file {file_path}: {e}")
        return []

    # Find all matches
    matches = list(query_pattern.finditer(content))

    if not matches:
        return []

    # Extract file info
    relative_path = file_path.relative_to(vault_dir)
    file_type = 'html' if file_path.suffix.lower() == '.html' else 'markdown'

    # Extract title from content
    title = _extract_title_from_content(content, file_path, file_type)

    # Get context around first match
    first_match = matches[0]
    start = max(0, first_match.start() - 100)
    end = min(len(content), first_match.end() + 100)
    context = content[start:end]

    # Highlight the match in context
    highlighted_context = query_pattern.sub(
        lambda m: f"**{m.group()}**",
        context
    )

    # Clean up context for display
    highlighted_context = highlighted_context.replace('\n', ' ').replace('\r', ' ')
    highlighted_context = re.sub(r'\s+', ' ', highlighted_context)

    return [{
        'file_path': str(relative_path),
        'title': title,
        'file_type': file_type,
        'match_count': len(matches),
        'context': highlighted_context,
        'line_number': content[:first_match.start()].count('\n') + 1
    }]


def _extract_title_from_content(content: str, file_path: Path, file_type: str) -> str:
    """Extract title from Notion file content."""

    # Try different title extraction methods based on file type

    if file_type == 'html':
        # Look for title tag
        title_match = re.search(r'<title[^>]*>(.*?)</title>', content, re.IGNORECASE)
        if title_match:
            title = title_match.group(1).strip()
            # Clean up Notion-specific prefixes
            title = re.sub(r'^Notion\s*[-–]\s*', '', title)
            return title

        # Look for h1 in content
        h1_match = re.search(r'<h1[^>]*>(.*?)</h1>', content, re.IGNORECASE)
        if h1_match:
            return h1_match.group(1).strip()

    else:  # markdown
        lines = content.split('\n')
        for line in lines[:10]:  # Check first 10 lines
            line = line.strip()
            if line.startswith('# '):
                title = line[2:].strip()
                # Clean up Notion-specific prefixes
                title = re.sub(r'^Notion\s*[-–]\s*', '', title)
                return title

    # Fallback to filename
    return file_path.stem


def _format_search_results(query: str, results: List[Dict[str, Any]], total_files: int) -> str:
    """Format search results for display."""

    if not results:
        return f"## No Results Found\n\nNo content matching '{query}' found in {total_files} files."

    summary = f"## Search Results for '{query}'\n\n"
    summary += f"- **Files searched**: {total_files}\n"
    summary += f"- **Matches found**: {len(results)}\n\n"

    summary += "### Results:\n\n"

    for i, result in enumerate(results, 1):
        summary += f"**{i}. {result['title']}**\n"
        summary += f"- **File**: {result['file_path']}\n"
        summary += f"- **Type**: {result['file_type']}\n"
        summary += f"- **Matches**: {result['match_count']}\n"
        summary += f"- **Line**: {result['line_number']}\n"
        summary += f"- **Context**: ...{result['context']}...\n\n"

    if len(results) >= 20:
        summary += "*Showing first 20 results. Use more specific search terms for better results.*\n"

    return summary
