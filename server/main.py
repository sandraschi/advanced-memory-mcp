#!/usr/bin/env python3
"""
Advanced Memory MCP Server - DXT Package Entry Point

This is the main entry point for the Advanced Memory MCP server when packaged as a DXT file.
It provides a streamlined interface that can be configured via the DXT manifest.json.
"""

import asyncio
import logging
import os
import sys
from pathlib import Path
from typing import Optional

# Add the src directory to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from fastmcp import FastMCP
from advanced_memory.mcp.server import create_mcp_server
from advanced_memory.config import AdvancedMemoryConfig

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_user_config() -> dict:
    """Get user configuration from environment variables set by DXT."""
    return {
        "project_path": os.getenv("DXT_USER_PROJECT_PATH", "~/Documents/advanced-memory"),
        "enable_portmanteau_tools": os.getenv("DXT_USER_ENABLE_PORTMANTEAU_TOOLS", "true").lower() == "true",
        "max_tools": int(os.getenv("DXT_USER_MAX_TOOLS", "50")),
    }

def create_advanced_memory_mcp() -> FastMCP:
    """Create and configure the Advanced Memory MCP server."""
    logger.info("Initializing Advanced Memory MCP Server (DXT Package)")
    
    # Get user configuration
    user_config = get_user_config()
    logger.info(f"User configuration: {user_config}")
    
    # Create MCP server
    mcp = FastMCP("Advanced Memory MCP")
    
    # Set up configuration
    config = AdvancedMemoryConfig()
    
    # Override project path if provided
    if user_config["project_path"]:
        project_path = Path(user_config["project_path"]).expanduser()
        config.home = project_path
        logger.info(f"Using project path: {project_path}")
    
    # Create the actual MCP server with our tools
    server = create_mcp_server(config)
    
    # Add all tools from the server to our FastMCP instance
    for tool in server.tools:
        mcp.tools.append(tool)
    
    # Add resources if any
    if hasattr(server, 'resources'):
        for resource in server.resources:
            mcp.resources.append(resource)
    
    # Add prompts if any
    if hasattr(server, 'prompts'):
        for prompt in server.prompts:
            mcp.prompts.append(prompt)
    
    logger.info(f"Advanced Memory MCP Server initialized with {len(mcp.tools)} tools")
    
    # Log tool information
    if user_config["enable_portmanteau_tools"]:
        portmanteau_tools = [tool.name for tool in mcp.tools if tool.name.startswith("adn_")]
        logger.info(f"Portmanteau tools enabled: {portmanteau_tools}")
    else:
        legacy_tools = [tool.name for tool in mcp.tools if not tool.name.startswith("adn_")]
        logger.info(f"Legacy tools enabled: {legacy_tools}")
    
    return mcp

def main():
    """Main entry point for the DXT package."""
    try:
        # Create the MCP server
        mcp = create_advanced_memory_mcp()
        
        # Run the server
        logger.info("Starting Advanced Memory MCP Server...")
        mcp.run()
        
    except Exception as e:
        logger.error(f"Failed to start Advanced Memory MCP Server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
