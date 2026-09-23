"""Management router for advanced-memory API."""

import asyncio
import json
from datetime import UTC, datetime
from pathlib import Path

from fastapi import APIRouter, Request
from loguru import logger
from pydantic import BaseModel, Field

from advanced_memory.config import WATCH_STATUS_JSON, ConfigManager
from advanced_memory.services.sync_status_service import sync_status_tracker

router = APIRouter(prefix="/management", tags=["management"])

# A running watcher that hasn't scanned in this long is presumed wedged, not idle.
WATCH_STALE_THRESHOLD_SECONDS = 900  # 15 minutes


class RagExtraRootsPayload(BaseModel):
    """Paths on the API server machine to include in LanceDB on the next full reindex."""

    paths: list[str] = Field(default_factory=list)


class WatchStatusResponse(BaseModel):
    """Response model for watch status."""

    running: bool
    """Whether the watch service is currently running (in-process asyncio task check)."""

    start_time: str | None = None
    """When the watch service (re)started, from watch-status.json."""

    last_scan: str | None = None
    """Timestamp of the most recent filesystem scan, from watch-status.json."""

    synced_files: int = 0
    """Files synced in the most recent scan."""

    error_count: int = 0
    """Cumulative watch-service error count since start_time."""

    last_error: str | None = None
    """Most recent watch-service error message, if any."""

    stale: bool = False
    """True when running=true but last_scan is older than the stale threshold -
    the watcher process is alive but not actually making progress (the exact
    failure mode that let a reindex sit stalled for 5+ hours with no visible sign)."""

    recent_events: list[dict] = Field(default_factory=list)
    """Last few filesystem sync events (path, action, status, timestamp)."""


def _read_watch_status_file() -> dict:
    """Read watch-status.json if present; returns {} on any error (missing/corrupt file
    should degrade the KPI display, not break the status endpoint)."""
    try:
        status_file = Path.home() / ".advanced-memory" / WATCH_STATUS_JSON
        if not status_file.exists():
            return {}
        with open(status_file, encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:  # pragma: no cover
        logger.warning(f"Could not read watch-status.json: {e}")
        return {}


def _is_stale(running: bool, last_scan: str | None) -> bool:
    if not running or not last_scan:
        return False
    try:
        last_scan_dt = datetime.fromisoformat(last_scan.replace("Z", "+00:00"))
        if last_scan_dt.tzinfo is None:
            last_scan_dt = last_scan_dt.replace(tzinfo=UTC)
        age_seconds = (datetime.now(UTC) - last_scan_dt).total_seconds()
        return age_seconds > WATCH_STALE_THRESHOLD_SECONDS
    except Exception:  # pragma: no cover
        return False


@router.get("/sync/status")
async def get_file_sync_status() -> dict:
    """Live filesystem sync progress (updated during ``POST /projects/{name}/sync``)."""
    projects: list[dict] = []
    for name, ps in sync_status_tracker.get_all_projects().items():
        pct: float | None = None
        if ps.files_total > 0:
            pct = round((ps.files_processed / ps.files_total) * 100, 1)
        projects.append(
            {
                "project_name": name,
                "status": ps.status.value,
                "message": ps.message,
                "files_processed": ps.files_processed,
                "files_total": ps.files_total,
                "percent": pct,
                "error": ps.error,
            }
        )
    return {
        "global_status": sync_status_tracker.global_status.value,
        "is_syncing": sync_status_tracker.is_syncing,
        "projects": projects,
    }


def _build_watch_status_response(running: bool) -> WatchStatusResponse:
    """Merge the live in-process running check with watch-status.json's history,
    so the API (and every UI/tool built on it) can tell 'alive and stuck' apart
    from 'alive and working' instead of just reporting a bare running flag."""
    data = _read_watch_status_file()
    last_scan = data.get("last_scan")
    return WatchStatusResponse(
        running=running,
        start_time=data.get("start_time"),
        last_scan=last_scan,
        synced_files=data.get("synced_files", 0),
        error_count=data.get("error_count", 0),
        last_error=data.get("last_error"),
        stale=_is_stale(running, last_scan),
        recent_events=data.get("recent_events", [])[-5:],
    )


def _get_sync_task(request: Request) -> asyncio.Task | None:
    # BUG (fixed): this used to read/write a separate `app.state.watch_task` that
    # nothing else in the app ever touched. The real watcher started at boot is
    # `app.state.sync_task` (see lifespan() in api/app.py, initialize_file_sync).
    # `watch_task` was always None unless this router itself set it, which it could
    # never do without a 422 (start_watch_service's dependency chain pulled in a
    # project-scoped repository that needs a {project} path param this route
    # doesn't have) - so Start/Stop/Status here were watching a phantom that was
    # permanently disconnected from the process actually indexing the vault.
    return getattr(request.app.state, "sync_task", None)


@router.get("/watch/status", response_model=WatchStatusResponse)
async def get_watch_status(request: Request) -> WatchStatusResponse:
    """Get the current status of the watch service."""
    sync_task = _get_sync_task(request)
    running = sync_task is not None and not sync_task.done()
    return _build_watch_status_response(running)


@router.post("/watch/start", response_model=WatchStatusResponse)
async def start_watch_service(request: Request) -> WatchStatusResponse:
    """Start the watch service if it's not already running."""
    from advanced_memory.services.initialization import initialize_file_sync
    from advanced_memory.utils.task_logging import attach_task_failure_logging

    existing = _get_sync_task(request)
    if existing is not None and not existing.done():
        # Watch service is already running
        return _build_watch_status_response(True)

    app_config = ConfigManager().config

    logger.info("Starting watch service via management API")
    sync_task = asyncio.create_task(
        initialize_file_sync(app_config),
        name="api_initialize_file_sync",
    )
    attach_task_failure_logging(sync_task, "api_initialize_file_sync")
    request.app.state.sync_task = sync_task

    return _build_watch_status_response(True)


@router.post("/watch/stop", response_model=WatchStatusResponse)
async def stop_watch_service(request: Request) -> WatchStatusResponse:  # pragma: no cover
    """Stop the watch service if it's running."""
    sync_task = _get_sync_task(request)
    if sync_task is None or sync_task.done():
        # Watch service is not running
        return _build_watch_status_response(False)

    # Cancel the running task
    logger.info("Stopping watch service via management API")
    sync_task.cancel()

    # Wait for it to be properly cancelled
    try:
        await sync_task
    except asyncio.CancelledError:
        logger.debug("Sync task cancelled via API")  # expected path, not an error
        pass

    request.app.state.sync_task = None
    return _build_watch_status_response(False)


@router.get("/llm-config")
async def get_llm_config():
    """Current persisted LLM provider/model selection (2026-07-17, backs LLMProviderSettings page)."""
    from advanced_memory.config import ConfigManager

    config = ConfigManager().load_config()
    return {"provider": config.llm_provider, "model": config.llm_model}


@router.put("/llm-config")
async def put_llm_config(request: Request):
    """Persist LLM provider/model selection to config.json and live session state."""
    body = await request.json()
    from advanced_memory.config import ConfigManager

    cm = ConfigManager()
    config = cm.load_config()
    config.llm_provider = (body.get("provider") or "").strip() or None
    config.llm_model = (body.get("model") or "").strip() or None
    cm.save_config(config)
    # Update in-session globals so an already-imported adn_llm sees the change immediately
    try:
        from advanced_memory.mcp.tools import adn_llm as _adn_llm_mod

        _adn_llm_mod._current_provider = config.llm_provider
        _adn_llm_mod._current_model = config.llm_model
    except Exception as e:
        logger.debug(f"Live adn_llm session update skipped: {e}")
        pass
    return {"success": True, "provider": config.llm_provider, "model": config.llm_model}


@router.get("/skills-inventory")
async def get_skills_inventory():
    """Skill catalog scan (2026-07-17, backs webapp skill pages).

    Top-level dirs in ~/.claude/skills are Claude-discoverable; category dirs
    hold nested sub-skills reachable via doorified hub SKILL.md files.
    """
    from pathlib import Path

    root = Path.home() / ".claude" / "skills"
    skills = []
    if root.is_dir():
        for d in sorted(root.iterdir()):
            if not d.is_dir() or d.name == "_archive":
                continue
            md = d / "SKILL.md"
            nested = sorted(c.name for c in d.iterdir() if c.is_dir() and (c / "SKILL.md").exists())
            if md.exists():
                skills.append(
                    {
                        "name": d.name,
                        "kind": "category-hub" if nested else "skill",
                        "size": md.stat().st_size,
                        "sub_skills": nested,
                    }
                )
    return {"root": str(root), "count": len(skills), "skills": skills}


@router.post("/skills-generate")
async def post_skills_generate(request: Request):
    """Research-first skill generation via make_skill_advanced (2026-07-17).

    Writes the finished skill to ~/.claude/skills/<slug> (top level, so Claude
    Code discovers it immediately). Takes ~15-40s with a local model.
    """
    import re
    from pathlib import Path

    body = await request.json()
    topic = (body.get("topic") or "").strip()
    if not topic:
        return {"success": False, "error": "topic required"}

    slug = (body.get("skill_name") or "").strip()
    if not slug:
        slug = re.sub(r"[^a-z0-9]+", "-", topic.lower())[:64].strip("-")
        slug = re.sub(r"-+", "-", slug)

    from advanced_memory.mcp.tools.make_skill_advanced import make_skill_advanced

    fn = getattr(make_skill_advanced, "fn", make_skill_advanced)
    root = Path.home() / ".claude" / "skills"
    result = await fn(
        operation="research_first_create",
        topic=topic,
        skill_name=slug,
        output_path=str(root),
        research_sources=body.get("sources") or ["web"],
        max_research_iterations=int(body.get("max_iterations") or 1),
        enable_review_loop=True,
    )
    if isinstance(result, dict) and result.get("success"):
        md = Path(result.get("skill_path", "")) / "SKILL.md"
        if md.exists():
            result["skill_content"] = md.read_text(encoding="utf-8", errors="replace")
    return result


@router.get("/rag-extra-roots")
async def get_rag_extra_roots() -> dict:
    """Configured LanceDB extra document roots (server paths)."""
    cfg = ConfigManager().load_config()
    return {"success": True, "data": {"paths": list(cfg.rag_extra_roots)}}


@router.put("/rag-extra-roots")
async def put_rag_extra_roots(body: RagExtraRootsPayload) -> dict:
    """Replace the list of extra RAG folder paths; persists to config.json."""
    cm = ConfigManager()
    cfg = cm.load_config()
    cleaned: list[str] = []
    seen: set[str] = set()
    for raw in body.paths:
        s = (raw or "").strip()
        if not s or s in seen:
            continue
        seen.add(s)
        cleaned.append(s)
    cfg.rag_extra_roots = cleaned
    cm.save_config(cfg)
    logger.info("Updated rag_extra_roots: {} path(s)", len(cleaned))
    return {"success": True, "data": {"paths": cleaned}}


@router.post("/rag-extra-roots/validate")
async def validate_rag_extra_roots(body: RagExtraRootsPayload) -> dict:
    """Check which paths exist as directories on the API host."""
    items: list[dict] = []
    for raw in body.paths:
        s = (raw or "").strip()
        if not s:
            continue
        p = Path(s)
        try:
            ok = p.is_dir()
            resolved = str(p.resolve()) if ok else str(p)
        except OSError as e:
            ok = False
            resolved = str(p)
            items.append({"path": s, "ok": False, "resolved": resolved, "error": str(e)})
            continue
        items.append({"path": s, "ok": ok, "resolved": resolved})
    return {"success": True, "data": {"items": items}}
