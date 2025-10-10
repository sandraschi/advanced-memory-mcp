"""
Advanced Memory FastMCP server with console output suppression.
"""

import asyncio
import sys
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from dataclasses import dataclass
from typing import Any

from fastmcp import FastMCP

from advanced_memory.config import ConfigManager
from advanced_memory.services.initialization import initialize_app


@dataclass
class AppContext:
    watch_task: asyncio.Task | None
    migration_manager: Any | None = None


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

# Import the shared MCP instance
from advanced_memory.mcp.mcp_instance import mcp

# Import and register all tools
from advanced_memory.mcp.tools import *

# Use the shared MCP instance as the server
server = mcp

# Add stdio runner for MCP protocol
if __name__ == "__main__":
    import asyncio
    asyncio.run(server.run_stdio_async())
