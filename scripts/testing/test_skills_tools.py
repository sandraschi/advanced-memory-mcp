"""Exercise the skills toolchain (adn_skills + adn_skills_creator).

The script covers CRUD-ish operations, packaging, creator workflows, and
negative cases to verify error payloads.  Network-heavy operations (GitHub
imports, Wikipedia/arXiv distillation) are optional flags.

Usage:
    uv run python scripts/testing/test_skills_tools.py
    uv run python scripts/testing/test_skills_tools.py --skip-network
    uv run python scripts/testing/test_skills_tools.py --skip-packaging
"""

from __future__ import annotations

import argparse
import asyncio
import json
import shutil
import tempfile
from collections.abc import Awaitable, Callable, Iterable
from dataclasses import dataclass
from pathlib import Path
from textwrap import shorten
from typing import Any

from loguru import logger

from advanced_memory.mcp.tools import adn_skills, adn_skills_creator

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


def build_tests(
    *,
    include_packaging: bool,
    include_network: bool,
) -> tuple[Iterable[ToolTest], list[Path]]:
    cleanup_targets: list[Path] = []
    tests: list[ToolTest] = [
        ToolTest("adn_skills/list", adn_skills.fn, {"operation": "list", "page_size": 5}),
        ToolTest(
            "adn_skills/validate",
            adn_skills.fn,
            {
                "operation": "validate",
                "identifier": "skills/advanced-memory/advanced-memory-skill-creator",
            },
        ),
        ToolTest(
            "adn_skills_creator/inspect",
            adn_skills_creator.fn,
            {
                "operation": "inspect",
                "skill_path": "skills/advanced-memory/advanced-memory-skill-creator",
            },
        ),
        ToolTest(
            "adn_skills_creator/invalid",
            adn_skills_creator.fn,
            {"operation": "explode"},
        ),
        ToolTest(
            "adn_skills/invalid",
            adn_skills.fn,
            {"operation": "explode"},
        ),
    ]

    if include_packaging:
        export_dir = Path(tempfile.mkdtemp(prefix="am-skills-"))
        cleanup_targets.append(export_dir)
        tests.append(
            ToolTest(
                "adn_skills/package",
                adn_skills.fn,
                {
                    "operation": "package",
                    "identifier": "skills/advanced-memory/advanced-memory-skill-creator",
                    "export_path": str(export_dir),
                    "package_format": "zip",
                },
            )
        )

    if include_network:
        tests.extend(
            [
                ToolTest(
                    "adn_skills/distill_wikipedia",
                    adn_skills.fn,
                    {
                        "operation": "distill_from_wikipedia",
                        "topic": "Claude AI",
                        "quality": "basic",
                        "include_related": False,
                    },
                ),
                ToolTest(
                    "adn_skills/distill_arxiv",
                    adn_skills.fn,
                    {
                        "operation": "distill_from_arxiv",
                        "query": "retrieval augmented generation",
                        "max_papers": 1,
                        "synthesis_level": "summary",
                    },
                ),
            ]
        )
    else:
        tests.extend(
            [
                ToolTest(
                    "adn_skills/distill_wikipedia_skipped",
                    adn_skills.fn,
                    {
                        "operation": "distill_from_wikipedia",
                        "topic": "NonexistentTopicXYZ",
                        "quality": "basic",
                        "include_related": False,
                    },
                ),
                ToolTest(
                    "adn_skills/distill_arxiv_skipped",
                    adn_skills.fn,
                    {
                        "operation": "distill_from_arxiv",
                        "query": "imaginary-field-123",
                        "max_papers": 1,
                        "synthesis_level": "summary",
                    },
                ),
            ]
        )

    # Always include GitHub import error case (safe even without network).
    tests.append(
        ToolTest(
            "adn_skills/import_from_github_missing",
            adn_skills.fn,
            {
                "operation": "import_from_github",
                "repository": "anthropics/missing-repo",
                "branch": "main",
            },
        )
    )

    return tests, cleanup_targets


async def main() -> None:
    parser = argparse.ArgumentParser(description="Exercise skills management tools.")
    parser.add_argument("--skip-network", action="store_true", help="Skip network-heavy tests.")
    parser.add_argument("--skip-packaging", action="store_true", help="Skip ZIP packaging tests.")
    args = parser.parse_args()

    tests, cleanup_targets = build_tests(
        include_packaging=not args.skip_packaging,
        include_network=not args.skip_network,
    )

    headers = ("Status", "Label", "Message")
    print(f"{headers[0]:<8} | {headers[1]:<40} | {headers[2]}")
    print("-" * 120)

    results: list[tuple[str, str, bool]] = []
    for test in tests:
        label, message, ok = await run_test(test)
        status = "OK" if ok else "FAIL"
        print(f"{status:<8} | {label:<40} | {message}")
        results.append((label, message, ok))

    print("-" * 120)
    succeeded = sum(1 for _, _, ok in results if ok)
    failed = len(results) - succeeded
    print(f"Completed {len(results)} calls — {succeeded} succeeded, {failed} failed.")
    if failed > 0:
        raise SystemExit(1)

    for target in cleanup_targets:
        try:
            if target.is_dir():
                shutil.rmtree(target, ignore_errors=True)
            elif target.exists():
                target.unlink(missing_ok=True)
        except Exception as exc:  # noqa: BLE001
            logger.warning(f"Cleanup failed target={target}: {exc}")


if __name__ == "__main__":
    asyncio.run(main())
