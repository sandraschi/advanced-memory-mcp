"""Studio persistence: CRUD over the isolated studio_* tables."""

from __future__ import annotations

import json
from datetime import datetime
from typing import Any

from sqlalchemy import delete, desc, func, select

from advanced_memory import db
from advanced_memory.config import ConfigManager
from advanced_memory.models.studio import StudioDistillJob, StudioEvent, StudioRun, StudioScenario


def _utcnow() -> datetime:
    from datetime import UTC

    return datetime.now(UTC).replace(tzinfo=None)


def _norm_skill_id(skill_id: str | None) -> str | None:
    """Normalize skill identifiers (Windows slash direction) so lab runs,
    telemetry, and the UI agree on one key per skill."""
    if skill_id is None:
        return None
    return skill_id.replace("/", "\\")


async def _session_maker():  # type: ignore[no-untyped-def]
    app_config = ConfigManager().load_config()
    _, session_maker = await db.get_or_create_db(app_config.database_path)
    return session_maker


def _row_to_dict(row: Any, fields: list[str]) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for f in fields:
        v = getattr(row, f, None)
        out[f] = v.isoformat() if isinstance(v, datetime) else v
    return out


_SCENARIO_FIELDS = ["id", "skill_id", "prompt", "should_fire", "notes", "created_at"]
_RUN_FIELDS = ["id", "skill_id", "model", "precision", "recall", "verdicts_json", "created_at"]
_EVENT_FIELDS = ["id", "skill_id", "event", "section", "created_at"]
_JOB_FIELDS = ["id", "skill_id", "source", "draft_md", "state", "created_at"]


async def scenario_create(skill_id: str, prompt: str, should_fire: bool, notes: str | None = None) -> dict[str, Any]:
    skill_id = _norm_skill_id(skill_id) or skill_id
    sm = await _session_maker()
    async with sm() as session:
        row = StudioScenario(
            skill_id=skill_id, prompt=prompt, should_fire=should_fire, notes=notes, created_at=_utcnow()
        )
        session.add(row)
        await session.commit()
        await session.refresh(row)
        return _row_to_dict(row, _SCENARIO_FIELDS)


async def scenario_list(skill_id: str | None = None) -> list[dict[str, Any]]:
    skill_id = _norm_skill_id(skill_id)
    sm = await _session_maker()
    async with sm() as session:
        stmt = select(StudioScenario).order_by(StudioScenario.id)
        if skill_id:
            stmt = stmt.where(StudioScenario.skill_id == skill_id)
        rows = (await session.execute(stmt)).scalars().all()
        return [_row_to_dict(r, _SCENARIO_FIELDS) for r in rows]


async def scenario_delete(scenario_id: int) -> bool:
    sm = await _session_maker()
    async with sm() as session:
        res = await session.execute(delete(StudioScenario).where(StudioScenario.id == scenario_id))
        await session.commit()
        return (res.rowcount or 0) > 0


async def run_record(
    skill_id: str, model: str, precision: float, recall: float, verdicts: list[dict[str, Any]]
) -> dict[str, Any]:
    skill_id = _norm_skill_id(skill_id) or skill_id
    sm = await _session_maker()
    async with sm() as session:
        row = StudioRun(
            skill_id=skill_id,
            model=model,
            precision=precision,
            recall=recall,
            verdicts_json=json.dumps(verdicts),
            created_at=_utcnow(),
        )
        session.add(row)
        await session.commit()
        await session.refresh(row)
        return _row_to_dict(row, _RUN_FIELDS)


async def run_history(skill_id: str, limit: int = 10) -> list[dict[str, Any]]:
    skill_id = _norm_skill_id(skill_id) or skill_id
    sm = await _session_maker()
    async with sm() as session:
        stmt = select(StudioRun).where(StudioRun.skill_id == skill_id).order_by(desc(StudioRun.id)).limit(limit)
        rows = (await session.execute(stmt)).scalars().all()
        out = [_row_to_dict(r, _RUN_FIELDS) for r in rows]
        for item in out:
            try:
                item["verdicts"] = json.loads(item.pop("verdicts_json", "[]"))
            except (ValueError, TypeError):
                item["verdicts"] = []
        return out


async def event_log(skill_id: str, event: str, section: str | None = None) -> None:
    skill_id = _norm_skill_id(skill_id) or skill_id
    sm = await _session_maker()
    async with sm() as session:
        session.add(StudioEvent(skill_id=skill_id, event=event, section=section, created_at=_utcnow()))
        await session.commit()


async def event_list(skill_id: str | None = None, since: str | None = None, limit: int = 200) -> list[dict[str, Any]]:
    skill_id = _norm_skill_id(skill_id)
    sm = await _session_maker()
    async with sm() as session:
        stmt = select(StudioEvent).order_by(desc(StudioEvent.id)).limit(limit)
        if skill_id:
            stmt = stmt.where(StudioEvent.skill_id == skill_id)
        if since:
            try:
                stmt = stmt.where(StudioEvent.created_at >= datetime.fromisoformat(since))
            except ValueError:
                pass
        rows = (await session.execute(stmt)).scalars().all()
        return [_row_to_dict(r, _EVENT_FIELDS) for r in rows]


async def event_counts(skill_id: str | None = None) -> dict[str, int]:
    skill_id = _norm_skill_id(skill_id)
    sm = await _session_maker()
    async with sm() as session:
        stmt = select(StudioEvent.event, func.count()).group_by(StudioEvent.event)
        if skill_id:
            stmt = stmt.where(StudioEvent.skill_id == skill_id)
        return {str(k): int(v) for k, v in (await session.execute(stmt)).all()}


async def job_create(skill_id: str, source: str, draft_md: str) -> dict[str, Any]:
    skill_id = _norm_skill_id(skill_id) or skill_id
    sm = await _session_maker()
    async with sm() as session:
        row = StudioDistillJob(
            skill_id=skill_id, source=source, draft_md=draft_md, state="pending", created_at=_utcnow()
        )
        session.add(row)
        await session.commit()
        await session.refresh(row)
        return _row_to_dict(row, _JOB_FIELDS)


async def job_list(state: str | None = None, limit: int = 50) -> list[dict[str, Any]]:
    sm = await _session_maker()
    async with sm() as session:
        stmt = select(StudioDistillJob).order_by(desc(StudioDistillJob.id)).limit(limit)
        if state:
            stmt = stmt.where(StudioDistillJob.state == state)
        rows = (await session.execute(stmt)).scalars().all()
        return [_row_to_dict(r, _JOB_FIELDS) for r in rows]


async def job_get(job_id: int) -> dict[str, Any] | None:
    sm = await _session_maker()
    async with sm() as session:
        row = await session.get(StudioDistillJob, job_id)
        return _row_to_dict(row, _JOB_FIELDS) if row else None


async def job_set_state(job_id: int, state: str, draft_md: str | None = None) -> bool:
    sm = await _session_maker()
    async with sm() as session:
        row = await session.get(StudioDistillJob, job_id)
        if row is None:
            return False
        row.state = state
        if draft_md is not None:
            row.draft_md = draft_md
        await session.commit()
        return True
