"""Fail fast when documented URL layout drifts from ``app.include_router`` mounts."""

import pytest

from advanced_memory.api.app import app


@pytest.fixture(scope="module")
def openapi_paths() -> set[str]:
    return set(app.openapi().get("paths", {}))


def test_openapi_global_routes(openapi_paths: set[str]) -> None:
    for path in (
        "/api/v1/health",
        "/api/v1/import/chatgpt",
        "/api/v1/projects",
    ):
        assert path in openapi_paths, f"OpenAPI missing route {path} — check app.include_router prefixes"


def test_openapi_project_scoped_routes(openapi_paths: set[str]) -> None:
    """Representative {project} paths; catches double ``/api/v1`` mistakes in tests."""
    for path in (
        "/api/v1/{project}/project/info",
        "/api/v1/{project}/knowledge/graph/subgraph",
    ):
        assert path in openapi_paths, f"OpenAPI missing route {path}"


def test_importer_not_mounted_under_project(openapi_paths: set[str]) -> None:
    """Import lives on ``/api/v1/import`` only (see ``route_prefixes.IMPORT_API_ROOT``)."""
    assert "/api/v1/{project}/import/chatgpt" not in openapi_paths
