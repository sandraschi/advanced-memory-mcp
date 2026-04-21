"""System endpoints for the webapp (logs, diagnostics)."""

from fastapi import APIRouter

from advanced_memory.api.log_buffer import get_log_lines

router = APIRouter(prefix="/system", tags=["system"])


@router.get("/logs")
async def list_recent_logs(limit: int = 500) -> dict:
    """Return recent API process log lines for the Logger page."""
    data = get_log_lines(limit)
    return {"success": True, "data": data}
