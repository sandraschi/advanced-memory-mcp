"""Advanced Memory MCP resources.

Resources provide read-only access to structured data via URI strings.
They return JSON or other string formats and are accessed via memory:// URIs.
"""

# Import individual resource modules to register them with the MCP server
from advanced_memory.mcp.resources import project_info, prompt_templates

__all__ = [
    "project_info",
    "prompt_templates",
]
