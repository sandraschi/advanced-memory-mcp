"""Read-only mode flag for Advanced Memory MCP.

When ADVANCED_MEMORY_READONLY=1, the server starts in read-only mode:
- The single-instance stdio lock is bypassed (multiple IDEs can connect)
- File sync is disabled
- The SQLite connection is opened read-only (writes raise an error)
- Mutating MCP tools return a clear error message instead of crashing

Usage in claude_desktop_config.json (secondary IDEs):
    "env": {"ADVANCED_MEMORY_READONLY": "1"}
"""

import os

IS_READONLY: bool = os.getenv("ADVANCED_MEMORY_READONLY", "0").strip() == "1"

READONLY_ERROR = (
    "This Advanced Memory instance is running in read-only mode "
    "(ADVANCED_MEMORY_READONLY=1). Use the primary instance to write notes."
)
