"""Door telemetry: log skill activations and staged loads (identifiers only)."""

from __future__ import annotations

import os

from loguru import logger

from advanced_memory.skills.studio import repository


def enabled() -> bool:
    """Default on locally; set ADN_SKILLS_TELEMETRY=0 to silence."""
    return os.getenv("ADN_SKILLS_TELEMETRY", "1") != "0"


async def log_event(skill_id: str, event: str, section: str | None = None) -> None:
    """Best-effort telemetry write. Never breaks the calling operation."""
    if not enabled() or not skill_id:
        return
    try:
        await repository.event_log(skill_id=str(skill_id), event=event, section=section)
    except Exception as exc:
        logger.debug(f"studio telemetry skipped: {exc}")
