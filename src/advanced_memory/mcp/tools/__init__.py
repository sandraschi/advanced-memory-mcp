"""MCP tools for Advanced Memory.

Following the FastMCP 3.2 GA Managed Namespace architecture.
Legacy portmanteau tools are no longer automatically registered here.
Tool registration is now managed by mounting domain-specific sub-apps in server.py.
"""

# Export common utilities if needed
from .utils import build_error_response, build_success_response

# Standalone functions can still be imported for internal use,
# but automatic registration via imports here is disabled.

__all__ = [
    "build_error_response",
    "build_success_response",
]
