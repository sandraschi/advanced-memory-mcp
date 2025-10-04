"""MCP tools for Advanced Memory.

This package provides the complete set of tools for interacting with
Advanced Memory through the MCP protocol. Importing this module registers
all tools with the MCP server.

The tools are organized into portmanteau tools for better Cursor IDE compatibility,
reducing the total number of tools while maintaining full functionality.
"""

# Import portmanteau tools (consolidated for Cursor IDE compatibility)
from advanced_memory.mcp.tools.content_manager import adn_content
from advanced_memory.mcp.tools.project_manager import adn_project
from advanced_memory.mcp.tools.adn_export import adn_export
from advanced_memory.mcp.tools.adn_import import adn_import
from advanced_memory.mcp.tools.adn_search import adn_search
from advanced_memory.mcp.tools.adn_knowledge import adn_knowledge
from advanced_memory.mcp.tools.adn_navigation import adn_navigation
from advanced_memory.mcp.tools.adn_editor import adn_editor

# Import legacy individual tools (for backward compatibility)
from advanced_memory.mcp.tools.delete_note import delete_note
from advanced_memory.mcp.tools.read_content import read_content
from advanced_memory.mcp.tools.build_context import build_context
from advanced_memory.mcp.tools.recent_activity import recent_activity
from advanced_memory.mcp.tools.read_note import read_note
from advanced_memory.mcp.tools.view_note import view_note
from advanced_memory.mcp.tools.write_note import write_note
from advanced_memory.mcp.tools.search import search_notes
from advanced_memory.mcp.tools.canvas import canvas
from advanced_memory.mcp.tools.export_docsify import export_docsify
from advanced_memory.mcp.tools.export_html_notes import export_html_notes
from advanced_memory.mcp.tools.export_joplin_notes import export_joplin_notes
from advanced_memory.mcp.tools.edit_in_notepadpp import edit_in_notepadpp, import_from_notepadpp
from advanced_memory.mcp.tools.export_pandoc import export_pandoc
from advanced_memory.mcp.tools.make_pdf_book import make_pdf_book
from advanced_memory.mcp.tools.export_to_archive import export_to_archive
from advanced_memory.mcp.tools.import_from_archive import import_from_archive
from advanced_memory.mcp.tools.knowledge_operations import knowledge_operations
from advanced_memory.mcp.tools.research_orchestrator import research_orchestrator
from advanced_memory.mcp.tools.load_canvas import load_obsidian_canvas
from advanced_memory.mcp.tools.load_joplin_vault import load_joplin_vault
from advanced_memory.mcp.tools.load_evernote_export import load_evernote_export
from advanced_memory.mcp.tools.load_notion_export import load_notion_export
from advanced_memory.mcp.tools.load_obsidian_vault import load_obsidian_vault
from advanced_memory.mcp.tools.search_evernote_vault import search_evernote_vault
from advanced_memory.mcp.tools.search_joplin_vault import search_joplin_vault
from advanced_memory.mcp.tools.search_notion_vault import search_notion_vault
from advanced_memory.mcp.tools.search_obsidian_vault import search_obsidian_vault
from advanced_memory.mcp.tools.list_directory import list_directory
from advanced_memory.mcp.tools.edit_note import edit_note
from advanced_memory.mcp.tools.help import help
from advanced_memory.mcp.tools.move_note import move_note
from advanced_memory.mcp.tools.status import status
from advanced_memory.mcp.tools.sync_status import sync_status
from advanced_memory.mcp.tools.typora_control import typora_control
from advanced_memory.mcp.tools.project_management import (
    list_memory_projects,
    switch_project,
    get_current_project,
    set_default_project,
    create_memory_project,
    delete_project,
)

# Portmanteau tools (recommended for Cursor IDE - reduces tool count)
__all__ = [
    # Complete portmanteau tool suite (8 tools total)
    "adn_content",          # Consolidates: write_note, read_note, view_note, edit_note, move_note, delete_note
    "adn_project",          # Consolidates: create_memory_project, switch_project, get_current_project, set_default_project, delete_project, list_memory_projects
    "adn_export",           # Consolidates: export_pandoc, export_docsify, export_html_notes, export_joplin_notes, make_pdf_book, export_to_archive, export_evernote_compatible, export_notion_compatible
    "adn_import",           # Consolidates: load_obsidian_vault, load_joplin_vault, load_notion_export, load_evernote_export, import_from_archive, load_obsidian_canvas
    "adn_search",           # Consolidates: search_notes, search_obsidian_vault, search_joplin_vault, search_notion_vault, search_evernote_vault
    "adn_knowledge",        # Consolidates: knowledge_operations, research_orchestrator
    "adn_navigation",       # Consolidates: build_context, recent_activity, list_directory, status, sync_status
    "adn_editor",           # Consolidates: edit_in_notepadpp, import_from_notepadpp, typora_control, canvas, read_content
    
    # Legacy individual tools (for backward compatibility)
    "build_context",
    "canvas",
    "create_memory_project",
    "edit_in_notepadpp",
    "export_docsify",
    "export_html_notes",
    "export_joplin_notes",
    "export_pandoc",
    "export_to_archive",
    "import_from_archive",
    "import_from_notepadpp",
    "knowledge_operations",
    "make_pdf_book",
    "research_orchestrator",
    "load_evernote_export",
    "load_joplin_vault",
    "load_notion_export",
    "load_obsidian_canvas",
    "load_obsidian_vault",
    "search_evernote_vault",
    "search_joplin_vault",
    "search_notion_vault",
    "search_obsidian_vault",
    "delete_note",
    "delete_project",
    "edit_note",
    "get_current_project",
    "help",
    "list_directory",
    "list_memory_projects",
    "move_note",
    "read_content",
    "read_note",
    "recent_activity",
    "search_notes",
    "set_default_project",
    "status",
    "switch_project",
    "sync_status",
    "typora_control",
    "view_note",
    "write_note",
]
