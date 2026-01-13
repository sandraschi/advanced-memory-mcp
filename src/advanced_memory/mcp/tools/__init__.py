"""MCP tools for Advanced Memory.

This package provides the complete set of tools for interacting with
Advanced Memory through the MCP protocol. Importing this module registers
all tools with the MCP server.

The tools are organized into portmanteau tools for better Cursor IDE compatibility,
reducing the total number of tools while maintaining full functionality and clear
conceptual boundaries.

Tool Exposure Modes:
- PORTMANTEAU MODE (default): 15 well-organized portmanteau tools
- FULL MODE (opt-in): All ~56 tools (set ADVANCED_MEMORY_FULL_TOOLS_MODE=true)

Recent Changes (v1.1.0):
- Audio operations (dictate, speak) extracted to adn_audio tool
- Typora editor exposed as standalone typora_control (for skill editing)
- Canvas creation exposed as standalone canvas tool
- Notepad++ integration removed (use notepadpp-mcp server)
- adn_editor portmanteau deprecated (empty after extractions)
"""

import os

# Check for full tools mode (opt-in)
_FULL_TOOLS_MODE = os.getenv("ADVANCED_MEMORY_FULL_TOOLS_MODE", "false").lower() in (
    "true",
    "1",
    "yes",
)

# CRITICAL FIX: Conditional imports control MCP registration
# FastMCP registers tools when IMPORTED, not from __all__!

if _FULL_TOOLS_MODE:
    # FULL MODE: Import ALL tools (~56 total)
    from .adn_audio import adn_audio
    from .adn_editor import adn_editor
    from .adn_export import adn_export
    from .adn_import import adn_import
    from .adn_inbox import adn_inbox
    from .adn_knowledge import adn_knowledge
    from .adn_llm import adn_llm
    from .adn_navigation import adn_navigation
    from .adn_search import adn_search
    from .adn_skills import adn_skills
    from .adn_skills_creator import adn_skills_creator
    from .build_context import build_context
    from .canvas import canvas
    from .content_manager import adn_content
    from .delete_note import delete_note
    from .edit_in_notepadpp import edit_in_notepadpp, import_from_notepadpp
    from .edit_note import edit_note
    from .export_docsify import export_docsify
    from .export_html_notes import export_html_notes
    from .export_joplin_notes import export_joplin_notes
    from .export_pandoc import export_pandoc
    from .export_to_archive import export_to_archive
    from .help import help
    from .import_from_archive import import_from_archive
    from .knowledge_operations import knowledge_operations
    from .list_directory import list_directory
    from .load_canvas import load_obsidian_canvas
    from .load_evernote_export import load_evernote_export
    from .load_joplin_vault import load_joplin_vault
    from .load_notion_export import load_notion_export
    from .load_obsidian_vault import load_obsidian_vault
    from .make_pdf_book import make_pdf_book
    from .move_note import move_note
    from .project_management import (
        create_memory_project,
        delete_project,
        get_current_project,
        list_memory_projects,
        set_default_project,
        switch_project,
    )
    from .project_manager import adn_project
    from .read_content import read_content
    from .read_note import read_note
    from .recent_activity import recent_activity
    from .research_orchestrator import research_orchestrator
    from .search import search_notes
    from .search_evernote_vault import search_evernote_vault
    from .search_joplin_vault import search_joplin_vault
    from .search_notion_vault import search_notion_vault
    from .search_obsidian_vault import search_obsidian_vault
    from .status import status
    from .sync_status import sync_status
    from .typora_control import typora_control
    from .view_note import view_note
    from .view_note_rendered import view_note_rendered
    from .write_note import write_note
    from .zettelmaker import adn_zettelmaker
else:
    # PORTMANTEAU MODE (default): Import ONLY 15 portmanteau tools
    from .adn_audio import adn_audio
    from .adn_export import adn_export
    from .adn_import import adn_import
    from .adn_inbox import adn_inbox
    from .adn_knowledge import adn_knowledge
    from .adn_llm import adn_llm
    from .adn_navigation import adn_navigation
    from .adn_search import adn_search
    from .adn_skills import adn_skills
    from .adn_skills_creator import adn_skills_creator
    from .canvas import canvas
    from .content_manager import adn_content
    from .help import help
    from .inter_server_tools import (
        orchestrate_batch_content_operation,
        chain_server_operations,
        server_federation_status,
    )
    from .project_manager import adn_project
    from .typora_control import typora_control
    from .view_note_rendered import view_note_rendered
    from .zettelmaker import adn_zettelmaker

# Simple __all__ export
__all__ = [
    "help",
    "canvas",
    "typora_control",
    "view_note_rendered",
    "adn_content",
    "adn_search",
    "adn_export",
    "adn_import",
    "adn_audio",
    "adn_knowledge",
    "adn_llm",
    "adn_zettelmaker",
    "adn_skills",
    "adn_skills_creator",
    "adn_navigation",
    "adn_project",
    "adn_inbox",
    "orchestrate_batch_content_operation",
    "chain_server_operations",
    "server_federation_status",
]
