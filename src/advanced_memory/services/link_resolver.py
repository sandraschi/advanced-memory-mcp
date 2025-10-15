"""Service for resolving markdown links to permalinks."""


from loguru import logger

from advanced_memory.models import Entity
from advanced_memory.repository.entity_repository import EntityRepository
from advanced_memory.schemas.search import SearchItemType, SearchQuery
from advanced_memory.services.search_service import SearchService


class LinkResolver:
    """Service for resolving markdown links to permalinks.

    Uses a combination of exact matching and search-based resolution:
    1. Try exact permalink match (fastest)
    2. Try exact title match
    3. Try exact file path match
    4. Try file path with .md extension (for folder/title patterns)
    5. Fall back to search for fuzzy matching
    """

    def __init__(self, entity_repository: EntityRepository, search_service: SearchService):
        """Initialize with repositories."""
        self.entity_repository = entity_repository
        self.search_service = search_service

    async def resolve_link(
        self, link_text: str, use_search: bool = True, strict: bool = False
    ) -> Entity | None:
        """Resolve a markdown link to a permalink.

        Args:
            link_text: The link text to resolve
            use_search: Whether to use search-based fuzzy matching as fallback
            strict: If True, only exact matches are allowed (no fuzzy search fallback)
        """
        logger.trace(f"Resolving link: {link_text}")

        # Clean link text and extract any alias
        clean_text, alias = self._normalize_link_text(link_text)

        # 1. Try exact permalink match first (most efficient)
        entity = await self.entity_repository.get_by_permalink(clean_text)
        if entity:
            logger.debug(f"Found exact permalink match: {entity.permalink}")
            return entity

        # 2. Try exact title match
        found = await self.entity_repository.get_by_title(clean_text)
        if found:
            # Return first match if there are duplicates (consistent behavior)
            entity = found[0]
            logger.debug(f"Found title match: {entity.title}")
            return entity

        # 3. Try file path
        found_path = await self.entity_repository.get_by_file_path(clean_text)
        if found_path:
            logger.debug(f"Found entity with path: {found_path.file_path}")
            return found_path

        # 4. Try file path with .md extension if not already present
        if not clean_text.endswith(".md") and "/" in clean_text:
            # Try different variations of the file path
            variations = [
                f"{clean_text}.md",  # Original with .md
                f"{clean_text.replace(' ', '_')}.md",  # Spaces to underscores with .md
            ]

            # Also try converting the last part (filename) to underscore format
            if "/" in clean_text:
                parts = clean_text.split("/")
                if len(parts) > 1:
                    # Convert only the last part (filename) to underscore format
                    last_part = parts[-1].replace(" ", "_")
                    folder_path = "/".join(parts[:-1])
                    variations.append(f"{folder_path}/{last_part}.md")

            # Normalize path separators for cross-platform compatibility
            from advanced_memory.sync.sync_service import normalize_file_path

            for file_path_variant in variations:
                file_path_normalized = normalize_file_path(file_path_variant)
                logger.debug(f"Trying to find entity with normalized path: {file_path_normalized}")
                found_path_md = await self.entity_repository.get_by_file_path(file_path_normalized)
                if found_path_md:
                    logger.debug(f"Found entity with path (with .md): {found_path_md.file_path}")
                    return found_path_md
                else:
                    logger.debug(f"No entity found with path: {file_path_normalized}")
                    # Try case-insensitive search by looking up all entities and matching file paths
                    # This handles cases where the input case doesn't match the stored case
                    all_entities: Sequence[Entity] = await self.entity_repository.find_all()
                    for entity in all_entities:
                        if entity.file_path and entity.file_path.lower() == file_path_normalized.lower():
                            logger.debug(f"Found entity with case-insensitive path match: {entity.file_path}")
                            return entity

        # In strict mode, don't try fuzzy search - return None if no exact match found
        if strict:
            return None

        # 5. Fall back to search for fuzzy matching (only if not in strict mode)
        if use_search and "*" not in clean_text:
            results = await self.search_service.search(
                query=SearchQuery(text=clean_text, entity_types=[SearchItemType.ENTITY]),
            )

            if results:
                # Look for best match
                best_match = min(results, key=lambda x: x.score)  # pyright: ignore
                logger.trace(
                    f"Selected best match from {len(results)} results: {best_match.permalink}"
                )
                if best_match.permalink:
                    return await self.entity_repository.get_by_permalink(best_match.permalink)

        # if we couldn't find anything then return None
        return None

    def _normalize_link_text(self, link_text: str) -> tuple[str, str | None]:
        """Normalize link text and extract alias if present.

        Args:
            link_text: Raw link text from markdown

        Returns:
            Tuple of (normalized_text, alias or None)
        """
        # Strip whitespace
        text = link_text.strip()

        # Remove enclosing brackets if present
        if text.startswith("[[") and text.endswith("]]"):
            text = text[2:-2]

        # Handle Obsidian-style aliases (format: [[actual|alias]])
        alias = None
        if "|" in text:
            text, alias = text.split("|", 1)
            text = text.strip()
            alias = alias.strip()
        else:
            # Strip whitespace from text even if no alias
            text = text.strip()

        # Normalize path separators for cross-platform compatibility
        text = text.replace("\\", "/")

        return text, alias
