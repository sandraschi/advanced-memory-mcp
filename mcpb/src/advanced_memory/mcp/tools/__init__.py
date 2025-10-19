"""MCP tools for Advanced Memory (MCPB Edition - Portmanteau Tools Only).

This MCPB-specific version imports ONLY portmanteau tools for Cursor IDE compatibility.
The standard Python package includes both portmanteau and individual tools.

Portmanteau tools consolidate 40+ individual tools into 10 comprehensive tools,
staying well within Cursor IDE's 50-tool limit while maintaining full functionality.
"""

# Import ONLY portmanteau tools (10 total for Cursor IDE compatibility)
from advanced_memory.mcp.tools.adn_editor import adn_editor
from advanced_memory.mcp.tools.adn_export import adn_export
from advanced_memory.mcp.tools.adn_import import adn_import
from advanced_memory.mcp.tools.adn_inbox import adn_inbox
from advanced_memory.mcp.tools.adn_knowledge import adn_knowledge
from advanced_memory.mcp.tools.adn_navigation import adn_navigation
from advanced_memory.mcp.tools.adn_search import adn_search
from advanced_memory.mcp.tools.content_manager import adn_content
from advanced_memory.mcp.tools.project_manager import adn_project
from advanced_memory.mcp.tools.zettelmaker import adn_zettelmaker

# MCPB exports ONLY portmanteau tools (10 total)
__all__ = [
    "adn_content",      # Content management (write, read, edit, move, delete, view)
    "adn_project",      # Project management (create, switch, list, status, etc.)
    "adn_zettelmaker",  # Zettelkasten generation and management
    "adn_inbox",        # Inbox file drop processing
    "adn_export",       # Export operations (pandoc, docsify, html, pdf, archive)
    "adn_import",       # Import operations (Obsidian, Joplin, Notion, Evernote)
    "adn_search",       # Search across knowledge base and external systems
    "adn_knowledge",    # Knowledge operations and research orchestration
    "adn_navigation",   # Navigate and explore knowledge base
    "adn_editor",       # Editor integration (Notepad++, Typora, etc.)
]
