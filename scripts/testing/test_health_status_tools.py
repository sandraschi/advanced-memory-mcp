"""Exercise health, status, and sync oriented tools."""

from __future__ import annotations

import asyncio
import json
from collections.abc import Awaitable, Callable, Iterable
from dataclasses import dataclass
from textwrap import shorten
from typing import Any

from loguru import logger

from advanced_memory.mcp.project_session import session
from advanced_memory.mcp.tools import adn_navigation, adn_project

ToolCallable = Callable[..., Awaitable[Any]]


@dataclass(slots=True)
class ToolTest:
    label: str
    tool: ToolCallable
    kwargs: dict[str, Any]


def serialize_result(result: Any) -> str:
    if isinstance(result, dict | list):
        try:
            payload = json.dumps(result, indent=2, ensure_ascii=False)
        except TypeError:
            payload = repr(result)
    else:
        payload = str(result)
    payload = payload.replace("\n", " ").replace("\r", " ")
    safe = payload.encode("cp1252", "replace").decode("cp1252")
    return shorten(safe, width=200, placeholder=" …")


async def run_test(test: ToolTest) -> tuple[str, str, bool]:
    try:
        logger.debug(f"Executing {test.label} kwargs={test.kwargs}")
        outcome = await test.tool(**test.kwargs)
        return (test.label, serialize_result(outcome), True)
    except Exception as exc:  # noqa: BLE001
        logger.exception(f"Tool invocation failed label={test.label}")
        return (test.label, f"Exception: {exc}", False)


async def main() -> None:
    current_project = session.get_current_project() or "advanced-memory"

    tests: Iterable[ToolTest] = [
        ToolTest(
            "adn_navigation/status_basic",
            adn_navigation.fn,
            {"operation": "status", "level": "basic"},
        ),
        ToolTest(
            "adn_navigation/sync_status",
            adn_navigation.fn,
            {"operation": "sync_status"},
        ),
        ToolTest(
            "adn_navigation/invalid",
            adn_navigation.fn,
            {"operation": "explode"},
        ),
        ToolTest(
            "adn_project/get_current",
            adn_project.fn,
            {"operation": "get_current"},
        ),
        ToolTest(
            "adn_project/status",
            adn_project.fn,
            {"operation": "status", "project_name": current_project},
        ),
        ToolTest(
            "adn_project/sync",
            adn_project.fn,
            {"operation": "sync", "project_name": current_project},
        ),
        ToolTest(
            "adn_project/invalid",
            adn_project.fn,
            {"operation": "explode"},
        ),
    ]

    headers = ("Status", "Label", "Message")
    print(f"{headers[0]:<8} | {headers[1]:<35} | {headers[2]}")
    print("-" * 110)

    results: list[tuple[str, str, bool]] = []
    for test in tests:
        label, message, ok = await run_test(test)
        status = "OK" if ok else "FAIL"
        print(f"{status:<8} | {label:<35} | {message}")
        results.append((label, message, ok))

    print("-" * 110)
    succeeded = sum(1 for _, _, ok in results if ok)
    failed = len(results) - succeeded
    print(f"Completed {len(results)} calls — {succeeded} succeeded, {failed} failed.")
    if failed > 0:
        raise SystemExit(1)


if __name__ == "__main__":
    asyncio.run(main())

