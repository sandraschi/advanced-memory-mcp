"""MCP tools for Basic Memory.

This package provides the complete set of tools for interacting with
Basic Memory through the MCP protocol. Importing this module registers
all tools with the MCP server.
"""

# Import tools to register them with MCP
from basic_memory.mcp.tools.delete_note import delete_note
from basic_memory.mcp.tools.read_content import read_content
from basic_memory.mcp.tools.build_context import build_context
from basic_memory.mcp.tools.recent_activity import recent_activity
from basic_memory.mcp.tools.read_note import read_note
from basic_memory.mcp.tools.view_note import view_note
from basic_memory.mcp.tools.write_note import write_note
from basic_memory.mcp.tools.search import search_notes
from basic_memory.mcp.tools.canvas import canvas
from basic_memory.mcp.tools.export_docsify import export_docsify
from basic_memory.mcp.tools.export_html_notes import export_html_notes
from basic_memory.mcp.tools.export_joplin_notes import export_joplin_notes
from basic_memory.mcp.tools.edit_in_notepadpp import edit_in_notepadpp, import_from_notepadpp
from basic_memory.mcp.tools.export_pandoc import export_pandoc
from basic_memory.mcp.tools.make_pdf_book import make_pdf_book
from basic_memory.mcp.tools.export_to_archive import export_to_archive
from basic_memory.mcp.tools.import_from_archive import import_from_archive
from basic_memory.mcp.tools.knowledge_operations import knowledge_operations
from basic_memory.mcp.tools.research_orchestrator import research_orchestrator
from basic_memory.mcp.tools.load_canvas import load_obsidian_canvas
from basic_memory.mcp.tools.load_joplin_vault import load_joplin_vault
from basic_memory.mcp.tools.load_evernote_export import load_evernote_export
from basic_memory.mcp.tools.load_notion_export import load_notion_export
from basic_memory.mcp.tools.load_obsidian_vault import load_obsidian_vault
from basic_memory.mcp.tools.search_evernote_vault import search_evernote_vault
from basic_memory.mcp.tools.search_joplin_vault import search_joplin_vault
from basic_memory.mcp.tools.search_notion_vault import search_notion_vault
from basic_memory.mcp.tools.search_obsidian_vault import search_obsidian_vault
from basic_memory.mcp.tools.list_directory import list_directory
from basic_memory.mcp.tools.edit_note import edit_note
from basic_memory.mcp.tools.help import help
from basic_memory.mcp.tools.move_note import move_note
from basic_memory.mcp.tools.status import status
from basic_memory.mcp.tools.sync_status import sync_status
from basic_memory.mcp.tools.typora_control import typora_control
from basic_memory.mcp.tools.project_management import (
    list_memory_projects,
    switch_project,
    get_current_project,
    set_default_project,
    create_memory_project,
    delete_project,
)

__all__ = [
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
