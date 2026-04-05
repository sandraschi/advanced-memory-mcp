"""Router for search operations."""

from fastapi import APIRouter, BackgroundTasks

from advanced_memory.api.routers.utils import to_search_results
from advanced_memory.deps import EntityServiceDep, SearchServiceDep
from advanced_memory.schemas.search import (
    SearchQuery,
    SearchResponse,
    SemanticSearchRequest,
    SemanticSearchResponse,
)

router = APIRouter(prefix="/search", tags=["search"])


@router.post("/semantic", response_model=SemanticSearchResponse)
async def semantic_search(
    body: SemanticSearchRequest,
    search_service: SearchServiceDep,
) -> SemanticSearchResponse:
    """Semantic (vector) search returning chunks with entity_id and permalink for UI."""
    chunks = await search_service.semantic_search_chunks(body.query, limit=body.limit)
    return SemanticSearchResponse(
        chunks=[
            {
                "entity_id": c["entity_id"],
                "permalink": c.get("permalink"),
                "title": c["title"],
                "snippet": c["snippet"],
                "chunk_text": c["chunk_text"],
                "score": c["score"],
            }
            for c in chunks
        ]
    )


@router.post("/", response_model=SearchResponse)
async def search(
    query: SearchQuery,
    search_service: SearchServiceDep,
    entity_service: EntityServiceDep,
    page: int = 1,
    page_size: int = 10,
):
    """Search across all knowledge and documents."""
    limit = page_size
    offset = (page - 1) * page_size
    results, total_count = await search_service.search(query, limit=limit, offset=offset)
    search_results = await to_search_results(entity_service, results)
    return SearchResponse(
        results=search_results,
        current_page=page,
        page_size=page_size,
        total_results=total_count,
    )


@router.post("/reindex")
async def reindex(background_tasks: BackgroundTasks, search_service: SearchServiceDep):
    """Recreate and populate the search index."""
    await search_service.reindex_all(background_tasks=background_tasks)
    return {"status": "ok", "message": "Reindex initiated"}
