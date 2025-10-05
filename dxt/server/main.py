#!/usr/bin/env python3
"""
Advanced Memory MCP Server Entry Point
Minimal entry point for MCPB package - dependencies installed by MCP client
"""

import os
import sys
from pathlib import Path

# Add the src directory to the Python path
# This assumes the MCP client will install the advanced-memory package
try:
    import advanced_memory
except ImportError:
    # If not installed as package, try to find src directory
    current_dir = Path(__file__).parent
    src_dir = current_dir.parent.parent / "src"
    if src_dir.exists():
        sys.path.insert(0, str(src_dir))
    else:
        raise ImportError(
            "Advanced Memory package not found. "
            "Please install with: pip install advanced-memory"
        )

from advanced_memory.mcp.server import mcp_server

if __name__ == "__main__":
    mcp_server.run()