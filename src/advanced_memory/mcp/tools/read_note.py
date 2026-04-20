"""Read note tool for Advanced Memory MCP server."""

from textwrap import dedent
from typing import Annotated, Any

from loguru import logger
from pydantic import Field

from advanced_memory.mcp.async_client import client
from advanced_memory.mcp.mcp_instance import mcp
from advanced_memory.mcp.project_session import get_active_project
from advanced_memory.mcp.tools.utils import call_get
from advanced_memory.schemas.memory import memory_url_path
from advanced_memory.schemas.search import SearchResponse
from advanced_memory.utils import sanitize_filename, validate_project_path


@mcp.tool
async def read_note(
    identifier: Annotated[
        str, Field(description="Title, permalink, or memory:// URL to retrieve")
    ],
    page: Annotated[int, Field(description="Page number for paginated large notes")] = 1,
    page_size: Annotated[int, Field(description="Number of results per page")] = 10,
    project: Annotated[str | None, Field(description="Optional project override")] = None,
) -> Any:
    """Read a markdown note by title, permalink, or content lookup.

    ## Return Format
    - Raw Markdown content if found.
    - If exact match fails, returns a list of **Related Results** or a helpful **Not Found** guide.

    ## Examples
    ```python
    read_note(identifier="Project Alpha")
    read_note(identifier="meetings/budget_2026.md")
    ```
    """
    active_project = get_active_project(project)

    from advanced_memory.mcp.tools.utils import wait_for_migration_or_return_status

    migration_status = await wait_for_migration_or_return_status(
        timeout=5.0, project_name=active_project.name
    )
    if migration_status:  # pragma: no cover
        return f"# System Status\n\n{migration_status}\n\nPlease wait for migration to complete before reading notes."
    project_url = active_project.project_url

    entity_path = memory_url_path(identifier)

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
            return response.text
    except Exception as e:  # pragma: no cover
        logger.info(f"Direct lookup failed for '{path}': {e}")

    # Try sanitized filename variant for bare titles
    if (
        not identifier.startswith("memory://")
        and "/" not in identifier
        and not identifier.endswith(".md")
    ):
        sanitized_path = sanitize_filename(identifier)
        if sanitized_path != identifier:
            sanitized_full_path = f"{project_url}/resource/{sanitized_path}.md"
            logger.info(f"Trying sanitized path: {sanitized_full_path}")
            try:
                response = await call_get(
                    client, sanitized_full_path, params={"page": page, "page_size": page_size}
                )
                if response.status_code == 200:
                    logger.info(f"Found note using sanitized path: {sanitized_full_path}")
                    return response.text
            except Exception as e:  # pragma: no cover
                logger.info(f"Sanitized path lookup also failed for '{sanitized_full_path}': {e}")

    # Fallback 1: title search via search API directly (bypass search_notes tool)
    logger.info(f"Search title for: {identifier}")
    try:
        search_response = await call_get(
            client,
            f"{project_url}/search/",
            params={"query": identifier, "search_type": "title", "page": 1, "page_size": 5},
        )
        if search_response.status_code == 200:
            search_result = SearchResponse.model_validate(search_response.json())
            if search_result.results:
                result = search_result.results[0]
                if result.permalink:
                    fetch_path = f"{project_url}/resource/{result.permalink}"
                    fetch_response = await call_get(
                        client, fetch_path, params={"page": page, "page_size": page_size}
                    )
                    if fetch_response.status_code == 200:
                        logger.info(f"Found note by title search: {result.permalink}")
                        return fetch_response.text
    except Exception as e:  # pragma: no cover
        logger.info(f"Title search fallback failed: {e}")

    # Fallback 2: text search
    logger.info(f"Title search failed, trying text search for: {identifier}")
    try:
        search_response = await call_get(
            client,
            f"{project_url}/search/",
            params={"query": identifier, "search_type": "text", "page": 1, "page_size": 5},
        )
        if search_response.status_code == 200:
            search_result = SearchResponse.model_validate(search_response.json())
            if search_result.results:
                return format_related_results(identifier, search_result.results[:5])
    except Exception as e:  # pragma: no cover
        logger.info(f"Text search fallback failed: {e}")

    return format_not_found_message(identifier)


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
    """)


def format_related_results(identifier: str, results) -> str:
    """Format a helpful message with related results when an exact match wasn't found."""
    message = dedent(f"""
        # Note Not Found: "{identifier}"

        I couldn't find an exact match, but found some related notes:

        """)

    for i, result in enumerate(results):
        type_val = result.type.value if hasattr(result.type, "value") else str(result.type)
        message += dedent(f"""
            ## {i + 1}. {result.title}
            - **Type**: {type_val}
            - **Permalink**: {result.permalink}

            You can read this note with:
            ```
            read_note("{result.permalink}")
            ```

            """)

    return message
