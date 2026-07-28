"""Advanced Memory MCP resources.

Resources provide read-only access to structured data via URI strings.
They return JSON or other string formats and are accessed via memory:// URIs.
"""

# Import individual resource modules to register them with the MCP server
from advanced_memory.mcp.resources import notes, project_info, prompt_templates, skills, status

__all__ = [
    "notes",
    "project_info",
    "prompt_templates",
    "skills",
    "status",
]
