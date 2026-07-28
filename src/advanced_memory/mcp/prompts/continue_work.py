"""Continue-work prompt: automatic session context injection.

Created 2026-07-17 (TODO P1). Replaces the manual "read the last basic-memory
note at chat start" convention: any MCP client can invoke this prompt and get
the latest START NOTE, the newest notes, and recent session-scribe digests.

Reads the vault directly (no API dependency) so it works in both proxy and
local modes, and degrades gracefully on an empty vault.
"""

from __future__ import annotations

from pathlib import Path
from typing import Annotated

from loguru import logger
from pydantic import Field

from advanced_memory.mcp.mcp_instance import mcp

_VAULT = Path.home() / ".advanced-memory" / "vault"
_MAX_NOTE_CHARS = 7000
_MAX_RECENT_TITLES = 8
_MAX_DIGESTS = 3


def _title_of(path: Path) -> str:
    """Frontmatter title, falling back to filename stem."""
    try:
        head = path.read_text(encoding="utf-8", errors="replace")[:500]
        for line in head.splitlines():
            if line.startswith("title:"):
                return line[6:].strip()
    except OSError:
        pass
    return path.stem


@mcp.prompt(
    name="Continue Work",
    description=(
        "Session context injection: latest START NOTE, recent notes, and "
        "session-scribe digests from the Advanced Memory vault."
    ),
)
def continue_work(
    project_folder: Annotated[str, Field(description="Vault folder to read start notes from")] = "projects",
) -> str:
    """Return the latest start-note context so a session can continue instantly."""
    logger.info("continue_work prompt invoked (folder=%s)", project_folder)

    folder = _VAULT / project_folder
    notes = sorted(folder.glob("*.md"), key=lambda p: p.name, reverse=True) if folder.is_dir() else []

    if not notes:
        return (
            "# Continue Work\n\nThe vault has no notes in "
            f"'{project_folder}' yet. Start by writing a timestamped START NOTE "
            "at the end of this session (adn_notes write)."
        )

    # Timestamped filenames sort chronologically; find newest START NOTE, else newest note.
    start_note = next((p for p in notes if "start" in p.name.lower() and "note" in p.name.lower()), notes[0])
    try:
        start_content = start_note.read_text(encoding="utf-8", errors="replace")[:_MAX_NOTE_CHARS]
    except OSError as exc:
        start_content = f"(could not read {start_note.name}: {exc})"

    recent_titles = [f"- {_title_of(p)}" for p in notes[:_MAX_RECENT_TITLES]]

    inbox = _VAULT / "inbox"
    digests = (
        sorted(inbox.glob("*session-scribe*.md"), key=lambda p: p.name, reverse=True)[:_MAX_DIGESTS]
        if inbox.is_dir()
        else []
    )
    digest_block = ""
    if digests:
        newest = digests[0]
        try:
            digest_text = newest.read_text(encoding="utf-8", errors="replace")[:3000]
        except OSError:
            digest_text = "(unreadable)"
        digest_block = (
            "\n## Latest session-scribe digest (auto-captured, unreviewed)\n\n"
            f"{digest_text}\n\n"
            f"({len(digests)} digest(s) awaiting review in inbox/)\n"
        )

    return (
        "# Continue Work — vault context\n\n"
        f"## Latest start note: {_title_of(start_note)}\n\n"
        f"{start_content}\n\n"
        "## Most recent notes\n\n"
        + "\n".join(recent_titles)
        + "\n"
        + digest_block
        + "\nFollow the conventions: timestamp new notes, tag with "
        "[project, technology, status, priority], mark superseded notes OBSOLETE."
    )
