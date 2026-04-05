"""Schemas for directory tree operations."""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel


class DirectoryNode(BaseModel):
    """Directory node in file system."""

    name: str
    file_path: str | None = None  # Original path without leading slash (matches DB)
    directory_path: str  # Path with leading slash for directory navigation
    type: Literal["directory", "file"]
    children: list["DirectoryNode"] = []  # Default to empty list
    title: str | None = None
    permalink: str | None = None
    entity_id: int | None = None
    entity_type: str | None = None
    content_type: str | None = None
    updated_at: datetime | None = None

    @property
    def has_children(self) -> bool:
        return bool(self.children)


# Support for recursive model
DirectoryNode.model_rebuild()


class DirectoryListPage(BaseModel):
    """Paginated flat listing from ``list_directory`` (bounded responses for large vaults)."""

    nodes: list[DirectoryNode]
    total: int
    limit: int
    offset: int
    has_more: bool
