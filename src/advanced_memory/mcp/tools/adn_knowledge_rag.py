from typing import Annotated, Any

from fastmcp import FastMCP
from pydantic import Field

from advanced_memory.deps import get_search_service


def _resolve_project(project: str | None) -> str | None:
    """Return the project to use: explicit override, or current session project."""
    if project:
        return project
    try:
        from advanced_memory.mcp.project_session import session

        return session.get_current_project()
    except Exception:
        return None


def register_rag_bridge(mcp: FastMCP):
    # @mcp.tool()
    async def adn_knowledge_rag(
        query: Annotated[str, Field(description="The semantic search query or context prompt")],
        limit: Annotated[int, Field(description="Maximum number of high-density chunks to return")] = 10,
        project: Annotated[
            str | None, Field(description="Optional project override (defaults to current active)")
        ] = None,
        min_score: Annotated[float, Field(description="Minimum relevance threshold (0.0 to 1.0)")] = 0.5,
        include_metadata: Annotated[
            bool, Field(description="Whether to include source metadata (file paths, timestamps)")
        ] = True,
    ) -> Any:
        """Specialized RAG retrieval for optimized knowledge management.

        Leverages LanceDB and vector search for high-precision context retrieval.
        """
        try:
            target_project = _resolve_project(project)
            search_service = await get_search_service()

            # Use the optimized knowledge_rag implementation from SearchService
            results = await search_service.knowledge_rag(
                query=query, limit=limit, project=target_project, min_score=min_score
            )

            # Format high-density context for Agentic models
            context_blocks = []
            sources = []
            explorer_results = []

            for i, chunk in enumerate(results.get("results", [])):
                score = chunk.get("score", 0.0)
                text = chunk.get("text", "")
                meta = chunk.get("metadata", {})
                source = meta.get("path") or meta.get("filename") or "Unknown"

                block = f"[Source {i + 1}: {source}] (Relevance: {score:.2f})\n{text}"
                context_blocks.append(block)
                sources.append(source)

                explorer_results.append(
                    {
                        "title": f"Source {i + 1}: {source}",
                        "permalink": source,
                        "content": text,
                        "score": score,
                        "type": "chunk",
                    }
                )

            formatted_context = "\n\n---\n\n".join(context_blocks)

            from fastmcp.tools import ToolResult

            from advanced_memory.mcp.prefabs import SearchExplorer

            return ToolResult(
                content=[f"## RAG Results for: {query}\n\n{formatted_context}"],
                app=SearchExplorer(f"RAG: {query}", explorer_results),
            )

        except Exception as e:
            from loguru import logger

            logger.error(f"RAG error: {e}")
            return {"success": False, "error": str(e)}
