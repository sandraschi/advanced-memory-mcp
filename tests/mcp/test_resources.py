import pytest

from tests.mcp.tool_invoker import mcp_fn

from advanced_memory.mcp.prompts.ai_assistant_guide import ai_assistant_guide


@pytest.mark.asyncio
async def test_ai_assistant_guide_exists(app):
    """Test that the canvas spec resource exists and returns content."""
    # Call the resource function
    guide = mcp_fn(ai_assistant_guide)()

    # Verify basic characteristics of the content
    assert guide is not None
    assert isinstance(guide, str)
    assert len(guide) > 0

    # Verify it contains expected sections of the Canvas spec
    assert "# AI Assistant Guide" in guide
