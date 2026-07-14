"""MCP server command with streamable HTTP transport."""

import asyncio
import contextlib
import os
from pathlib import Path

import typer
from loguru import logger

# Import prompts to register them
import advanced_memory.mcp.prompts  # pragma: no cover

# Import mcp tools to register them
import advanced_memory.mcp.tools  # pragma: no cover
from advanced_memory.cli.app import app
from advanced_memory.config import ConfigManager

# Import mcp instance
from advanced_memory.mcp.server import mcp as mcp_server  # pragma: no cover


@contextlib.contextmanager
def _stdio_single_instance_lock():
    """Guard stdio mode with a named mutex on Windows (auto-releases on process death)."""
    if os.getenv("ADVANCED_MEMORY_STDIN_SINGLE_INSTANCE", "1") != "1":
        yield
        return

    if os.name == "nt":
        import ctypes

        ERROR_ALREADY_EXISTS = 183
        mutex_name = "Local\\AdvancedMemoryMCP-0a3f7b"

        kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
        handle = kernel32.CreateMutexW(None, True, mutex_name)
        error = ctypes.get_last_error()

        if handle and error == 0:
            try:
                yield
            finally:
                kernel32.ReleaseMutex(handle)
                kernel32.CloseHandle(handle)
        elif error == ERROR_ALREADY_EXISTS:
            logger.error("advanced-memory stdio already running (named mutex detected)")
            raise typer.Exit(1)
        else:
            yield
    else:
        yield


@app.command()
def mcp(
    transport: str = typer.Option("stdio", help="Transport type: stdio, streamable-http, or sse"),
    host: str = typer.Option(  # nosec B104 - binding to 0.0.0.0 is intentional for LAN access
        "0.0.0.0", help="Host for HTTP transports (use 0.0.0.0 to allow external connections)"
    ),
    port: int = typer.Option(8000, help="Port for HTTP transports"),
    path: str = typer.Option("/mcp", help="Path prefix for streamable-http transport"),
    agentic: bool = typer.Option(
        False,
        "--agentic",
        help=(
            "Enable agentic mode: apply CodeMode transform so all tools collapse into "
            "search+execute meta-tools. Intended for automated agent pipelines. "
            "Default off (interactive mode shows all portmanteau tools)."
        ),
    ),
):  # pragma: no cover
    """Run the MCP server with configurable transport options.

    This command starts an MCP server using one of three transport options:

    - stdio: Standard I/O (good for local usage, default)
    - streamable-http: Recommended for web deployments
    - sse: Server-Sent Events (for compatibility with existing clients)

    Use --agentic for automated agent pipelines (CodeMode: 2 meta-tools).
    Default (no --agentic) exposes all portmanteau tools for human use.
    """

    # Use unified thread-based sync approach for both transports
    import threading

    from advanced_memory.readonly import IS_READONLY
    from advanced_memory.services.initialization import initialize_file_sync

    app_config = ConfigManager().config

    def run_file_sync():
        """Run file sync in a separate thread with its own event loop."""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(initialize_file_sync(app_config))
        except Exception as e:
            logger.error(f"File sync error: {e}", err=True)
        finally:
            loop.close()

    # Configure logging based on transport mode
    import sys

    if transport == "stdio":
        # In stdio mode, suppress all logging to stdout to prevent JSON-RPC interference
        # Only critical errors go to stderr
        from loguru import logger as loguru_logger

        loguru_logger.remove()
        loguru_logger.add(sys.stderr, level="ERROR", format="{message}")
    else:
        # For HTTP transports, normal logging is fine
        logger.info(f"Sync changes enabled: {app_config.sync_changes}")

    if app_config.sync_changes and not IS_READONLY:
        # Start the sync thread (skipped in read-only mode)
        sync_thread = threading.Thread(target=run_file_sync, daemon=True)
        sync_thread.start()
        if transport != "stdio":
            logger.info("Started file sync in background")

    # Probe for existing HTTP memops if ADVANCED_MEMORY_HTTP_PROXY is explicitly set
    HTTP_PROXY_URL = os.getenv("ADVANCED_MEMORY_HTTP_PROXY")
    if HTTP_PROXY_URL and transport == "stdio":
        try:
            import httpx

            _probe = httpx.post(
                HTTP_PROXY_URL,
                json={
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "initialize",
                    "params": {
                        "protocolVersion": "2025-11-25",
                        "capabilities": {},
                        "clientInfo": {"name": "probe", "version": "1"},
                    },
                },
                headers={"Accept": "application/json, text/event-stream"},
                timeout=5.0,
            )
            if _probe.status_code == 200:
                from fastmcp.server import create_proxy

                logger.info(f"HTTP memops found at {HTTP_PROXY_URL} - proxying tool calls")
                _proxied = create_proxy(HTTP_PROXY_URL, name="Advanced Memory MCP")
                _proxied.run(transport="stdio")
                return
            else:
                logger.error(
                    f"HTTP proxy probe to {HTTP_PROXY_URL} returned status "
                    f"{_probe.status_code}, falling back to local instance"
                )
        except Exception as _probe_err:
            logger.error(
                f"HTTP proxy probe to {HTTP_PROXY_URL} failed ({_probe_err!r}), "
                f"falling back to local instance"
            )

    # Now run the MCP server (blocks)
    if transport == "stdio":
        # Restore stdout before FastMCP.run() - FastMCP needs it for JSON-RPC communication
        # The stdout was patched in mcp_instance.py/server.py during imports
        if hasattr(sys, "_original_stdout"):
            # Flush any buffered output from the null device
            sys.stdout.flush()
            # Restore original stdout
            sys.stdout = sys._original_stdout
            # Ensure stdout is clean and unbuffered for JSON-RPC
            sys.stdout.flush()
            # Set unbuffered mode to prevent any buffering issues
            os.environ.setdefault("PYTHONUNBUFFERED", "1")

        # Apply CodeMode AFTER imports, BEFORE run — only in agentic mode.
        # This collapses all tools into search+execute meta-tools for agents.
        # NEVER apply this in server.py module scope (breaks interactive use).
        if agentic:
            from fastmcp.experimental.transforms.code_mode import CodeMode

            mcp_server.add_transform(CodeMode())

        if IS_READONLY:
            # Read-only mode: bypass single-instance lock so multiple IDEs can connect
            mcp_server.run(
                transport=transport,
                show_banner=False,  # CRITICAL: Suppress banner to prevent stdout pollution
            )
        else:
            with _stdio_single_instance_lock():
                mcp_server.run(
                    transport=transport,
                    show_banner=False,  # CRITICAL: Suppress banner to prevent stdout pollution
                )
    elif transport == "streamable-http" or transport == "sse":
        # Apply CodeMode for HTTP transports too if agentic mode requested
        if agentic:
            from fastmcp.experimental.transforms.code_mode import CodeMode

            mcp_server.add_transform(CodeMode())

        mcp_server.run(
            transport=transport,
            host=host,
            port=port,
            path=path,
            log_level="INFO",
        )
