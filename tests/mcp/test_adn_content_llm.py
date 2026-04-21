"""Tests for LLM-powered adn_content operations."""

from unittest.mock import AsyncMock

import pytest

from tests.mcp.tool_invoker import mcp_fn

from advanced_memory.mcp.tools.content_manager import adn_content


def _out(x) -> str:
    """Normalize adn_content return values (markdown str vs structured dict)."""
    if isinstance(x, dict):
        for k in ("content", "message", "technical_summary", "error"):
            v = x.get(k)
            if isinstance(v, str) and v.strip():
                return v
        return str(x)
    return str(x)


@pytest.mark.asyncio
async def test_suggest_tags(mock_llm_client, test_project):
    """Test semantic tag suggestions."""
    # Create a test note first
    create_result = await mcp_fn(adn_content)(
        operation="write",
        identifier="Test Note",
        content="# Test Note\n\nThis is about butterflies and biology.",
        folder="test",
        tags=["test"],
    )
    assert "created" in _out(create_result).lower() or "updated" in _out(create_result).lower()

    # Mock LLM response
    mock_llm_client.generate_json = AsyncMock(return_value=["butterflies", "biology", "insects", "nature", "science"])

    result = await mcp_fn(adn_content)(operation="suggest_tags", identifier="Test Note")
    text = _out(result)
    assert "Tag Suggestions" in text
    assert "butterflies" in text.lower()
    assert "biology" in text.lower()

    # Verify LLM was called
    mock_llm_client.generate_json.assert_called_once()


@pytest.mark.asyncio
async def test_summarize(mock_llm_client, test_project):
    """Test note summarization."""
    # Create a test note first
    create_result = await mcp_fn(adn_content)(
        operation="write",
        identifier="Long Note",
        content="# Long Note\n\n" + "This is a very long note. " * 50,
        folder="test",
    )
    assert "created" in _out(create_result).lower() or "updated" in _out(create_result).lower()

    # Mock LLM response
    mock_llm_client.generate = AsyncMock(return_value="This is a summary of the long note.")

    result = await mcp_fn(adn_content)(operation="summarize", identifier="Long Note")
    text = _out(result)
    assert "Note Summary" in text
    assert "summary" in text.lower()

    # Verify LLM was called
    mock_llm_client.generate.assert_called_once()


@pytest.mark.asyncio
async def test_enhance(mock_llm_client, test_project):
    """Test note enhancement."""
    # Create a test note first
    create_result = await mcp_fn(adn_content)(
        operation="write",
        identifier="Test Note",
        content="# Test\n\nSome content here.",
        folder="test",
    )
    assert "created" in _out(create_result).lower() or "updated" in _out(create_result).lower()

    # Mock LLM response
    mock_llm_client.generate = AsyncMock(return_value="# Test\n\n## Introduction\n\nSome enhanced content here.")

    result = await mcp_fn(adn_content)(operation="enhance", identifier="Test Note")
    assert "Note Enhanced" in _out(result)

    # Verify LLM was called
    mock_llm_client.generate.assert_called_once()


@pytest.mark.asyncio
async def test_generate(mock_llm_client, test_project):
    """Test content generation."""
    # Mock LLM response
    mock_llm_client.generate = AsyncMock(
        return_value="# Python Functions\n\nPython functions are reusable blocks of code..."
    )

    result = await mcp_fn(adn_content)(operation="generate", content="Python functions tutorial", folder="tutorials")
    assert "created" in _out(result).lower() or "updated" in _out(result).lower()

    # Verify LLM was called
    mock_llm_client.generate.assert_called_once()


@pytest.mark.asyncio
async def test_suggest_tags_nonexistent_note(mock_llm_client):
    """Test suggest_tags with nonexistent note."""
    result = await mcp_fn(adn_content)(operation="suggest_tags", identifier="Nonexistent Note")
    text = _out(result)
    assert "Nonexistent" in text
    assert "tag" in text.lower()


@pytest.mark.asyncio
async def test_summarize_nonexistent_note(mock_llm_client):
    """Test summarize with nonexistent note."""
    result = await mcp_fn(adn_content)(operation="summarize", identifier="Nonexistent Note")
    text = _out(result)
    assert "Nonexistent" in text
    assert "summary" in text.lower() or "note" in text.lower()


@pytest.mark.asyncio
async def test_enhance_nonexistent_note(mock_llm_client):
    """Test enhance with nonexistent note."""
    result = await mcp_fn(adn_content)(operation="enhance", identifier="Nonexistent Note")
    text = _out(result)
    assert "Nonexistent" in text
    assert "enhance" in text.lower() or "note" in text.lower()


@pytest.mark.asyncio
async def test_generate_missing_content(mock_llm_client):
    """Test generate without content parameter."""
    result = await mcp_fn(adn_content)(operation="generate")
    text = _out(result)
    assert "content" in text.lower() or "missing" in text.lower()
