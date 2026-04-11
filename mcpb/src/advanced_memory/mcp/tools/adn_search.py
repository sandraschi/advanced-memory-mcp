"""Search Manager portmanteau tool for Advanced Memory MCP server.

This tool consolidates all search operations: notes, obsidian, joplin, notion, evernote.
It reduces the number of MCP tools while maintaining full functionality.
"""

import re
from typing import Literal

from loguru import logger

from advanced_memory.mcp.mcp_instance import mcp


@mcp.tool
async def adn_search(
    operation: Literal["notes", "obsidian", "joplin", "notion", "evernote"],
    query: str,
    source_path: str | None = None,
    search_type: Literal["text", "title", "permalink", "tag", "file", "link", "frontmatter"] | None = "text",
    page: int = 1,
    page_size: int = 10,
    results_per_page: int | None = None,  # Alias for page_size (compatibility with standalone search_notes)
    max_results: int = 20,
    case_sensitive: bool = False,
    include_content: bool = False,
    types: list[str] | None = None,
    entity_types: list[str] | None = None,
    after_date: str | None = None,
    before_date: str | None = None,
    tags: list[str] | None = None,
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
        operation: The search operation to perform. MUST be one of:
            - "notes": Search Advanced Memory knowledge base (use this for most searches)
            - "obsidian": Search external Obsidian vault
            - "joplin": Search external Joplin export
            - "notion": Search external Notion export
            - "evernote": Search external Evernote export
        query: Search terms with boolean operators and phrases (required)
        source_path: Path to external vault/export (required for obsidian/joplin/notion/evernote operations)
        search_type: Type of search. MUST be one of:
            - "text": Full-text search (default)
            - "title": Search titles only
            - "permalink": Search by path/permalink
            - "tag": Search by tag (external vaults)
            - "file": Search by filename (external vaults)
            - "link": Search by wikilinks (external vaults)
            - "frontmatter": Search YAML frontmatter (external vaults)
            Default: "text"
        page: Result page for pagination (default: 1)
        page_size: Results per page (default: 10)
        results_per_page: Alias for page_size (compatibility with standalone search_notes tool)
                          Note: Use this to maintain compatibility with standalone tools. The 'page_size' parameter is preferred.
        max_results: Maximum number of results to return (default: 20)
        case_sensitive: Whether search should be case-sensitive (default: False)
        include_content: Include content previews in results (default: False)
        types: Content type filters for notes search (e.g., ["note", "person"])
        entity_types: Entity category filters for notes search (e.g., ["entity", "observation"])
        after_date: Date filter - content FROM this date (e.g., "1 week", "spring 2024", "2024-01-01"). Default: None (all time)
        before_date: Date filter - content UNTIL this date (e.g., "summer 2024", "2024-12-31"). Default: None (all time)
        tags: Tag filter for notes search - notes must have ALL specified tags (e.g., ["dog", "training"])
        file_type: File type filter for external searches
        notebook_filter: Filter results to specific notebook
        tag_filter: Filter results by tag name
        project: Optional project name

    Returns:
        Operation-specific result with search details and match counts

    Examples:
        # Search Advanced Memory notes (using page_size parameter)
        adn_search("notes", query="machine learning", page=1, page_size=10)

        # Search with results_per_page alias (compatibility with standalone search_notes tool)
        adn_search("notes", query="machine learning", page=1, results_per_page=10)

        # Search external Obsidian vault
        adn_search("obsidian", query="project planning", source_path="/path/to/vault")

        # Search external Joplin export
        adn_search("joplin", query="meeting notes", source_path="/path/to/export")

        # Search with filters
        adn_search("notes", query="research", entity_types=["note"], after_date="2024-01-01")

        # Search with tags and date range
        adn_search("notes", query="german shepherd", tags=["dog", "training"], after_date="spring 2024", before_date="summer 2024")
    """

    # Normalize list parameters to handle both list and string formats
    # This fixes schema validation issues where FastMCP might not properly handle list[str] | None
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
    tags = _normalize_list_param(tags)

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
        if normalized_operation in ("text", "plaintext") and search_type not in (None, "text"):
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
        return await _obsidian_search(query, source_path, actual_search_type, max_results, include_content)
    elif operation == "joplin":
        actual_search_type = search_type if search_type else "text"
        return await _joplin_search(query, source_path, actual_search_type, max_results, include_content)
    elif operation == "notion":
        return await _notion_search(query, source_path, case_sensitive, file_type, max_results)
    elif operation == "evernote":
        return await _evernote_search(
            query, source_path, case_sensitive, file_type, notebook_filter, tag_filter, max_results
        )
    else:
        return f"""# Error: Invalid Search Operation

**You provided:** operation="{operation}"

**Valid search operations are:**
- "notes" - Search Advanced Memory knowledge base (use this for most searches)
- "obsidian" - Search external Obsidian vault (requires source_path)
- "joplin" - Search external Joplin export (requires source_path)
- "notion" - Search external Notion export (requires source_path)
- "evernote" - Search external Evernote export (requires source_path)

**Example for searching your notes:**
```
adn_search(
    operation="notes",
    query="german shepherd",
    tags=["dog"],
    after_date="spring 2024"
)
```

**Check your operation parameter spelling and try again.**"""


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
) -> str:
    """Handle Advanced Memory notes search operation."""
    from advanced_memory.mcp.tools.search import search_notes

    # Use provided search_type or default to "text"
    actual_search_type = search_type if search_type else "text"

    result = await (search_notes.fn if hasattr(search_notes, "fn") else search_notes)(
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
        item_type = item.type.value if hasattr(item.type, "value") else str(item.type)

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
    output.append(
        f"**Page:** {result.current_page} of {((len(result.results) // result.page_size) + 1 if result.results else 1)}"
    )

    return "\n".join(output)


async def _obsidian_search(
    query: str, source_path: str | None, search_type: str, max_results: int, include_content: bool
) -> str:
    """Handle Obsidian vault search operation."""
    if not source_path:
        return """# Error: Missing Required Parameter

**Operation:** obsidian

**Missing:** source_path parameter

The obsidian operation searches an external Obsidian vault.
You must provide the path to the vault directory.

**Example:**
```
adn_search(
    operation="obsidian",
    query="meeting notes",
    source_path="/path/to/vault"
)
```"""

    from advanced_memory.mcp.tools.search_obsidian_vault import search_obsidian_vault

    return await search_obsidian_vault(source_path, query, search_type, max_results, include_content)  # type: ignore[operator,no-any-return]


async def _joplin_search(
    query: str, source_path: str | None, search_type: str, max_results: int, include_content: bool
) -> str:
    """Handle Joplin export search operation."""
    if not source_path:
        return """# Error: Missing Required Parameter

**Operation:** joplin

**Missing:** source_path parameter

The joplin operation searches an external Joplin export directory.
You must provide the path to the export folder.

**Example:**
```
adn_search(
    operation="joplin",
    query="project notes",
    source_path="/path/to/joplin-export"
)
```"""

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
        return """# Error: Missing Required Parameter

**Operation:** notion

**Missing:** source_path parameter

The notion operation searches an external Notion export directory.
You must provide the path to the export folder.

**Example:**
```
adn_search(
    operation="notion",
    query="project notes",
    source_path="/path/to/notion-export"
)
```

**Provide the source_path parameter and try again.**"""

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
        return """# Error: Missing Required Parameter

**Operation:** evernote

**Missing:** source_path parameter

The evernote operation searches an external Evernote export directory.
You must provide the path to the export folder containing .enex files.

**Example:**
```
adn_search(
    operation="evernote",
    query="meeting notes",
    source_path="/path/to/evernote-export"
)
```

**Provide the source_path parameter and try again.**"""

    from advanced_memory.mcp.tools.search_evernote_vault import search_evernote_vault

    return await search_evernote_vault(
        source_path, query, case_sensitive, file_type, notebook_filter, tag_filter, max_results
    )  # type: ignore[operator,no-any-return]
