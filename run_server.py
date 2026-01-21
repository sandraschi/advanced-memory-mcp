#!/usr/bin/env python3
"""
Simple script to run the Advanced Memory MCP server
"""

import os
import sys

# Add src to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

try:
    from advanced_memory.cli.main import app

    # Run MCP server with HTTP transport
    app(["mcp", "--transport", "streamable-http", "--port", "8000"])
except ImportError as e:
    print(f"Import error: {e}")
    print("Make sure the package is installed with: pip install -e .")
    sys.exit(1)
except Exception as e:
    print(f"Error running server: {e}")
    sys.exit(1)
