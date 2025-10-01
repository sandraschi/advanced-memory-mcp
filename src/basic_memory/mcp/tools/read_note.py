"""Read note tool for Basic Memory MCP server."""

from textwrap import dedent
from typing import Optional

from loguru import logger

from basic_memory.mcp.async_client import client
from basic_memory.mcp.server import mcp
from basic_memory.mcp.tools.search import search_notes
from basic_memory.mcp.tools.utils import call_get, sanitize_unicode_content
from basic_memory.mcp.project_session import get_active_project
from basic_memory.schemas.memory import memory_url_path
from basic_memory.utils import validate_project_path, sanitize_filename


@mcp.tool(
    description="""Retrieve complete note content from Basic Memory with intelligent lookup and fallback strategies.

This essential tool provides flexible access to notes using multiple identification methods,
with automatic fallback to search when direct lookup fails, ensuring content accessibility.

LOOKUP STRATEGIES (tried in order):
1. Exact permalink match (memory:// URLs)
2. Direct title match in current project
3. Sanitized filename match (handles special characters)
4. Full-text search fallback with scoring
5. Partial title matching

CONTENT RETURNED:
- Full markdown content with formatting
- Frontmatter metadata (YAML headers)
- Semantic relationships and observations
- Creation/modification timestamps
- Author and project information

PARAMETERS:
- identifier (str, REQUIRED): Note identification (title, permalink, memory:// URL, or search terms)
- page (int, default=1): Pagination page for search results
- page_size (int, default=10): Items per page for paginated content
- project (str, optional): Specific project to search in (defaults to active project)

INTELLIGENT FEATURES:
- Automatic content sanitization handling
- Path traversal attack prevention
- Project boundary validation
- Relationship context inclusion
- Content preview generation

USAGE EXAMPLES:
By title: read_note("Meeting Notes")
By permalink: read_note("notes/meeting-notes")
Memory URL: read_note("memory://notes/meeting-notes")
Search fallback: read_note("urgent meeting about budget")
With pagination: read_note("long-document", page=2, page_size=50)

RETURNS:
Complete note content as formatted markdown, or error message if not found.

SECURITY:
- Path traversal attacks blocked
- Project boundary enforcement
- Input validation and sanitization
- Safe file access with permissions checking

NOTE: This tool uses intelligent lookup strategies to find content even with partial information or special characters in titles.""",
)
async def read_note(
    identifier: str, page: int = 1, page_size: int = 10, project: Optional[str] = None
) -> str:
    """Read a markdown note from the knowledge base.

    This tool finds and retrieves a note by its title, permalink, or content search,
    returning the raw markdown content including observations, relations, and metadata.
    It will try multiple lookup strategies to find the most relevant note.

    Args:
        identifier: The title or permalink of the note to read
                   Can be a full memory:// URL, a permalink, a title, or search text
        page: Page number for paginated results (default: 1)
        page_size: Number of items per page (default: 10)
        project: Optional project name to read from. If not provided, uses current active project.

    Returns:
        The full markdown content of the note if found, or helpful guidance if not found.

    Examples:
        # Read by permalink
        read_note("specs/search-spec")

        # Read by title
        read_note("Search Specification")

        # Read with memory URL
        read_note("memory://specs/search-spec")

        # Read with pagination
        read_note("Project Updates", page=2, page_size=5)

        # Read from specific project
        read_note("Meeting Notes", project="work-project")
    """

    # Get the active project first to check project-specific sync status
    active_project = get_active_project(project)

    # Check migration status and wait briefly if needed
    from basic_memory.mcp.tools.utils import wait_for_migration_or_return_status

    migration_status = await wait_for_migration_or_return_status(
        timeout=5.0, project_name=active_project.name
    )
    if migration_status:  # pragma: no cover
        return f"# System Status\n\n{migration_status}\n\nPlease wait for migration to complete before reading notes."
    project_url = active_project.project_url

    # Get the file via REST API - first try direct permalink lookup
    entity_path = memory_url_path(identifier)

    # Validate path to prevent path traversal attacks
    project_path = active_project.home
    if not validate_project_path(entity_path, project_path):
        logger.warning(
            "Attempted path traversal attack blocked",
            identifier=identifier,
            entity_path=entity_path,
            project=active_project.name,
        )
        return f"# Error\n\nPath '{identifier}' is not allowed - paths must stay within project boundaries"

    # Try direct lookup first
    path = f"{project_url}/resource/{entity_path}"
    logger.info(f"Attempting to read note from URL: {path}")

    try:
        response = await call_get(client, path, params={"page": page, "page_size": page_size})
        if response.status_code == 200:
            logger.info("Returning read_note result from resource: {path}", path=entity_path)
            return sanitize_unicode_content(response.text)
    except Exception as e:  # pragma: no cover
        logger.info(f"Direct lookup failed for '{path}': {e}")
        # Continue to try sanitized version

    # If direct lookup failed and identifier looks like a title (not a permalink),
    # try with sanitized filename for markdown files
    if not identifier.startswith("memory://") and "/" not in identifier and not identifier.endswith(".md"):
        sanitized_path = sanitize_filename(identifier)
        if sanitized_path != identifier:  # Only try if different
            sanitized_full_path = f"{project_url}/resource/{sanitized_path}.md"
            logger.info(f"Trying sanitized path: {sanitized_full_path}")
            try:
                response = await call_get(client, sanitized_full_path, params={"page": page, "page_size": page_size})
                if response.status_code == 200:
                    logger.info(f"Found note using sanitized path: {sanitized_full_path}")
                    return sanitize_unicode_content(response.text)
            except Exception as e:  # pragma: no cover
                logger.info(f"Sanitized path lookup also failed for '{sanitized_full_path}': {e}")
                # Continue to fallback methods

    # Fallback 1: Try title search via API
    logger.info(f"Search title for: {identifier}")
    title_results = await search_notes.fn(query=identifier, search_type="title", project=project)

    if title_results and title_results.results:
        result = title_results.results[0]  # Get the first/best match
        if result.permalink:
            try:
                # Try to fetch the content using the found permalink
                path = f"{project_url}/resource/{result.permalink}"
                response = await call_get(
                    client, path, params={"page": page, "page_size": page_size}
                )

                if response.status_code == 200:
                    logger.info(f"Found note by title search: {result.permalink}")
                    return sanitize_unicode_content(response.text)
            except Exception as e:  # pragma: no cover
                logger.info(
                    f"Failed to fetch content for found title match {result.permalink}: {e}"
                )
    else:
        logger.info(f"No results in title search for: {identifier}")

    # Fallback 2: Text search as a last resort
    logger.info(f"Title search failed, trying text search for: {identifier}")
    text_results = await search_notes.fn(query=identifier, search_type="text", project=project)

    # We didn't find a direct match, construct a helpful error message
    if not text_results or not text_results.results:
        # No results at all
        return format_not_found_message(identifier)
    else:
        # We found some related results
        return format_related_results(identifier, text_results.results[:5])


def format_not_found_message(identifier: str) -> str:
    """Format a helpful message when no note was found."""
    return dedent(f"""
        # Note Not Found: "{identifier}"
        
        I searched for "{identifier}" using multiple methods (direct lookup, title search, and text search) but couldn't find any matching notes. Here are some suggestions:
        
        ## Check Identifier Type
        - If you provided a title, try using the exact permalink instead
        - If you provided a permalink, check for typos or try a broader search
        
        ## Search Instead
        Try searching for related content:
        ```
        search_notes(query="{identifier}")
        ```
        
        ## Recent Activity
        Check recently modified notes:
        ```
        recent_activity(timeframe="7d")
        ```
        
        ## Create New Note
        This might be a good opportunity to create a new note on this topic:
        ```
        write_note(
            title="{identifier.capitalize()}",
            content='''
            # {identifier.capitalize()}
            
            ## Overview
            [Your content here]
            
            ## Observations
            - [category] [Observation about {identifier}]
            
            ## Relations
            - relates_to [[Related Topic]]
            ''',
            folder="notes"
        )
        ```
    """)


def format_related_results(identifier: str, results) -> str:
    """Format a helpful message with related results when an exact match wasn't found."""
    message = dedent(f"""
        # Note Not Found: "{identifier}"
        
        I searched for "{identifier}" using direct lookup and title search but couldn't find an exact match. However, I found some related notes through text search:
        
        """)

    for i, result in enumerate(results):
        message += dedent(f"""
            ## {i + 1}. {result.title}
            - **Type**: {result.type.value}
            - **Permalink**: {result.permalink}
            
            You can read this note with:
            ```
            read_note("{result.permalink}")
            ```
            
            """)

    message += dedent("""
        ## Try More Specific Lookup
        For exact matches, try using the full permalink from one of the results above.
        
        ## Search For More Results
        To see more related content:
        ```
        search_notes(query="{identifier}")
        ```
        
        ## Create New Note
        If none of these match what you're looking for, consider creating a new note:
        ```
        write_note(
            title="[Your title]",
            content="[Your content]",
            folder="notes"
        )
        ```
    """)

    return message
