"""Tests for LLM-powered adn_content operations."""

from unittest.mock import AsyncMock

import pytest

from advanced_memory.mcp.tools.content_manager import adn_content


@pytest.mark.asyncio
async def test_suggest_tags(mock_llm_client, test_project):
    """Test semantic tag suggestions."""
    # Create a test note first
    create_result = await adn_content.fn(
        operation="write",
        identifier="Test Note",
        content="# Test Note\n\nThis is about butterflies and biology.",
        folder="test",
        tags=["test"],
    )
    assert "created" in create_result.lower() or "updated" in create_result.lower()

    # Mock LLM response
    mock_llm_client.generate_json = AsyncMock(return_value=["butterflies", "biology", "insects", "nature", "science"])

    result = await adn_content.fn(operation="suggest_tags", identifier="Test Note")
    assert "Tag Suggestions" in result
    assert "butterflies" in result.lower()
    assert "biology" in result.lower()

    # Verify LLM was called
    mock_llm_client.generate_json.assert_called_once()


@pytest.mark.asyncio
async def test_summarize(mock_llm_client, test_project):
    """Test note summarization."""
    # Create a test note first
    create_result = await adn_content.fn(
        operation="write",
        identifier="Long Note",
        content="# Long Note\n\n" + "This is a very long note. " * 50,
        folder="test",
    )
    assert "created" in create_result.lower() or "updated" in create_result.lower()

    # Mock LLM response
    mock_llm_client.generate = AsyncMock(return_value="This is a summary of the long note.")

    result = await adn_content.fn(operation="summarize", identifier="Long Note")
    assert "Note Summary" in result
    assert "summary" in result.lower()

    # Verify LLM was called
    mock_llm_client.generate.assert_called_once()


@pytest.mark.asyncio
async def test_enhance(mock_llm_client, test_project):
    """Test note enhancement."""
    # Create a test note first
    create_result = await adn_content.fn(
        operation="write",
        identifier="Test Note",
        content="# Test\n\nSome content here.",
        folder="test",
    )
    assert "created" in create_result.lower() or "updated" in create_result.lower()

    # Mock LLM response
    mock_llm_client.generate = AsyncMock(return_value="# Test\n\n## Introduction\n\nSome enhanced content here.")

    result = await adn_content.fn(operation="enhance", identifier="Test Note")
    assert "Note Enhanced" in result

    # Verify LLM was called
    mock_llm_client.generate.assert_called_once()


@pytest.mark.asyncio
async def test_generate(mock_llm_client, test_project):
    """Test content generation."""
    # Mock LLM response
    mock_llm_client.generate = AsyncMock(
        return_value="# Python Functions\n\nPython functions are reusable blocks of code..."
    )

    result = await adn_content.fn(operation="generate", content="Python functions tutorial", folder="tutorials")
    assert "created" in result.lower() or "updated" in result.lower()

    # Verify LLM was called
    mock_llm_client.generate.assert_called_once()


@pytest.mark.asyncio
async def test_suggest_tags_nonexistent_note(mock_llm_client):
    """Test suggest_tags with nonexistent note."""
    result = await adn_content.fn(operation="suggest_tags", identifier="Nonexistent Note")
    assert "Error" in result
    assert "Could not read note" in result


@pytest.mark.asyncio
async def test_summarize_nonexistent_note(mock_llm_client):
    """Test summarize with nonexistent note."""
    result = await adn_content.fn(operation="summarize", identifier="Nonexistent Note")
    assert "Error" in result
    assert "Could not read note" in result


@pytest.mark.asyncio
async def test_enhance_nonexistent_note(mock_llm_client):
    """Test enhance with nonexistent note."""
    result = await adn_content.fn(operation="enhance", identifier="Nonexistent Note")
    assert "Error" in result
    assert "Could not read note" in result


@pytest.mark.asyncio
async def test_generate_missing_content(mock_llm_client):
    """Test generate without content parameter."""
    result = await adn_content.fn(operation="generate")
    assert "Error" in result
    assert "content parameter" in result.lower()
