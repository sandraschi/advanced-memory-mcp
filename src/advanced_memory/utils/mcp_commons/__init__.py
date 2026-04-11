"""MCP Commons - Shared utilities for MCP servers.

Bulletproof components:
- sync_health: Health monitoring and stall detection
- file_validator: Robust file validation
- link_parser: Timeout-safe link parsing
"""

from .file_validator import FileValidator, validate_markdown_file
from .link_parser import LinkParser, parse_links_safe
from .sync_health import SyncHealthMonitor, SyncMetrics, SyncState

__version__ = "1.0.0"
__all__ = [
    "FileValidator",
    "LinkParser",
    "SyncHealthMonitor",
    "SyncMetrics",
    "SyncState",
    "parse_links_safe",
    "validate_markdown_file",
]
