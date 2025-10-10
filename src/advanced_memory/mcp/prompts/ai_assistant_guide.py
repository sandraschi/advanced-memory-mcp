from pathlib import Path

from loguru import logger

from advanced_memory.mcp.server import mcp


@mcp.resource(
    uri="memory://ai_assistant_guide",
    name="ai assistant guide",
    description="Give an AI assistant guidance on how to use Advanced Memory tools effectively",
)
def ai_assistant_guide() -> str:
    """Return a concise guide on Advanced Memory tools and how to use them.

    Args:
        focus: Optional area to focus on ("writing", "context", "search", etc.)

    Returns:
        A focused guide on Advanced Memory usage.
    """
    logger.info("Loading AI assistant guide resource")
    guide_doc = Path(__file__).parent.parent / "resources" / "ai_assistant_guide.md"
    content = guide_doc.read_text(encoding="utf-8")
    logger.info(f"Loaded AI assistant guide ({len(content)} chars)")
    return content
