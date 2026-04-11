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
    """Guard stdio mode with a process lock on Windows (opt-out via env)."""
    if os.getenv("ADVANCED_MEMORY_STDIN_SINGLE_INSTANCE", "1") != "1":
        yield
        return

    lock_path = Path(os.getenv("ADVANCED_MEMORY_HOME", str(Path.home()))) / ".advanced-memory" / "mcp-stdio.lock"
    lock_path.parent.mkdir(parents=True, exist_ok=True)

    if os.name == "nt":
        import msvcrt

        # Use 'r+' to read/write if exists, or 'w+' to create
        mode = "r+b" if lock_path.exists() else "w+b"
        lock_file = open(lock_path, mode)
        try:
            # Try to acquire a non-blocking lock on the first byte
            msvcrt.locking(lock_file.fileno(), msvcrt.LK_NBLCK, 1)

            # Successfully locked! Write our PID for diagnostics
            lock_file.seek(0)
            lock_file.truncate()
            lock_file.write(str(os.getpid()).encode())
            lock_file.flush()
        except OSError as e:
            # Lock failed. Try to read the PID of the holder
            holder_pid = "Unknown"
            try:
                lock_file.seek(0)
                content = lock_file.read().decode().strip()
                if content.isdigit():
                    holder_pid = content
            except Exception:
                pass

            logger.error(
                f"advanced-memory stdio already running (PID: {holder_pid}, lock: {lock_path}). "
                "Close the other instance or set ADVANCED_MEMORY_STDIN_SINGLE_INSTANCE=0."
            )
            lock_file.close()
            raise typer.Exit(1) from e
        try:
            yield
        finally:
            try:
                # Clean up: clear PID and unlock
                lock_file.seek(0)
                lock_file.truncate()
                msvcrt.locking(lock_file.fileno(), msvcrt.LK_UNLCK, 1)
            finally:
                lock_file.close()
                # Try to remove the file if we are the last ones out
                with contextlib.suppress(OSError):
                    lock_path.unlink()
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
        import os
        import sys

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
