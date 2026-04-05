"""Dedicated visualization tools for Advanced Memory Knowledge Graphs."""

from typing import Annotated, Literal

import mcp.types as types
from pydantic import Field

from advanced_memory.mcp.mcp_instance import mcp
from advanced_memory.mcp.project_session import get_active_project


@mcp.tool
async def adn_visualize(
    mode: Annotated[
        Literal["point_cloud", "hub_and_spoke", "temporal"],
        Field(description="Visualization mode for the knowledge graph."),
    ] = "point_cloud",
    project: Annotated[
        str | None,
        Field(description="Project to visualize; defaults to active project."),
    ] = None,
    query: Annotated[
        str | None,
        Field(description="Optional query to filter the graph."),
    ] = None,
) -> types.ToolResult:
    """Visualize the Knowledge Graph in various immersive modes.

    The 'point_cloud' mode focuses on semantic density and clusters, ideal for large memories.
    The 'hub_and_spoke' mode highlights central concepts and their direct relations.
    The 'temporal' mode shows the evolution of nodes over time.
    """
    active_project = get_active_project(project)
    if not active_project:
        return types.ToolResult(
            content=[types.TextContent(type="text", text="Error: No active project context.")],
            is_error=True,
        )

    from advanced_memory.deps import get_search_service

    search_service = await get_search_service()

    # Fetch notes and build a graph
    from advanced_memory.schemas.search import SearchQuery

    search_query = SearchQuery(query=query or "*", limit=100 if mode == "point_cloud" else 50)

    search_results = await search_service.search_notes(
        query=search_query, project=active_project.name
    )

    # Build a simple Hub and Spoke graph for visualization
    nodes = []
    edges = []

    # Primary "Hub" node if query exists
    if query:
        nodes.append(
            {"id": "query_hub", "label": f"Search: {query}", "type": "hub", "color": "#00d2ff"}
        )

    for r in search_results.results:
        node_id = r.permalink or r.id
        nodes.append(
            {
                "id": node_id,
                "label": r.title or "Untitled",
                "type": "particle",
                "content": r.content[:100] if r.content else "",
            }
        )
        if query:
            edges.append({"from": "query_hub", "to": node_id, "type": "spoke"})

    from advanced_memory.mcp.prefabs import KnowledgeGraph

    return mcp.ToolResult(
        content=[
            f"# Knowledge Graph: {mode.replace('_', ' ').capitalize()}\nProject: {active_project.name}"
        ],
        app=KnowledgeGraph(nodes=nodes, edges=edges, title=f"KG ({mode}): {active_project.name}"),
    )
