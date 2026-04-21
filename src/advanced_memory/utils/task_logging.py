"""Attach logging to asyncio.Task completion so failures are never silent."""

from __future__ import annotations

import asyncio
import traceback
from collections.abc import Callable
from typing import Any

from loguru import logger


def attach_task_failure_logging(task: asyncio.Task[Any], name: str) -> asyncio.Task[Any]:
    """Log cancellation, success, or failure when the task finishes.

    Use on every ``create_task`` that is not ``await``ed (fire-and-forget or long-running).
    """

    def _done(t: asyncio.Task[Any]) -> None:
        try:
            if t.cancelled():
                logger.info("Background task {!r} cancelled (shutdown or explicit cancel)", name)
                return
            exc = t.exception()
            if exc is None:
                logger.info("Background task {!r} completed normally", name)
                return
            tb = "".join(traceback.format_exception(type(exc), exc, exc.__traceback__))
            logger.error(
                "Background task {!r} exited with {}: {}\n{}",
                name,
                type(exc).__name__,
                exc,
                tb,
            )
        except Exception as cb_err:  # pragma: no cover — defensive
            logger.exception("Bug in task done-callback for {!r}: {}", name, cb_err)

    task.add_done_callback(_done)
    return task


def chain_asyncio_exception_handler(
    previous: Callable[[asyncio.AbstractEventLoop, dict[str, Any]], None] | None,
) -> Callable[[asyncio.AbstractEventLoop, dict[str, Any]], None]:
    """Return a handler that logs ``asyncio`` context errors then delegates."""

    def _handler(loop: asyncio.AbstractEventLoop, context: dict[str, Any]) -> None:
        msg = context.get("message", "")
        exc = context.get("exception")
        task = context.get("task")
        task_name = "unknown"
        if task is not None:
            try:
                task_name = task.get_name()
            except (AttributeError, TypeError):
                task_name = repr(task)
        if exc is not None:
            tb = "".join(traceback.format_exception(type(exc), exc, exc.__traceback__))
            logger.error(
                "asyncio exception context: {} | task={} | {}: {}\n{}",
                msg,
                task_name,
                type(exc).__name__,
                exc,
                tb,
            )
        else:
            logger.error("asyncio error context (no exception): {} | {}", msg, context)

        if previous is not None:
            previous(loop, context)
        else:
            try:
                loop.default_exception_handler(context)
            except AttributeError:
                pass

    return _handler
