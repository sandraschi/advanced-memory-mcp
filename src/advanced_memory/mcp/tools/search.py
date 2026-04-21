"""Search namespaced app for Advanced Memory MCP.

Decomposed from the legacy adn_search and adn_knowledge_rag tools.
Follows FastMCP 3.2 GA Managed Namespace standards.

This module also retains the legacy `search_notes` implementation (plus its
helpers) as a plain logic-provider function — it is not registered as a tool,
but is imported by `adn_search._notes_search` and the CLI `tool.py` command.
"""

import re
from textwrap import dedent
from typing import Annotated, Any, Literal

from fastmcp import FastMCP
from loguru import logger
from pydantic import Field

from advanced_memory.mcp.async_client import client
from advanced_memory.mcp.project_session import get_active_project
from advanced_memory.mcp.tools.utils import call_post
from advanced_memory.schemas.search import SearchItemType, SearchQuery, SearchResponse

# Initialize the namespaced app
search_app = FastMCP("search")


@search_app.tool(task=True)
async def query(
    text: Annotated[str, Field(description="Search term or boolean logic query")],
    search_type: Annotated[Literal["text", "title", "permalink", "tag"], Field(description="Scope of the search focus")] = "text",
    page: Annotated[int, Field(description="Results page number", ge=1)] = 1,
    page_size: Annotated[int, Field(description="Items per page", ge=1, le=50)] = 20,
    project: Annotated[str | None, Field(description="Project context override")] = None,
) -> Any:
    """Internal Discovery Engine

    Performs high-speed full-text search across all notes in the knowledge base using Boolean logic.
    """
    from advanced_memory.mcp.tools.adn_search import adn_search
    return await adn_search(
        operation="notes",
        query=text,
        search_type=search_type,
        page=page,
        page_size=page_size,
        project=project
    )


@search_app.tool(task=True)
async def rag(
    prompt: Annotated[str, Field(description="Semantic query or context prompt to ground")],
    limit: Annotated[int, Field(description="Maximum number of high-density chunks to return")] = 5,
    min_score: Annotated[float, Field(description="Relevance threshold (0.0 to 1.0)")] = 0.5,
    project: Annotated[str | None, Field(description="Project context override")] = None,
) -> Any:
    """Semantic Retrieval Engine (RAG)

    Leverages LanceDB and vector embeddings to find relevant knowledge chunks based on semantic meaning.
    """
    from advanced_memory.deps import get_search_service
    from advanced_memory.mcp.tools.adn_knowledge_rag import _resolve_project

    target_project = _resolve_project(project)
    search_service = await get_search_service()

    results = await search_service.knowledge_rag(
        query=prompt, limit=limit, project=target_project, min_score=min_score
    )

    # Format for model consumption
    context_blocks = []
    explorer_results = []
    for i, chunk in enumerate(results.get("results", [])):
        score = chunk.get("score", 0.0)
        text = chunk.get("text", "")
        meta = chunk.get("metadata", {})
        source = meta.get("path") or meta.get("filename") or "Unknown"

        block = f"[Source {i + 1}: {source}] (Relevance: {score:.2f})\n{text}"
        context_blocks.append(block)
        explorer_results.append({
            "title": f"Source {i + 1}: {source}",
            "permalink": source,
            "content": text,
            "score": score,
            "type": "chunk"
        })

    formatted_context = "\n\n---\n\n".join(context_blocks)

    from fastmcp.tools import ToolResult

    from advanced_memory.mcp.prefabs import SearchExplorer

    return ToolResult(
        content=[f"## RAG Results for: {prompt}\n\n{formatted_context}"],
        app=SearchExplorer(f"RAG: {prompt}", explorer_results),
    )


@search_app.tool(task=True)
async def external(
    source: Annotated[Literal["obsidian", "joplin", "notion", "evernote"], Field(description="External storage platform")],
    path: Annotated[str, Field(description="Absolute path to the vault or export directory")],
    query: Annotated[str, Field(description="Search term")],
    max_results: Annotated[int, Field(description="Limit on returned items")] = 10,
) -> Any:
    """External Knowledge Bridge

    Searches across non-native knowledge silos like Obsidian vaults or Evernote exports.
    """
    from advanced_memory.mcp.tools.adn_search import adn_search
    return await adn_search(
        operation=source,
        query=query,
        source_path=path,
        max_results=max_results
    )


# ---------------------------------------------------------------------------
# Legacy logic provider: search_notes and formatting helpers.
# Not registered as a tool; imported by adn_search._notes_search and CLI.
# ---------------------------------------------------------------------------

_TAG_FILTER_PATTERN = re.compile(
    r"(?<!\S)tag:(?P<value>\"[^\"]+\"|'[^']+'|[^\s]+)",
    flags=re.IGNORECASE,
)


def _extract_tags_from_query_string(query: str) -> tuple[str, list[str]]:
    """Extract tag filters (tag:foo) from a free-form query string."""
    if not query:
        return "", []

    extracted_tags: list[str] = []

    def _replacement(match: re.Match[str]) -> str:
        raw_value = match.group("value") or ""
        tag_value = raw_value.strip().strip(",;")

        if len(tag_value) >= 2 and tag_value[0] in ("'", '"') and tag_value[-1] == tag_value[0]:
            tag_value = tag_value[1:-1]

        tag_value = tag_value.strip().strip(",;")
        tag_value = tag_value.lstrip("#")

        if tag_value:
            extracted_tags.append(tag_value)

        # Replace with single space to avoid concatenating words
        return " "

    cleaned_query = _TAG_FILTER_PATTERN.sub(_replacement, query)
    cleaned_query = " ".join(cleaned_query.split())
    return cleaned_query, extracted_tags


def _format_search_results_as_markdown(
    search_response: SearchResponse, query: str, projects: list[str]
) -> str:
    """Convert SearchResponse to formatted markdown string for MCP compliance."""
    output = [f'# Search Results for: "{query}"\n']

    if not search_response.results:
        output.append("No results found for your query.\n")
        output.append("## Suggestions:")
        output.append("- Try broader search terms")
        output.append("- Check spelling")
        output.append("- Use fewer search terms")
        output.append("- Try recent_activity() to see latest notes")
        return "\n".join(output)

    output.append(
        f"Found {search_response.total_results} result(s) from project(s): {', '.join(projects)}\n"
    )

    for idx, item in enumerate(search_response.results, 1):
        title = item.title or "Untitled"
        permalink = item.permalink or ""

        output.append(f"## {idx}. {title}")
        output.append(f"**Type:** {item.type}")
        output.append(f"**Permalink:** `{permalink}`")
        output.append(f"**Score:** {item.score:.2f}")

        # Add content snippet if available
        if item.content:
            snippet = item.content[:200] + "..." if len(item.content) > 200 else item.content
            output.append(f"**Preview:** {snippet}")

        output.append("")

    # Add pagination info
    total_pages = (
        (search_response.total_results + search_response.page_size - 1) // search_response.page_size
        if search_response.total_results > 0
        else 1
    )
    output.append(f"**Page:** {search_response.current_page} of {total_pages}")

    return "\n".join(output)


def _format_search_error_response(error_message: str, query: str, search_type: str = "text") -> str:
    """Format helpful error responses for search failures that guide users to successful searches."""

    # FTS5 syntax errors
    if "syntax error" in error_message.lower() or "fts5" in error_message.lower():
        clean_query = (
            query.replace('"', "")
            .replace("(", "")
            .replace(")", "")
            .replace("+", "")
            .replace("*", "")
        )
        return dedent(f"""
            # Search Failed - Invalid Syntax

            The search query '{query}' contains invalid syntax that the search engine cannot process.

            ## Common syntax issues:
            1. **Special characters**: Characters like `+`, `*`, `"`, `(`, `)` have special meaning in search
            2. **Unmatched quotes**: Make sure quotes are properly paired
            3. **Invalid operators**: Check AND, OR, NOT operators are used correctly

            ## How to fix:
            1. **Simplify your search**: Try using simple words instead: `{clean_query}`
            2. **Remove special characters**: Use alphanumeric characters and spaces
            3. **Use basic boolean operators**: `word1 AND word2`, `word1 OR word2`, `word1 NOT word2`

            ## Examples of valid searches:
            - Simple text: `project planning`
            - Boolean AND: `project AND planning`
            - Boolean OR: `meeting OR discussion`
            - Boolean NOT: `project NOT archived`
            - Grouped: `(project OR planning) AND notes`
            - Exact phrases: `"weekly standup meeting"`
            - Content-specific: `tag:example` or `category:observation`

            ## Try again with:
            ```
            search_notes("{clean_query}")
            ```

            ## Alternative search strategies:
            - Break into simpler terms: `search_notes("{" ".join(clean_query.split()[:2])}")`
            - Try different search types: `search_notes("{clean_query}", search_type="title")`
            - Use filtering: `search_notes("{clean_query}", types=["entity"])`
            """).strip()

    # Project not found errors (check before general "not found")
    if "project not found" in error_message.lower():
        return dedent(f"""
            # Search Failed - Project Not Found

            The current project is not accessible or doesn't exist: {error_message}

            ## How to resolve:
            1. **Check available projects**: `list_projects()`
            2. **Switch to valid project**: `switch_project("valid-project-name")`
            3. **Verify project setup**: Ensure your project is properly configured

            ## Current session info:
            - Check current project: `get_current_project()`
            - See available projects: `list_projects()`
            """).strip()

    # No results found
    if "no results" in error_message.lower() or "not found" in error_message.lower():
        simplified_query = (
            " ".join(query.split()[:2])
            if len(query.split()) > 2
            else query.split()[0]
            if query.split()
            else "notes"
        )
        return dedent(f"""
            # Search Complete - No Results Found

            No content found matching '{query}' in the current project.

            ## Search strategy suggestions:
            1. **Broaden your search**: Try fewer or more general terms
               - Instead of: `{query}`
               - Try: `{simplified_query}`

            2. **Check spelling and try variations**:
               - Verify terms are spelled correctly
               - Try synonyms or related terms

            3. **Use different search approaches**:
               - **Text search**: `search_notes("{query}", search_type="text")` (searches full content)
               - **Title search**: `search_notes("{query}", search_type="title")` (searches only titles)
               - **Permalink search**: `search_notes("{query}", search_type="permalink")` (searches file paths)

            4. **Try boolean operators for broader results**:
               - OR search: `search_notes("{" OR ".join(query.split()[:3])}")`
               - Remove restrictive terms: Focus on the most important keywords

            5. **Use filtering to narrow scope**:
               - By content type: `search_notes("{query}", types=["entity"])`
               - By recent content: `search_notes("{query}", after_date="1 week")`
               - By entity type: `search_notes("{query}", entity_types=["observation"])`

            6. **Try advanced search patterns**:
               - Tag search: `search_notes("tag:your-tag")`
               - Category search: `search_notes("category:observation")`
               - Pattern matching: `search_notes("*{query}*", search_type="permalink")`

            ## Explore what content exists:
            - **Recent activity**: `recent_activity(timeframe="7d")` - See what's been updated recently
            - **List directories**: `list_directory("/")` - Browse all content
            - **Browse by folder**: `list_directory("/notes")` or `list_directory("/docs")`
            - **Check project**: `get_current_project()` - Verify you're in the right project
            """).strip()

    # Server/API errors
    if "server error" in error_message.lower() or "internal" in error_message.lower():
        return dedent(f"""
            # Search Failed - Server Error

            The search service encountered an error while processing '{query}': {error_message}

            ## Immediate steps:
            1. **Try again**: The error might be temporary
            2. **Simplify the query**: Use simpler search terms
            3. **Check project status**: Ensure your project is properly synced

            ## Alternative approaches:
            - Browse files directly: `list_directory("/")`
            - Check recent activity: `recent_activity(timeframe="7d")`
            - Try a different search type: `search_notes("{query}", search_type="title")`

            ## If the problem persists:
            The search index might need to be rebuilt. Send a message to support@basicmachines.co or check the project sync status.
            """).strip()

    # Permission/access errors
    if (
        "permission" in error_message.lower()
        or "access" in error_message.lower()
        or "forbidden" in error_message.lower()
    ):
        return f"""# Search Failed - Access Error

You don't have permission to search in the current project: {error_message}

## How to resolve:
1. **Check your project access**: Verify you have read permissions for this project
2. **Switch projects**: Try searching in a different project you have access to
3. **Check authentication**: You might need to re-authenticate

## Alternative actions:
- List available projects: `list_projects()`
- Switch to accessible project: `switch_project("project-name")`
- Check current project: `get_current_project()`"""

    # Generic fallback
    return f"""# Search Failed

Error searching for '{query}': {error_message}

## Troubleshooting steps:
1. **Simplify your query**: Try basic words without special characters
2. **Check search syntax**: Ensure boolean operators are correctly formatted
3. **Verify project access**: Make sure you can access the current project
4. **Test with simple search**: Try `search_notes("test")` to verify search is working

## Alternative search approaches:
- **Different search types**:
  - Title only: `search_notes("{query}", search_type="title")`
  - Permalink patterns: `search_notes("{query}*", search_type="permalink")`
- **With filters**: `search_notes("{query}", types=["entity"])`
- **Recent content**: `search_notes("{query}", after_date="1 week")`
- **Boolean variations**: `search_notes("{" OR ".join(query.split()[:2])}")`

## Explore your content:
- **Browse files**: `list_directory("/")` - See all available content
- **Recent activity**: `recent_activity(timeframe="7d")` - Check what's been updated
- **Project info**: `get_current_project()` - Verify current project
- **All projects**: `list_projects()` - Switch to different project if needed

## Search syntax reference:
- **Basic**: `keyword` or `multiple words`
- **Boolean**: `term1 AND term2`, `term1 OR term2`, `term1 NOT term2`
- **Phrases**: `"exact phrase"`
- **Grouping**: `(term1 OR term2) AND term3`
- **Patterns**: `tag:example`, `category:observation`"""


async def search_notes(
    query: Annotated[
        str,
        Field(
            description="Search term/logic (e.g. 'planning AND project', 'tag:work', '\"exact phrase\"')"
        ),
    ],
    page: Annotated[int, Field(description="Results page number for large result sets")] = 1,
    results_per_page: Annotated[
        int, Field(description="Number of results to return (max: 50)")
    ] = 10,
    search_type: Annotated[
        str | None,
        Field(description="Scope: 'text' (full-text), 'title' (titles only), 'permalink' (paths)"),
    ] = "text",
    types: Annotated[
        list[str] | None, Field(description="Filter by primary category (e.g. ['note'])")
    ] = None,
    entity_types: Annotated[
        list[str] | None,
        Field(description="Structural filter: 'entity', 'observation', 'relation'"),
    ] = None,
    after_date: Annotated[
        str | None, Field(description="Results FROM this date (e.g. '1 week ago', '2026-01-01')")
    ] = None,
    before_date: Annotated[
        str | None, Field(description="Results UNTIL this date (e.g. 'yesterday')")
    ] = None,
    tags: Annotated[
        list[str] | None, Field(description="Match all tags in this list")
    ] = None,
    projects: Annotated[
        str | None, Field(description="Match specific projects: 'p1,p2' or 'ALL'")
    ] = None,
    project: Annotated[str | None, Field(description="Alias for projects parameter")] = None,
    search_all_projects: Annotated[
        bool, Field(description="Shortcut to search across all accessible projects")
    ] = False,
) -> str:
    """Advanced search with boolean logic and semantic filtering.

    ## Return Format
    - A Markdown-formatted list of search results.
    - Includes title, type, permalink, score, and content snippet for each result.
    - Provides pagination info at the bottom.

    ## Examples
    ```python
    search_notes(query="project AND planning", types=["note"])
    search_notes(query="tag:urgent", projects="ALL")
    search_notes(query="docs/2026-*", search_type="permalink")
    ```
    """
    # Normalize query and extract inline tag filters when applicable
    raw_query = (query or "").strip()
    inline_tags: list[str] = []

    parse_tag_filters = search_type in (None, "", "text", "tag")
    if parse_tag_filters and raw_query:
        raw_query, inline_tags = _extract_tags_from_query_string(raw_query)

    # Combine explicit tags parameter with inline tag filters
    combined_tags: list[str] = []
    seen_tag_keys: set[str] = set()

    def _add_tag_value(value: str) -> None:
        normalized_value = str(value).strip()
        if not normalized_value:
            return

        normalized_value = normalized_value.lstrip("#")
        tag_key = normalized_value.lower()

        if tag_key in seen_tag_keys:
            return

        seen_tag_keys.add(tag_key)
        combined_tags.append(normalized_value)

    if tags:
        for explicit_tag in tags:
            _add_tag_value(explicit_tag)

    for inline_tag in inline_tags:
        _add_tag_value(inline_tag)

    if search_type == "tag" and not combined_tags and raw_query:
        _add_tag_value(raw_query)
        raw_query = ""

    # Create a SearchQuery object based on the parameters
    search_query = SearchQuery()

    search_term = raw_query.strip()

    # Set the appropriate search field based on search_type
    if search_type == "text":
        if search_term:
            search_query.text = search_term
    elif search_type == "title":
        if search_term:
            search_query.title = search_term
    elif search_type == "permalink" and "*" in search_term:
        search_query.permalink_match = search_term
    elif search_type == "permalink":
        if search_term:
            search_query.permalink = search_term
    elif search_type == "tag":
        # Tags handled separately; no text criteria required
        pass
    else:
        if search_term:
            search_query.text = search_term  # Default to text search when not empty

    # Add optional filters if provided
    if entity_types:
        # Validate entity_types with graceful fallback
        validated_entity_types = []
        invalid_entity_types = []
        for t in entity_types:
            try:
                validated_entity_types.append(SearchItemType(t))
            except ValueError:
                # Track invalid types but don't fail
                invalid_entity_types.append(t)
                logger.warning(
                    f"Invalid entity_type value: '{t}'. Ignoring and continuing with valid types."
                )

        # If we have valid types, use them. If all were invalid, fall back to all types
        if validated_entity_types:
            search_query.entity_types = validated_entity_types
        elif invalid_entity_types:
            # All types were invalid - fallback to all types with warning
            valid_types = [t.value for t in SearchItemType]
            logger.warning(
                f"All provided entity_types were invalid: {invalid_entity_types}. "
                f"Falling back to all types. Valid options: {valid_types}"
            )
    if types:
        search_query.types = types
    if after_date:
        search_query.after_date = after_date
    if before_date:
        search_query.before_date = before_date
    if combined_tags:
        search_query.tags = combined_tags

    if project and not projects:
        projects = project

    if search_all_projects and projects:
        return dedent(
            """# Error: Conflicting Parameters

Cannot use both `projects` and `search_all_projects=True` in the same request.

**How to fix:**
- Set `search_all_projects=True` without specifying `projects`
- Or remove `search_all_projects` and provide a specific project list
"""
        ).strip()

    if search_all_projects:
        projects = "ALL"

    # Parse projects parameter to determine which projects to search
    from advanced_memory.schemas.project_info import ProjectList

    search_multiple = False
    project_names_to_search = []

    if projects:
        if projects.upper() == "ALL":
            # Search all projects
            logger.info("Searching across ALL projects")
            projects_response = await call_post(client, "/projects/projects", json={})
            project_list = ProjectList.model_validate(projects_response.json())
            project_names_to_search = [p.name for p in project_list.projects]
            search_multiple = True

        elif projects.upper().startswith("ALL_EXCEPT:"):
            # Search all except specified
            excluded = projects[11:].split(",")  # Remove "ALL_EXCEPT:"
            excluded = [e.strip() for e in excluded]
            logger.info(f"Searching ALL projects except: {excluded}")
            projects_response = await call_post(client, "/projects/projects", json={})
            project_list = ProjectList.model_validate(projects_response.json())
            project_names_to_search = [
                p.name for p in project_list.projects if p.name not in excluded
            ]
            search_multiple = True

        elif "," in projects:
            # Multiple specific projects (comma-delimited)
            project_names_to_search = [p.strip() for p in projects.split(",")]
            logger.info(f"Searching specific projects: {project_names_to_search}")
            search_multiple = True

        else:
            # Single specific project
            project_names_to_search = [projects]
            logger.info(f"Searching specific project: {projects}")

    # Handle multi-project search
    if search_multiple and project_names_to_search:
        logger.info(f"Multi-project search across {len(project_names_to_search)} project(s)")

        all_results = []
        searched_projects = []

        for proj_name in project_names_to_search:
            try:
                proj_obj = get_active_project(proj_name)
                response = await call_post(
                    client,
                    f"{proj_obj.project_url}/search/",
                    json=search_query.model_dump(),
                    params={"page": page, "page_size": results_per_page},
                )
                proj_result = SearchResponse.model_validate(response.json())

                # Add project name to each result for context
                for item in proj_result.results:
                    if hasattr(item, "title"):
                        item.title = f"[{proj_name}] {item.title}"

                all_results.extend(proj_result.results)
                searched_projects.append(proj_name)
            except Exception as e:
                logger.warning(f"Failed to search project {proj_name}: {e}")
                continue

        # Return merged results with project context
        logger.info(
            f"Searched {len(searched_projects)} projects, found {len(all_results)} total results"
        )

        # Format as markdown string for MCP compliance
        search_response = SearchResponse(
            results=all_results[:results_per_page],
            current_page=page,
            page_size=results_per_page,
            total_results=len(all_results),
        )

        # Build Point Cloud Graph data (Hub and Spoke)
        nodes = [{"id": "query", "label": query, "type": "hub"}]
        edges = []
        for r in search_response.results:
            node_id = r.permalink or r.title
            nodes.append({"id": node_id, "label": r.title, "type": "particle"})
            edges.append({"from": "query", "to": node_id})

        return _format_search_results_as_markdown(search_response, query, searched_projects)

    # Single project search (default behavior)
    active_project = get_active_project(
        projects
    )  # Will use projects as single project name, or current if None
    project_url = active_project.project_url

    logger.info(f"Searching for {search_query}")

    try:
        response = await call_post(
            client,
            f"{project_url}/search/",
            json=search_query.model_dump(),
            params={"page": page, "page_size": results_per_page},
        )
        result = SearchResponse.model_validate(response.json())

        # Check if we got no results and provide helpful guidance
        if not result.results:
            logger.info(f"Search returned no results for query: {query}")
            # Don't treat this as an error, but the user might want guidance
            # We return the empty result as normal - the user can decide if they need help

        return _format_search_results_as_markdown(result, query, [active_project.name])

    except Exception as e:
        logger.error(f"Search failed for query '{query}': {e}")
        # Return formatted error message as string for better user experience
        return _format_search_error_response(str(e), query, search_type)
