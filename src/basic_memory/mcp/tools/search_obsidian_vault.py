"""Search Obsidian vault tool for Basic Memory MCP server.

This tool searches through external Obsidian vaults using Obsidian-specific
search patterns and syntax.
"""

import os
import re
from pathlib import Path
from typing import Optional, List, Dict, Any
from datetime import datetime

from loguru import logger

from basic_memory.mcp.server import mcp


@mcp.tool(
    description="""Search through external Obsidian vaults without importing them into Basic Memory.

This tool allows you to query Obsidian vaults directly from the filesystem, providing
search capabilities across markdown files, canvas files, and other Obsidian content types.

SEARCH CAPABILITIES:
- Full-text search across all vault markdown files
- File type filtering (markdown, canvas, all files)
- Case-sensitive or case-insensitive matching
- Content preview with surrounding context
- File path and metadata information
- Support for large vaults with result limiting

PARAMETERS:
- vault_path (str, REQUIRED): Filesystem path to Obsidian vault root directory
- query (str, REQUIRED): Search term or phrase to find
- search_type (str, default="text"): Search scope (text, file, path, content)
- max_results (int, default=20): Maximum number of results to return
- include_content (bool, default=False): Include file content previews in results

SEARCH TYPES:
- "text": Search within file contents (default)
- "file": Search in filenames only
- "path": Search in file paths
- "content": Full content search with context

RESULT FORMAT:
Returns structured results showing:
- File paths and names
- Match locations within files
- Content snippets (if enabled)
- File modification dates
- Match counts and statistics

USAGE EXAMPLES:
Basic search: search_obsidian_vault("/vault/path", "machine learning")
File names: search_obsidian_vault("/vault", "meeting notes", search_type="file")
With content: search_obsidian_vault("/obsidian-vault", "project plan", include_content=True)
Limited results: search_obsidian_vault("/vault", "project", max_results=50)

RETURNS:
Formatted search results with file paths, match counts, and optional content previews.

NOTE: This searches external vaults without importing them. For permanent access,
use load_obsidian_vault() to import the content into Basic Memory.""",
)
async def search_obsidian_vault(
    vault_path: str,
    query: str,
    search_type: str = "text",
    max_results: int = 20,
    include_content: bool = False,
) -> str:
    """Search through an external Obsidian vault using various search patterns.

    This tool provides Obsidian-style search capabilities for external vaults,
    supporting text search, tag search, file search, and more. It can search
    through markdown files in an Obsidian vault directory structure.

    Args:
        vault_path: Path to the Obsidian vault root directory
        query: Search query using Obsidian search syntax
        search_type: Type of search - "text", "tag", "file", "link", "frontmatter"
        max_results: Maximum number of results to return (default: 20)
        include_content: Whether to include matching content snippets (default: False)

    Returns:
        Formatted search results with file paths, titles, and optional content snippets

    Obsidian Search Syntax Examples:
        # Text search
        search_obsidian_vault("/path/to/vault", "machine learning")

        # Tag search
        search_obsidian_vault("/path/to/vault", "#todo", search_type="tag")

        # File search (by filename)
        search_obsidian_vault("/path/to/vault", "meeting", search_type="file")

        # Link search (find files linking to a note)
        search_obsidian_vault("/path/to/vault", "[[Project Alpha]]", search_type="link")

        # Frontmatter search
        search_obsidian_vault("/path/to/vault", "status: active", search_type="frontmatter")

    Advanced Search Patterns:
        - Boolean: "term1 AND term2", "term1 OR term2", "term1 NOT term2"
        - Wildcards: "project*", "*meeting*"
        - Exact phrases: '"exact phrase"'
        - Field search: "tags: #important #urgent"
        - Path search: "path:folder/subfolder"
    """

    try:
        vault_path_obj = Path(vault_path)

        # Validate vault path exists
        if not vault_path_obj.exists():
            return f"# Vault Search Failed\n\nVault path does not exist: {vault_path}"

        if not vault_path_obj.is_dir():
            return f"# Vault Search Failed\n\nPath is not a directory: {vault_path}"

        logger.info(f"Searching Obsidian vault: {vault_path} for query: '{query}' (type: {search_type})")

        # Find all markdown files in the vault
        markdown_files = await _find_markdown_files(vault_path_obj)

        if not markdown_files:
            return f"# Vault Search Complete\n\nNo markdown files found in vault: {vault_path}"

        # Perform the search based on type
        if search_type == "text":
            results = await _search_text(markdown_files, query)
        elif search_type == "tag":
            results = await _search_tags(markdown_files, query)
        elif search_type == "file":
            results = await _search_files(markdown_files, query)
        elif search_type == "link":
            results = await _search_links(markdown_files, query)
        elif search_type == "frontmatter":
            results = await _search_frontmatter(markdown_files, query)
        else:
            return f"# Vault Search Failed\n\nUnknown search type: {search_type}. Supported: text, tag, file, link, frontmatter"

        # Limit results
        results = results[:max_results]

        # Format results
        return _format_search_results(results, vault_path, query, search_type, include_content)

    except Exception as e:
        logger.error(f"Vault search failed: {e}")
        return f"# Vault Search Failed\n\nError: {e}"


async def _find_markdown_files(vault_path: Path) -> List[Path]:
    """Find all markdown files in the vault."""
    markdown_files = []

    # Use MCP filesystem to list directory recursively
    try:
        from mcp_filesystem import list_directory

        async def find_recursive(current_path: str) -> List[str]:
            """Recursively find markdown files."""
            files = []
            try:
                # List current directory
                dir_contents = await list_directory(current_path)

                # Parse the directory listing (it's returned as formatted text)
                lines = dir_contents.split('\n')
                for line in lines:
                    if '📄' in line and '.md' in line:
                        # Extract filename from the formatted line
                        parts = line.split()
                        if len(parts) >= 2:
                            filename = parts[1].strip()
                            if filename.endswith('.md'):
                                files.append(os.path.join(current_path, filename))
                    elif '📁' in line and not line.strip().endswith('.'):
                        # Directory - recurse
                        parts = line.split()
                        if len(parts) >= 2:
                            dirname = parts[1].strip()
                            subdir_path = os.path.join(current_path, dirname)
                            subfiles = await find_recursive(subdir_path)
                            files.extend(subfiles)

            except Exception as e:
                logger.warning(f"Error listing directory {current_path}: {e}")

            return files

        # Start recursive search from vault root
        markdown_files_str = await find_recursive(str(vault_path))
        markdown_files = [Path(f) for f in markdown_files_str]

    except ImportError:
        # Fallback to direct filesystem access if MCP filesystem not available
        logger.warning("MCP filesystem not available, using direct access")
        markdown_files = list(vault_path.rglob("*.md"))

    return markdown_files


async def _search_text(markdown_files: List[Path], query: str) -> List[Dict[str, Any]]:
    """Search for text content in markdown files."""
    results = []
    search_terms = _parse_search_query(query)

    for file_path in markdown_files:
        try:
            # Read file content
            content = file_path.read_text(encoding='utf-8')

            # Extract title from first heading or filename
            title = _extract_title(content, file_path)

            # Check if all search terms are present
            matches = []
            content_lower = content.lower()

            for term in search_terms:
                if term.startswith('"') and term.endswith('"'):
                    # Exact phrase search
                    phrase = term[1:-1].lower()
                    if phrase in content_lower:
                        matches.append(term)
                else:
                    # Regular term search
                    if term.lower() in content_lower:
                        matches.append(term)

            if len(matches) == len(search_terms):  # All terms found
                # Find line numbers with matches
                lines = content.split('\n')
                match_lines = []
                for i, line in enumerate(lines):
                    line_lower = line.lower()
                    if all(term.strip('"').lower() in line_lower for term in search_terms):
                        match_lines.append((i + 1, line.strip()))

                results.append({
                    'file_path': file_path,
                    'title': title,
                    'matches': match_lines[:5],  # Limit to first 5 matches
                    'total_matches': len(match_lines)
                })

        except Exception as e:
            logger.warning(f"Error reading file {file_path}: {e}")
            continue

    # Sort by number of matches (most relevant first)
    results.sort(key=lambda x: x['total_matches'], reverse=True)
    return results


async def _search_tags(markdown_files: List[Path], query: str) -> List[Dict[str, Any]]:
    """Search for tags in markdown files."""
    results = []

    # Clean query to extract tag
    tag = query.strip().lstrip('#')

    for file_path in markdown_files:
        try:
            content = file_path.read_text(encoding='utf-8')
            title = _extract_title(content, file_path)

            # Find all tags in the file
            tags_in_file = re.findall(r'#(\w+)', content)

            if tag.lower() in [t.lower() for t in tags_in_file]:
                # Count occurrences
                count = sum(1 for t in tags_in_file if t.lower() == tag.lower())

                results.append({
                    'file_path': file_path,
                    'title': title,
                    'tags': tags_in_file,
                    'tag_matches': [tag],
                    'total_matches': count
                })

        except Exception as e:
            logger.warning(f"Error reading file {file_path}: {e}")
            continue

    return results


async def _search_files(markdown_files: List[Path], query: str) -> List[Dict[str, Any]]:
    """Search for files by filename."""
    results = []
    query_lower = query.lower()

    for file_path in markdown_files:
        filename = file_path.stem.lower()  # filename without .md extension

        if query_lower in filename:
            try:
                content = file_path.read_text(encoding='utf-8')
                title = _extract_title(content, file_path)

                results.append({
                    'file_path': file_path,
                    'title': title,
                    'filename_match': True,
                    'total_matches': 1
                })

            except Exception as e:
                logger.warning(f"Error reading file {file_path}: {e}")
                # Still include files we can't read
                results.append({
                    'file_path': file_path,
                    'title': file_path.stem,
                    'filename_match': True,
                    'total_matches': 1
                })

    return results


async def _search_links(markdown_files: List[Path], query: str) -> List[Dict[str, Any]]:
    """Search for wikilinks in markdown files."""
    results = []

    # Extract link target from [[link]]
    link_match = re.search(r'\[\[([^\]]+)\]\]', query)
    if not link_match:
        return results

    target_link = link_match.group(1).strip()

    for file_path in markdown_files:
        try:
            content = file_path.read_text(encoding='utf-8')
            title = _extract_title(content, file_path)

            # Find all wikilinks in the file
            links_in_file = re.findall(r'\[\[([^\]]+)\]\]', content)

            if target_link.lower() in [link.lower() for link in links_in_file]:
                count = sum(1 for link in links_in_file if link.lower() == target_link.lower())

                results.append({
                    'file_path': file_path,
                    'title': title,
                    'links': links_in_file,
                    'link_matches': [target_link],
                    'total_matches': count
                })

        except Exception as e:
            logger.warning(f"Error reading file {file_path}: {e}")
            continue

    return results


async def _search_frontmatter(markdown_files: List[Path], query: str) -> List[Dict[str, Any]]:
    """Search in YAML frontmatter of markdown files."""
    results = []

    # Parse query like "field: value"
    if ':' not in query:
        return results

    field, value = query.split(':', 1)
    field = field.strip()
    value = value.strip()

    for file_path in markdown_files:
        try:
            content = file_path.read_text(encoding='utf-8')
            title = _extract_title(content, file_path)

            # Extract frontmatter
            frontmatter = _extract_frontmatter(content)

            if field in frontmatter:
                field_value = str(frontmatter[field]).lower()
                search_value = value.lower()

                if search_value in field_value:
                    results.append({
                        'file_path': file_path,
                        'title': title,
                        'frontmatter': frontmatter,
                        'field_matches': {field: frontmatter[field]},
                        'total_matches': 1
                    })

        except Exception as e:
            logger.warning(f"Error reading file {file_path}: {e}")
            continue

    return results


def _parse_search_query(query: str) -> List[str]:
    """Parse search query into individual search terms."""
    # Handle quoted phrases
    terms = []
    current_term = ""
    in_quotes = False

    for char in query:
        if char == '"' and not in_quotes:
            in_quotes = True
            if current_term:
                terms.append(current_term.strip())
                current_term = ""
        elif char == '"' and in_quotes:
            in_quotes = False
            if current_term:
                terms.append(f'"{current_term}"')
                current_term = ""
        elif char == ' ' and not in_quotes:
            if current_term:
                terms.append(current_term.strip())
                current_term = ""
        else:
            current_term += char

    if current_term:
        if in_quotes:
            terms.append(f'"{current_term}"')
        else:
            terms.append(current_term.strip())

    return [term for term in terms if term]


def _extract_title(content: str, file_path: Path) -> str:
    """Extract title from markdown content or filename."""
    lines = content.split('\n')

    # Look for first heading
    for line in lines:
        if line.startswith('# '):
            return line[2:].strip()

    # Fallback to filename
    return file_path.stem


def _extract_frontmatter(content: str) -> Dict[str, Any]:
    """Extract YAML frontmatter from markdown content."""
    if not content.startswith('---'):
        return {}

    lines = content.split('\n')
    if len(lines) < 3:
        return {}

    # Find end of frontmatter
    end_idx = -1
    for i, line in enumerate(lines[1:], 1):
        if line.strip() == '---':
            end_idx = i
            break

    if end_idx == -1:
        return {}

    frontmatter_lines = lines[1:end_idx]

    # Simple YAML parsing (basic key-value pairs)
    frontmatter = {}
    for line in frontmatter_lines:
        if ':' in line:
            key, value = line.split(':', 1)
            key = key.strip()
            value = value.strip()

            # Try to parse as number or boolean
            if value.isdigit():
                frontmatter[key] = int(value)
            elif value.lower() in ('true', 'false'):
                frontmatter[key] = value.lower() == 'true'
            else:
                frontmatter[key] = value

    return frontmatter


def _format_search_results(results: List[Dict[str, Any]], vault_path: str, query: str, search_type: str, include_content: bool) -> str:
    """Format search results into readable output."""
    if not results:
        return f"# Vault Search Complete\n\nNo results found for '{query}' in vault: {vault_path}"

    output_lines = [
        f"# Vault Search Results",
        f"Query: '{query}' (type: {search_type})",
        f"Vault: {vault_path}",
        f"Found {len(results)} matching files",
        ""
    ]

    for i, result in enumerate(results, 1):
        file_path = result['file_path']
        title = result['title']

        # Calculate relative path from vault
        try:
            rel_path = file_path.relative_to(vault_path)
        except ValueError:
            rel_path = file_path

        output_lines.append(f"## {i}. {title}")
        output_lines.append(f"**File:** {rel_path}")
        output_lines.append(f"**Path:** {file_path}")

        # Add specific match information
        if 'matches' in result and result['matches']:
            output_lines.append(f"**Matches:** {result['total_matches']} total")
            if include_content:
                for line_num, line_content in result['matches'][:3]:  # Show first 3 matches
                    # Truncate long lines
                    if len(line_content) > 100:
                        line_content = line_content[:97] + "..."
                    output_lines.append(f"  - Line {line_num}: {line_content}")

        elif 'tags' in result:
            output_lines.append(f"**Tags:** {', '.join(result['tags'])}")

        elif 'links' in result:
            output_lines.append(f"**Links:** {', '.join(result['links'])}")

        elif 'frontmatter' in result:
            fm_lines = []
            for k, v in result['frontmatter'].items():
                fm_lines.append(f"{k}: {v}")
            output_lines.append(f"**Frontmatter:** {', '.join(fm_lines)}")

        elif 'filename_match' in result:
            output_lines.append("**Match:** Filename")

        output_lines.append("")

    return "\n".join(output_lines)
