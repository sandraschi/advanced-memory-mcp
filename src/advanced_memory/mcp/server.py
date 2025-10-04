"""
Basic Memory FastMCP server with console output suppression.
"""

import asyncio
import sys
import os
from contextlib import asynccontextmanager
from dataclasses import dataclass
from typing import AsyncIterator, Optional, Any

from fastmcp import FastMCP

from advanced_memory.config import ConfigManager
from advanced_memory.services.initialization import initialize_app


@dataclass
class AppContext:
    watch_task: Optional[asyncio.Task]
    migration_manager: Optional[Any] = None


@asynccontextmanager
async def app_lifespan(server: FastMCP) -> AsyncIterator[AppContext]:  # pragma: no cover
    """ """
    # defer import so tests can monkeypatch
    from advanced_memory.mcp.project_session import session

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


# Configure logging to suppress non-JSON output in MCP stdio mode
def configure_mcp_logging():
    """Configure logging to prevent interference with JSON responses."""
    if not sys.stdout.isatty():  # MCP stdio mode
        try:
            from loguru import logger
            # Remove all existing handlers
            logger.remove()
            # Add a minimal handler that only logs critical errors to stderr
            logger.add(sys.stderr, level="ERROR", format="{message}")
        except ImportError:
            pass


# Apply logging configuration
configure_mcp_logging()

# Create the shared server instance
mcp = FastMCP(
    name="Basic Memory",
    lifespan=app_lifespan,
)
