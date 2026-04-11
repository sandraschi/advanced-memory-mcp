"""Shared MCP instance for tool registration.

This module provides a shared MCP instance that tools can import and use
for registration, avoiding circular import issues.
"""

# CRITICAL: Configure logging FIRST for MCP stdio mode
# This must happen before any imports that might log
import os
import sys

from advanced_memory.utils.stdio import setup_stdio_binary_mode, suppress_stdout_pollution

# CRITICAL: Set stdio to binary mode on Windows for Antigravity IDE compatibility
# MUST be done BEFORE patching stdout, otherwise DevNullStdout won't have fileno()
# Antigravity IDE is strict about JSON-RPC protocol and interprets trailing \r as "invalid trailing data"
setup_stdio_binary_mode()

# Detect if we're running in stdio mode (MCP server)
# Check environment variable or if stdout is not a TTY
_is_stdio_mode = not sys.stdout.isatty() or os.getenv("MCP_STDIO_MODE", "").lower() == "true" or "stdio" in sys.argv

if _is_stdio_mode:
    # CRITICAL: Patch stdout FIRST to prevent ANY writes during initialization
    # This catches print statements, Rich console, FastMCP banners, etc.
    suppress_stdout_pollution()

    # NUCLEAR OPTION: Completely disable loguru during stdio mode
    try:
        # Create a complete no-op logger class
        class NoOpLogger:
            """Complete no-op logger that does nothing - nuclear option for stdio mode."""

            def __call__(self, *args, **kwargs):
                return self

            def info(self, *args, **kwargs):
                pass

            def error(self, *args, **kwargs):
                pass

            def warning(self, *args, **kwargs):
                pass

            def debug(self, *args, **kwargs):
                pass

            def exception(self, *args, **kwargs):
                pass

            def critical(self, *args, **kwargs):
                pass

            def success(self, *args, **kwargs):
                pass

            def trace(self, *args, **kwargs):
                pass

            def remove(self, *args, **kwargs):
                return self

            def add(self, *args, **kwargs):
                return self

            def disable(self, *args, **kwargs):
                return self

            def enable(self, *args, **kwargs):
                return self

            def bind(self, *args, **kwargs):
                return self

            def patch(self, *args, **kwargs):
                return self

            def opt(self, *args, **kwargs):
                return self

        # Replace loguru logger module with no-op
        import sys

        if "loguru" not in sys.modules:
            sys.modules["loguru"] = type("Module", (), {"logger": NoOpLogger()})()

        # Use no-op logger for stdio mode
        logger = NoOpLogger()
    except Exception:
        # If anything fails, create a no-op logger anyway
        class NoOpLogger:
            def __call__(self, *args, **kwargs):
                return self

            def info(self, *args, **kwargs):
                pass

            def error(self, *args, **kwargs):
                pass

            def warning(self, *args, **kwargs):
                pass

            def debug(self, *args, **kwargs):
                pass

            def exception(self, *args, **kwargs):
                pass

            def critical(self, *args, **kwargs):
                pass

            def success(self, *args, **kwargs):
                pass

            def trace(self, *args, **kwargs):
                pass

            def remove(self, *args, **kwargs):
                return self

            def add(self, *args, **kwargs):
                return self

        logger = NoOpLogger()

import asyncio
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from dataclasses import dataclass
from typing import Any

from fastmcp import FastMCP
from loguru import logger


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

    # Initialize LLM configuration from saved config
    if app_config.llm_provider and app_config.llm_model:
        try:
            import advanced_memory.mcp.tools.adn_llm as adn_llm_module

            adn_llm_module._current_provider = app_config.llm_provider
            adn_llm_module._current_model = app_config.llm_model
            # Suppress logging in stdio mode to prevent JSON-RPC stream pollution
            if not _is_stdio_mode:
                logger.info(
                    f"Initialized LLM from config: provider={app_config.llm_provider}, model={app_config.llm_model}"
                )
        except Exception as e:
            # Suppress logging in stdio mode to prevent JSON-RPC stream pollution
            if not _is_stdio_mode:
                logger.warning(f"Failed to initialize LLM from config: {e}")

    try:
        yield AppContext(watch_task=None, migration_manager=migration_manager)
    finally:
        # Cleanup on shutdown - migration tasks will be cancelled automatically
        pass


# Create a shared MCP instance that tools can import
# Note: lifespan is set later in server.py to avoid expensive initialization during import
mcp = FastMCP(
    name="Advanced Memory MCP",
)

# Store references to prompts and resources to prevent garbage collection
# This follows FastMCP 2.12+ best practices for prompt/resource registration
_prompt_refs: list[Any] = []
_resource_refs: list[Any] = []


def _initialize_prompts_and_resources() -> None:
    """Initialize prompts and resources, storing references to prevent garbage collection.

    This function imports all prompt and resource modules, which causes their
    decorators to register with the MCP instance. We then store references to
    the registered functions to prevent garbage collection.

    Following FastMCP 2.12+ best practices for prompt/resource registration.
    """
    # Import prompts module to register all prompts via __init__.py
    # Import resources module to register all resources via __init__.py
    # Import individual prompt modules to get function references
    # Import resources to get function references
    # Note: ai_assistant_guide is in prompts/ but is actually a resource
    import advanced_memory.mcp.prompts.ai_assistant_guide as ai_assistant_guide
    import advanced_memory.mcp.prompts.continue_conversation as continue_conversation
    import advanced_memory.mcp.prompts.recent_activity as recent_activity
    import advanced_memory.mcp.prompts.search as search
    import advanced_memory.mcp.resources.project_info as project_info
    import advanced_memory.mcp.resources.prompt_templates as prompt_templates
    from advanced_memory.mcp import (
        prompts,
        resources,
    )

    # Store references to prevent garbage collection
    # The actual functions are registered via decorators, but we store
    # references to ensure they stay in memory
    global _prompt_refs, _resource_refs
    _prompt_refs = [
        recent_activity.recent_activity_prompt,
        search.search_prompt,
        continue_conversation.continue_conversation,
    ]
    _resource_refs = [
        ai_assistant_guide.ai_assistant_guide,  # Resource, despite being in prompts/
        project_info.project_info,
        prompt_templates.search_prompt_template,
        prompt_templates.continue_conversation_prompt_template,
    ]


# For MCP server mode, we need prompts available immediately but can delay resources
_is_stdio_mode = not sys.stdout.isatty() or os.getenv("MCP_STDIO_MODE", "").lower() == "true" or "stdio" in sys.argv

if _is_stdio_mode:
    # For MCP stdio mode, load prompts immediately but delay resource loading
    # Import individual prompt modules to register them via decorators
    try:
        import advanced_memory.mcp.prompts.continue_conversation
        import advanced_memory.mcp.prompts.recent_activity
        import advanced_memory.mcp.prompts.search
    except ImportError:
        # If there are import issues, continue anyway
        pass

    # Resources will be loaded later when server starts
    def initialize_mcp_resources():
        """Initialize MCP resources - call this when MCP server starts."""
        try:
            # Import resources module to register all resources via __init__.py
            # Also import the ai_assistant_guide which is a resource in prompts
            import advanced_memory.mcp.prompts.ai_assistant_guide
            import advanced_memory.mcp.resources
        except ImportError:
            pass

else:
    # For CLI/non-MCP usage, initialize everything immediately
    _initialize_prompts_and_resources()
