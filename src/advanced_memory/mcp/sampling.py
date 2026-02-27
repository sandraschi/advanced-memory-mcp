"""
FastMCP 2.14.1+ Sampling — NOTE: This module is OBSOLETE.

The SamplingClient wrapper tried to access mcp.ctx which does not exist.
FastMCP injects Context via the 'ctx: Context' parameter on tool functions.
Call ctx.sample() directly inside your tool.  See inter_server_tools.py.
"""

# Kept as empty stub so any stale import doesn't crash the server at startup.
