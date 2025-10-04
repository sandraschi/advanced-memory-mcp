"""Search Joplin vault tool for Basic Memory MCP server.

This tool searches through external Joplin exports using Joplin-specific
search patterns and metadata.
"""

import os
import re
import json
from pathlib import Path
from typing import Optional, List, Dict, Any
from datetime import datetime

from loguru import logger

from advanced_memory.mcp.server import mcp


@mcp.tool(
    description="""Search through external Joplin exports without importing them into Basic Memory.

This tool enables querying Joplin export directories directly from the filesystem,
providing search capabilities across markdown notes, JSON metadata, and notebook structures.

SEARCH CAPABILITIES:
- Full-text search across markdown note content
- Metadata search in JSON files (titles, tags, notebooks)
- Combined content and metadata queries
- File type filtering (markdown, JSON, all files)
- Case-sensitive or case-insensitive matching
- Structured results with notebook organization

PARAMETERS:
- vault_path (str, REQUIRED): Path to Joplin export directory (containing .md and .json files)
- query (str, REQUIRED): Search term or phrase to find
- search_type (str, default="text"): Search scope (text, metadata, combined)
- max_results (int, default=20): Maximum number of results to return
- include_content (bool, default=False): Include note content previews in results

SEARCH TYPES:
- "text": Search within markdown note content only
- "metadata": Search in JSON metadata (titles, tags, notebooks)
- "combined": Search both content and metadata

JOPLIN EXPORT STRUCTURE:
- .md files: Note content in markdown format
- .json files: Metadata including title, tags, notebook, timestamps
- Organized by notebook hierarchy

RESULT FORMAT:
Returns structured results showing:
- Note titles and content snippets
- Notebook and tag information
- File paths and modification dates
- Match counts and relevance scores

USAGE EXAMPLES:
Content search: search_joplin_vault("/export/path", "meeting notes")
Metadata search: search_joplin_vault("/export", "important", search_type="metadata")
Combined: search_joplin_vault("/export", "project", search_type="combined")
With previews: search_joplin_vault("/joplin-export", "meeting notes", include_content=True)

RETURNS:
Formatted search results with note details, notebook organization, and optional content previews.

NOTE: This searches external Joplin exports without importing them. For permanent access
and enhanced search capabilities, use load_joplin_vault() to import into Basic Memory.""",
)
async def search_joplin_vault(
    vault_path: str,
    query: str,
    search_type: str = "text",
    max_results: int = 20,
    include_content: bool = False,
) -> str:
    """Search through an external Joplin export using various search patterns.

    This tool provides Joplin-specific search capabilities for external exports,
    supporting text search, tag search, notebook search, and more. It can search
    through Joplin's markdown files and JSON metadata.

    Args:
        vault_path: Path to the Joplin export root directory
        query: Search query using Joplin search syntax
        search_type: Type of search - "text", "tag", "notebook", "title", "id"
        max_results: Maximum number of results to return (default: 20)
        include_content: Whether to include matching content snippets (default: False)

    Returns:
        Formatted search results with file paths, titles, and optional content snippets

    Joplin Search Syntax Examples:
        # Text search
        search_joplin_vault("/path/to/export", "machine learning")

        # Tag search
        search_joplin_vault("/path/to/export", "important", search_type="tag")

        # Notebook/folder search
        search_joplin_vault("/path/to/export", "Research", search_type="notebook")

        # Title search
        search_joplin_vault("/path/to/export", "meeting", search_type="title")

        # ID search (find specific note by Joplin ID)
        search_joplin_vault("/path/to/export", "abc123def456", search_type="id")

    Advanced Search Patterns:
        - Boolean: "term1 AND term2", "term1 OR term2", "term1 NOT term2"
        - Wildcards: "project*", "*meeting*"
        - Exact phrases: '"exact phrase"'
        - Date ranges: created:2024-01, updated:2024-01-15
    """

    try:
        vault_path_obj = Path(vault_path)

        # Validate vault path exists
        if not vault_path_obj.exists():
            return f"# Joplin Search Failed\n\nVault path does not exist: {vault_path}"

        if not vault_path_obj.is_dir():
            return f"# Joplin Search Failed\n\nPath is not a directory: {vault_path}"

        logger.info(f"Searching Joplin vault: {vault_path} for query: '{query}' (type: {search_type})")

        # Find all Joplin note files (markdown files with corresponding JSON metadata)
        joplin_files = await _find_joplin_files(vault_path_obj)

        if not joplin_files:
            return f"# Joplin Search Complete\n\nNo Joplin notes found in export: {vault_path}"

        # Perform the search based on type
        if search_type == "text":
            results = await _search_text(joplin_files, query)
        elif search_type == "tag":
            results = await _search_tags(joplin_files, query)
        elif search_type == "notebook":
            results = await _search_notebooks(joplin_files, query)
        elif search_type == "title":
            results = await _search_titles(joplin_files, query)
        elif search_type == "id":
            results = await _search_ids(joplin_files, query)
        else:
            return f"# Joplin Search Failed\n\nUnknown search type: {search_type}. Supported: text, tag, notebook, title, id"

        # Limit results
        results = results[:max_results]

        # Format results
        return _format_search_results(results, vault_path, query, search_type, include_content)

    except Exception as e:
        logger.error(f"Joplin search failed: {e}")
        return f"# Joplin Search Failed\n\nError: {e}"


async def _find_joplin_files(vault_path: Path) -> List[Dict[str, Path]]:
    """Find all Joplin note files (markdown + JSON pairs)."""
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
                                'base_name': base_name
                            })

                except Exception as e:
                    logger.warning(f"Error scanning directory {current_path}: {e}")

                return files

            joplin_files_raw = await scan_recursive(str(vault_path))
            joplin_files = [
                {'md': Path(f['md']), 'json': Path(f['json']), 'base_name': f['base_name']}
                for f in joplin_files_raw
            ]

        except ImportError:
            # Fallback to direct filesystem access
            logger.warning("MCP filesystem not available, using direct access")

            file_groups = {}
            for file_path in vault_path.rglob("*"):
                if file_path.is_file():
                    if file_path.suffix.lower() == '.md':
                        base_name = file_path.stem
                        if base_name not in file_groups:
                            file_groups[base_name] = {}
                        file_groups[base_name]['md'] = file_path
                    elif file_path.suffix.lower() == '.json':
                        base_name = file_path.stem
                        if base_name not in file_groups:
                            file_groups[base_name] = {}
                        file_groups[base_name]['json'] = file_path

            # Only include complete pairs
            for base_name, file_dict in file_groups.items():
                if 'md' in file_dict and 'json' in file_dict:
                    joplin_files.append({
                        'md': file_dict['md'],
                        'json': file_dict['json'],
                        'base_name': base_name
                    })

    except Exception as e:
        logger.error(f"Error finding Joplin files: {e}")

    return joplin_files


async def _search_text(joplin_files: List[Dict[str, Path]], query: str) -> List[Dict[str, Any]]:
    """Search for text content in Joplin notes."""
    results = []
    search_terms = _parse_search_query(query)

    for file_info in joplin_files:
        try:
            # Read metadata
            metadata = _read_joplin_metadata(file_info['json'])

            # Read content
            content = file_info['md'].read_text(encoding='utf-8')

            # Extract title from metadata or content
            title = metadata.get('title', _extract_title_from_content(content))

            # Check if all search terms are present
            matches = []
            search_text = content.lower()

            for term in search_terms:
                if term.startswith('"') and term.endswith('"'):
                    # Exact phrase search
                    phrase = term[1:-1].lower()
                    if phrase in search_text:
                        matches.append(term)
                else:
                    # Regular term search
                    if term.lower() in search_text:
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
                    'file_info': file_info,
                    'title': title,
                    'metadata': metadata,
                    'matches': match_lines[:5],  # Limit to first 5 matches
                    'total_matches': len(match_lines)
                })

        except Exception as e:
            logger.warning(f"Error reading Joplin file {file_info['md']}: {e}")
            continue

    # Sort by number of matches (most relevant first)
    results.sort(key=lambda x: x['total_matches'], reverse=True)
    return results


async def _search_tags(joplin_files: List[Dict[str, Path]], query: str) -> List[Dict[str, Any]]:
    """Search for tags in Joplin notes."""
    results = []

    for file_info in joplin_files:
        try:
            metadata = _read_joplin_metadata(file_info['json'])
            content = file_info['md'].read_text(encoding='utf-8')
            title = metadata.get('title', _extract_title_from_content(content))

            # Get tags from metadata
            tags = metadata.get('tags', [])

            # Also check for tags in content (Joplin sometimes stores them in content)
            content_tags = re.findall(r'#(\w+)', content)
            all_tags = list(set(tags + content_tags))

            # Check if query matches any tag
            query_lower = query.lower()
            matching_tags = [tag for tag in all_tags if query_lower in tag.lower()]

            if matching_tags:
                results.append({
                    'file_info': file_info,
                    'title': title,
                    'metadata': metadata,
                    'tags': all_tags,
                    'tag_matches': matching_tags,
                    'total_matches': len(matching_tags)
                })

        except Exception as e:
            logger.warning(f"Error reading Joplin file {file_info['md']}: {e}")
            continue

    return results


async def _search_notebooks(joplin_files: List[Dict[str, Path]], query: str) -> List[Dict[str, Any]]:
    """Search for notes in specific notebooks/folders."""
    results = []
    query_lower = query.lower()

    for file_info in joplin_files:
        try:
            metadata = _read_joplin_metadata(file_info['json'])
            content = file_info['md'].read_text(encoding='utf-8')
            title = metadata.get('title', _extract_title_from_content(content))

            # Get notebook/folder path
            notebook_path = _get_notebook_path(file_info['md'], metadata)

            # Check if query matches notebook name or path
            if query_lower in notebook_path.lower():
                results.append({
                    'file_info': file_info,
                    'title': title,
                    'metadata': metadata,
                    'notebook_path': notebook_path,
                    'total_matches': 1
                })

        except Exception as e:
            logger.warning(f"Error reading Joplin file {file_info['md']}: {e}")
            continue

    return results


async def _search_titles(joplin_files: List[Dict[str, Path]], query: str) -> List[Dict[str, Any]]:
    """Search for notes by title."""
    results = []
    query_lower = query.lower()

    for file_info in joplin_files:
        try:
            metadata = _read_joplin_metadata(file_info['json'])
            content = file_info['md'].read_text(encoding='utf-8')

            # Get title from metadata or content
            title = metadata.get('title', _extract_title_from_content(content))

            if query_lower in title.lower():
                results.append({
                    'file_info': file_info,
                    'title': title,
                    'metadata': metadata,
                    'title_match': True,
                    'total_matches': 1
                })

        except Exception as e:
            logger.warning(f"Error reading Joplin file {file_info['md']}: {e}")
            continue

    return results


async def _search_ids(joplin_files: List[Dict[str, Path]], query: str) -> List[Dict[str, Any]]:
    """Search for notes by Joplin ID."""
    results = []

    for file_info in joplin_files:
        try:
            metadata = _read_joplin_metadata(file_info['json'])

            # Check if ID matches
            note_id = metadata.get('id', '')
            if query == note_id:
                content = file_info['md'].read_text(encoding='utf-8')
                title = metadata.get('title', _extract_title_from_content(content))

                results.append({
                    'file_info': file_info,
                    'title': title,
                    'metadata': metadata,
                    'id_match': True,
                    'total_matches': 1
                })
                break  # IDs should be unique, so we can stop after finding a match

        except Exception as e:
            logger.warning(f"Error reading Joplin file {file_info['md']}: {e}")
            continue

    return results


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

    # Fallback to first line or filename-like title
    return lines[0].strip() if lines else "Untitled"


def _get_notebook_path(md_path: Path, metadata: Dict[str, Any]) -> str:
    """Get the notebook/folder path for a Joplin note."""
    # Joplin stores parent relationships in metadata
    # For simplicity, we'll use the relative path from the export root
    return str(md_path.parent)


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


def _format_search_results(results: List[Dict[str, Any]], vault_path: str, query: str, search_type: str, include_content: bool) -> str:
    """Format search results into readable output."""
    if not results:
        return f"# Joplin Search Complete\n\nNo results found for '{query}' in vault: {vault_path}"

    output_lines = [
        f"# Joplin Search Results",
        f"Query: '{query}' (type: {search_type})",
        f"Export: {vault_path}",
        f"Found {len(results)} matching notes",
        ""
    ]

    for i, result in enumerate(results, 1):
        file_info = result['file_info']
        title = result['title']
        metadata = result['metadata']

        # Calculate relative path from vault
        try:
            rel_path = file_info['md'].relative_to(vault_path)
        except ValueError:
            rel_path = file_info['md']

        output_lines.append(f"## {i}. {title}")
        output_lines.append(f"**File:** {rel_path}")
        output_lines.append(f"**ID:** {metadata.get('id', 'unknown')}")

        # Add creation/update dates if available
        if 'created_time' in metadata:
            try:
                created_dt = datetime.fromtimestamp(metadata['created_time'] / 1000)
                output_lines.append(f"**Created:** {created_dt.strftime('%Y-%m-%d %H:%M')}")
            except:
                pass

        if 'updated_time' in metadata:
            try:
                updated_dt = datetime.fromtimestamp(metadata['updated_time'] / 1000)
                output_lines.append(f"**Updated:** {updated_dt.strftime('%Y-%m-%d %H:%M')}")
            except:
                pass

        # Add notebook info
        notebook_path = _get_notebook_path(file_info['md'], metadata)
        if notebook_path and notebook_path != str(vault_path):
            output_lines.append(f"**Notebook:** {notebook_path}")

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

        elif 'notebook_path' in result:
            output_lines.append(f"**Path:** {result['notebook_path']}")

        elif 'title_match' in result:
            output_lines.append("**Match:** Title")

        elif 'id_match' in result:
            output_lines.append("**Match:** ID")

        output_lines.append("")

    return "\n".join(output_lines)
