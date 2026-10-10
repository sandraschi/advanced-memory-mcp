"""Regression tests: note writes must ACK fast even when background work is slow.

History: the same symptom (write times out client-side, lands server-side)
regressed repeatedly because heavy post-write work (vector indexing, relation
resolution) ran in the request/response path - either awaited directly or via
Starlette BackgroundTasks, which execute BEFORE the response is sent.

These tests install deliberately slow fakes for the background work and assert
the PUT response still returns inside a tight budget. If anyone moves heavy
work back into the awaited path, these fail deterministically instead of
surfacing as another 3am "writes hang again" incident.

Related: BUG-048 (open), 2026-10-05 fire-and-forget fix in knowledge_router.
"""

import asyncio
import subprocess
import sys
import time
from pathlib import Path

import pytest
from httpx import AsyncClient

from advanced_memory.api.routers import knowledge_router
from advanced_memory.db import DatabaseType, claim_writer_lock

SLOW_WORK_SECONDS = 15.0
RESPONSE_BUDGET_SECONDS = 10.0


async def _drain_fire_and_forget() -> None:
    """Cancel leftover fire-and-forget tasks so tests don't leak tasks."""
    pending = list(knowledge_router._FIRE_AND_FORGET_TASKS)
    for task in pending:
        task.cancel()
    if pending:
        await asyncio.gather(*pending, return_exceptions=True)


@pytest.mark.asyncio
async def test_put_create_returns_before_relation_resolution(
    client: AsyncClient, project_url: str, monkeypatch: pytest.MonkeyPatch
):
    """PUT create must not wait for relation resolution (slow vault scan)."""

    async def slow_resolve(*args, **kwargs) -> None:
        await asyncio.sleep(SLOW_WORK_SECONDS)

    monkeypatch.setattr(knowledge_router, "_resolve_relations_logged", slow_resolve)
    try:
        data = {"title": "LatencyProbeResolve", "folder": "latency", "content": "probe"}
        started = time.perf_counter()
        response = await client.put(
            f"{project_url}/knowledge/entities/latency/latency-probe-resolve",
            json=data,
        )
        elapsed = time.perf_counter() - started
    finally:
        await _drain_fire_and_forget()

    assert response.status_code in (200, 201)
    assert elapsed < RESPONSE_BUDGET_SECONDS, (
        f"PUT create blocked {elapsed:.1f}s on relation resolution "
        f"(budget {RESPONSE_BUDGET_SECONDS}s) - heavy work regressed into the response path"
    )


@pytest.mark.asyncio
async def test_put_create_returns_before_indexing(
    client: AsyncClient, project_url: str, monkeypatch: pytest.MonkeyPatch
):
    """PUT create must not wait for vector/FTS indexing (ONNX load + writes)."""
    from advanced_memory.services.search_service import SearchService

    # NOTE: tests/conftest.py forces ADVANCED_MEMORY_SYNC_INDEX=1 globally so
    # legacy search assertions stay deterministic. That flag bypasses the
    # production fire-and-forget path - which is exactly the path this test
    # guards - so opt back out to production behavior here.
    monkeypatch.setenv("ADVANCED_MEMORY_SYNC_INDEX", "0")

    release = asyncio.Event()

    async def slow_index(self, entity) -> None:
        await release.wait()

    monkeypatch.setattr(SearchService, "index_entity_data", slow_index)
    try:
        data = {"title": "LatencyProbeIndex", "folder": "latency", "content": "probe"}
        started = time.perf_counter()
        response = await client.put(
            f"{project_url}/knowledge/entities/latency/latency-probe-index",
            json=data,
        )
        elapsed = time.perf_counter() - started
    finally:
        release.set()
        await _drain_fire_and_forget()

    assert response.status_code in (200, 201)
    assert elapsed < RESPONSE_BUDGET_SECONDS, (
        f"PUT create blocked {elapsed:.1f}s on indexing "
        f"(budget {RESPONSE_BUDGET_SECONDS}s) - heavy work regressed into the response path"
    )


def test_writer_lock_rejects_second_process(tmp_path: Path):
    """A second writer process on the same vault must die loudly (BUG-048).

    Same-process double claim is fine (reentrant engine creation); a separate
    OS process claiming the same vault must fail with the actionable error.
    """
    from advanced_memory.db import _WRITER_LOCK_FDS

    db_file = tmp_path / "vault" / "memory.db"
    db_file.parent.mkdir(parents=True)
    db_file.touch()

    claim_writer_lock(db_file, DatabaseType.FILESYSTEM)
    claim_writer_lock(db_file, DatabaseType.FILESYSTEM)  # reentrant: must not raise
    import os as _os

    assert any(_os.path.normcase(str(db_file.parent)) in k for k in _WRITER_LOCK_FDS), (
        "parent did not retain the writer lock"
    )

    src_dir = str(Path(__file__).resolve().parents[2] / "src")
    child = subprocess.run(
        [
            sys.executable,
            "-c",
            "import sys; sys.path.insert(0, r'" + src_dir + "'); "
            "from pathlib import Path; "
            "from advanced_memory.db import claim_writer_lock, DatabaseType; "
            "claim_writer_lock(Path(r'" + str(db_file) + "'), DatabaseType.FILESYSTEM); "
            "print('CLAIMED-BY-CHILD')",
        ],
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert child.returncode != 0, f"second writer claimed the vault: {child.stdout}"
    assert "already opened for writing" in child.stderr, child.stderr[-2000:]
