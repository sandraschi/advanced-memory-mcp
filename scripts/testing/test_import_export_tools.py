"""Exercise Advanced Memory import/export portmanteau tools.

This covers happy-path archive export (optional) plus a suite of failure-mode
checks so we can verify error payloads are descriptive and structured.

Usage:
    uv run python scripts/testing/test_import_export_tools.py
    uv run python scripts/testing/test_import_export_tools.py --skip-heavy
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

from advanced_memory.mcp.tools import adn_export, adn_import

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


def build_tests(include_heavy: bool) -> tuple[Iterable[ToolTest], list[Path]]:
    cleanup_targets: list[Path] = []
    tests: list[ToolTest] = [
        ToolTest(
            "adn_export/invalid_operation",
            adn_export.fn,
            {"operation": "explode"},
        ),
        ToolTest(
            "adn_export/missing_project",
            adn_export.fn,
            {
                "operation": "pandoc",
                "project": "non-existent-project",
                "show_after_export": False,
            },
        ),
        ToolTest(
            "adn_import/missing_archive",
            adn_import.fn,
            {
                "operation": "archive",
                "source_path": str(Path(tempfile.gettempdir()) / "missing-archive.zip"),
                "destination_folder": "import-test",
            },
        ),
        ToolTest(
            "adn_import/invalid_operation",
            adn_import.fn,
            {"operation": "explode", "source_path": "dummy"},
        ),
    ]

    if include_heavy:
        export_dir = Path(tempfile.mkdtemp(prefix="am-export-"))
        cleanup_targets.append(export_dir)
        tests.append(
            ToolTest(
                "adn_export/archive_success",
                adn_export.fn,
                {
                    "operation": "archive",
                    "export_path": str(export_dir / "advanced-memory-export.zip"),
                    "show_after_export": False,
                },
            )
        )

        # Prepare a minimal faux archive for testing restore failure modes.
        import_src = export_dir / "sample_import"
        import_src.mkdir(parents=True, exist_ok=True)
        (import_src / "README.txt").write_text("sample archive payload", encoding="utf-8")
        archive_path = shutil.make_archive(
            base_name=str(import_src),
            format="zip",
            root_dir=import_src,
        )
        cleanup_targets.append(Path(archive_path))
        tests.append(
            ToolTest(
                "adn_import/archive_sample",
                adn_import.fn,
                {
                    "operation": "archive",
                    "source_path": archive_path,
                    "destination_folder": "tmp/test-import",
                    "restore_mode": "merge",
                },
            )
        )

    return tests, cleanup_targets


async def main() -> None:
    parser = argparse.ArgumentParser(description="Exercise import/export tools.")
    parser.add_argument(
        "--skip-heavy",
        action="store_true",
        help="Skip operations that write large archives to disk.",
    )
    args = parser.parse_args()

    tests, cleanup_targets = build_tests(include_heavy=not args.skip_heavy)

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

