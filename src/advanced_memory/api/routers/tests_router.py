"""Router for running tests from the webapp (dev/local only)."""

import asyncio
import os
import time
from pathlib import Path

from fastapi import APIRouter, HTTPException
from loguru import logger
from pydantic import BaseModel

router = APIRouter(prefix="/tests", tags=["tests"])


def _tests_enabled() -> bool:
    """Only allow test runs when explicitly enabled (dev/local)."""
    return os.environ.get("ENABLE_WEBAPP_TESTS", "").lower() in ("1", "true", "yes")


def _repo_root() -> Path:
    """Resolve repository root (where pyproject.toml / tests/ live)."""
    # .../src/advanced_memory/api/routers/tests_router.py -> repo root
    path = Path(__file__).resolve()
    for _ in range(5):
        path = path.parent
        if (path / "pyproject.toml").exists() or (path / "tests").is_dir():
            return path
    return Path(__file__).resolve().parents[4]


class RunTestsRequest(BaseModel):
    """Request body for running tests."""

    target: str = "tests"
    timeout_seconds: int = 300
    extra_args: list[str] = []


class RunTestsResponse(BaseModel):
    """Response from test run."""

    success: bool
    exit_code: int
    stdout: str
    stderr: str
    duration_seconds: float


@router.post("/run", response_model=RunTestsResponse)
async def run_tests(body: RunTestsRequest) -> RunTestsResponse:
    """Run pytest in the repo and return stdout/stderr and exit code.

    Only available when ENABLE_WEBAPP_TESTS=1 (or true/yes). Intended for
    local/dev use; do not enable in production.
    """
    if not _tests_enabled():
        raise HTTPException(
            status_code=403,
            detail="Test runner is disabled. Set ENABLE_WEBAPP_TESTS=1 to enable.",
        )
    repo = _repo_root()
    if not repo.exists():
        raise HTTPException(status_code=500, detail="Repository root not found")
    cmd = [
        "python",
        "-m",
        "pytest",
        body.target,
        "-v",
        "--tb=short",
        "-q",
        *body.extra_args,
    ]
    logger.info("Webapp test run: cwd=%s cmd=%s", repo, cmd)
    start = time.monotonic()
    proc = None
    try:
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            cwd=repo,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout_bytes, stderr_bytes = await asyncio.wait_for(
            proc.communicate(),
            timeout=float(body.timeout_seconds),
        )
        exit_code = proc.returncode if proc.returncode is not None else -1
    except TimeoutError:
        if proc is not None and proc.returncode is None:
            try:
                proc.kill()
                await asyncio.wait_for(proc.wait(), timeout=5.0)
            except Exception:
                pass
        logger.warning("Test run timed out after %s seconds", body.timeout_seconds)
        raise HTTPException(
            status_code=408,
            detail=f"Tests timed out after {body.timeout_seconds}s",
        ) from None
    except FileNotFoundError as e:
        logger.warning("pytest not found: %s", e)
        raise HTTPException(
            status_code=503,
            detail="pytest not found. Install with: pip install pytest pytest-asyncio",
        ) from e
    duration = time.monotonic() - start
    stdout = stdout_bytes.decode("utf-8", errors="replace")
    stderr = stderr_bytes.decode("utf-8", errors="replace")
    return RunTestsResponse(
        success=exit_code == 0,
        exit_code=exit_code,
        stdout=stdout,
        stderr=stderr,
        duration_seconds=round(duration, 2),
    )
