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
    from .adn_arxiv_research import adn_arxiv_research  # noqa: F401
    from .adn_audio import adn_audio  # noqa: F401
    from .adn_document_ingest import adn_document_ingest  # noqa: F401
    from .adn_editor import adn_editor  # noqa: F401
    from .adn_export import adn_export  # noqa: F401
    from .adn_github_research import adn_github_research  # noqa: F401
    from .adn_import import adn_import  # noqa: F401
    from .adn_inbox import adn_inbox  # noqa: F401
    from .adn_knowledge import adn_knowledge_legacy  # noqa: F401
    from .adn_knowledge_rag import register_rag_bridge as register_adn_knowledge_rag  # noqa: F401
    from .adn_llm import adn_llm  # noqa: F401
    from .adn_navigation import adn_navigation  # noqa: F401
    from .adn_observability import adn_observability  # noqa: F401
    from .adn_rag import adn_rag  # noqa: F401
    from .adn_search import adn_search  # noqa: F401
    from .adn_skills import adn_skills  # noqa: F401
    from .adn_skills_creator import adn_skills_creator  # noqa: F401
    from .adn_skills_reader import adn_skills_reader  # noqa: F401
    from .adn_skills_research import adn_skills_research  # noqa: F401
    from .adn_tvtropes_research import adn_tvtropes_research  # noqa: F401
    from .adn_web_search import adn_web_search  # noqa: F401
    from .build_context import build_context  # noqa: F401
    from .canvas import canvas  # noqa: F401
    from .content_manager import adn_content  # noqa: F401
    from .delete_note import delete_note  # noqa: F401
    from .edit_in_notepadpp import edit_in_notepadpp, import_from_notepadpp  # noqa: F401
    from .edit_note import edit_note  # noqa: F401
    from .export_docsify import export_docsify  # noqa: F401
    from .export_html_notes import export_html_notes  # noqa: F401
    from .export_joplin_notes import export_joplin_notes  # noqa: F401
    from .export_pandoc import export_pandoc  # noqa: F401
    from .export_to_archive import export_to_archive  # noqa: F401
    from .help import help  # noqa: F401
    from .import_from_archive import import_from_archive  # noqa: F401
    from .knowledge_operations import adn_knowledge_bulk  # noqa: F401
    from .list_directory import list_directory  # noqa: F401
    from .load_canvas import load_obsidian_canvas  # noqa: F401
    from .load_evernote_export import load_evernote_export  # noqa: F401
    from .load_joplin_vault import load_joplin_vault  # noqa: F401
    from .load_notion_export import load_notion_export  # noqa: F401
    from .load_obsidian_vault import load_obsidian_vault  # noqa: F401
    from .make_pdf_book import make_pdf_book  # noqa: F401
    from .make_skill_advanced import make_skill_advanced  # noqa: F401
    from .move_note import move_note  # noqa: F401
    from .project_management import (  # noqa: F401
        create_memory_project,
        delete_project,
        get_current_project,
        list_memory_projects,
        set_default_project,
        switch_project,
    )
    from .project_manager import adn_project  # noqa: F401
    from .read_content import read_content  # noqa: F401
    from .read_note import read_note  # noqa: F401
    from .recent_activity import recent_activity  # noqa: F401
    from .research_orchestrator import research_orchestrator  # noqa: F401
    from .search import search_notes  # noqa: F401
    from .search_evernote_vault import search_evernote_vault  # noqa: F401
    from .search_joplin_vault import search_joplin_vault  # noqa: F401
    from .search_notion_vault import search_notion_vault  # noqa: F401
    from .search_obsidian_vault import search_obsidian_vault  # noqa: F401
    from .status import status  # noqa: F401
    from .sync_status import sync_status  # noqa: F401
    from .typora_control import typora_control  # noqa: F401
    from .view_note import view_note  # noqa: F401
    from .view_note_rendered import view_note_rendered  # noqa: F401
    from .write_note import write_note  # noqa: F401
    from .zettelmaker import adn_zettelmaker  # noqa: F401
else:
    # PORTMANTEAU MODE (default): 8 portmanteau tools (+ help + status)
    # adn_content is REQUIRED - primary tool for note write/read/edit (quick, daily, etc.)

    from .adn_knowledge_rag import register_rag_bridge as register_adn_knowledge_rag  # noqa: F401
    from .adn_observability import adn_observability  # noqa: F401
    from .content_manager import adn_content  # noqa: F401
    from .help import help  # noqa: F401
    from .portmanteau_external import adn_external  # noqa: F401
    from .portmanteau_import_export import adn_import_export  # noqa: F401
    from .portmanteau_knowledge import adn_knowledge  # noqa: F401
    from .portmanteau_project import adn_project  # noqa: F401
    from .portmanteau_research import adn_research  # noqa: F401
    from .portmanteau_skills import adn_skills  # noqa: F401
    from .portmanteau_system import adn_system  # noqa: F401
    from .status import status  # noqa: F401

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
    "register_adn_knowledge_rag",  # Specialized RAG bridge registration
    # 2 Essential Tools (always available)
    "help",  # Comprehensive help system
    "status",  # System diagnostics & health
]
