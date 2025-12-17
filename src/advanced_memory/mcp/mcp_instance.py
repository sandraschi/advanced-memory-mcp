"""Shared MCP instance for tool registration.

This module provides a shared MCP instance that tools can import and use
for registration, avoiding circular import issues.
"""

# CRITICAL: Configure logging FIRST for MCP stdio mode
# This must happen before any imports that might log
import sys
import warnings
import logging
import os

# CRITICAL: Set stdio to binary mode on Windows for Antigravity IDE compatibility
# MUST be done BEFORE patching stdout, otherwise DevNullStdout won't have fileno()
# Antigravity IDE is strict about JSON-RPC protocol and interprets trailing \r as "invalid trailing data"
# Binary mode prevents Python from automatically converting line endings
if os.name == 'nt':  # Windows
    try:
        import msvcrt
        # Set stdin/stdout to binary mode to prevent line ending conversion
        # This fixes "invalid trailing data" errors with Antigravity IDE
        # Store original filenos before any patching
        # Use try/except to handle cases where fileno() doesn't exist or isn't callable
        try:
            msvcrt.setmode(sys.stdin.fileno(), os.O_BINARY)
        except (OSError, AttributeError):
            pass  # stdin might not be a real file descriptor or already patched
        try:
            msvcrt.setmode(sys.stdout.fileno(), os.O_BINARY)
        except (OSError, AttributeError):
            pass  # stdout might not be a real file descriptor or already patched
    except (ImportError, OSError, AttributeError):
        # If msvcrt is not available or setting fails, continue without it
        # This might happen in some environments, but it's not critical
        pass

# Detect if we're running in stdio mode (MCP server)
# Check environment variable or if stdout is not a TTY
_is_stdio_mode = (
    not sys.stdout.isatty() 
    or os.getenv("MCP_STDIO_MODE", "").lower() == "true"
    or "stdio" in sys.argv
)

if _is_stdio_mode:
    # CRITICAL: Patch stdout FIRST to prevent ANY writes during initialization
    # This catches print statements, Rich console, FastMCP banners, etc.
    class DevNullStdout:
        """A file-like object that discards all writes (like /dev/null)."""
        def write(self, s: str) -> int:
            # Discard all writes to stdout - they would break JSON-RPC
            return len(s)
        
        def flush(self) -> None:
            pass
        
        def isatty(self) -> bool:
            return False
        
        def readable(self) -> bool:
            return False
        
        def writable(self) -> bool:
            return True
        
        def seekable(self) -> bool:
            return False
    
    # Store original stdout and replace with null device
    # This will be restored before FastMCP.run() in server.py or mcp.py
    if not hasattr(sys, '_original_stdout'):
        sys._original_stdout = sys.stdout
    sys.stdout = DevNullStdout()
    
    # Suppress SQLAlchemy deprecation warnings
    warnings.filterwarnings("ignore", category=DeprecationWarning, module="sqlalchemy")
    warnings.filterwarnings("ignore", category=DeprecationWarning)
    
    # Configure Python's logging module to prevent stdout pollution
    # FastMCP uses Python's logging module internally
    logging.basicConfig(
        level=logging.CRITICAL,  # Only show CRITICAL (suppress everything else)
        format="%(message)s",
        stream=sys.stderr,  # Send to stderr, not stdout
        force=True,  # Override any existing configuration
    )
    
    # Suppress ALL loggers to prevent any output
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.CRITICAL)
    root_logger.handlers = []
    
    # Suppress FastMCP and other noisy loggers completely
    for logger_name in ['fastmcp', 'mcp', 'httpx', 'httpcore', 'h11', 'uvicorn', 'asyncio']:
        log = logging.getLogger(logger_name)
        log.setLevel(logging.CRITICAL)
        log.handlers = []
        log.propagate = False
    
    # NUCLEAR OPTION: Completely disable loguru during stdio mode
    try:
        # Create a complete no-op logger class
        class NoOpLogger:
            """Complete no-op logger that does nothing - nuclear option for stdio mode."""
            def __call__(self, *args, **kwargs):
                return self
            def info(self, *args, **kwargs): pass
            def error(self, *args, **kwargs): pass
            def warning(self, *args, **kwargs): pass
            def debug(self, *args, **kwargs): pass
            def exception(self, *args, **kwargs): pass
            def critical(self, *args, **kwargs): pass
            def success(self, *args, **kwargs): pass
            def trace(self, *args, **kwargs): pass
            def remove(self, *args, **kwargs): return self
            def add(self, *args, **kwargs): return self
            def disable(self, *args, **kwargs): return self
            def enable(self, *args, **kwargs): return self
            def bind(self, *args, **kwargs): return self
            def patch(self, *args, **kwargs): return self
            def opt(self, *args, **kwargs): return self
        
        # Replace loguru logger module with no-op
        import sys
        if 'loguru' not in sys.modules:
            sys.modules['loguru'] = type('Module', (), {'logger': NoOpLogger()})()
        from loguru import logger
        # Force replace the logger instance
        logger = NoOpLogger()
    except Exception:
        # If anything fails, create a no-op logger anyway
        class NoOpLogger:
            def __call__(self, *args, **kwargs): return self
            def info(self, *args, **kwargs): pass
            def error(self, *args, **kwargs): pass
            def warning(self, *args, **kwargs): pass
            def debug(self, *args, **kwargs): pass
            def exception(self, *args, **kwargs): pass
            def critical(self, *args, **kwargs): pass
            def success(self, *args, **kwargs): pass
            def trace(self, *args, **kwargs): pass
            def remove(self, *args, **kwargs): return self
            def add(self, *args, **kwargs): return self
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
mcp = FastMCP(
    name="Advanced Memory MCP",
    lifespan=app_lifespan,
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
    from advanced_memory.mcp import (
        prompts,  # noqa: F401
        resources,  # noqa: F401
    )

    # Import individual prompt modules to get function references
    # Import resources to get function references
    # Note: ai_assistant_guide is in prompts/ but is actually a resource
    from advanced_memory.mcp.prompts import (
        ai_assistant_guide,
        continue_conversation,
        recent_activity,
        search,
    )
    from advanced_memory.mcp.resources import project_info, prompt_templates

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


# Initialize prompts and resources when module is imported
_initialize_prompts_and_resources()
