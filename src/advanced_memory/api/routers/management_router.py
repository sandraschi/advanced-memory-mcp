"""Management router for advanced-memory API."""

import asyncio
from pathlib import Path

from fastapi import APIRouter, Request
from loguru import logger
from pydantic import BaseModel, Field

from advanced_memory.config import ConfigManager
from advanced_memory.deps import ProjectRepositoryDep, SyncServiceDep
from advanced_memory.services.sync_status_service import sync_status_tracker

router = APIRouter(prefix="/management", tags=["management"])


class RagExtraRootsPayload(BaseModel):
    """Paths on the API server machine to include in LanceDB on the next full reindex."""

    paths: list[str] = Field(default_factory=list)


class WatchStatusResponse(BaseModel):
    """Response model for watch status."""

    running: bool
    """Whether the watch service is currently running."""


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


@router.get("/watch/status", response_model=WatchStatusResponse)
async def get_watch_status(request: Request) -> WatchStatusResponse:
    """Get the current status of the watch service."""
    watch_task = getattr(request.app.state, "watch_task", None)
    return WatchStatusResponse(running=watch_task is not None and not watch_task.done())


@router.post("/watch/start", response_model=WatchStatusResponse)
async def start_watch_service(
    request: Request, project_repository: ProjectRepositoryDep, sync_service: SyncServiceDep
) -> WatchStatusResponse:
    """Start the watch service if it's not already running."""

    # needed because of circular imports from sync -> app
    from advanced_memory.sync import WatchService
    from advanced_memory.sync.background_sync import create_background_sync_task

    watch_existing = getattr(request.app.state, "watch_task", None)
    if watch_existing is not None and not watch_existing.done():
        # Watch service is already running
        return WatchStatusResponse(running=True)

    app_config = ConfigManager().config

    # Create and start a new watch service
    logger.info("Starting watch service via management API")

    # Get services needed for the watch task
    watch_service = WatchService(
        app_config=app_config,
        project_repository=project_repository,
    )

    # Create and store the task
    watch_task = create_background_sync_task(sync_service, watch_service)
    request.app.state.watch_task = watch_task

    return WatchStatusResponse(running=True)


@router.post("/watch/stop", response_model=WatchStatusResponse)
async def stop_watch_service(request: Request) -> WatchStatusResponse:  # pragma: no cover
    """Stop the watch service if it's running."""
    watch_task = getattr(request.app.state, "watch_task", None)
    if watch_task is None or watch_task.done():
        # Watch service is not running
        return WatchStatusResponse(running=False)

    # Cancel the running task
    logger.info("Stopping watch service via management API")
    watch_task.cancel()

    # Wait for it to be properly cancelled
    try:
        await watch_task
    except asyncio.CancelledError:
        pass

    request.app.state.watch_task = None
    return WatchStatusResponse(running=False)


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
    except Exception:
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
