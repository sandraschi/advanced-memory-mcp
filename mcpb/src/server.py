"""
ASGI entry point for uvicorn (webapp backend).

Usage:
    uv run uvicorn advanced_memory.server:app --port 10705
"""

from advanced_memory.api.app import app

__all__ = ["app"]
