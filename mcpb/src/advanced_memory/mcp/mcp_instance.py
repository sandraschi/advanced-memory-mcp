"""Shared MCP instance for tool registration.

This module provides a shared MCP instance that tools can import and use
for registration, avoiding circular import issues.
"""

import asyncio
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from dataclasses import dataclass
from typing import Any

from fastmcp import FastMCP


@dataclass
class AppContext:
    watch_task: asyncio.Task | None
    migration_manager: Any | None = None

@asynccontextmanager
async def app_lifespan(server: FastMCP) -> AsyncIterator[AppContext]:  # pragma: no cover
    """Application lifespan manager."""
    # defer import so tests can monkeypatch
    from advanced_memory.config import ConfigManager
    from advanced_memory.mcp.project_session import session
    from advanced_memory.services.initialization import initialize_app

    app_config = ConfigManager().config
    # Initialize on startup (now returns migration_manager)
    migration_manager = await initialize_app(app_config)

    # Initialize project session with default project
    session.initialize(app_config.default_project)

    try:
        yield AppContext(watch_task=None, migration_manager=migration_manager)
    finally:
        # Cleanup on shutdown - migration tasks will be cancelled automatically
        pass

# Create a shared MCP instance that tools can import
mcp = FastMCP(
    name="Advanced Memory MCP",
    lifespan=app_lifespan,
)
