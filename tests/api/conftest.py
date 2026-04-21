"""Tests for knowledge graph API routes."""

from collections.abc import AsyncGenerator

import pytest
import pytest_asyncio
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from advanced_memory.deps import get_app_config, get_engine_factory, get_project_config
from advanced_memory.models import Project

from tests.api.route_prefixes import project_api_root


@pytest_asyncio.fixture
async def app(test_config, engine_factory, app_config) -> FastAPI:
    """Create FastAPI test application."""
    from advanced_memory.api.app import app

    app.dependency_overrides[get_app_config] = lambda: app_config
    app.dependency_overrides[get_project_config] = lambda: test_config.project_config
    app.dependency_overrides[get_engine_factory] = lambda: engine_factory
    return app


@pytest_asyncio.fixture
async def client(app: FastAPI) -> AsyncGenerator[AsyncClient, None]:
    """Create client using ASGI transport - same as CLI will use."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        yield client


@pytest.fixture
def project_url(test_project: Project) -> str:
    """Create a URL prefix for the project routes.

    Project-scoped routers are mounted at ``/api/v1/{project}`` where ``{project}`` is the
    project's permalink (see ``get_project_id`` / ``get_project_config`` in deps).
    """
    return project_api_root(test_project.permalink)
