"""Build context tool for Basic Memory MCP server."""

from typing import Optional

from loguru import logger

from advanced_memory.mcp.async_client import client
from advanced_memory.mcp.server import mcp
from advanced_memory.mcp.tools.utils import call_get
from advanced_memory.mcp.project_session import get_active_project
from advanced_memory.schemas.base import TimeFrame
from advanced_memory.schemas.memory import (
    GraphContext,
    MemoryUrl,
    memory_url_path,
)


@mcp.tool(
    description="""Build comprehensive context from knowledge base content for AI conversations.

This advanced context-building tool retrieves and organizes relevant information from your knowledge base
to provide rich context for AI assistants, enabling natural conversation continuation and topic exploration.

CONTEXT BUILDING FEATURES:
- Retrieves full note content with relationships
- Explores connected topics and related information
- Provides temporal context with activity history
- Supports pattern matching for topic discovery
- Builds conversation continuity across sessions

MEMORY URL SYNTAX:
- Direct notes: "folder/note" or "memory://folder/note"
- Folder patterns: "folder/*" (all notes in folder)
- Topic exploration: "projects/ai/*" (AI project notes)
- Valid characters: letters, numbers, hyphens, underscores, forward slashes

TIMEFRAME FILTERING:
- Natural language: "2 days ago", "last week", "today", "3 months ago"
- Standard formats: "7d" (7 days), "24h" (24 hours), "30d" (30 days)
- Recent activity: "today", "yesterday", "this week"
- Historical context: "6 months ago", "1 year ago"

PARAMETERS:
- url (str, REQUIRED): Memory URL or pattern for context building
- depth (int, default=1): Relationship exploration depth (1-5)
- timeframe (str, default="7d"): Time window for activity filtering
- page (int, default=1): Pagination for large result sets
- page_size (int, default=10): Results per page
- max_related (int, default=10): Maximum related items to include

CONTEXT ORGANIZATION:
- Primary content with full details
- Related notes and connections
- Recent activity and updates
- Temporal relationships and history
- Semantic connections and references

USAGE EXAMPLES:
Specific note: build_context("projects/alpha/meeting-notes")
Folder pattern: build_context("research/*")
Recent activity: build_context("projects/current", timeframe="today")
Deep exploration: build_context("concepts/ai", depth=3)
Historical context: build_context("meetings/strategy", timeframe="3 months ago")

RETURNS:
Structured context information including:
- Primary content and metadata
- Related notes and relationships
- Activity timeline and changes
- Connection network and references
- Conversation continuity hints

CONVERSATION CONTINUITY:
- Preserves discussion context across sessions
- Maintains topic relationships and threads
- Provides historical conversation background
- Enables natural follow-up discussions

NOTE: This tool provides rich context for AI conversations. Use specific URLs for focused context,
or patterns for broader topic exploration within timeframes.""",
)
async def build_context(
    url: MemoryUrl,
    depth: Optional[int] = 1,
    timeframe: Optional[TimeFrame] = "7d",
    page: int = 1,
    page_size: int = 10,
    max_related: int = 10,
    project: Optional[str] = None,
) -> GraphContext:
    """Get context needed to continue a discussion.

    This tool enables natural continuation of discussions by loading relevant context
    from memory:// URIs. It uses pattern matching to find relevant content and builds
    a rich context graph of related information.

    Args:
        url: memory:// URI pointing to discussion content (e.g. memory://specs/search)
        depth: How many relation hops to traverse (1-3 recommended for performance)
        timeframe: How far back to look. Supports natural language like "2 days ago", "last week"
        page: Page number of results to return (default: 1)
        page_size: Number of results to return per page (default: 10)
        max_related: Maximum number of related results to return (default: 10)
        project: Optional project name to build context from. If not provided, uses current active project.

    Returns:
        GraphContext containing:
            - primary_results: Content matching the memory:// URI
            - related_results: Connected content via relations
            - metadata: Context building details

    Examples:
        # Continue a specific discussion
        build_context("memory://specs/search")

        # Get deeper context about a component
        build_context("memory://components/memory-service", depth=2)

        # Look at recent changes to a specification
        build_context("memory://specs/document-format", timeframe="today")

        # Research the history of a feature
        build_context("memory://features/knowledge-graph", timeframe="3 months ago")

        # Build context from specific project
        build_context("memory://specs/search", project="work-project")
    """
    logger.info(f"Building context from {url}")
    # URL is already validated and normalized by MemoryUrl type annotation

    # Get the active project first to check project-specific sync status
    active_project = get_active_project(project)

    # Check migration status and wait briefly if needed
    from advanced_memory.mcp.tools.utils import wait_for_migration_or_return_status

    migration_status = await wait_for_migration_or_return_status(
        timeout=5.0, project_name=active_project.name
    )
    if migration_status:  # pragma: no cover
        # Return a proper GraphContext with status message
        from advanced_memory.schemas.memory import MemoryMetadata
        from datetime import datetime

        return GraphContext(
            results=[],
            metadata=MemoryMetadata(
                depth=depth or 1,
                timeframe=timeframe,
                generated_at=datetime.now(),
                primary_count=0,
                related_count=0,
                uri=migration_status,  # Include status in metadata
            ),
        )
    project_url = active_project.project_url

    response = await call_get(
        client,
        f"{project_url}/memory/{memory_url_path(url)}",
        params={
            "depth": depth,
            "timeframe": timeframe,
            "page": page,
            "page_size": page_size,
            "max_related": max_related,
        },
    )
    return GraphContext.model_validate(response.json())
