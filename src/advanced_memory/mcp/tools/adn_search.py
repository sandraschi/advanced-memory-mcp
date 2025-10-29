"""Search Manager portmanteau tool for Advanced Memory MCP server.

This tool consolidates all search operations: notes, obsidian, joplin, notion, evernote.
It reduces the number of MCP tools while maintaining full functionality.
"""

from loguru import logger

from advanced_memory.mcp.mcp_instance import mcp


@mcp.tool
async def adn_search(
    operation: str,
    query: str,
    source_path: str | None = None,
    search_type: str = "text",
    page: int = 1,
    page_size: int = 10,
    max_results: int = 20,
    case_sensitive: bool = False,
    include_content: bool = False,
    types: list[str] | None = None,
    entity_types: list[str] | None = None,
    after_date: str | None = None,
    file_type: str | None = None,
    notebook_filter: str | None = None,
    tag_filter: str | None = None,
    project: str | None = None,
) -> str:
    """Comprehensive search management tool for Advanced Memory knowledge base.

    This portmanteau tool consolidates all search operations into a single interface,
    reducing MCP tool count while maintaining full functionality for Cursor IDE compatibility.

    ⚠️ IMPORTANT: The "notes" operation searches CONTENT (text within notes), not by date/recency.
    
    - To find "latest notes" or "recent notes": Use `adn_navigation("recent_activity", timeframe="1d")`
    - To search by topic AND filter by date: Use the `after_date` parameter
    - Queries like "latest note today" will search for those WORDS in content, not actual latest notes

    SUPPORTED OPERATIONS:
    - notes: Full-text search across Advanced Memory knowledge base
    - obsidian: Search through external Obsidian vaults without importing
    - joplin: Search through external Joplin exports without importing
    - notion: Search through external Notion exports without importing
    - evernote: Search through external Evernote exports without importing

    SEARCH FEATURES:
    - Full-text content search with relevance ranking
    - Metadata search (titles, tags, notebooks)
    - Boolean operators (AND, OR, NOT) for complex queries
    - Phrase matching with quotes for exact phrases
    - Wildcard support for pattern matching
    - Case-sensitive and case-insensitive options
    - Pagination support for large result sets
    - Content previews and context highlighting

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
        return await _evernote_search(
            query, source_path, case_sensitive, file_type, notebook_filter, tag_filter, max_results
        )
    else:
        return f"# Error\n\nInvalid operation '{operation}'. Supported operations: notes, obsidian, joplin, notion, evernote"


async def _notes_search(
    query: str,
    page: int,
    page_size: int,
    types: list[str] | None,
    entity_types: list[str] | None,
    after_date: str | None,
    project: str | None,
) -> str:
    """Handle Advanced Memory notes search operation."""
    from advanced_memory.mcp.tools.search import search_notes

    result = await search_notes(
        query, page, page_size, "text", types, entity_types, after_date, project
    )

    # Convert SearchResponse to string if needed
    if isinstance(result, str):
        return result

    # Format SearchResponse as markdown string
    output = [f"# Search Results: {len(result.results)} matches\n"]

    if not result.results:
        output.append("No results found for your query.\n")
        output.append("**Suggestions:**")
        output.append("- Try broader terms")
        output.append("- Check spelling")
        output.append("- Use fewer search terms")
        return "\n".join(output)

    for idx, item in enumerate(result.results, 1):
        title = item.title or "Untitled"
        permalink = item.permalink or ""
        item_type = item.type.value if hasattr(item.type, 'value') else str(item.type)

        output.append(f"## {idx}. {title}")
        output.append(f"**Type:** {item_type}")
        output.append(f"**Permalink:** `{permalink}`")
        output.append(f"**Score:** {item.score:.2f}")

        # Add content snippet if available
        if item.content:
            snippet = item.content[:200] + "..." if len(item.content) > 200 else item.content
            output.append(f"**Preview:** {snippet}")

        output.append("")

    # Add pagination info
    output.append(f"**Page:** {result.current_page} of {((len(result.results) // result.page_size) + 1 if result.results else 1)}")

    return "\n".join(output)


async def _obsidian_search(
    query: str, source_path: str | None, search_type: str, max_results: int, include_content: bool
) -> str:
    """Handle Obsidian vault search operation."""
    if not source_path:
        return "# Error\n\nObsidian search requires: source_path parameter"

    from advanced_memory.mcp.tools.search_obsidian_vault import search_obsidian_vault

    return await search_obsidian_vault(
        source_path, query, search_type, max_results, include_content
    )  # type: ignore[operator,no-any-return]


async def _joplin_search(
    query: str, source_path: str | None, search_type: str, max_results: int, include_content: bool
) -> str:
    """Handle Joplin export search operation."""
    if not source_path:
        return "# Error\n\nJoplin search requires: source_path parameter"

    from advanced_memory.mcp.tools.search_joplin_vault import search_joplin_vault

    return await search_joplin_vault(source_path, query, search_type, max_results, include_content)  # type: ignore[operator,no-any-return]


async def _notion_search(
    query: str,
    source_path: str | None,
    case_sensitive: bool,
    file_type: str | None,
    max_results: int,
) -> str:
    """Handle Notion export search operation."""
    if not source_path:
        return "# Error\n\nNotion search requires: source_path parameter"

    from advanced_memory.mcp.tools.search_notion_vault import search_notion_vault

    return await search_notion_vault(source_path, query, case_sensitive, file_type, max_results)  # type: ignore[operator,no-any-return]


async def _evernote_search(
    query: str,
    source_path: str | None,
    case_sensitive: bool,
    file_type: str | None,
    notebook_filter: str | None,
    tag_filter: str | None,
    max_results: int,
) -> str:
    """Handle Evernote export search operation."""
    if not source_path:
        return "# Error\n\nEvernote search requires: source_path parameter"

    from advanced_memory.mcp.tools.search_evernote_vault import search_evernote_vault

    return await search_evernote_vault(
        source_path, query, case_sensitive, file_type, notebook_filter, tag_filter, max_results
    )  # type: ignore[operator,no-any-return]
