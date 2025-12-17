"""Prompt template resources for Advanced Memory MCP server.

These resources expose Handlebars templates used for prompt rendering,
allowing direct access to template content via memory:// URIs.
"""

from pathlib import Path

from loguru import logger

from advanced_memory.mcp.mcp_instance import mcp


@mcp.resource(
    uri="memory://prompt_templates/search",
    description="Handlebars template for search prompt rendering",
)
def search_prompt_template() -> str:
    """Get the Handlebars template used for rendering search prompts.

    This template formats search results into a user-friendly prompt with
    context and suggestions for next steps.

    Returns:
        The Handlebars template content as a string
    """
    logger.info("Loading search prompt template")
    # Try src structure first (resources -> mcp -> advanced_memory -> templates)
    template_path = Path(__file__).parent.parent.parent / "templates" / "prompts" / "search.hbs"

    if not template_path.exists():
        # Fallback: try mcpb path structure (resources -> mcp -> advanced_memory -> src -> templates)
        template_path = (
            Path(__file__).parent.parent.parent.parent / "templates" / "prompts" / "search.hbs"
        )

    if not template_path.exists():
        logger.warning(f"Search template not found, tried: {template_path}")
        return "# Search Prompt Template\n\nTemplate file not found."

    content = template_path.read_text(encoding="utf-8")
    logger.info(f"Loaded search prompt template ({len(content)} chars)")
    return content


@mcp.resource(
    uri="memory://prompt_templates/continue_conversation",
    description="Handlebars template for continue conversation prompt rendering",
)
def continue_conversation_prompt_template() -> str:
    """Get the Handlebars template used for rendering continue conversation prompts.

    This template formats context from previous conversations into a prompt
    that helps continue work on a specific topic.

    Returns:
        The Handlebars template content as a string
    """
    logger.info("Loading continue conversation prompt template")
    # Try src structure first (resources -> mcp -> advanced_memory -> templates)
    template_path = (
        Path(__file__).parent.parent.parent / "templates" / "prompts" / "continue_conversation.hbs"
    )

    if not template_path.exists():
        # Fallback: try mcpb path structure (resources -> mcp -> advanced_memory -> src -> templates)
        template_path = (
            Path(__file__).parent.parent.parent.parent
            / "templates"
            / "prompts"
            / "continue_conversation.hbs"
        )

    if not template_path.exists():
        logger.warning(f"Continue conversation template not found, tried: {template_path}")
        return "# Continue Conversation Prompt Template\n\nTemplate file not found."

    content = template_path.read_text(encoding="utf-8")
    logger.info(f"Loaded continue conversation prompt template ({len(content)} chars)")
    return content
