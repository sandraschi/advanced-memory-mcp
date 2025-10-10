"""Advanced Memory MCP prompts.

Prompts are a special type of tool that returns a string response
formatted for a user to read, typically invoking one or more tools
and transforming their results into user-friendly text.
"""

# Import individual prompt modules to register them with the MCP server
from advanced_memory.mcp.prompts import (
    ai_assistant_guide,
    continue_conversation,
    recent_activity,
    search,
)

__all__ = [
    "ai_assistant_guide",
    "continue_conversation",
    "recent_activity",
    "search",
]
