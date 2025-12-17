"""Ad-hoc exerciser for Advanced Memory core portmanteau tools.

This script calls every primary portmanteau tool with both representative
arguments and deliberately invalid parameters (“operation='explode'”) so we
can manually inspect success payloads and error messages.  The goal is to
confirm responses remain AI-parseable and richly descriptive.

Usage:
    uv run python scripts/testing/test_core_tools.py
"""

from __future__ import annotations

import asyncio
import json
import tempfile
from collections.abc import Awaitable, Callable, Iterable
from dataclasses import dataclass
from pathlib import Path
from textwrap import shorten
from typing import Any

from loguru import logger

from advanced_memory.mcp.tools import (
    adn_audio,
    adn_content,
    adn_export,
    adn_import,
    adn_inbox,
    adn_knowledge,
    adn_navigation,
    adn_project,
    adn_search,
    adn_skills,
    adn_skills_creator,
    adn_zettelmaker,
)

# Type alias for the callable signature FastMCP exposes on tools (.fn attribute).
ToolCallable = Callable[..., Awaitable[Any]]


@dataclass(slots=True)
class ToolTest:
    """Container describing a single tool invocation to execute."""

    label: str
    tool: ToolCallable
    kwargs: dict[str, Any]


def serialize_result(result: Any) -> str:
    """Render tool results into a compact, human readable snippet."""

    if isinstance(result, dict | list):
        try:
            pretty = json.dumps(result, indent=2, ensure_ascii=False)
        except TypeError:
            pretty = repr(result)
    else:
        pretty = str(result)

    pretty = pretty.replace("\n", " ").replace("\r", " ")
    safe = pretty.encode("cp1252", "replace").decode("cp1252")
    return shorten(safe, width=220, placeholder=" …")


async def run_test(test: ToolTest) -> tuple[str, str, bool]:
    """Execute a tool call and return a structured summary tuple.

    Returns:
        A tuple of (label, message, success_flag).
    """

    try:
        logger.debug(f"Executing {test.label} with args={test.kwargs}")
        result = await test.tool(**test.kwargs)
        return (test.label, serialize_result(result), True)
    except Exception as exc:  # noqa: BLE001 - we explicitly report any failure
        logger.exception(f"Tool invocation failed label={test.label}")
        return (test.label, f"Exception: {exc}", False)


async def main() -> None:
    """Run the complete core-tool exercise suite."""

    tests: Iterable[ToolTest] = [
        ToolTest("adn_content/read_latest", adn_content.fn, {"operation": "read_latest"}),
        ToolTest("adn_content/invalid", adn_content.fn, {"operation": "explode"}),
        ToolTest(
            "adn_search/notes", adn_search.fn, {"operation": "notes", "query": "advanced memory"}
        ),
        ToolTest(
            "adn_search/invalid", adn_search.fn, {"operation": "explode", "query": "advanced"}
        ),
        ToolTest(
            "adn_navigation/status", adn_navigation.fn, {"operation": "status", "level": "basic"}
        ),
        ToolTest("adn_navigation/invalid", adn_navigation.fn, {"operation": "explode"}),
        ToolTest("adn_project/status", adn_project.fn, {"operation": "status"}),
        ToolTest("adn_project/invalid", adn_project.fn, {"operation": "explode"}),
        ToolTest("adn_inbox/status", adn_inbox.fn, {"operation": "status"}),
        ToolTest("adn_inbox/invalid", adn_inbox.fn, {"operation": "explode"}),
        ToolTest(
            "adn_knowledge/project_stats",
            adn_knowledge.fn,
            {"operation": "project_stats", "dry_run": True},
        ),
        ToolTest("adn_knowledge/invalid", adn_knowledge.fn, {"operation": "explode"}),
        ToolTest(
            "adn_zettelmaker/suggest",
            adn_zettelmaker.fn,
            {"operation": "suggest", "category": "developer", "count": 2},
        ),
        ToolTest("adn_zettelmaker/invalid", adn_zettelmaker.fn, {"operation": "explode"}),
        ToolTest(
            "adn_skills/list",
            adn_skills.fn,
            {"operation": "list", "page_size": 5},
        ),
        ToolTest("adn_skills/invalid", adn_skills.fn, {"operation": "explode"}),
        ToolTest(
            "adn_skills_creator/inspect",
            adn_skills_creator.fn,
            {
                "operation": "inspect",
                "skill_path": "skills/advanced-memory/advanced-memory-skill-creator",
            },
        ),
        ToolTest("adn_skills_creator/invalid", adn_skills_creator.fn, {"operation": "explode"}),
        ToolTest(
            "adn_import/missing_source",
            adn_import.fn,
            {
                "operation": "archive",
                "source_path": "C:/nonexistent/path.zip",
                "destination_folder": "imported/test",
            },
        ),
        ToolTest(
            "adn_import/invalid",
            adn_import.fn,
            {"operation": "explode", "source_path": "dummy"},
        ),
        ToolTest(
            "adn_export/archive",
            adn_export.fn,
            {
                "operation": "archive",
                "export_path": str(
                    Path(tempfile.gettempdir()) / "advanced-memory-test-archive.zip"
                ),
                "show_after_export": False,
            },
        ),
        ToolTest("adn_export/invalid", adn_export.fn, {"operation": "explode"}),
        ToolTest(
            "adn_audio/dictate_missing_file",
            adn_audio.fn,
            {"operation": "dictate", "audio_path": "C:/nonexistent/audio.wav"},
        ),
        ToolTest("adn_audio/invalid", adn_audio.fn, {"operation": "explode"}),
    ]

    headers = ("Status", "Label", "Message")
    print(f"{headers[0]:<8} | {headers[1]:<40} | {headers[2]}")
    print("-" * 120)

    results: list[tuple[str, str, bool]] = []
    for test in tests:
        result = await run_test(test)
        status = "OK" if result[2] else "FAIL"
        print(f"{status:<8} | {result[0]:<40} | {result[1]}")
        results.append(result)

    successes = sum(1 for _, _, ok in results if ok)
    failures = len(results) - successes
    print("-" * 120)
    print(
        f"Completed {len(results)} tool calls — {successes} succeeded, {failures} raised exceptions."
    )
    if failures > 0:
        raise SystemExit(1)


if __name__ == "__main__":
    asyncio.run(main())
