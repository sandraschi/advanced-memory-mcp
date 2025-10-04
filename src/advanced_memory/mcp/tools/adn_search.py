"""Search Manager portmanteau tool for Advanced Memory MCP server.

This tool consolidates all search operations: notes, obsidian, joplin, notion, evernote.
It reduces the number of MCP tools while maintaining full functionality.
"""

from typing import Optional, List, Dict, Any

from loguru import logger

from advanced_memory.mcp.server import mcp


@mcp.tool(
    description="""Comprehensive search management tool for Advanced Memory knowledge base.

This portmanteau tool consolidates all search operations into a single interface,
reducing MCP tool count while maintaining full functionality for Cursor IDE compatibility.

SUPPORTED OPERATIONS:
- **notes**: Full-text search across Advanced Memory knowledge base
- **obsidian**: Search through external Obsidian vaults without importing
- **joplin**: Search through external Joplin exports without importing
- **notion**: Search through external Notion exports without importing
- **evernote**: Search through external Evernote exports without importing

SEARCH FEATURES:
- Full-text content search with relevance ranking
- Metadata search (titles, tags, notebooks)
- Boolean operators (AND, OR, NOT) for complex queries
- Phrase matching with quotes for exact phrases
- Wildcard support for pattern matching
- Case-sensitive and case-insensitive options
- Pagination support for large result sets
- Content previews and context highlighting

PARAMETERS:
- operation (str, REQUIRED): Search operation type (notes, obsidian, joplin, notion, evernote)
- query (str, REQUIRED): Search terms with boolean operators and phrases
- source_path (str, optional): Path to external vault/export for external searches
- search_type (str, default="text"): Search scope (text, metadata, combined, file, path)
- page (int, default=1): Result page for pagination
- page_size (int, default=10): Results per page (max 100)
- max_results (int, default=20): Maximum number of results to return
- case_sensitive (bool, default=False): Whether search should be case-sensitive
- include_content (bool, default=False): Include content previews in results
- types (List[str], optional): Content type filters for notes search
- entity_types (List[str], optional): Entity category filters for notes search
- after_date (str, optional): Date filter (ISO format or relative like "7d")
- file_type (str, optional): File type filter for external searches
- notebook_filter (str, optional): Filter results to specific notebook
- tag_filter (str, optional): Filter results by tag name
- project (str, optional): Project scope for notes search

USAGE EXAMPLES:
Notes search: adn_search("notes", query="machine learning", page=1, page_size=10)
Obsidian search: adn_search("obsidian", query="project planning", source_path="/path/to/vault")
Joplin search: adn_search("joplin", query="meeting notes", source_path="/path/to/export")
Notion search: adn_search("notion", query="database design", source_path="/path/to/notion-export")
Evernote search: adn_search("evernote", query="research", source_path="/path/to/exports")

RETURNS:
Operation-specific results with search details, match counts, and content previews.

NOTE: This tool provides all search functionality in a single interface for better MCP client compatibility.""",
)
async def adn_search(
    operation: str,
    query: str,
    source_path: Optional[str] = None,
    search_type: str = "text",
    page: int = 1,
    page_size: int = 10,
    max_results: int = 20,
    case_sensitive: bool = False,
    include_content: bool = False,
    types: Optional[List[str]] = None,
    entity_types: Optional[List[str]] = None,
    after_date: Optional[str] = None,
    file_type: Optional[str] = None,
    notebook_filter: Optional[str] = None,
    tag_filter: Optional[str] = None,
    project: Optional[str] = None,
) -> str:
    """Comprehensive search management for Advanced Memory knowledge base.

    This portmanteau tool consolidates all search operations:
    - notes: Full-text search across Advanced Memory knowledge base
    - obsidian: Search through external Obsidian vaults
    - joplin: Search through external Joplin exports
    - notion: Search through external Notion exports
    - evernote: Search through external Evernote exports

    Args:
        operation: The search operation to perform
        query: Search terms with boolean operators and phrases
        source_path: Path to external vault/export for external searches
        search_type: Search scope for external searches
        page: Result page for pagination
        page_size: Results per page
        max_results: Maximum number of results to return
        case_sensitive: Whether search should be case-sensitive
        include_content: Include content previews in results
        types: Content type filters for notes search
        entity_types: Entity category filters for notes search
        after_date: Date filter for notes search
        file_type: File type filter for external searches
        notebook_filter: Filter results to specific notebook
        tag_filter: Filter results by tag name
        project: Optional project name

    Returns:
        Operation-specific result with search details and match counts

    Examples:
        # Search Advanced Memory notes
        adn_search("notes", query="machine learning", page=1, page_size=10)

        # Search external Obsidian vault
        adn_search("obsidian", query="project planning", source_path="/path/to/vault")

        # Search external Joplin export
        adn_search("joplin", query="meeting notes", source_path="/path/to/export")

        # Search with filters
        adn_search("notes", query="research", entity_types=["note"], after_date="2024-01-01")
    """
    logger.info(f"MCP tool call tool=adn_search operation={operation} query={query}")

    # Route to appropriate operation
    if operation == "notes":
        return await _notes_search(query, page, page_size, types, entity_types, after_date, project)
    elif operation == "obsidian":
        return await _obsidian_search(query, source_path, search_type, max_results, include_content)
    elif operation == "joplin":
        return await _joplin_search(query, source_path, search_type, max_results, include_content)
    elif operation == "notion":
        return await _notion_search(query, source_path, case_sensitive, file_type, max_results)
    elif operation == "evernote":
        return await _evernote_search(query, source_path, case_sensitive, file_type, notebook_filter, tag_filter, max_results)
    else:
        return f"# Error\n\nInvalid operation '{operation}'. Supported operations: notes, obsidian, joplin, notion, evernote"


async def _notes_search(query: str, page: int, page_size: int, types: Optional[List[str]], entity_types: Optional[List[str]], after_date: Optional[str], project: Optional[str]) -> str:
    """Handle Advanced Memory notes search operation."""
    from advanced_memory.mcp.tools.search_notes import search_notes
    return await search_notes(query, page, page_size, "text", types, entity_types, after_date, project)


async def _obsidian_search(query: str, source_path: Optional[str], search_type: str, max_results: int, include_content: bool) -> str:
    """Handle Obsidian vault search operation."""
    if not source_path:
        return "# Error\n\nObsidian search requires: source_path parameter"
    
    from advanced_memory.mcp.tools.search_obsidian_vault import search_obsidian_vault
    return await search_obsidian_vault(source_path, query, search_type, max_results, include_content)


async def _joplin_search(query: str, source_path: Optional[str], search_type: str, max_results: int, include_content: bool) -> str:
    """Handle Joplin export search operation."""
    if not source_path:
        return "# Error\n\nJoplin search requires: source_path parameter"
    
    from advanced_memory.mcp.tools.search_joplin_vault import search_joplin_vault
    return await search_joplin_vault(source_path, query, search_type, max_results, include_content)


async def _notion_search(query: str, source_path: Optional[str], case_sensitive: bool, file_type: Optional[str], max_results: int) -> str:
    """Handle Notion export search operation."""
    if not source_path:
        return "# Error\n\nNotion search requires: source_path parameter"
    
    from advanced_memory.mcp.tools.search_notion_vault import search_notion_vault
    return await search_notion_vault(source_path, query, case_sensitive, file_type, max_results)


async def _evernote_search(query: str, source_path: Optional[str], case_sensitive: bool, file_type: Optional[str], notebook_filter: Optional[str], tag_filter: Optional[str], max_results: int) -> str:
    """Handle Evernote export search operation."""
    if not source_path:
        return "# Error\n\nEvernote search requires: source_path parameter"
    
    from advanced_memory.mcp.tools.search_evernote_vault import search_evernote_vault
    return await search_evernote_vault(source_path, query, case_sensitive, file_type, notebook_filter, tag_filter, max_results)
