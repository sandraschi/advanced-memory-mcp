"""Skill model for Claude Skills integration."""

from datetime import datetime

from sqlalchemy import Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from advanced_memory.models.base import Base


class Skill(Base):
    """Claude Skill model."""

    __tablename__ = "skills"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False, unique=True, index=True)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    entity_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("entity.id"), nullable=True, index=True
    )
    version: Mapped[str] = mapped_column(String, nullable=False, server_default="1.0.0")
    category: Mapped[str | None] = mapped_column(String, nullable=True, index=True)
    difficulty: Mapped[str | None] = mapped_column(String, nullable=True)
    license: Mapped[str | None] = mapped_column(String, nullable=True)
    allowed_tools: Mapped[str | None] = mapped_column(Text, nullable=True)  # JSON array
    custom_metadata: Mapped[str | None] = mapped_column(Text, nullable=True)  # JSON object
    usage_count: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    effectiveness_rating: Mapped[float | None] = mapped_column(Float, nullable=True)
    created_at: Mapped[datetime] = mapped_column(nullable=False)
    updated_at: Mapped[datetime] = mapped_column(nullable=False)

    def __repr__(self) -> str:
        """String representation."""
        return f"<Skill(name='{self.name}', category='{self.category}')>"
