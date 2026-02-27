"""Service for search operations."""

import ast
from collections.abc import Sequence
from datetime import datetime
from typing import Any

from dateparser import parse
from fastapi import BackgroundTasks
from loguru import logger
from sqlalchemy import text

from advanced_memory.config import AdvancedMemoryConfig
from advanced_memory.models import Entity
from advanced_memory.repository import EntityRepository
from advanced_memory.repository.search_repository import (
    SearchIndexRow,
    SearchRepository,
)
from advanced_memory.repository.vector_repository import VectorRepository
from advanced_memory.schemas.search import SearchItemType, SearchQuery
from advanced_memory.services.file_service import FileService


class SearchService:
    """Service for search operations.

    Supports three primary search modes:
    1. Exact permalink lookup
    2. Pattern matching with * (e.g., 'specs/*')
    3. Full-text search across title/content
    """

    def __init__(
        self,
        search_repository: SearchRepository,
        entity_repository: EntityRepository,
        vector_repository: VectorRepository,
        file_service: FileService,
        app_config: AdvancedMemoryConfig,
    ):
        self.repository = search_repository
        self.entity_repository = entity_repository
        self.vector_repository = vector_repository
        self.file_service = file_service
        self.app_config = app_config

    async def init_search_index(self) -> None:
        """Create FTS5 virtual table if it doesn't exist."""
        await self.repository.init_search_index()

    async def reindex_all(self, background_tasks: BackgroundTasks | None = None) -> None:
        """Reindex all content from database."""

        logger.info("Starting full reindex")
        # Clear and recreate search index
        await self.repository.execute_query(text("DROP TABLE IF EXISTS search_index"), params={})
        await self.init_search_index()

        # Reindex all entities
        logger.debug("Indexing entities")
        entities: Sequence[Entity] = await self.entity_repository.find_all()
        for entity in entities:
            await self.index_entity(entity, background_tasks)

        # Vector indexing is handled inside index_entity
        logger.info("Reindex complete")

    async def search(
        self, query: SearchQuery, limit: int = 10, offset: int = 0
    ) -> tuple[list[SearchIndexRow], int]:
        """Search across all indexed content.

        Supports three modes:
        1. Exact permalink: finds direct matches for a specific path
        2. Pattern match: handles * wildcards in paths
        3. Text search: full-text search across title/content
        """
        if query.no_criteria():
            logger.debug("no criteria passed to query")
            return [], 0

        logger.trace(f"Searching with query: {query}")

        after_date = (
            (
                query.after_date
                if isinstance(query.after_date, datetime)
                else parse(query.after_date)
            )
            if query.after_date
            else None
        )

        before_date = (
            (
                query.before_date
                if isinstance(query.before_date, datetime)
                else parse(query.before_date)
            )
            if query.before_date
            else None
        )

        # Perform keyword search in SQLite
        results, total_count = await self.repository.search(
            search_text=query.text,
            permalink=query.permalink,
            permalink_match=query.permalink_match,
            title=query.title,
            types=query.types,
            search_item_types=query.entity_types,
            after_date=after_date,
            before_date=before_date,
            tags=query.tags,
            limit=limit,
            offset=offset,
        )

        # If query has text, augment with vector results or perform hybrid search
        if query.text and not query.permalink and not query.permalink_match:
            try:
                # Use project filter for vector search
                project_filter = f"metadata.project_id = {self.repository.project_id}"

                # Decide if we use native hybrid search or simple vector augmentation
                candidate_limit = (
                    self.app_config.rag_top_k_candidates
                    if self.app_config.rag_use_reranker
                    else limit * 2
                )

                query_type = "hybrid" if self.app_config.rag_hybrid_search else "vector"

                logger.debug(
                    f"Performing vector/hybrid search (type={query_type}, limit={candidate_limit})"
                )
                vector_results = await self.vector_repository.search(
                    query.text,
                    limit=candidate_limit,
                    query_type=query_type,
                    filter=project_filter,
                )

                # Merge vector results if they are not already in FTS results
                existing_ids = {r.entity_id for r in results}

                # Convert vector results to SearchIndexRow for merging/reranking
                merged_results = list(results)
                for v_res in vector_results:
                    entity_id = v_res["metadata"]["entity_id"]
                    if entity_id not in existing_ids:
                        row = SearchIndexRow(
                            id=int(v_res["id"].split("_")[0])
                            if "_" in v_res["id"]
                            else 0,  # Fallback
                            entity_id=entity_id,
                            type=v_res["metadata"]["type"],
                            title=v_res["metadata"].get("title", "Vector Match"),
                            content_snippet=v_res["text"][:250],
                            project_id=v_res["metadata"]["project_id"],
                            created_at=datetime.now(),
                            updated_at=datetime.now(),
                            score=v_res.get("_score", 0.0),  # Native LanceDB score if available
                        )
                        # Store full text for reranker
                        row.content_stems = v_res["text"]
                        merged_results.append(row)
                        existing_ids.add(entity_id)

                # Perform reranking if enabled
                if self.app_config.rag_use_reranker and merged_results:
                    logger.debug(
                        f"Reranking {len(merged_results)} candidates using {self.app_config.rag_reranker_model}"
                    )

                    # Convert SearchIndexRows to dicts for rerank method
                    docs_to_rerank = []
                    for r in merged_results:
                        docs_to_rerank.append(
                            {
                                "text": f"Title: {r.title}\n\n{r.content_stems or r.content_snippet}",
                                "row": r,  # Keep reference to original row
                            }
                        )

                    reranked_docs = await self.vector_repository.rerank(
                        query.text,
                        docs_to_rerank,
                        self.app_config.rag_reranker_model,
                        attn_implementation=self.app_config.rag_attn_implementation,
                    )

                    # Extract top K final results
                    results = [d["row"] for d in reranked_docs[: self.app_config.rag_top_k_final]]
                    # Update scores with rerank scores
                    for i, r in enumerate(results):
                        r.score = reranked_docs[i]["rerank_score"]
                else:
                    results = merged_results[:limit]

                # Update total count
                total_count = max(total_count, len(existing_ids))

            except Exception as e:
                logger.error(f"Enhanced search failed: {e}")
                import traceback

                logger.debug(traceback.format_exc())

        return results, total_count

    async def knowledge_rag(self, query: str, limit: int = 20) -> list[dict[str, Any]]:
        """Optimized RAG tool for OpenFang/Agentic cognitive bridge.

        Retrieves high-density knowledge context with reranking and FA2.
        """
        project_filter = f"metadata.project_id = {self.repository.project_id}"

        # 1. Broad retrieval
        candidate_limit = self.app_config.rag_top_k_candidates
        vector_results = await self.vector_repository.search(
            query,
            limit=candidate_limit,
            query_type="hybrid" if self.app_config.rag_hybrid_search else "vector",
            filter=project_filter,
        )

        if not vector_results:
            return []

        # 2. Reranking with Flash Attention 2
        reranked_docs = await self.vector_repository.rerank(
            query,
            vector_results,
            self.app_config.rag_reranker_model,
            attn_implementation=self.app_config.rag_attn_implementation,
        )

        # 3. Format for context consumption
        final_results = reranked_docs[:limit]
        formatted = []
        for doc in final_results:
            formatted.append(
                {
                    "content": doc["text"],
                    "source": doc["metadata"].get("title", "Unknown"),
                    "relevance": doc.get("rerank_score", 0.0),
                    "type": doc["metadata"].get("type", "note"),
                }
            )

        return formatted

    @staticmethod
    def _generate_variants(text: str) -> set[str]:
        """Generate text variants for better fuzzy matching.

        Creates variations of the text to improve match chances:
        - Original form
        - Lowercase form
        - Path segments (for permalinks)
        - Common word boundaries
        """
        variants = {text, text.lower()}

        # Add path segments
        if "/" in text:
            variants.update(p.strip() for p in text.split("/") if p.strip())

        # Add word boundaries
        variants.update(w.strip() for w in text.lower().split() if w.strip())

        # Add trigrams for fuzzy matching
        variants.update(text[i : i + 3].lower() for i in range(len(text) - 2))

        return variants

    def _extract_entity_tags(self, entity: Entity) -> list[str]:
        """Extract tags from entity metadata for search indexing.

        Handles multiple tag formats:
        - List format: ["tag1", "tag2"]
        - String format: "['tag1', 'tag2']" or "[tag1, tag2]"
        - Empty: [] or "[]"

        Returns a list of tag strings for search indexing.
        """
        if not entity.entity_metadata or "tags" not in entity.entity_metadata:
            return []

        tags = entity.entity_metadata["tags"]

        # Handle list format (preferred)
        if isinstance(tags, list):
            return [str(tag) for tag in tags if tag]

        # Handle string format (legacy)
        if isinstance(tags, str):
            try:
                # Parse string representation of list
                parsed_tags = ast.literal_eval(tags)
                if isinstance(parsed_tags, list):
                    return [str(tag) for tag in parsed_tags if tag]
            except (ValueError, SyntaxError):
                # If parsing fails, treat as single tag
                return [tags] if tags.strip() else []

        return []  # pragma: no cover

    async def index_entity(
        self,
        entity: Entity,
        background_tasks: BackgroundTasks | None = None,
    ) -> None:
        if background_tasks:
            background_tasks.add_task(self.index_entity_data, entity)
        else:
            await self.index_entity_data(entity)

    async def index_entity_data(
        self,
        entity: Entity,
    ) -> None:
        # delete all search index data associated with entity
        await self.repository.delete_by_entity_id(entity_id=entity.id)
        await self.vector_repository.delete_by_entity_id(entity_id=entity.id)

        # reindex
        await self.index_entity_markdown(
            entity
        ) if entity.is_markdown else await self.index_entity_file(entity)

    async def index_entity_file(
        self,
        entity: Entity,
    ) -> None:
        # Index entity file with no content
        await self.repository.index_item(
            SearchIndexRow(
                id=entity.id,
                entity_id=entity.id,
                type=SearchItemType.ENTITY.value,
                title=entity.title,
                file_path=entity.file_path,
                metadata={
                    "entity_type": entity.entity_type,
                },
                created_at=entity.created_at,
                updated_at=entity.updated_at,
                project_id=entity.project_id,
            )
        )

    async def index_entity_markdown(
        self,
        entity: Entity,
    ) -> None:
        """Index an entity and all its observations and relations.

        Indexing structure:
        1. Entities
           - permalink: direct from entity (e.g., "specs/search")
           - file_path: physical file location
           - project_id: project context for isolation

        2. Observations
           - permalink: entity permalink + /observations/id (e.g., "specs/search/observations/123")
           - file_path: parent entity's file (where observation is defined)
           - project_id: inherited from parent entity

        3. Relations (only index outgoing relations defined in this file)
           - permalink: from_entity/relation_type/to_entity (e.g., "specs/search/implements/features/search-ui")
           - file_path: source entity's file (where relation is defined)
           - project_id: inherited from source entity

        Each type gets its own row in the search index with appropriate metadata.
        The project_id is automatically added by the repository when indexing.
        """

        content_stems: list[str] = []
        content_snippet = ""
        title_variants = self._generate_variants(entity.title)
        content_stems.extend(title_variants)

        content = await self.file_service.read_entity_content(entity)
        if content:
            content_stems.append(content)
            content_snippet = f"{content[:250]}"

        if entity.permalink:
            content_stems.extend(self._generate_variants(entity.permalink))

        content_stems.extend(self._generate_variants(entity.file_path))

        # Add entity tags from frontmatter to search content
        entity_tags = self._extract_entity_tags(entity)
        if entity_tags:
            content_stems.extend(entity_tags)

        entity_content_stems = "\n".join(p for p in content_stems if p and p.strip())

        # Build metadata including tags for tag-based search filtering
        metadata: dict[str, str | list[str]] = {
            "entity_type": entity.entity_type,
        }

        if entity_tags:
            metadata["tags"] = entity_tags

        # Index entity in FTS
        await self.repository.index_item(
            SearchIndexRow(
                id=entity.id,
                type=SearchItemType.ENTITY.value,
                title=entity.title,
                content_stems=entity_content_stems,
                content_snippet=content_snippet,
                permalink=entity.permalink,
                file_path=entity.file_path,
                entity_id=entity.id,
                metadata=metadata,
                created_at=entity.created_at,
                updated_at=entity.updated_at,
                project_id=entity.project_id,
            )
        )

        # Index entity in Vector store
        if content:
            # Simple chunking: strategy - group by paragraphs, max 1000 chars
            chunks = []
            paragraphs = content.split("\n\n")
            current_chunk = ""
            for p in paragraphs:
                if len(current_chunk) + len(p) < 1000:
                    current_chunk += p + "\n\n"
                else:
                    if current_chunk:
                        chunks.append(current_chunk.strip())
                    current_chunk = p + "\n\n"
            if current_chunk:
                chunks.append(current_chunk.strip())

            vector_docs = []
            for i, chunk in enumerate(chunks):
                vector_docs.append(
                    {
                        "id": f"{entity.id}_{i}",
                        "text": f"Title: {entity.title}\n\n{chunk}",
                        "metadata": {
                            "entity_id": entity.id,
                            "type": SearchItemType.ENTITY.value,
                            "project_id": entity.project_id,
                            "title": entity.title,
                            "chunk_index": i,
                        },
                    }
                )

            if vector_docs:
                await self.vector_repository.add_documents(vector_docs)

        # Index each observation with permalink
        for obs in entity.observations:
            # Index with parent entity's file path since that's where it's defined
            obs_content_stems = "\n".join(
                p for p in self._generate_variants(obs.content) if p and p.strip()
            )
            await self.repository.index_item(
                SearchIndexRow(
                    id=obs.id,
                    type=SearchItemType.OBSERVATION.value,
                    title=f"{obs.category}: {obs.content[:100]}...",
                    content_stems=obs_content_stems,
                    content_snippet=obs.content,
                    permalink=obs.permalink,
                    file_path=entity.file_path,
                    category=obs.category,
                    entity_id=entity.id,
                    metadata={
                        "tags": obs.tags,
                    },
                    created_at=entity.created_at,
                    updated_at=entity.updated_at,
                    project_id=entity.project_id,
                )
            )

        # Only index outgoing relations (ones defined in this file)
        for rel in entity.outgoing_relations:
            # Create descriptive title showing the relationship
            relation_title = (
                f"{rel.from_entity.title} -> {rel.to_entity.title}"
                if rel.to_entity
                else f"{rel.from_entity.title}"
            )

            rel_content_stems = "\n".join(
                p for p in self._generate_variants(relation_title) if p and p.strip()
            )
            await self.repository.index_item(
                SearchIndexRow(
                    id=rel.id,
                    title=relation_title,
                    permalink=rel.permalink,
                    content_stems=rel_content_stems,
                    file_path=entity.file_path,
                    type=SearchItemType.RELATION.value,
                    entity_id=entity.id,
                    from_id=rel.from_id,
                    to_id=rel.to_id,
                    relation_type=rel.relation_type,
                    created_at=entity.created_at,
                    updated_at=entity.updated_at,
                    project_id=entity.project_id,
                )
            )

    async def delete_by_permalink(self, permalink: str) -> None:
        """Delete an item from the search index."""
        await self.repository.delete_by_permalink(permalink)

    async def delete_by_entity_id(self, entity_id: int) -> None:
        """Delete an item from the search index."""
        await self.repository.delete_by_entity_id(entity_id)

    async def handle_delete(self, entity: Entity) -> None:
        """Handle complete entity deletion from search index including observations and relations.

        This replicates the logic from sync_service.handle_delete() to properly clean up
        all search index entries for an entity and its related data.
        """
        logger.debug(
            f"Cleaning up search index for entity_id={entity.id}, file_path={entity.file_path}, "
            f"observations={len(entity.observations)}, relations={len(entity.outgoing_relations)}"
        )

        # Clean up search index - same logic as sync_service.handle_delete()
        permalinks = (
            [entity.permalink]
            + [o.permalink for o in entity.observations]
            + [r.permalink for r in entity.outgoing_relations]
        )

        logger.debug(
            f"Deleting search index entries for entity_id={entity.id}, "
            f"index_entries={len(permalinks)}"
        )

        for permalink in permalinks:
            if permalink:
                await self.delete_by_permalink(permalink)
            else:
                await self.delete_by_entity_id(entity.id)

        # Cleanup vector store
        await self.vector_repository.delete_by_entity_id(entity.id)
