"""MCP tools for Advanced Memory - Portmanteau architecture.

Default mode: portmanteau tools only (reduced tool count for Claude Desktop).
Full mode: all tools via ADVANCED_MEMORY_FULL_TOOLS_MODE=true env var.

FastMCP registers tools at IMPORT time via @mcp.tool decorator.
"""

import os

from .adn_knowledge_rag import register_rag_bridge as register_adn_knowledge_rag  # noqa: F401

# ── PORTMANTEAU TOOLS (always imported) ──────────────────────────────────────
# These are the 6 consolidated tools visible in Claude Desktop by default.

from .portmanteau_knowledge import adn_knowledge  # noqa: F401
from .portmanteau_research import adn_research  # noqa: F401
from .portmanteau_skills import adn_skills  # noqa: F401
from .portmanteau_system import adn_system  # noqa: F401
from .portmanteau_external import adn_external  # noqa: F401
from .portmanteau_import_export import adn_import_export  # noqa: F401

# ── HELP TOOL (always imported) ───────────────────────────────────────────────
from .help import help  # noqa: F401

# ── FULL TOOLS MODE (opt-in) ──────────────────────────────────────────────────
# Set ADVANCED_MEMORY_FULL_TOOLS_MODE=true to expose all individual tools.

if os.getenv("ADVANCED_MEMORY_FULL_TOOLS_MODE", "").lower() == "true":
    from .adn_knowledge import adn_knowledge_legacy  # noqa: F401
    from .search import search_notes  # noqa: F401
    from .adn_rag import adn_rag  # noqa: F401
    from .adn_document_ingest import adn_document_ingest  # noqa: F401
    from .adn_llm import adn_llm  # noqa: F401
    from .adn_skills import adn_skills as _adn_skills_full  # noqa: F401
    from .adn_skills_reader import adn_skills_reader  # noqa: F401
    from .adn_skills_creator import adn_skills_creator  # noqa: F401
    from .adn_skills_operations_new import adn_skills_operations  # noqa: F401
    from .adn_skills_research import adn_skills_research  # noqa: F401
    from .adn_audio import adn_audio  # noqa: F401
    from .adn_inbox import adn_inbox  # noqa: F401
    from .adn_navigation import adn_navigation  # noqa: F401
    from .adn_observability import adn_observability  # noqa: F401
    from .adn_editor import adn_editor  # noqa: F401
    from .adn_export import adn_export  # noqa: F401
    from .adn_import import adn_import  # noqa: F401
    from .build_context import build_context  # noqa: F401
    from .canvas import canvas  # noqa: F401
    from .delete_note import delete_note  # noqa: F401
    from .edit_note import edit_note  # noqa: F401
    from .external_mcp_clients import skeleton_key, call_external_mcp_tool, list_external_mcp_tools  # noqa: F401
    from .inter_server_tools import agentic_content_workflow  # noqa: F401
    from .knowledge_operations import adn_knowledge_bulk  # noqa: F401
    from .list_directory import list_directory  # noqa: F401
    from .move_note import move_note  # noqa: F401
    from .project_management import list_memory_projects, switch_project, get_current_project, set_default_project, create_memory_project  # noqa: F401
    from .project_manager import adn_project  # noqa: F401
    from .read_note import read_note  # noqa: F401
    from .recent_activity import recent_activity  # noqa: F401
    from .research_orchestrator import research_orchestrator  # noqa: F401
    from .search import search_notes as _search_notes_full  # noqa: F401
    from .status import status  # noqa: F401
    from .sync_status import sync_status  # noqa: F401
    from .typora_control import typora_control  # noqa: F401
    from .write_note import write_note  # noqa: F401
    from .zettelmaker import adn_zettelmaker  # noqa: F401

__all__ = [
    "register_adn_knowledge_rag",
    "adn_knowledge",
    "adn_research",
    "adn_skills",
    "adn_system",
    "adn_external",
    "adn_import_export",
    "help",
]
