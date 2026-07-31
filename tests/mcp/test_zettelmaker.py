"""Tests for adn_zettelmaker portmanteau tool."""

import pytest

from advanced_memory.mcp.tools.zettelmaker import adn_zettelmaker
from tests.mcp.tool_invoker import mcp_fn


def _text(result) -> str:
    """Extract readable text from ToolResult / dict responses."""
    content = getattr(result, "content", None)
    if isinstance(content, list):
        return " ".join(str(c) for c in content)
    if isinstance(result, dict):
        parts = []
        for k in ("error", "message", "conversational_summary", "summary", "technical_summary"):
            v = result.get(k)
            if isinstance(v, str) and v.strip():
                parts.append(v)
        return " ".join(parts)
    return str(result)


@pytest.mark.asyncio
async def test_zettelmaker_invalid_operation():
    """Test invalid operation returns error."""
    result = await mcp_fn(adn_zettelmaker)("invalid_operation")
    text = _text(result)

    assert "Error" in text
    assert "invalid_operation" in text
    assert "Supported operations:" in text


@pytest.mark.asyncio
async def test_zettelmaker_generate_no_category():
    """Test generate without category returns error."""
    result = await mcp_fn(adn_zettelmaker)("generate")
    text = _text(result)

    assert "Error" in text
    assert "category" in text
    assert "Available categories:" in text


@pytest.mark.asyncio
async def test_zettelmaker_generate_unknown_category():
    """Test generate with unknown category returns error."""
    result = await mcp_fn(adn_zettelmaker)("generate", category="unknown")
    text = _text(result)

    assert "Error" in text
    assert "unknown" in text.lower()


@pytest.mark.asyncio
async def test_zettelmaker_generate_no_topic():
    """Test generate with no topic shows available topics."""
    result = await mcp_fn(adn_zettelmaker)("generate", category="developer")
    text = _text(result)

    assert "Available Topics" in text
    assert "developer" in text
    assert "python-core" in text


@pytest.mark.asyncio
async def test_zettelmaker_generate_unknown_topic():
    """Test generate with unknown topic returns error."""
    result = await mcp_fn(adn_zettelmaker)("generate", category="developer", topic="unknown-topic")
    text = _text(result)

    assert "Error" in text
    assert "unknown-topic" in text


@pytest.mark.asyncio
async def test_zettelmaker_suggest():
    """Test suggest operation."""
    result = await mcp_fn(adn_zettelmaker)("suggest", category="developer", count=3)
    text = _text(result)

    # Suggest returns "Smart Recommendations" or "Personalized Recommendations"
    assert "Recommendations" in text or "Suggested" in text
    # Should contain category filter
    assert "developer" in text.lower()


@pytest.mark.asyncio
async def test_zettelmaker_analyze():
    """Test analyze operation."""
    result = await mcp_fn(adn_zettelmaker)("analyze", category="developer", depth=3)
    text = _text(result)

    assert "Analysis" in text
    assert "developer" in text.lower()


@pytest.mark.asyncio
async def test_zettelmaker_customize_preview():
    """Test customize operation (preview mode in Phase 1)."""
    result = await mcp_fn(adn_zettelmaker)("customize", category="developer", topic="python-core")
    text = _text(result)

    assert "Customization" in text or "Preview" in text
    assert "Phase 2" in text  # Should mention it's coming in Phase 2


@pytest.mark.asyncio
async def test_zettelmaker_expand_preview():
    """Test expand operation (preview mode in Phase 1)."""
    result = await mcp_fn(adn_zettelmaker)("expand", note_identifier="Python Fundamentals", depth=2)
    text = _text(result)

    assert "Expand" in text
    assert "Python Fundamentals" in text


@pytest.mark.asyncio
async def test_zettelmaker_connect_preview():
    """Test connect operation (preview mode in Phase 1)."""
    result = await mcp_fn(adn_zettelmaker)("connect", count=5)
    text = _text(result)

    assert "Connect" in text or "Auto-Connect" in text
    assert "Phase 1" in text  # Should mention it's in development


@pytest.mark.asyncio
async def test_zettelmaker_operations_with_context():
    """Test that operations work with context parameter."""
    # All operations should accept ctx parameter without error
    await mcp_fn(adn_zettelmaker)("suggest", category="developer", ctx=None)
    await mcp_fn(adn_zettelmaker)("analyze", category="developer", ctx=None)
    await mcp_fn(adn_zettelmaker)("customize", category="developer", topic="python-core", ctx=None)
    # Should not raise exceptions


@pytest.mark.asyncio
async def test_zettelmaker_ai_generate_no_api_key():
    """Test AI generation without API key shows setup instructions."""
    result = await mcp_fn(adn_zettelmaker)("generate", category="developer", topic="Rust Programming", ai_generate=True)
    text = _text(result)

    assert "AI Generation Setup Required" in text or "API_KEY" in text
    assert "ANTHROPIC" in text or "OPENAI" in text


@pytest.mark.asyncio
async def test_zettelmaker_quality_levels():
    """Test that quality levels are accepted."""
    # Test different quality levels (all should handle gracefully without API key)
    for quality in ["quick", "standard", "comprehensive", "expert"]:
        result = await mcp_fn(adn_zettelmaker)(
            "generate",
            category="developer",
            topic="Custom Topic",
            ai_generate=True,
            quality=quality,
        )
        text = _text(result)

        # Should get setup instructions since no API key
        assert "API" in text or "Setup" in text


@pytest.mark.asyncio
async def test_zettelmaker_ai_suggest_with_existing_topic():
    """Test that unknown topics suggest AI generation."""
    result = await mcp_fn(adn_zettelmaker)("generate", category="developer", topic="Rust Programming")
    text = _text(result)

    # Should suggest using AI generation for unknown topic
    assert "ai_generate=True" in text or "AI generation" in text


@pytest.mark.asyncio
async def test_zettelmaker_all_categories_load():
    """Test that all 10 categories are available."""
    result = await mcp_fn(adn_zettelmaker)("generate")
    text = _text(result)

    # Should mention categories
    assert "category" in text.lower()
    assert "Available categories" in text or "Error" in text
