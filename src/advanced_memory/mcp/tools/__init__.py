"""MCP tools for Advanced Memory - Portmanteau architecture.

Default mode: portmanteau tools only (reduced tool count for Claude Desktop).
Full mode: all tools via ADVANCED_MEMORY_FULL_TOOLS_MODE=true env var.

FastMCP registers tools at IMPORT time via @mcp.tool decorator.
"""

import os

from .adn_knowledge_rag import register_rag_bridge as register_adn_knowledge_rag

# ── HELP TOOL (always imported) ───────────────────────────────────────────────
from .help import help
from .portmanteau_external import adn_external
from .portmanteau_import_export import adn_import_export

# ── PORTMANTEAU TOOLS (always imported) ──────────────────────────────────────
# These are the 6 consolidated tools visible in Claude Desktop by default.
from .portmanteau_knowledge import adn_knowledge
from .portmanteau_research import adn_research
from .portmanteau_skills import adn_skills
from .portmanteau_system import adn_system

# ── FULL TOOLS MODE (opt-in) ──────────────────────────────────────────────────
# Set ADVANCED_MEMORY_FULL_TOOLS_MODE=true to expose all individual tools.

if os.getenv("ADVANCED_MEMORY_FULL_TOOLS_MODE", "").lower() == "true":
    from .adn_audio import adn_audio
    from .adn_document_ingest import adn_document_ingest
    from .adn_editor import adn_editor
    from .adn_export import adn_export
    from .adn_import import adn_import
    from .adn_inbox import adn_inbox
    from .adn_knowledge import adn_knowledge_legacy
    from .adn_llm import adn_llm
    from .adn_navigation import adn_navigation
    from .adn_observability import adn_observability
    from .adn_rag import adn_rag
    from .adn_skills import adn_skills as _adn_skills_full
    from .adn_skills_creator import adn_skills_creator
    from .adn_skills_operations_new import adn_skills_operations
    from .adn_skills_reader import adn_skills_reader
    from .adn_skills_research import adn_skills_research
    from .build_context import build_context
    from .canvas import canvas
    from .delete_note import delete_note
    from .edit_note import edit_note
    from .external_mcp_clients import call_external_mcp_tool, list_external_mcp_tools, skeleton_key
    from .inter_server_tools import agentic_content_workflow
    from .knowledge_operations import adn_knowledge_bulk
    from .list_directory import list_directory
    from .move_note import move_note
    from .project_management import (
        create_memory_project,
        get_current_project,
        list_memory_projects,
        set_default_project,
        switch_project,
    )
    from .project_manager import adn_project
    from .read_note import read_note
    from .recent_activity import recent_activity
    from .research_orchestrator import research_orchestrator
    from .search import search_notes
    from .search import search_notes as _search_notes_full
    from .status import status
    from .sync_status import sync_status
    from .typora_control import typora_control
    from .write_note import write_note
    from .zettelmaker import adn_zettelmaker

__all__ = [
    "adn_external",
    "adn_import_export",
    "adn_knowledge",
    "adn_research",
    "adn_skills",
    "adn_system",
    "help",
    "register_adn_knowledge_rag",
]
