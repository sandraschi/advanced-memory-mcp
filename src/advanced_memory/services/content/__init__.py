"""Content domain services (ARCHITECTURE_2_0.md Phase 1, Step 1).

Business logic extracted from the content_manager.py monolith, grouped
by concern:

- crud      — write, read, read_latest, view, view_rendered, edit, move, delete
- capture   — quick_capture, daily_note
- tagging   — edit_tags, extract_content_tags, suggest_tags
- ai_enrich — summarize_note, enhance_note, generate_note

Tool entry points (namespace apps and, until deleted, the adn_*
portmanteaus) call these services directly (Phase 1 Step 2). The
_dispatch_content_operations hub and content_manager.py itself are
deleted in Step 5.
"""

from advanced_memory.services.content.ai_enrich import (
    enhance_note,
    generate_note,
    summarize_note,
)
from advanced_memory.services.content.capture import daily_note, quick_capture
from advanced_memory.services.content.crud import (
    delete_note,
    edit_note,
    get_latest_identifier,
    move_note,
    read_latest_note,
    read_note,
    view_note,
    view_note_rendered,
    write_note,
)
from advanced_memory.services.content.tagging import (
    edit_tags,
    extract_content_tags,
    suggest_tags,
)

__all__ = [
    "daily_note",
    "delete_note",
    "edit_note",
    # tagging
    "edit_tags",
    "enhance_note",
    "extract_content_tags",
    "generate_note",
    "get_latest_identifier",
    "move_note",
    # capture
    "quick_capture",
    "read_latest_note",
    "read_note",
    "suggest_tags",
    # ai_enrich
    "summarize_note",
    "view_note",
    "view_note_rendered",
    # crud
    "write_note",
]
