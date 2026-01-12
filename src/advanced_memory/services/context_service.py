"""Service for building rich context from the knowledge graph."""

import datetime
from dataclasses import dataclass, field
from typing import Optional

UTC = datetime.timezone.utc

from loguru import logger
from sqlalchemy import text

from advanced_memory.repository.entity_repository import EntityRepository
from advanced_memory.repository.observation_repository import ObservationRepository
from advanced_memory.repository.search_repository import SearchIndexRow, SearchRepository
from advanced_memory.schemas.memory import MemoryUrl, memory_url_path
from advanced_memory.schemas.search import SearchItemType
from advanced_memory.utils import generate_permalink


@dataclass
class ContextResultRow:
    type: str
    id: int
    title: str
    permalink: str
    file_path: str
    depth: int
    root_id: int
    created_at: datetime
    from_id: int | None = None
    to_id: int | None = None
    relation_type: str | None = None
    content: str | None = None
    category: str | None = None
    entity_id: int | None = None


@dataclass
class ContextResultItem:
    """A hierarchical result containing a primary item with its observations and related items."""

    primary_result: ContextResultRow | SearchIndexRow
    observations: list[ContextResultRow] = field(default_factory=list)
    related_results: list[ContextResultRow] = field(default_factory=list)


@dataclass
class ContextMetadata:
    """Metadata about a context result."""

    uri: str | None = None
    types: list[SearchItemType] | None = None
    depth: int = 1
    timeframe: str | None = None
    generated_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    primary_count: int = 0
    related_count: int = 0
    total_observations: int = 0
    total_relations: int = 0


@dataclass
class ContextResult:
    """Complete context result with metadata."""

    results: list[ContextResultItem] = field(default_factory=list)
    metadata: ContextMetadata = field(default_factory=ContextMetadata)


class ContextService:
    """Service for building rich context from memory:// URIs.

    Handles three types of context building:
    1. Direct permalink lookup - exact match on path
    2. Pattern matching - using * wildcards
    3. Special modes via params (e.g., 'related')
    """

    def __init__(
        self,
        search_repository: SearchRepository,
        entity_repository: EntityRepository,
        observation_repository: ObservationRepository,
    ):
        self.search_repository = search_repository
        self.entity_repository = entity_repository
        self.observation_repository = observation_repository

    async def build_context(
        self,
        memory_url: MemoryUrl | None = None,
        types: list[SearchItemType] | None = None,
        depth: int = 1,
        since: datetime.datetime | None = None,
        limit: int = 10,
        offset: int = 0,
        max_related: int = 10,
        include_observations: bool = True,
    ) -> ContextResult:
        """Build rich context from a memory:// URI."""
        logger.debug(
            f"Building context for URI: '{memory_url}' depth: '{depth}' since: '{since}' limit: '{limit}' offset: '{offset}'  max_related: '{max_related}'"
        )

        if memory_url:
            path = memory_url_path(memory_url)
            # Pattern matching - use search
            if "*" in path:
                logger.debug(f"Pattern search for '{path}'")
                primary = await self.search_repository.search(
                    permalink_match=path, limit=limit, offset=offset
                )

            # Direct lookup for exact path
            else:
                logger.debug(f"Direct lookup for '{path}'")
                primary = await self.search_repository.search(
                    permalink=path, limit=limit, offset=offset
                )
        else:
            logger.debug(f"Build context for '{types}'")
            primary = await self.search_repository.search(
                search_item_types=types, after_date=since, limit=limit, offset=offset
            )

        # Get type_id pairs for traversal

        type_id_pairs = [(r.type, r.id) for r in primary] if primary else []
        logger.debug(f"found primary type_id_pairs: {len(type_id_pairs)}")

        # Find related content
        related = await self.find_related(
            type_id_pairs, max_depth=depth, since=since, max_results=max_related
        )
        logger.debug(f"Found {len(related)} related results")

        # Collect entity IDs from primary and related results
        entity_ids = []
        for result in primary:
            if result.type == SearchItemType.ENTITY.value:
                entity_ids.append(result.id)

        for result in related:
            if result.type == SearchItemType.ENTITY.value:
                entity_ids.append(result.id)

        # Fetch observations for all entities if requested
        observations_by_entity = {}
        if include_observations and entity_ids:
            # Use our observation repository to get observations for all entities at once
            observations_by_entity = await self.observation_repository.find_by_entities(entity_ids)
            logger.debug(f"Found observations for {len(observations_by_entity)} entities")

        # Create metadata dataclass
        metadata = ContextMetadata(
            uri=memory_url_path(memory_url) if memory_url else None,
            types=types,
            depth=depth,
            timeframe=since.isoformat() if since else None,
            primary_count=len(primary),
            related_count=len(related),
            total_observations=sum(len(obs) for obs in observations_by_entity.values()),
            total_relations=sum(1 for r in related if r.type == SearchItemType.RELATION),
        )

        # Build context results list directly with ContextResultItem objects
        context_results = []

        # For each primary result
        for primary_item in primary:
            # Find all related items with this primary item as root
            related_to_primary = [r for r in related if r.root_id == primary_item.id]

            # Get observations for this item if it's an entity
            item_observations = []
            if primary_item.type == SearchItemType.ENTITY.value and include_observations:
                # Convert Observation models to ContextResultRows
                for obs in observations_by_entity.get(primary_item.id, []):
                    item_observations.append(
                        ContextResultRow(
                            type="observation",
                            id=obs.id,
                            title=f"{obs.category}: {obs.content[:50]}...",
                            permalink=generate_permalink(
                                f"{primary_item.permalink}/observations/{obs.category}/{obs.content}"
                            ),
                            file_path=primary_item.file_path,
                            content=obs.content,
                            category=obs.category,
                            entity_id=primary_item.id,
                            depth=0,
                            root_id=primary_item.id,
                            created_at=primary_item.created_at,  # created_at time from entity
                        )
                    )

            # Create ContextResultItem directly
            context_item = ContextResultItem(
                primary_result=primary_item,
                observations=item_observations,
                related_results=related_to_primary,
            )

            context_results.append(context_item)

        # Return the structured ContextResult
        return ContextResult(results=context_results, metadata=metadata)

    async def find_related(
        self,
        type_id_pairs: list[tuple[str, int]],
        max_depth: int = 1,
        since: datetime.datetime | None = None,
        max_results: int = 10,
    ) -> list[ContextResultRow]:
        """Find items connected through relations.

        Uses recursive CTE to find:
        - Connected entities
        - Relations that connect them

        Note on depth:
        Each traversal step requires two depth levels - one to find the relation,
        and another to follow that relation to an entity. So a max_depth of 4 allows
        traversal through two entities (relation->entity->relation->entity), while reaching
        an entity three steps away requires max_depth=6 (relation->entity->relation->entity->relation->entity).
        """
        max_depth = max_depth * 2

        if not type_id_pairs:
            return []

        # Extract entity IDs from type_id_pairs for the optimized query
        entity_ids = [i for t, i in type_id_pairs if t == "entity"]

        if not entity_ids:
            logger.debug("No entity IDs found in type_id_pairs")
            return []

        logger.debug(
            f"Finding connected items for {len(entity_ids)} entities with depth {max_depth}"
        )

        # Build the VALUES clause for entity IDs
        entity_id_values = ", ".join([str(i) for i in entity_ids])

        # For compatibility with the old query, we still need this for filtering
        values = ", ".join([f"('{t}', {i})" for t, i in type_id_pairs])

        # Parameters for bindings
        params = {"max_depth": max_depth, "max_results": max_results}

        # Build date and timeframe filters conditionally based on since parameter
        if since:
            params["since_date"] = since.isoformat()  # pyright: ignore
            date_filter = "AND e.created_at >= :since_date"
            relation_date_filter = "AND e_from.created_at >= :since_date"
            timeframe_condition = "AND eg.relation_date >= :since_date"
        else:
            date_filter = ""
            relation_date_filter = ""
            timeframe_condition = ""

        # Use a CTE that operates directly on entity and relation tables
        # This avoids the overhead of the search_index virtual table
        # nosec B608 - uses parameterized query with :max_depth and :max_results params
        query = text(f"""
        WITH RECURSIVE entity_graph AS (
            -- Base case: seed entities
            SELECT
                e.id,
                'entity' as type,
                e.title,
                e.permalink,
                e.file_path,
                NULL as from_id,
                NULL as to_id,
                NULL as relation_type,
                NULL as content,
                NULL as category,
                NULL as entity_id,
                0 as depth,
                e.id as root_id,
                e.created_at,
                e.created_at as relation_date,
                0 as is_incoming
            FROM entity e
            WHERE e.id IN ({entity_id_values})
            {date_filter}

            UNION ALL

            -- Get relations from current entities
            SELECT
                r.id,
                'relation' as type,
                r.relation_type || ': ' || r.to_name as title,
                -- Relation model doesn't have permalink column - we'll generate it at runtime
                '' as permalink,
                e_from.file_path,
                r.from_id,
                r.to_id,
                r.relation_type,
                NULL as content,
                NULL as category,
                NULL as entity_id,
                eg.depth + 1,
                eg.root_id,
                e_from.created_at, -- Use the from_entity's created_at since relation has no timestamp
                e_from.created_at as relation_date,
                CASE WHEN r.from_id = eg.id THEN 0 ELSE 1 END as is_incoming
            FROM entity_graph eg
            JOIN relation r ON (
                eg.type = 'entity' AND
                (r.from_id = eg.id OR r.to_id = eg.id)
            )
            JOIN entity e_from ON (
                r.from_id = e_from.id
                {relation_date_filter}
            )
            WHERE eg.depth < :max_depth

            UNION ALL

            -- Get entities connected by relations
            SELECT
                e.id,
                'entity' as type,
                e.title,
                CASE
                    WHEN e.permalink IS NULL THEN ''
                    ELSE e.permalink
                END as permalink,
                e.file_path,
                NULL as from_id,
                NULL as to_id,
                NULL as relation_type,
                NULL as content,
                NULL as category,
                NULL as entity_id,
                eg.depth + 1,
                eg.root_id,
                e.created_at,
                eg.relation_date,
                eg.is_incoming
            FROM entity_graph eg
            JOIN entity e ON (
                eg.type = 'relation' AND
                e.id = CASE
                    WHEN eg.is_incoming = 0 THEN eg.to_id
                    ELSE eg.from_id
                END
                {date_filter}
            )
            WHERE eg.depth < :max_depth
            -- Only include entities connected by relations within timeframe if specified
            {timeframe_condition}
        )
        SELECT DISTINCT
            type,
            id,
            title,
            permalink,
            file_path,
            from_id,
            to_id,
            relation_type,
            content,
            category,
            entity_id,
            MIN(depth) as depth,
            root_id,
            created_at
        FROM entity_graph
        WHERE (type, id) NOT IN ({values})
        GROUP BY
            type, id
        ORDER BY depth, type, id
        LIMIT :max_results
       """)

        result = await self.search_repository.execute_query(query, params=params)
        rows = result.all()

        context_rows = [
            ContextResultRow(
                type=row.type,
                id=row.id,
                title=row.title,
                permalink=row.permalink,
                file_path=row.file_path,
                from_id=row.from_id,
                to_id=row.to_id,
                relation_type=row.relation_type,
                content=row.content,
                category=row.category,
                entity_id=row.entity_id,
                depth=row.depth,
                root_id=row.root_id,
                created_at=row.created_at,
            )
            for row in rows
        ]
        return context_rows
"""Skill service for Claude Skills management."""

import datetime
import json

UTC = datetime.timezone.utc

from loguru import logger
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from advanced_memory.models import Skill
from advanced_memory.repository.repository import Repository


class SkillService:
    """Service for managing Claude Skills in Advanced Memory."""

    def __init__(self, session: AsyncSession, repository: Repository):
        """Initialize skill service.

        Args:
            session: Database session
            repository: Repository instance for database operations
        """
        self.session = session
        self.repository = repository
        logger.debug("SkillService initialized")

    async def create_skill(
        self,
        name: str,
        description: str,
        entity_id: int | None = None,
        version: str = "1.0.0",
        category: str | None = None,
        difficulty: str | None = None,
        license: str | None = None,
        allowed_tools: list[str] | None = None,
        custom_metadata: dict | None = None,
    ) -> Skill:
        """Create a new skill.

        Args:
            name: Skill name in hyphen-case
            description: When Claude should use this skill
            entity_id: Optional link to entity
            version: Skill version
            category: Skill category (developer, researcher, etc.)
            difficulty: Difficulty level
            license: License name or path
            allowed_tools: List of pre-approved tools
            custom_metadata: Additional metadata

        Returns:
            Created Skill instance
        """
        now = datetime.now(UTC)

        skill_data = {
            "name": name,
            "description": description,
            "entity_id": entity_id,
            "version": version,
            "category": category,
            "difficulty": difficulty,
            "license": license,
            "allowed_tools": json.dumps(allowed_tools) if allowed_tools else None,
            "custom_metadata": json.dumps(custom_metadata) if custom_metadata else None,
            "usage_count": 0,
            "created_at": now,
            "updated_at": now,
        }

        skill = await self.repository.create(Skill, skill_data)
        logger.info(f"Created skill: {name}")
        return skill

    async def get_skill(self, name: str) -> Skill | None:
        """Get skill by name.

        Args:
            name: Skill name

        Returns:
            Skill instance or None if not found
        """
        stmt = select(Skill).where(Skill.name == name)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def update_skill(
        self,
        name: str,
        description: str | None = None,
        version: str | None = None,
        category: str | None = None,
        custom_metadata: dict | None = None,
    ) -> Skill | None:
        """Update an existing skill.

        Args:
            name: Skill name to update
            description: New description
            version: New version
            category: New category
            custom_metadata: Updated metadata

        Returns:
            Updated Skill instance or None if not found
        """
        skill = await self.get_skill(name)
        if not skill:
            logger.warning(f"Skill not found for update: {name}")
            return None

        update_data = {"updated_at": datetime.now(UTC)}

        if description is not None:
            update_data["description"] = description
        if version is not None:
            update_data["version"] = version
        if category is not None:
            update_data["category"] = category
        if custom_metadata is not None:
            update_data["custom_metadata"] = json.dumps(custom_metadata)

        updated_skill = await self.repository.update(Skill, skill.id, update_data)
        logger.info(f"Updated skill: {name}")
        return updated_skill

    async def delete_skill(self, name: str) -> bool:
        """Delete a skill.

        Args:
            name: Skill name to delete

        Returns:
            True if deleted, False if not found
        """
        skill = await self.get_skill(name)
        if not skill:
            logger.warning(f"Skill not found for deletion: {name}")
            return False

        await self.repository.delete(Skill, skill.id)
        logger.info(f"Deleted skill: {name}")
        return True

    async def list_skills(
        self, category: str | None = None, limit: int = 100, offset: int = 0
    ) -> list[Skill]:
        """List all skills with optional filtering.

        Args:
            category: Filter by category
            limit: Maximum results
            offset: Pagination offset

        Returns:
            List of Skill instances
        """
        stmt = select(Skill)

        if category:
            stmt = stmt.where(Skill.category == category)

        stmt = stmt.limit(limit).offset(offset).order_by(Skill.created_at.desc())

        result = await self.session.execute(stmt)
        skills = result.scalars().all()
        logger.debug(f"Listed {len(skills)} skills")
        return list(skills)

    async def increment_usage(self, name: str) -> None:
        """Increment usage counter for a skill.

        Args:
            name: Skill name
        """
        skill = await self.get_skill(name)
        if skill:
            await self.repository.update(
                Skill,
                skill.id,
                {
                    "usage_count": skill.usage_count + 1,
                    "updated_at": datetime.now(UTC),
                },
            )
            logger.debug(f"Incremented usage for skill: {name}")

    def validate_skill_name(self, name: str) -> tuple[bool, str]:
        """Validate skill name format (Anthropic spec).

        Args:
            name: Skill name to validate

        Returns:
            Tuple of (valid: bool, message: str)
        """
        import re

        # Check hyphen-case format
        if not re.match(r"^[a-z0-9-]+$", name):
            return (
                False,
                f"Name '{name}' must be hyphen-case (lowercase letters, digits, and hyphens only)",
            )

        # Check no leading/trailing/consecutive hyphens
        if name.startswith("-") or name.endswith("-") or "--" in name:
            return (
                False,
                f"Name '{name}' cannot start/end with hyphen or contain consecutive hyphens",
            )

        # Check length (reasonable limit)
        if len(name) > 50:
            return False, f"Name '{name}' is too long (max 50 characters)"

        return True, "Valid skill name"

    def validate_description(self, description: str) -> tuple[bool, str]:
        """Validate skill description (Anthropic spec).

        Args:
            description: Description to validate

        Returns:
            Tuple of (valid: bool, message: str)
        """
        # Check for angle brackets (not allowed)
        if "<" in description or ">" in description:
            return False, "Description cannot contain angle brackets (< or >)"

        # Check minimum length
        if len(description.strip()) < 20:
            return False, "Description is too short (minimum 20 characters)"

        return True, "Valid description"
"""Router for prompt-related operations.

This router is responsible for rendering various prompts using Handlebars templates.
It centralizes all prompt formatting logic that was previously in the MCP prompts.
"""

import datetime

UTC = datetime.timezone.utc

from fastapi import APIRouter, HTTPException, status
from loguru import logger

from advanced_memory.api.routers.utils import to_graph_context, to_search_results
from advanced_memory.api.template_loader import template_loader
from advanced_memory.deps import (
    ContextServiceDep,
    EntityRepositoryDep,
    EntityServiceDep,
    SearchServiceDep,
)
from advanced_memory.schemas.base import parse_timeframe
from advanced_memory.schemas.prompt import (
    ContinueConversationRequest,
    PromptMetadata,
    PromptResponse,
    SearchPromptRequest,
)
from advanced_memory.schemas.search import SearchItemType, SearchQuery

router = APIRouter(prefix="/prompt", tags=["prompt"])


@router.post("/continue-conversation", response_model=PromptResponse)
async def continue_conversation(
    search_service: SearchServiceDep,
    entity_service: EntityServiceDep,
    context_service: ContextServiceDep,
    entity_repository: EntityRepositoryDep,
    request: ContinueConversationRequest,
) -> PromptResponse:
    """Generate a prompt for continuing a conversation.

    This endpoint takes a topic and/or timeframe and generates a prompt with
    relevant context from the knowledge base.

    Args:
        request: The request parameters

    Returns:
        Formatted continuation prompt with context
    """
    logger.info(
        f"Generating continue conversation prompt, topic: {request.topic}, timeframe: {request.timeframe}"
    )

    since = parse_timeframe(request.timeframe) if request.timeframe else None

    # Initialize search results
    search_results = []

    # Get data needed for template
    if request.topic:
        query = SearchQuery(text=request.topic, after_date=request.timeframe)
        results = await search_service.search(query, limit=request.search_items_limit)
        search_results = await to_search_results(entity_service, results)

        # Build context from results
        all_hierarchical_results = []
        for result in search_results:
            if hasattr(result, "permalink") and result.permalink:
                # Get hierarchical context using the new dataclass-based approach
                context_result = await context_service.build_context(
                    result.permalink,
                    depth=request.depth,
                    since=since,
                    max_related=request.related_items_limit,
                    include_observations=True,  # Include observations for entities
                )

                # Process results into the schema format
                graph_context = await to_graph_context(
                    context_result, entity_repository=entity_repository
                )

                # Add results to our collection (limit to top results for each permalink)
                if graph_context.results:
                    all_hierarchical_results.extend(graph_context.results[:3])

        # Limit to a reasonable number of total results
        all_hierarchical_results = all_hierarchical_results[:10]

        template_context = {
            "topic": request.topic,
            "timeframe": request.timeframe,
            "hierarchical_results": all_hierarchical_results,
            "has_results": len(all_hierarchical_results) > 0,
        }
    else:
        # If no topic, get recent activity
        context_result = await context_service.build_context(
            types=[SearchItemType.ENTITY],
            depth=request.depth,
            since=since,
            max_related=request.related_items_limit,
            include_observations=True,
        )
        recent_context = await to_graph_context(context_result, entity_repository=entity_repository)

        hierarchical_results = recent_context.results[:5]  # Limit to top 5 recent items

        template_context = {
            "topic": f"Recent Activity from ({request.timeframe})",
            "timeframe": request.timeframe,
            "hierarchical_results": hierarchical_results,
            "has_results": len(hierarchical_results) > 0,
        }

    try:
        # Render template
        rendered_prompt = await template_loader.render(
            "prompts/continue_conversation.hbs", template_context
        )

        # Calculate metadata
        # Count items of different types
        observation_count = 0
        relation_count = 0
        entity_count = 0

        # Get the hierarchical results from the template context
        hierarchical_results_for_count = template_context.get("hierarchical_results", [])

        # For topic-based search
        if request.topic:
            for item in hierarchical_results_for_count:
                if hasattr(item, "observations"):
                    observation_count += len(item.observations) if item.observations else 0

                if hasattr(item, "related_results"):
                    for related in item.related_results or []:
                        if hasattr(related, "type"):
                            if related.type == "relation":
                                relation_count += 1
                            elif related.type == "entity":  # pragma: no cover
                                entity_count += 1  # pragma: no cover
        # For recent activity
        else:
            for item in hierarchical_results_for_count:
                if hasattr(item, "observations"):
                    observation_count += len(item.observations) if item.observations else 0

                if hasattr(item, "related_results"):
                    for related in item.related_results or []:
                        if hasattr(related, "type"):
                            if related.type == "relation":
                                relation_count += 1
                            elif related.type == "entity":  # pragma: no cover
                                entity_count += 1  # pragma: no cover

        # Build metadata
        metadata = {
            "query": request.topic,
            "timeframe": request.timeframe,
            "search_count": len(search_results)
            if request.topic
            else 0,  # Original search results count
            "context_count": len(hierarchical_results_for_count),
            "observation_count": observation_count,
            "relation_count": relation_count,
            "total_items": (
                len(hierarchical_results_for_count)
                + observation_count
                + relation_count
                + entity_count
            ),
            "search_limit": request.search_items_limit,
            "context_depth": request.depth,
            "related_limit": request.related_items_limit,
            "generated_at": datetime.now(UTC).isoformat(),
        }

        prompt_metadata = PromptMetadata(**metadata)

        return PromptResponse(
            prompt=rendered_prompt, context=template_context, metadata=prompt_metadata
        )
    except Exception as e:
        logger.error(f"Error rendering continue conversation template: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error rendering prompt template: {str(e)}",
        ) from e


@router.post("/search", response_model=PromptResponse)
async def search_prompt(
    search_service: SearchServiceDep,
    entity_service: EntityServiceDep,
    request: SearchPromptRequest,
    page: int = 1,
    page_size: int = 10,
) -> PromptResponse:
    """Generate a prompt for search results.

    This endpoint takes a search query and formats the results into a helpful
    prompt with context and suggestions.

    Args:
        request: The search parameters
        page: The page number for pagination
        page_size: The number of results per page, defaults to 10

    Returns:
        Formatted search results prompt with context
    """
    logger.info(f"Generating search prompt, query: {request.query}, timeframe: {request.timeframe}")

    limit = page_size
    offset = (page - 1) * page_size

    query = SearchQuery(text=request.query, after_date=request.timeframe)
    results = await search_service.search(query, limit=limit, offset=offset)
    search_results = await to_search_results(entity_service, results)

    template_context = {
        "query": request.query,
        "timeframe": request.timeframe,
        "results": search_results,
        "has_results": len(search_results) > 0,
        "result_count": len(search_results),
    }

    try:
        # Render template
        rendered_prompt = await template_loader.render("prompts/search.hbs", template_context)

        # Build metadata
        metadata = {
            "query": request.query,
            "timeframe": request.timeframe,
            "search_count": len(search_results),
            "context_count": len(search_results),
            "observation_count": 0,  # Search results don't include observations
            "relation_count": 0,  # Search results don't include relations
            "total_items": len(search_results),
            "search_limit": limit,
            "context_depth": 0,  # No context depth for basic search
            "related_limit": 0,  # No related items for basic search
            "generated_at": datetime.now(UTC).isoformat(),
        }

        prompt_metadata = PromptMetadata(**metadata)

        return PromptResponse(
            prompt=rendered_prompt, context=template_context, metadata=prompt_metadata
        )
    except Exception as e:
        logger.error(f"Error rendering search template: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error rendering prompt template: {str(e)}",
        ) from e
"""Recent activity tool for Advanced Memory MCP server."""

import datetime

UTC = datetime.timezone.utc
from typing import Any

from loguru import logger

from advanced_memory.mcp.async_client import client
from advanced_memory.mcp.mcp_instance import mcp
from advanced_memory.mcp.project_session import get_active_project
from advanced_memory.mcp.tools.utils import call_get
from advanced_memory.schemas.base import TimeFrame
from advanced_memory.schemas.memory import GraphContext
from advanced_memory.schemas.search import SearchItemType


@mcp.tool
async def recent_activity(
    type_filter: str | list[str] = "",
    depth: int = 1,
    timeframe: TimeFrame = "7d",
    page: int = 1,
    page_size: int = 10,
    max_related: int = 10,
    project: str | None = None,
) -> dict[str, Any]:
    """Get recent activity across the knowledge base.

    Args:
        type_filter: Filter by content type(s). Can be a string or list of strings.
            Valid options:
            - "entity" or ["entity"] for knowledge entities
            - "relation" or ["relation"] for connections between entities
            - "observation" or ["observation"] for notes and observations
            Multiple types can be combined: ["entity", "relation"]
            Case-insensitive: "ENTITY" and "entity" are treated the same.
            Default is an empty string, which returns all types.
            Fallback: Invalid types are ignored. If all types are invalid, falls back to all types with a warning.
        depth: How many relation hops to traverse (1-3 recommended)
        timeframe: Time window to search. Supports natural language:
            - Relative: "2 days ago", "last week", "yesterday"
            - Points in time: "2024-01-01", "January 1st"
            - Standard format: "7d", "24h"
        page: Page number of results to return (default: 1)
        page_size: Number of results to return per page (default: 10)
        max_related: Maximum number of related results to return (default: 10)
        project: Optional project name to get activity from. If not provided, uses current active project.

    Returns:
        Dictionary containing:
            - results: Latest activities matching the filters
            - metadata: Query details and statistics
            - page/page_size: Pagination info (when available)

    Examples:
        # Get all entities for the last 10 days (default)
        recent_activity()

        # Get all entities from yesterday (string format)
        recent_activity(type_filter="entity", timeframe="yesterday")

        # Get all entities from yesterday (list format)
        recent_activity(type_filter=["entity"], timeframe="yesterday")

        # Get recent relations and observations
        recent_activity(type_filter=["relation", "observation"], timeframe="today")

        # Look back further with more context
        recent_activity(type_filter="entity", depth=2, timeframe="2 weeks ago")

        # Get activity from specific project
        recent_activity(type_filter="entity", project="work-project")

    Errors:
        - "Invalid timeframe": Returned if the provided 'timeframe' natural language format is not recognized.
        - "Project not found": Returned if the specified 'project' name does not exist.

    Notes:
        - Higher depth values (>3) may impact performance with large result sets
        - For focused queries, consider using build_context with a specific URI
        - Max timeframe is 1 year in the past
    """
    logger.info(
        f"Getting recent activity from type_filter={type_filter}, depth={depth}, timeframe={timeframe}, page={page}, page_size={page_size}, max_related={max_related}"
    )
    params = {
        "page": page,
        "page_size": page_size,
        "max_related": max_related,
    }
    if depth:
        params["depth"] = depth
    if timeframe:
        params["timeframe"] = timeframe  # pyright: ignore

    # Validate and convert type_filter parameter
    invalid_types = []
    if type_filter:
        # Convert single string to list
        if isinstance(type_filter, str):
            type_list = [type_filter]
        else:
            type_list = type_filter

        # Validate each type against SearchItemType enum
        validated_types = []
        for t in type_list:
            try:
                # Try to convert string to enum
                if isinstance(t, str):
                    validated_types.append(SearchItemType(t.lower()))
            except ValueError:
                # Track invalid types but don't fail
                invalid_types.append(t)
                logger.warning(
                    f"Invalid type_filter value: '{t}'. Ignoring and continuing with valid types."
                )

        # If we have valid types, use them. If all were invalid, fall back to all types
        if validated_types:
            params["type"] = [t.value for t in validated_types]  # pyright: ignore
        elif invalid_types:
            # All types were invalid - fallback to all types with warning
            valid_types = [t.value for t in SearchItemType]
            logger.warning(
                f"All provided types were invalid: {invalid_types}. "
                f"Falling back to all types. Valid options: {valid_types}"
            )

    active_project = get_active_project(project)
    project_url = active_project.project_url

    response = await call_get(
        client,
        f"{project_url}/memory/recent",
        params=params,
    )
    raw_data = response.json()

    def normalize_timestamp(value: Any) -> str | None:
        if value is None:
            return None
        if isinstance(value, str):
            try:
                # Handle timestamps with or without timezone info
                ts = value.replace("Z", "+00:00")
                dt = datetime.fromisoformat(ts)
            except ValueError:
                return value
        elif isinstance(value, datetime):
            dt = value
        else:
            return str(value)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=UTC)
        return dt.astimezone(UTC).strftime("%Y-%m-%dT%H:%M:%S+00:00")

    def normalize_summary(summary: dict[str, Any]) -> dict[str, Any]:
        summary_type = summary.get("type")

        if summary_type == "relation":
            summary["relation_type"] = summary.get("relation_type") or "related_to"
            summary["from_entity"] = summary.get("from_entity")
            summary["to_entity"] = summary.get("to_entity")
        elif summary_type == "observation":
            summary["category"] = summary.get("category") or "general"
            summary["content"] = summary.get("content") or ""

        summary["created_at"] = normalize_timestamp(summary.get("created_at"))
        return summary

    results = raw_data.get("results", [])
    for item in results:
        if "primary_result" in item and isinstance(item["primary_result"], dict):
            item["primary_result"] = normalize_summary(item["primary_result"])

        observations = item.get("observations", [])
        item["observations"] = [
            normalize_summary(obs) for obs in observations if isinstance(obs, dict)
        ]

        related = item.get("related_results", [])
        item["related_results"] = [
            normalize_summary(rel) for rel in related if isinstance(rel, dict)
        ]

    metadata = raw_data.get("metadata", {})
    metadata["generated_at"] = normalize_timestamp(metadata.get("generated_at"))
    metadata["timeframe"] = metadata.get("timeframe")
    raw_data["metadata"] = metadata

    raw_data["results"] = results

    context = GraphContext.model_validate(raw_data)
    return context.model_dump(mode="json")
