"""Note resources for Advanced Memory MCP server."""

from datetime import datetime

from loguru import logger

from advanced_memory.mcp.mcp_instance import mcp
from advanced_memory.mcp.project_session import get_active_project
from advanced_memory.mcp.tools.read_note import read_note
from advanced_memory.mcp.tools.recent_activity import _format_activity_as_markdown
from advanced_memory.mcp.tools.recent_activity import recent_activity as recent_activity_tool
from advanced_memory.schemas.memory import GraphContext


@mcp.resource(
    uri="memory://notes/recent",
    description="Recently updated notes and entities in the active project.",
)
async def recent_notes() -> str:
    """Return recent note activity as markdown (default 7-day window)."""
    logger.info("Loading recent notes resource")
    active_project = get_active_project()
    raw = await (recent_activity_tool.fn if hasattr(recent_activity_tool, "fn") else recent_activity_tool)(
        timeframe="7d",
        page=1,
        page_size=20,
        project=active_project.name,
    )
    context = raw if isinstance(raw, GraphContext) else GraphContext.model_validate(raw)
    return _format_activity_as_markdown(context, "7d", active_project=active_project)


@mcp.resource(
    uri="memory://notes/{permalink}",
    description="Read a single note by permalink (e.g. journal/2026-07-28).",
)
async def note_file(permalink: str) -> str:
    """Return markdown content for a note permalink."""
    logger.info(f"Loading note resource: {permalink}")
    result = await (read_note.fn if hasattr(read_note, "fn") else read_note)(
        identifier=permalink,
        page=1,
        page_size=1000,
    )
    return str(result)


@mcp.resource(
    uri="memory://notes/daily",
    description="Today's daily journal note (creates empty stub if missing).",
)
async def daily_note() -> str:
    """Return today's journal note content."""
    today = datetime.now().strftime("%Y-%m-%d")
    journal_path = f"journal/{today}"
    logger.info(f"Loading daily note resource: {journal_path}")
    result = await (read_note.fn if hasattr(read_note, "fn") else read_note)(
        identifier=journal_path,
        page=1,
        page_size=1000,
    )
    return str(result)
