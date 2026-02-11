"""Search Manager portmanteau tool for Advanced Memory MCP server.

This tool consolidates all search operations: notes, obsidian, joplin, notion, evernote.
It reduces the number of MCP tools while maintaining full functionality.

RESPONSES:
Success: {"success": true, "operation": "...", "summary": "...", "results": [...], "metadata": {...}}
Error: {"success": false, "error": "...", "error_code": "...", "message": "...", "recovery_options": [...]}

For errors, check recovery_options for next steps. Use adn_project first to set context.
"""

import re
from typing import Literal

from loguru import logger

from advanced_memory.mcp.mcp_instance import mcp
from advanced_memory.mcp.tools.utils import build_error_response, build_success_response
from advanced_memory.utils import parse_tags


@mcp.tool
async def adn_search(
    operation: Literal["notes", "obsidian", "joplin", "notion", "evernote"],
    query: str,
    source_path: str | None = None,
    search_type: Literal["text", "title", "permalink", "tag", "file", "link", "frontmatter"]
    | None = "text",
    page: int = 1,
    page_size: int = 10,
    results_per_page: int
    | None = None,  # Alias for page_size (compatibility with standalone search_notes)
    max_results: int = 20,
    case_sensitive: bool = False,
    include_content: bool = False,
    types: list[str] | None = None,
    entity_types: list[str] | None = None,
    after_date: str | None = None,
    before_date: str | None = None,
    tags: list[str] | str | None = None,
    file_type: str | None = None,
    notebook_filter: str | None = None,
    tag_filter: str | None = None,
    project: str | None = None,
) -> dict:
    """Comprehensive search management tool for Advanced Memory knowledge base.

    This point-of-entry tool provides a unified interface for full-text search,
    pattern matching, and metadata filtering. It can search both the internal
    knowledge base (Advanced Memory) and external vault formats.

    RESPONSES:
    Success: {"success": true, "operation": "search", "summary": "...", "result": {...}}
    Error: {"success": false, "error": "...", "error_code": "...", "message": "...", "recovery_options": [...]}

    ---------------------------------------------------------------------------
    [PORTMANTEAU PATTERN RATIONALE]
    Consolidates 5 search operations into one tool to prevent tool explosion while maintaining full functionality.

    ---------------------------------------------------------------------------
    [PARAMETER DESIGN]
    The parameters are designed to be flexible and powerful:
    - Internal Search (notes): Supports advanced boolean logic, date filters, and tags.
    - External Search (obsidian, joplin, notion, evernote): Requires 'source_path'.
    - Aliasing: Operation names like 'title' or 'tag' automatically map to 'notes' with
      the corresponding 'search_type' pre-applied.

    ---------------------------------------------------------------------------
    [TOPIC SEARCH VS. RECENCY SEARCH]
    The 'notes' operation searches CONTENT (text within notes).
    - To find "latest notes" or "recent notes": Use 'adn_navigation("recent_activity", timeframe="1d")'.
    - To search by topic AND filter by date: Use the 'after_date' parameter.
    - Queries like "latest note today" search for those WORDS, they do not sort by date.

    ---------------------------------------------------------------------------
    [SUPPORTED OPERATIONS]
    - notes: Full-text search across Advanced Memory knowledge base (local data).
    - obsidian: Search through external Obsidian vaults without importing.
    - joplin: Search through external Joplin exports without importing.
    - notion: Search through external Notion exports without importing.
    - evernote: Search through external Evernote exports without importing.

    ---------------------------------------------------------------------------
    [SEARCH FEATURES]
    - Full-text content search with relevance ranking.
    - Metadata search (titles, tags, permalinks, frontmatter).
    - Boolean operators (AND, OR, NOT) and phrase matching ("quoted text").
    - Recursive pattern matching and wildcards (e.g., "docs/*").
    - Date range filtering (after_date, before_date).
    - Tag filtering (must match ALL specified tags).

    ---------------------------------------------------------------------------
    [PREREQUISITES]
    - For 'notes': Active project session must be established.
    - For external formats: Valid 'source_path' pointing to the vault/export folder.

    ---------------------------------------------------------------------------
    [PARAMETERS]
    - operation (str): Search operation to perform. MUST be one of:
      "notes", "obsidian", "joplin", "notion", "evernote"
    - query (str): Search terms with boolean operators and phrases (Required)
    - source_path (str): Path to external vault/export (Required for non-notes operations)
    - search_type (str): Type of search. One of: "text", "title", "permalink", "tag", "file", "link", "frontmatter"
    - page (int): Result page for pagination (Default: 1)
    - page_size (int): Results per page (Default: 10)
    - results_per_page (int): Alias for page_size (Compatibility)
    - max_results (int): Maximum results to return (Default: 20)
    - case_sensitive (bool): Whether search should be case-sensitive (Default: False)
    - include_content (bool): Include content previews in results (Default: False)
    - types (list): Content type filters (e.g., ["note", "person"])
    - entity_types (list): Entity category filters (e.g., ["entity", "observation"])
    - after_date (str): Date filter - content FROM this date (e.g., "2024-01-01", "1 week")
    - before_date (str): Date filter - content UNTIL this date (e.g., "winter 2024")
    - tags (list|str): Tag filter - notes must have ALL specified tags (List or comma-separated)
    - file_type (str): File type filter for external searches (e.g., "md", "html")
    - notebook_filter (str): Evernote specific - filter by notebook name
    - tag_filter (str): Evernote specific - filter by tag name
    - project (str): Optional override for active project name

    ---------------------------------------------------------------------------
    [USAGE]
    Use this tool for all content discovery tasks. Start with simple queries and
    narrow down results using tags, dates, and entity types as needed.

    ---------------------------------------------------------------------------
    [EXAMPLES]
    - Search for a specific topic in your notes:
      adn_search("notes", query="machine learning", page_size=10)
    - Search external Obsidian vault:
      adn_search("obsidian", query="planning", source_path="/path/to/vault")
    - Combined boolean and date search:
      adn_search("notes", query="research AND python", after_date="2024-01-01")
    - Search for notes with specific tags:
      adn_search("notes", query="benny", tags="dog, training")

    ---------------------------------------------------------------------------
    [ERRORS]
    - Required Parameter: 'source_path' missing for external searches or 'query' missing.
    - Invalid Operation: The specified search operation is not supported.
    - Empty Results: No matches found (check spelling and filters).
    """

    # Normalize list parameters to handle both list and string formats (including JSON strings)
    # This fixes schema validation issues where FastMCP might not properly handle list[str] | None
    # Uses parse_tags for tags to handle JSON array strings properly
    def _normalize_list_param(value: list[str] | str | None) -> list[str] | None:
        """Normalize list parameter from various input formats."""
        if value is None:
            return None
        if isinstance(value, list):
            return [str(item).strip() for item in value if item]
        if isinstance(value, str):
            # Handle comma-separated string format
            if "," in value:
                return [item.strip() for item in value.split(",") if item.strip()]
            # Single string value
            return [value.strip()] if value.strip() else None
        # Fallback: convert to string and create list
        return [str(value).strip()] if value else None

    # Normalize list-based filter parameters
    types = _normalize_list_param(types)
    entity_types = _normalize_list_param(entity_types)
    # Use parse_tags for tags to properly handle JSON array strings and prevent YAML corruption
    tags_parsed = parse_tags(tags) if tags is not None else None
    tags = tags_parsed if tags_parsed else None

    # Parameter aliasing for compatibility with standalone search_notes tool
    # results_per_page → page_size
    if results_per_page is not None and page_size == 10:  # Only if default value
        page_size = results_per_page
        logger.debug(f"Using 'results_per_page' alias as page_size: {page_size}")

    original_operation = operation
    normalized_operation = re.sub(r"(?<!^)(?=[A-Z])", "_", operation)
    normalized_operation = normalized_operation.replace("-", "_").replace(" ", "_").lower()
    alias_map: dict[str, Literal["notes", "obsidian", "joplin", "notion", "evernote"]] = {
        "note": "notes",
        "notesearch": "notes",
        "searchnotes": "notes",
        "search": "notes",
        "text": "notes",
        "plaintext": "notes",
        "title": "notes",
        "permalink": "notes",
        "tags": "notes",
        "tag": "notes",
        "files": "notes",
        "file": "notes",
        "wikilink": "notes",
        "links": "notes",
        "frontmatter": "notes",
    }
    # Type-safe operation mapping
    mapped_operation = alias_map.get(normalized_operation, normalized_operation)
    if mapped_operation in ("notes", "obsidian", "joplin", "notion", "evernote"):
        operation = mapped_operation  # type: ignore[assignment]

    search_type_overrides = {
        "title": "title",
        "permalink": "permalink",
        "tag": "tag",
        "tags": "tag",
        "file": "file",
        "files": "file",
        "link": "link",
        "links": "link",
        "frontmatter": "frontmatter",
        "wikilink": "link",
        "text": "text",
        "plaintext": "text",
    }
    entity_types_override: list[str] | None = None

    if operation == "notes" and normalized_operation in search_type_overrides:
        override_type = search_type_overrides[normalized_operation]
        applied = False
        if normalized_operation in ("text", "plaintext") and search_type not in (
            None,
            "text",
        ):
            logger.info(
                "adn_search_text_no_override",
                original_operation=original_operation,
                normalized_operation=normalized_operation,
                requested_search_type=search_type,
            )
        else:
            # Type-safe search_type assignment
            if override_type in (
                "text",
                "title",
                "permalink",
                "tag",
                "file",
                "link",
                "frontmatter",
            ):
                search_type = override_type  # type: ignore[assignment]
            applied = True

        if applied:
            logger.debug(
                "adn_search_operation_alias_applied",
                original_operation=original_operation,
                normalized_operation=normalized_operation,
                resolved_operation=operation,
                search_type=search_type,
            )
            if normalized_operation in ("text", "plaintext", "title", "permalink"):
                entity_types_override = ["entity", "observation"]

    if entity_types_override and not entity_types:
        entity_types = entity_types_override

    logger.info(f"MCP tool call tool=adn_search operation={operation} query={query}")

    # Route to appropriate operation
    if operation == "notes":
        return await _notes_search(
            query,
            page,
            page_size,
            search_type,
            types,
            entity_types,
            after_date,
            before_date,
            tags,
            project,
        )
    elif operation == "obsidian":
        actual_search_type = search_type if search_type else "text"
        return await _obsidian_search(
            query, source_path, actual_search_type, max_results, include_content
        )
    elif operation == "joplin":
        actual_search_type = search_type if search_type else "text"
        return await _joplin_search(
            query, source_path, actual_search_type, max_results, include_content
        )
    elif operation == "notion":
        return await _notion_search(query, source_path, case_sensitive, file_type, max_results)
    elif operation == "evernote":
        return await _evernote_search(
            query,
            source_path,
            case_sensitive,
            file_type,
            notebook_filter,
            tag_filter,
            max_results,
        )
    else:
        return build_error_response(
            error="Invalid search operation",
            error_code="INVALID_OPERATION",
            message=f"You provided operation='{operation}'. Valid operations: notes, obsidian, joplin, notion, evernote",
            recovery_options=[
                "Use operation='notes' to search your knowledge base",
                "Use operation='obsidian' with source_path to search external vaults",
                "Use operation='joplin' with source_path to search Joplin exports",
                "Use operation='notion' with source_path to search Notion exports",
                "Use operation='evernote' with source_path to search Evernote exports",
            ],
            examples=[
                {
                    "operation": "notes",
                    "query": "german shepherd",
                    "tags": ["dog"],
                    "after_date": "spring 2024",
                },
                {
                    "operation": "obsidian",
                    "query": "meeting notes",
                    "source_path": "/path/to/vault",
                },
            ],
            urgency="medium",
        )


async def _notes_search(
    query: str,
    page: int,
    page_size: int,
    search_type: str | None,
    types: list[str] | None,
    entity_types: list[str] | None,
    after_date: str | None,
    before_date: str | None,
    tags: list[str] | None,
    project: str | None,
) -> dict:
    """Handle Advanced Memory notes search operation."""
    from advanced_memory.mcp.tools.search import search_notes

    # Use provided search_type or default to "text"
    actual_search_type = search_type if search_type else "text"

    result = await search_notes.fn(
        query,
        page,
        page_size,
        actual_search_type,
        types,
        entity_types,
        after_date,
        before_date,
        tags,
        project,
    )

    # Convert SearchResponse to string if needed
    if isinstance(result, str):
        return result

    # Prepare structured search results
    formatted_results = []
    for idx, item in enumerate(result.results, 1):
        title = item.title or "Untitled"
        permalink = item.permalink or ""
        item_type = item.type.value if hasattr(item.type, "value") else str(item.type)

        result_item = {
            "index": idx,
            "title": title,
            "type": item_type,
            "permalink": permalink,
            "score": round(item.score, 2),
            "content_preview": None,
        }

        # Add content snippet if available
        if item.content:
            snippet = item.content[:200] + "..." if len(item.content) > 200 else item.content
            result_item["content_preview"] = snippet

        formatted_results.append(result_item)

    # Calculate pagination info
    total_pages = ((len(result.results) // result.page_size) + 1) if result.results else 1

    if not result.results:
        return build_success_response(
            operation="search",
            summary=f"No results found for query '{query}' in notes search",
            result={
                "query": query,
                "operation": "notes",
                "total_results": 0,
                "results": [],
                "current_page": result.current_page,
                "total_pages": total_pages,
                "page_size": result.page_size,
            },
            suggestions=[
                "Try broader search terms",
                "Check spelling and try again",
                "Use fewer search terms for broader results",
                "Consider different search types (title, text, permalink)",
            ],
            next_steps=[
                f"Try a broader search: adn_search(operation='notes', query='{query.split()[0]}')",
                "Use different search parameters or filters",
                "Check your query syntax and try again",
            ],
        )

    return build_success_response(
        operation="search",
        summary=f"Found {len(result.results)} matches for '{query}' in notes search",
        result={
            "query": query,
            "operation": "notes",
            "total_results": len(result.results),
            "results": formatted_results,
            "current_page": result.current_page,
            "total_pages": total_pages,
            "page_size": result.page_size,
        },
        next_steps=[
            "View a specific result: adn_content('read', identifier='result_permalink')",
            "Refine search with additional filters or different query",
            "Use results to continue with knowledge operations",
        ],
    )


async def _obsidian_search(
    query: str,
    source_path: str | None,
    search_type: str,
    max_results: int,
    include_content: bool,
) -> dict:
    """Handle Obsidian vault search operation."""
    if not source_path:
        return build_error_response(
            error="Missing required parameter",
            error_code="MISSING_SOURCE_PATH",
            message="The obsidian operation requires a source_path to the vault directory",
            recovery_options=[
                "Provide source_path parameter pointing to your Obsidian vault",
                "Check that the vault directory exists and is accessible",
                "Use absolute paths for reliability",
            ],
            example={
                "operation": "obsidian",
                "query": "meeting notes",
                "source_path": "/path/to/vault",
            },
            urgency="medium",
        )

    from advanced_memory.mcp.tools.search_obsidian_vault import search_obsidian_vault

    return await search_obsidian_vault.fn(
        source_path, query, search_type, max_results, include_content
    )  # type: ignore[operator,no-any-return]


async def _joplin_search(
    query: str,
    source_path: str | None,
    search_type: str,
    max_results: int,
    include_content: bool,
) -> dict:
    """Handle Joplin export search operation."""
    if not source_path:
        return build_error_response(
            error="Missing required parameter",
            error_code="MISSING_SOURCE_PATH",
            message="The joplin operation requires a source_path to the export directory",
            recovery_options=[
                "Provide source_path parameter pointing to your Joplin export folder",
                "Check that the export directory exists and contains Joplin data",
                "Use absolute paths for reliability",
            ],
            example={
                "operation": "joplin",
                "query": "project notes",
                "source_path": "/path/to/joplin-export",
            },
            urgency="medium",
        )

    from advanced_memory.mcp.tools.search_joplin_vault import search_joplin_vault

    return await search_joplin_vault.fn(
        source_path, query, search_type, max_results, include_content
    )  # type: ignore[operator,no-any-return]


async def _notion_search(
    query: str,
    source_path: str | None,
    case_sensitive: bool,
    file_type: str | None,
    max_results: int,
) -> dict:
    """Handle Notion export search operation."""
    if not source_path:
        return build_error_response(
            error="Missing required parameter",
            error_code="MISSING_SOURCE_PATH",
            message="The notion operation requires a source_path to the export directory",
            recovery_options=[
                "Provide source_path parameter pointing to your Notion export folder",
                "Check that the export directory exists and contains Notion data",
                "Use absolute paths for reliability",
            ],
            example={
                "operation": "notion",
                "query": "project notes",
                "source_path": "/path/to/notion-export",
            },
            urgency="medium",
        )

    from advanced_memory.mcp.tools.search_notion_vault import search_notion_vault

    return await search_notion_vault.fn(source_path, query, case_sensitive, file_type, max_results)  # type: ignore[operator,no-any-return]


async def _evernote_search(
    query: str,
    source_path: str | None,
    case_sensitive: bool,
    file_type: str | None,
    notebook_filter: str | None,
    tag_filter: str | None,
    max_results: int,
) -> dict:
    """Handle Evernote export search operation."""
    if not source_path:
        return build_error_response(
            error="Missing required parameter",
            error_code="MISSING_SOURCE_PATH",
            message="The evernote operation requires a source_path to the export directory containing .enex files",
            recovery_options=[
                "Provide source_path parameter pointing to your Evernote export folder",
                "Check that the export directory exists and contains .enex files",
                "Use absolute paths for reliability",
            ],
            example={
                "operation": "evernote",
                "query": "meeting notes",
                "source_path": "/path/to/evernote-export",
            },
            urgency="medium",
        )

    from advanced_memory.mcp.tools.search_evernote_vault import search_evernote_vault

    return await search_evernote_vault.fn(
        source_path,
        query,
        case_sensitive,
        file_type,
        notebook_filter,
        tag_filter,
        max_results,
    )  # type: ignore[operator,no-any-return]
