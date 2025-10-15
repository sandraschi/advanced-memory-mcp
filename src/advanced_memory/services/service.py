"""Base service class."""

from typing import Generic, TypeVar

from advanced_memory.models import Base

T = TypeVar("T", bound=Base)


class BaseService(Generic[T]):
    """Base service that takes a repository."""

    def __init__(self, repository) -> None:  # type: ignore[no-untyped-def]
        """Initialize service with repository."""
        self.repository = repository
