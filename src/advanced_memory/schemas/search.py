"""Search schemas for Advanced Memory.

The search system supports three primary modes:
1. Exact permalink lookup
2. Pattern matching with *
3. Full-text search across content
"""

from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, field_validator

from advanced_memory.schemas.base import Permalink


class SearchItemType(StrEnum):
    """Types of searchable items."""

    ENTITY = "entity"
    OBSERVATION = "observation"
    RELATION = "relation"


class SearchQuery(BaseModel):
    """Search query parameters.

    Use ONE of these primary search modes:
    - permalink: Exact permalink match
    - permalink_match: Path pattern with *
    - text: Full-text search of title/content (supports boolean operators: AND, OR, NOT)

    Optionally filter results by:
    - types: Limit to specific item types
    - entity_types: Limit to specific entity types
    - after_date: Only items after date

    Boolean search examples:
    - "python AND flask" - Find items with both terms
    - "python OR django" - Find items with either term
    - "python NOT django" - Find items with python but not django
    - "(python OR flask) AND web" - Use parentheses for grouping
    """

    # Primary search modes (use ONE of these)
    permalink: str | None = None  # Exact permalink match
    permalink_match: str | None = None  # Glob permalink match
    text: str | None = None  # Full-text search (now supports boolean operators)
    title: str | None = None  # title only search

    # Optional filters
    types: list[str] | None = None  # Filter by type
    entity_types: list[SearchItemType] | None = None  # Filter by entity type
    after_date: datetime | str | None = None  # Time-based filter (from this date/time)
    before_date: datetime | str | None = None  # Time-based filter (until this date/time)
    tags: list[str] | None = None  # Filter by tags (notes must have ALL specified tags)

    @field_validator("after_date", "before_date")
    @classmethod
    def validate_date(cls, v: datetime | str | None) -> str | None:
        """Convert datetime to ISO format if needed."""
        if isinstance(v, datetime):
            return v.isoformat()
        return v

    def no_criteria(self) -> bool:
        return (
            self.permalink is None
            and self.permalink_match is None
            and self.title is None
            and self.text is None
            and self.after_date is None
            and self.before_date is None
            and self.types is None
            and self.entity_types is None
            and self.tags is None
        )

    def has_boolean_operators(self) -> bool:
        """Check if the text query contains boolean operators (AND, OR, NOT)."""
        if not self.text:  # pragma: no cover
            return False

        # Check for common boolean operators with correct word boundaries
        # to avoid matching substrings like "GRAND" containing "AND"
        boolean_patterns = [" AND ", " OR ", " NOT ", "(", ")"]
        text = f" {self.text} "  # Add spaces to ensure we match word boundaries
        return any(pattern in text for pattern in boolean_patterns)


class SearchResult(BaseModel):
    """Search result with score and metadata."""

    title: str
    type: SearchItemType
    score: float
    entity: Permalink | None = None
    permalink: str | None
    content: str | None = None
    file_path: str

    metadata: dict | None = None
    created_at: str | None = None
    updated_at: str | None = None

    # Type-specific fields
    category: str | None = None  # For observations
    from_entity: Permalink | None = None  # For relations
    to_entity: Permalink | None = None  # For relations
    relation_type: str | None = None  # For relations


class SearchResponse(BaseModel):
    """Wrapper for search results."""

    results: list[SearchResult]
    current_page: int
    page_size: int
    total_results: int


class SemanticSearchRequest(BaseModel):
    """Request body for semantic (vector) search."""

    query: str
    limit: int = 20


class SemanticChunkResult(BaseModel):
    """Single chunk from semantic search for UI."""

    entity_id: int
    permalink: str | None
    title: str
    snippet: str
    chunk_text: str
    score: float


class SemanticSearchResponse(BaseModel):
    """Response for semantic search chunks."""

    chunks: list[SemanticChunkResult]
