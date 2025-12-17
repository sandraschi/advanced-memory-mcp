"""MCP server command with streamable HTTP transport."""

import asyncio

import typer
from loguru import logger

# Import prompts to register them
import advanced_memory.mcp.prompts  # noqa: F401  # pragma: no cover

# Import mcp tools to register them
import advanced_memory.mcp.tools  # noqa: F401  # pragma: no cover
from advanced_memory.cli.app import app
from advanced_memory.config import ConfigManager

# Import mcp instance
from advanced_memory.mcp.server import mcp as mcp_server  # pragma: no cover


@app.command()
def mcp(
    transport: str = typer.Option("stdio", help="Transport type: stdio, streamable-http, or sse"),
    host: str = typer.Option(  # nosec B104 - binding to 0.0.0.0 is intentional for LAN access
        "0.0.0.0", help="Host for HTTP transports (use 0.0.0.0 to allow external connections)"
    ),
    port: int = typer.Option(8000, help="Port for HTTP transports"),
    path: str = typer.Option("/mcp", help="Path prefix for streamable-http transport"),
):  # pragma: no cover
    """Run the MCP server with configurable transport options.

    This command starts an MCP server using one of three transport options:

    - stdio: Standard I/O (good for local usage)
    - streamable-http: Recommended for web deployments (default)
    - sse: Server-Sent Events (for compatibility with existing clients)
    """

    # Use unified thread-based sync approach for both transports
    import threading

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
    
    if app_config.sync_changes:
        # Start the sync thread
        sync_thread = threading.Thread(target=run_file_sync, daemon=True)
        sync_thread.start()
        if transport != "stdio":
            logger.info("Started file sync in background")

    # Now run the MCP server (blocks)
    if transport == "stdio":
        # Restore stdout before FastMCP.run() - FastMCP needs it for JSON-RPC communication
        # The stdout was patched in mcp_instance.py/server.py during imports
        import sys
        import os
        if hasattr(sys, '_original_stdout'):
            # Flush any buffered output from the null device
            sys.stdout.flush()
            # Restore original stdout
            sys.stdout = sys._original_stdout
            # Ensure stdout is clean and unbuffered for JSON-RPC
            sys.stdout.flush()
            # Set unbuffered mode to prevent any buffering issues
            os.environ.setdefault('PYTHONUNBUFFERED', '1')
        
        mcp_server.run(
            transport=transport,
            show_banner=False,  # CRITICAL: Suppress banner to prevent stdout pollution
        )
    elif transport == "streamable-http" or transport == "sse":
        mcp_server.run(
            transport=transport,
            host=host,
            port=port,
            path=path,
            log_level="INFO",
        )
