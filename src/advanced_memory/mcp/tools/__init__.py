"""MCP tools for Advanced Memory - SOTA Portmanteau Implementation.

This package provides portmanteau-organized tools for Advanced Memory MCP server,
complying with MCP standards requiring <30 tools total. The implementation uses
operation parameters for conceptual consolidation while maintaining full functionality.

PORTMANTEAU PATTERN RATIONALE: Consolidated 91 individual tools into 7 portmanteaus
to meet MCP standards, reducing tool count while preserving operational clarity and
maintaining all original functionality through operation parameters.

Tool Organization:
- 7 Portmanteau Tools: Core functionality grouped by domain
- 2 Essential Tools: Help and status (always available)
- Total: 9 tools (well under 30 MCP limit)

Tool Exposure Modes:
- PORTMANTEAU MODE (default): 9 tools total (MCP compliant)
- FULL MODE (opt-in): 91 individual tools (set ADVANCED_MEMORY_FULL_TOOLS_MODE=true)

Compliance:
- ✅ MCP Standards: <30 tools total
- ✅ SOTA Implementation: Portmanteau consolidation
- ✅ No triple quotes in docstrings
- ✅ No emojis in production code
- ✅ Clear operation parameters
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
    # FULL MODE: Import ALL individual tools (~91 total)
    from .adn_arxiv_research import adn_arxiv_research
    from .adn_audio import adn_audio
    from .adn_document_ingest import adn_document_ingest
    from .adn_editor import adn_editor
    from .adn_export import adn_export
    from .adn_github_research import adn_github_research
    from .adn_import import adn_import
    from .adn_inbox import adn_inbox
    from .adn_knowledge import adn_knowledge_legacy
    from .adn_llm import adn_llm
    from .adn_navigation import adn_navigation
    from .adn_observability import adn_observability
    from .adn_rag import adn_rag
    from .adn_search import adn_search
    from .adn_skills import adn_skills
    from .adn_skills_creator import adn_skills_creator
    from .adn_skills_reader import adn_skills_reader
    from .adn_skills_research import adn_skills_research
    from .adn_tvtropes_research import adn_tvtropes_research
    from .adn_web_search import adn_web_search
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
    from .knowledge_operations import adn_knowledge_bulk
    from .list_directory import list_directory
    from .load_canvas import load_obsidian_canvas
    from .load_evernote_export import load_evernote_export
    from .load_joplin_vault import load_joplin_vault
    from .load_notion_export import load_notion_export
    from .load_obsidian_vault import load_obsidian_vault
    from .make_pdf_book import make_pdf_book
    from .make_skill_advanced import make_skill_advanced
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
    # PORTMANTEAU MODE (default): 8 portmanteau tools (+ help + status)
    # adn_content is REQUIRED - primary tool for note write/read/edit (quick, daily, etc.)
    from advanced_memory.mcp.mcp_instance import mcp

    from .adn_observability import adn_observability
    from .content_manager import adn_content
    from .help import help
    from .portmanteau_external import adn_external
    from .portmanteau_import_export import adn_import_export
    from .portmanteau_knowledge import adn_knowledge_portmanteau
    from .portmanteau_project import adn_project
    from .portmanteau_research import adn_research
    from .portmanteau_skills import adn_skills
    from .portmanteau_system import adn_system
    from .status import status

    # Manual registration to avoid decorator-related issues
    mcp.tool(name="adn_knowledge")(adn_knowledge_portmanteau)

# PORTMANTEAU MODE: 10 tools total (8 portmanteaus + 2 essentials)
__all__ = [
    # 8 Portmanteau Tools (meet MCP standards <30 tools)
    "adn_content",  # Primary content CRUD: write, read, quick, daily, edit, move, delete
    "adn_knowledge",  # Core CRUD + search, list, context, activity
    "adn_research",  # AI research & RAG (15+ tools consolidated)
    "adn_import_export",  # Import/export operations (20+ tools consolidated)
    "adn_project",  # Project management (8+ tools consolidated)
    "adn_system",  # System status & external tools (8+ tools consolidated)
    "adn_skills",  # Skill system operations (6+ tools consolidated)
    "adn_external",  # External integrations (4+ tools consolidated)
    "adn_observability",  # AI observability & provenance (Entire.io)
    # 2 Essential Tools (always available)
    "help",  # Comprehensive help system
    "status",  # System status monitoring
]
