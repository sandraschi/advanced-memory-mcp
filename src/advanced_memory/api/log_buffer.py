"""In-memory ring buffer of log lines for the webapp logger page."""

from __future__ import annotations

from collections import deque
from threading import Lock
from typing import Any

from loguru import logger

_BUFFER: deque[dict[str, Any]] = deque(maxlen=2000)
_LOCK = Lock()
_SINK_ID: int | None = None


def _sink(message: Any) -> None:
    rec = message.record
    ts = rec["time"].strftime("%Y-%m-%d %H:%M:%S")
    level = rec["level"].name
    if level == "TRACE":
        level = "DEBUG"
    if level not in ("ERROR", "WARNING", "INFO", "SUCCESS", "DEBUG"):
        level = "INFO"
    name = rec["name"] or "app"
    line = {
        "timestamp": ts,
        "level": level,
        "message": str(rec["message"]),
        "source": name,
    }
    with _LOCK:
        _BUFFER.append(line)


def install_api_log_buffer_sink() -> None:
    """Attach a loguru sink once so GET /api/v1/system/logs can return recent lines."""
    global _SINK_ID
    if _SINK_ID is not None:
        return
    _SINK_ID = logger.add(_sink, level="DEBUG", enqueue=True)


def get_log_lines(limit: int) -> list[dict[str, Any]]:
    """Return up to `limit` most recent lines (oldest first)."""
    cap = max(1, min(limit, 2000))
    with _LOCK:
        snap = list(_BUFFER)
    return snap[-cap:]
