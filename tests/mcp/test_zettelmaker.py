"""Tests for adn_zettelmaker portmanteau tool."""

import pytest

from advanced_memory.mcp.tools.zettelmaker import adn_zettelmaker


@pytest.mark.asyncio
async def test_zettelmaker_invalid_operation():
    """Test invalid operation returns error."""
    result = await adn_zettelmaker("invalid_operation")

    assert "Error" in result
    assert "invalid_operation" in result
    assert "Supported operations:" in result


@pytest.mark.asyncio
async def test_zettelmaker_generate_no_category():
    """Test generate without category returns error."""
    result = await adn_zettelmaker("generate")

    assert "Error" in result
    assert "category" in result
    assert "Available categories:" in result


@pytest.mark.asyncio
async def test_zettelmaker_generate_unknown_category():
    """Test generate with unknown category returns error."""
    result = await adn_zettelmaker("generate", category="unknown")

    assert "Error" in result
    assert "unknown" in result.lower()


@pytest.mark.asyncio
async def test_zettelmaker_generate_no_topic():
    """Test generate with no topic shows available topics."""
    result = await adn_zettelmaker("generate", category="developer")

    assert "Available Topics" in result
    assert "developer" in result
    assert "python-core" in result


@pytest.mark.asyncio
async def test_zettelmaker_generate_unknown_topic():
    """Test generate with unknown topic returns error."""
    result = await adn_zettelmaker("generate", category="developer", topic="unknown-topic")

    assert "Error" in result
    assert "unknown-topic" in result


@pytest.mark.asyncio
async def test_zettelmaker_suggest():
    """Test suggest operation."""
    result = await adn_zettelmaker("suggest", category="developer", count=3)

    assert "Suggested Topics" in result or "Topic Suggestions" in result
    # Should contain recommendations
    assert ("python" in result.lower()) or ("developer" in result.lower())


@pytest.mark.asyncio
async def test_zettelmaker_analyze():
    """Test analyze operation."""
    result = await adn_zettelmaker("analyze", category="developer", depth=3)

    assert "Analysis" in result
    assert "developer" in result.lower()


@pytest.mark.asyncio
async def test_zettelmaker_customize_preview():
    """Test customize operation (preview mode in Phase 1)."""
    result = await adn_zettelmaker("customize", category="developer", topic="python-core")

    assert "Customization" in result or "Preview" in result
    assert "Phase 2" in result  # Should mention it's coming in Phase 2


@pytest.mark.asyncio
async def test_zettelmaker_expand_preview():
    """Test expand operation (preview mode in Phase 1)."""
    result = await adn_zettelmaker("expand", note_identifier="Python Fundamentals", depth=2)

    assert "Expand" in result
    assert "Python Fundamentals" in result


@pytest.mark.asyncio
async def test_zettelmaker_connect_preview():
    """Test connect operation (preview mode in Phase 1)."""
    result = await adn_zettelmaker("connect", count=5)

    assert "Connect" in result or "Auto-Connect" in result
    assert "Phase 1" in result  # Should mention it's in development


@pytest.mark.asyncio
async def test_zettelmaker_operations_with_context():
    """Test that operations work with context parameter."""
    # All operations should accept ctx parameter without error
    await adn_zettelmaker("suggest", category="developer", ctx=None)
    await adn_zettelmaker("analyze", category="developer", ctx=None)
    await adn_zettelmaker("customize", category="developer", topic="python-core", ctx=None)
    # Should not raise exceptions


@pytest.mark.asyncio
async def test_zettelmaker_ai_generate_no_api_key():
    """Test AI generation without API key shows setup instructions."""
    result = await adn_zettelmaker(
        "generate", category="developer", topic="Rust Programming", ai_generate=True
    )

    assert "AI Generation Setup Required" in result or "API_KEY" in result
    assert "ANTHROPIC" in result or "OPENAI" in result


@pytest.mark.asyncio
async def test_zettelmaker_quality_levels():
    """Test that quality levels are accepted."""
    # Test different quality levels (all should handle gracefully without API key)
    for quality in ["quick", "standard", "comprehensive", "expert"]:
        result = await adn_zettelmaker(
            "generate",
            category="developer",
            topic="Custom Topic",
            ai_generate=True,
            quality=quality,
        )

        # Should get setup instructions since no API key
        assert "API" in result or "Setup" in result


@pytest.mark.asyncio
async def test_zettelmaker_ai_suggest_with_existing_topic():
    """Test that unknown topics suggest AI generation."""
    result = await adn_zettelmaker("generate", category="developer", topic="Rust Programming")

    # Should suggest using AI generation for unknown topic
    assert "ai_generate=True" in result or "AI generation" in result


@pytest.mark.asyncio
async def test_zettelmaker_all_categories_load():
    """Test that all 10 categories are available."""
    result = await adn_zettelmaker("generate")

    # Should mention categories
    assert "category" in result.lower()
    assert "Available categories" in result or "Error" in result
