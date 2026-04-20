"""MCP tools for Advanced Memory - Portmanteau architecture.

Default mode: portmanteau tools only (reduced tool count for Claude Desktop).
Full mode: all tools via ADVANCED_MEMORY_FULL_TOOLS_MODE=true env var.

FastMCP registers tools at IMPORT time via @mcp.tool decorator.
"""

import os

from .adn_knowledge_rag import register_rag_bridge as register_adn_knowledge_rag

# ── HELP TOOL (always imported) ───────────────────────────────────────────────
from .help import help
# Default to SOTA 2026 (Namespaced Atomic Discovery)
_is_reduced_mode = os.getenv("ADVANCED_MEMORY_REDUCED_MODE", "").lower() == "true"
_full_tools_mode = os.getenv("ADVANCED_MEMORY_FULL_TOOLS_MODE", "").lower() == "true"

# ── PILOT: SOTA NAMESPACED ATOMICS ──────────────────────────────────────────
# These now auto-unroll into knowledge/create, research/search, etc.
# unless _is_reduced_mode is True.
from .portmanteau_knowledge import adn_knowledge
from .portmanteau_research import adn_research

# ── OTHER SYSTEM TOOLS ────────────────────────────────────────────────────────
from .portmanteau_skills import adn_skills
from .portmanteau_system import adn_system
from .portmanteau_external import adn_external
from .portmanteau_import_export import adn_import_export

# ── STANDALONE TOOLS (Imported if not in restricted mode) ─────────────────────
if not _is_reduced_mode or _full_tools_mode:
    from .adn_audio import adn_audio
    from .adn_inbox import adn_inbox
    from .adn_navigation import adn_navigation
    from .adn_observability import adn_observability
    from .canvas import canvas
    from .typora_control import typora_control
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
