"""Backward-compatible shim for the legacy adn_project module.

The canonical project management tool now lives in project_manager.py,
but legacy imports still reference advanced_memory.mcp.tools.adn_project.
Re-export the main entry point to keep those imports working.
"""

from .project_manager import adn_project

__all__ = ["adn_project"]

