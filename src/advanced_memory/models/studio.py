"""SkillStudio v1 models (isolated `studio_*` tables for clean future extraction)."""

from datetime import datetime

from sqlalchemy import Boolean, DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from advanced_memory.models.base import Base


def _utcnow() -> datetime:
    from datetime import UTC

    return datetime.now(UTC).replace(tzinfo=None)


class StudioScenario(Base):
    """One graded trigger scenario for a skill."""

    __tablename__ = "studio_scenarios"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    skill_id: Mapped[str] = mapped_column(String, nullable=False, index=True)
    prompt: Mapped[str] = mapped_column(Text, nullable=False)
    should_fire: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="1")
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=_utcnow)


class StudioRun(Base):
    """One lab eval run over a skill's scenario suite."""

    __tablename__ = "studio_runs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    skill_id: Mapped[str] = mapped_column(String, nullable=False, index=True)
    model: Mapped[str] = mapped_column(String, nullable=False, server_default="")
    precision: Mapped[float] = mapped_column(nullable=False, server_default="0")
    recall: Mapped[float] = mapped_column(nullable=False, server_default="0")
    verdicts_json: Mapped[str] = mapped_column(Text, nullable=False, server_default="[]")
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=_utcnow)


class StudioEvent(Base):
    """Door telemetry: skill activations and staged loads (identifiers only)."""

    __tablename__ = "studio_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    skill_id: Mapped[str] = mapped_column(String, nullable=False, index=True)
    event: Mapped[str] = mapped_column(String, nullable=False)  # activate|load_section|load_resource
    section: Mapped[str | None] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=_utcnow)


class StudioDistillJob(Base):
    """Q&A/note/issue distillation job with approval gate."""

    __tablename__ = "studio_distill_jobs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    skill_id: Mapped[str] = mapped_column(String, nullable=False, index=True)
    source: Mapped[str] = mapped_column(String, nullable=False)  # discussion:<n>|issue:<n>|note:<permalink>
    draft_md: Mapped[str] = mapped_column(Text, nullable=False, server_default="")
    state: Mapped[str] = mapped_column(String, nullable=False, server_default="pending")
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=_utcnow)
