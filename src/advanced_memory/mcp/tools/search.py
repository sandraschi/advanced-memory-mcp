"""Search namespaced app for Advanced Memory MCP.

Decomposed from the legacy adn_search and adn_knowledge_rag tools.
Follows FastMCP 3.2 GA Managed Namespace standards.
"""

from typing import Annotated, Any, Literal

from fastmcp import FastMCP
from pydantic import Field

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
    from advanced_memory.mcp.tools.adn_knowledge_rag import _resolve_project
    from advanced_memory.deps import get_search_service
    
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

    from advanced_memory.mcp.prefabs import SearchExplorer
    from fastmcp.tools import ToolResult

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
