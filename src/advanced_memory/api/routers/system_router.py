"""System endpoints for the webapp (logs, diagnostics)."""

import importlib.metadata
import time

import psutil
from fastapi import APIRouter

from advanced_memory.api.log_buffer import get_log_lines

router = APIRouter(prefix="/system", tags=["system"])

_start_time = time.time()


@router.get("/logs")
async def list_recent_logs(limit: int = 500) -> dict:
    """Return recent API process log lines for the Logger page."""
    data = get_log_lines(limit)
    return {"success": True, "data": data}


@router.get("/status")
async def system_status() -> dict:
    """Return system health, process info, and server metadata."""
    uptime = time.time() - _start_time
    cpu = psutil.cpu_percent(interval=0.3)
    mem = psutil.virtual_memory()
    disk = psutil.disk_usage("/")
    try:
        ver = importlib.metadata.version("advanced-memory")
    except Exception:
        ver = "0.1.0"
    return {
        "status": "ok",
        "server": "advanced-memory-mcp",
        "version": ver,
        "uptime_seconds": int(uptime),
        "cpu_percent": cpu,
        "memory": {
            "total": mem.total,
            "available": mem.available,
            "percent": mem.percent,
        },
        "disk": {
            "total": disk.total,
            "free": disk.free,
            "percent": disk.percent,
        },
    }
