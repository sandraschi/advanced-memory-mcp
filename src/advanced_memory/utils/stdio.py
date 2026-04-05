"""Stdio management utilities for MCP servers.

This module provides cross-platform utilities for managing stdin/stdout,
especially for Windows binary mode and suppressing output pollution.
"""

import logging
import os
import sys
import warnings


def setup_stdio_binary_mode():
    """Set stdin/stdout to binary mode on Windows.

    This is CRITICAL for Antigravity IDE compatibility to prevent JSON-RPC
    protocol corruption from automatic line ending conversion (\r\n).
    """
    if os.name == "nt":  # Windows
        try:
            import msvcrt

            # Set stdin/stdout to binary mode to prevent line ending conversion
            try:
                msvcrt.setmode(sys.stdin.fileno(), os.O_BINARY)
            except (OSError, AttributeError):
                pass
            try:
                msvcrt.setmode(sys.stdout.fileno(), os.O_BINARY)
            except (OSError, AttributeError):
                pass
        except (ImportError, OSError, AttributeError):
            pass


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


def suppress_nuclear_loguru():
    """Completely disable loguru via sys.modules patch."""
    try:
        # Replace loguru logger module with no-op
        if "loguru" not in sys.modules:
            sys.modules["loguru"] = type("Module", (), {"logger": NoOpLogger()})()
    except Exception:
        pass


class DevNullStdout:
    """A file-like object that discards all writes (like /dev/null)."""

    def write(self, s: str) -> int:
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


def suppress_stdout_pollution():
    """Patch sys.stdout and configure logging to prevent protocol corruption."""
    if not hasattr(sys, "_original_stdout"):
        sys._original_stdout = sys.stdout
    sys.stdout = DevNullStdout()

    # Suppress warnings
    warnings.filterwarnings("ignore", category=DeprecationWarning)

    # Configure Python logging to stderr-only
    logging.basicConfig(
        level=logging.CRITICAL,
        format="%(message)s",
        stream=sys.stderr,
        force=True,
    )

    # Suppress common noisy loggers
    for logger_name in ["fastmcp", "mcp", "httpx", "httpcore", "h11", "uvicorn", "asyncio"]:
        log = logging.getLogger(logger_name)
        log.setLevel(logging.CRITICAL)
        log.handlers = []
        log.propagate = False

    # Nucleare loguru suppression
    suppress_nuclear_loguru()


def restore_stdout():
    """Restore the original stdout."""
    if hasattr(sys, "_original_stdout"):
        sys.stdout = sys._original_stdout
