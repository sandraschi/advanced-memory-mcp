"""Router for knowledge graph operations."""

from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query, Response
from loguru import logger
from sqlalchemy import select

from advanced_memory.deps import (
    AppConfigDep,
    EntityRepositoryDep,
    EntityServiceDep,
    FileServiceDep,
    LinkResolverDep,
    ProjectConfigDep,
    ProjectIdDep,
    ProjectPathDep,
    SearchServiceDep,
    SessionMakerDep,
    SyncServiceDep,
    get_search_service,
)
from advanced_memory.models.knowledge import Entity as EntityModel
from advanced_memory.schemas import (
    DeleteEntitiesRequest,
    DeleteEntitiesResponse,
    EntityListResponse,
    EntityResponse,
    NoteContentResponse,
)
from advanced_memory.schemas.base import Entity, Permalink
from advanced_memory.schemas.request import EditEntityRequest, MoveEntityRequest
from advanced_memory.services.graph_subgraph import fetch_link_subgraph

router = APIRouter(prefix="/knowledge", tags=["knowledge"])

## Create endpoints


def _coerce_tags(value: object) -> list[str]:
    """Normalize a stored `tags` metadata value into a real list[str].

    Some historically-imported entities have `tags` stored as the string
    repr of a Python list (e.g. "['a', 'b']") instead of an actual list,
    which crashes frontend code expecting `tags.map(...)`. Coerce any shape
    into a clean list so API consumers never have to special-case this.
    """
    if isinstance(value, list):
        return [str(t) for t in value]
    if isinstance(value, str):
        stripped = value.strip()
        if stripped.startswith("[") and stripped.endswith("]"):
            import ast

            try:
                parsed = ast.literal_eval(stripped)
                if isinstance(parsed, list | tuple | set):
                    return [str(t) for t in parsed]
            except (ValueError, SyntaxError):
                pass
        # Fallback: treat as a single tag, or empty if blank
        return [stripped] if stripped else []
    return []


@router.post("/entities", response_model=EntityResponse)
async def create_entity(
    data: Entity,
    background_tasks: BackgroundTasks,
    entity_service: EntityServiceDep,
    search_service: SearchServiceDep,
) -> EntityResponse:
    """Create an entity."""
    logger.info("API request", endpoint="create_entity", entity_type=data.entity_type, title=data.title)

    entity = await entity_service.create_entity(data)

    # reindex
    await search_service.index_entity(entity, background_tasks=background_tasks)
    result = EntityResponse.model_validate(entity)

    logger.info(
        f"API response: endpoint='create_entity' title={result.title}, permalink={result.permalink}, status_code=201"
    )
    return result


@router.put("/entities/{permalink:path}", response_model=EntityResponse)
async def create_or_update_entity(
    project: ProjectPathDep,
    permalink: Permalink,
    data: Entity,
    response: Response,
    background_tasks: BackgroundTasks,
    entity_service: EntityServiceDep,
    search_service: SearchServiceDep,
    file_service: FileServiceDep,
    sync_service: SyncServiceDep,
) -> EntityResponse:
    """Create or update an entity. If entity exists, it will be updated, otherwise created."""
    logger.info(
        f"API request: create_or_update_entity for {project=}, {permalink=}, {data.entity_type=}, {data.title=}"
    )

    # Validate permalink matches
    if data.permalink != permalink:
        logger.warning(
            f"API validation error: creating/updating entity with permalink mismatch - url={permalink}, data={data.permalink}",
        )
        raise HTTPException(
            status_code=400,
            detail=f"Entity permalink {data.permalink} must match URL path: '{permalink}'",
        )

    # Try create_or_update operation
    entity, created = await entity_service.create_or_update_entity(data)
    response.status_code = 201 if created else 200

    # reindex
    await search_service.index_entity(entity, background_tasks=background_tasks)

    # Attempt immediate relation resolution when creating new entities
    # This helps resolve forward references when related entities are created in the same session
    if created:
        try:
            await sync_service.resolve_relations()
            logger.debug(f"Resolved relations after creating entity: {entity.permalink}")
        except Exception as e:  # pragma: no cover
            # Don't fail the entire request if relation resolution fails
            logger.warning(f"Failed to resolve relations after entity creation: {e}")

    result = EntityResponse.model_validate(entity)

    logger.info(f"API response: {result.title=}, {result.permalink=}, {created=}, status_code={response.status_code}")
    return result


@router.patch("/entities/{identifier:path}", response_model=EntityResponse)
async def edit_entity(
    identifier: str,
    data: EditEntityRequest,
    background_tasks: BackgroundTasks,
    entity_service: EntityServiceDep,
    search_service: SearchServiceDep,
) -> EntityResponse:
    """Edit an existing entity using various operations like append, prepend, find_replace, or replace_section.

    This endpoint allows for targeted edits without requiring the full entity content.
    """
    logger.info(f"API request: endpoint='edit_entity', identifier='{identifier}', operation='{data.operation}'")

    try:
        # Edit the entity using the service
        entity = await entity_service.edit_entity(
            identifier=identifier,
            operation=data.operation,
            content=data.content,
            section=data.section,
            find_text=data.find_text,
            expected_replacements=data.expected_replacements,
            use_regex=data.use_regex,
        )

        # Reindex the updated entity
        await search_service.index_entity(entity, background_tasks=background_tasks)

        # Return the updated entity response
        result = EntityResponse.model_validate(entity)

        logger.info(
            "API response",
            endpoint="edit_entity",
            identifier=identifier,
            operation=data.operation,
            permalink=result.permalink,
            status_code=200,
        )

        return result

    except Exception as e:
        logger.error(f"Error editing entity: {e}")
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.post("/move")
async def move_entity(
    data: MoveEntityRequest,
    background_tasks: BackgroundTasks,
    entity_service: EntityServiceDep,
    project_config: ProjectConfigDep,
    app_config: AppConfigDep,
    search_service: SearchServiceDep,
) -> EntityResponse:
    """Move an entity to a new file location with project consistency.

    This endpoint moves a note to a different path while maintaining project
    consistency and optionally updating permalinks based on configuration.
    """
    logger.info(
        f"API request: endpoint='move_entity', identifier='{data.identifier}', destination='{data.destination_path}'"
    )

    try:
        # Move the entity using the service
        moved_entity = await entity_service.move_entity(
            identifier=data.identifier,
            destination_path=data.destination_path,
            project_config=project_config,
            app_config=app_config,
        )

        # Get the moved entity to reindex it
        entity = await entity_service.link_resolver.resolve_link(data.destination_path)
        if entity:
            await search_service.index_entity(entity, background_tasks=background_tasks)

        logger.info(
            "API response",
            endpoint="move_entity",
            identifier=data.identifier,
            destination=data.destination_path,
            status_code=200,
        )
        result = EntityResponse.model_validate(moved_entity)
        return result

    except Exception as e:
        logger.error(f"Error moving entity: {e}")
        raise HTTPException(status_code=400, detail=str(e)) from e


## Read endpoints


@router.get("/entities/{identifier:path}/content", response_model=NoteContentResponse)
async def get_entity_content(
    link_resolver: LinkResolverDep,
    file_service: FileServiceDep,
    identifier: str,
) -> NoteContentResponse:
    """Get full note content by permalink or path (for semantic search chunk click)."""
    entity = await link_resolver.resolve_link(identifier)
    if not entity:
        raise HTTPException(status_code=404, detail=f"Entity {identifier} not found")
    try:
        content = await file_service.read_entity_content(entity)
    except Exception as e:
        logger.warning(f"Failed to read entity content: {e}")
        raise HTTPException(status_code=500, detail="Failed to read note content") from e
    return NoteContentResponse(
        title=entity.title,
        permalink=getattr(entity, "permalink", None),
        content=content,
    )


@router.get("/entities/{identifier:path}", response_model=EntityResponse)
async def get_entity(
    entity_service: EntityServiceDep,
    link_resolver: LinkResolverDep,
    identifier: str,
) -> EntityResponse:
    """Get a specific entity by file path or permalink..

    Args:
        identifier: Entity file path or permalink
        :param entity_service: EntityService
        :param link_resolver: LinkResolver
    """
    logger.info(f"request: get_entity with identifier={identifier}")
    entity = await link_resolver.resolve_link(identifier)
    if not entity:
        raise HTTPException(status_code=404, detail=f"Entity {identifier} not found")

    result = EntityResponse.model_validate(entity)
    return result


@router.get("/entities", response_model=EntityListResponse)
async def get_entities(
    entity_service: EntityServiceDep,
    permalink: Annotated[list[str] | None, Query()] = None,
) -> EntityListResponse:
    """Open specific entities"""
    logger.info(f"request: get_entities with permalinks={permalink}")

    entities = await entity_service.get_entities_by_permalinks(permalink) if permalink else []
    result = EntityListResponse(entities=[EntityResponse.model_validate(entity) for entity in entities])
    return result


@router.get("/skills")
async def list_skills(
    session_maker: SessionMakerDep,
    project_id: ProjectIdDep,
) -> dict:
    """List all skills (entities with entity_type='skill') for the project."""
    async with session_maker() as session:
        stmt = (
            select(EntityModel)
            .where(EntityModel.project_id == project_id, EntityModel.entity_type == "skill")
            .order_by(EntityModel.updated_at.desc())
        )
        result = await session.execute(stmt)
        entities = result.scalars().all()
    folders: set[str] = set()
    skills_list = []
    for e in entities:
        folder = str(Path(e.file_path).parent) if e.file_path else ""
        if folder:
            folders.add(folder)
        skills_list.append(
            {
                "id": e.permalink or str(e.id),
                "title": e.title,
                "description": (e.entity_metadata or {}).get("description", ""),
                "folder": folder,
                "tags": _coerce_tags((e.entity_metadata or {}).get("tags", [])),
                "created": str(e.created_at),
                "modified": str(e.updated_at),
                "content": "",
                "filePath": e.file_path or "",
                "sources": 0,
            }
        )
    return {"success": True, "data": {"skills": skills_list, "folders": sorted(folders)}}


@router.get("/graph/subgraph")
async def knowledge_graph_subgraph(
    project_id: ProjectIdDep,
    session_maker: SessionMakerDep,
    entity_repository: EntityRepositoryDep,
    center: Annotated[str | None, Query(description="Focus permalink or entity:<numeric_id>")] = None,
    depth: Annotated[int, Query(ge=1, le=5)] = 2,
    max_nodes: Annotated[int, Query(ge=10, le=5000)] = 400,
    max_edges: Annotated[int, Query(ge=10, le=20000)] = 800,
    include_unresolved: Annotated[bool, Query()] = True,
    seed_size: Annotated[
        int, Query(ge=10, le=2000, description="Number of recent notes to seed BFS when no center is given")
    ] = 200,
) -> dict:
    """Bounded link graph for the vault (BFS from ``center`` or recent notes).

    Returns JSON ``{ nodes, links, meta }`` suitable for force-graph UIs.
    """
    return await fetch_link_subgraph(
        session_maker,
        project_id,
        entity_repository,
        center=center,
        depth=depth,
        max_nodes=max_nodes,
        max_edges=max_edges,
        include_unresolved=include_unresolved,
        seed_size=seed_size,
    )


## Delete endpoints


@router.delete("/entities/{identifier:path}", response_model=DeleteEntitiesResponse)
async def delete_entity(
    identifier: str,
    background_tasks: BackgroundTasks,
    entity_service: EntityServiceDep,
    link_resolver: LinkResolverDep,
    search_service=Depends(get_search_service),
) -> DeleteEntitiesResponse:
    """Delete a single entity and remove from search index."""
    logger.info(f"request: delete_entity with identifier={identifier}")

    entity = await link_resolver.resolve_link(identifier)
    if entity is None:
        return DeleteEntitiesResponse(deleted=False)

    # Delete the entity
    deleted = await entity_service.delete_entity(entity.permalink or entity.id)

    # Remove from search index (entity, observations, and relations)
    background_tasks.add_task(search_service.handle_delete, entity)

    result = DeleteEntitiesResponse(deleted=deleted)
    return result


@router.post("/entities/delete", response_model=DeleteEntitiesResponse)
async def delete_entities(
    data: DeleteEntitiesRequest,
    background_tasks: BackgroundTasks,
    entity_service: EntityServiceDep,
    search_service=Depends(get_search_service),
) -> DeleteEntitiesResponse:
    """Delete entities and remove from search index."""
    logger.info(f"request: delete_entities with data={data}")
    deleted = False

    # Remove each deleted entity from search index
    for permalink in data.permalinks:
        deleted = await entity_service.delete_entity(permalink)
        background_tasks.add_task(search_service.delete_by_permalink, permalink)

    result = DeleteEntitiesResponse(deleted=deleted)
    return result
