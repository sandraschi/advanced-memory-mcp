"""Tests for LLM-powered adn_knowledge operations."""

from unittest.mock import AsyncMock

import pytest

from tests.mcp.tool_invoker import mcp_fn

from advanced_memory.mcp.tools.adn_knowledge import adn_knowledge_legacy as adn_knowledge


@pytest.mark.asyncio
async def test_analyze_quality(mock_llm_client, test_project):
    """Test content quality analysis."""
    # Create test notes first
    from advanced_memory.mcp.tools.content_manager import adn_content

    await mcp_fn(adn_content)(
        operation="write",
        identifier="Test Note 1",
        content="# Test Note\n\nSome content here.",
        folder="test",
    )

    # Mock LLM response
    mock_llm_client.generate_json = AsyncMock(
        return_value=[
            {
                "note_title": "Test Note 1",
                "readability": "good",
                "completeness": "partial",
                "organization": "good",
                "freshness": "current",
                "quality_score": 7,
                "suggestions": ["Add more detail"],
            }
        ]
    )

    result = await mcp_fn(adn_knowledge)(operation="analyze_quality", filters={"query": "test"}, limit=10)
    assert "Quality Analysis" in result
    assert "Test Note 1" in result

    # Verify LLM was called
    mock_llm_client.generate_json.assert_called_once()


@pytest.mark.asyncio
async def test_suggest_relationships(mock_llm_client, test_project):
    """Test relationship suggestions."""
    # Create test notes first
    from advanced_memory.mcp.tools.content_manager import adn_content

    await mcp_fn(adn_content)(
        operation="write",
        identifier="Note A",
        content="# Note A\n\nThis relates to Note B.",
        folder="test",
    )

    await mcp_fn(adn_content)(
        operation="write",
        identifier="Note B",
        content="# Note B\n\nThis is related to Note A.",
        folder="test",
    )

    # Mock LLM response
    mock_llm_client.generate_json = AsyncMock(
        return_value=[
            {
                "source_note": "Note A",
                "target_note": "Note B",
                "relationship_type": "relates_to",
                "reason": "Both notes discuss related topics",
            }
        ]
    )

    result = await mcp_fn(adn_knowledge)(operation="suggest_relationships", filters={"note_id": "Note A"})
    assert "Relationship" in result
    assert "Note A" in result
    mock_llm_client.generate_json.assert_called_once()


@pytest.mark.asyncio
async def test_find_gaps(mock_llm_client, test_project):
    """Test knowledge gap identification."""
    # Create test notes first
    from advanced_memory.mcp.tools.content_manager import adn_content

    await mcp_fn(adn_content)(
        operation="write",
        identifier="ML Basics",
        content="# Machine Learning Basics\n\nIntroduction to ML.",
        folder="test",
    )

    # Mock LLM response
    mock_llm_client.generate_json = AsyncMock(
        return_value={
            "gaps": [
                {
                    "topic": "deep learning",
                    "gap_type": "missing_subtopic",
                    "description": "No coverage of deep learning",
                    "priority": "high",
                }
            ]
        }
    )

    result = await mcp_fn(adn_knowledge)(operation="find_gaps", filters={"topics": ["machine-learning"]})
    assert "gap" in result.lower() or "knowledge" in result.lower()
    assert "machine-learning" in result.lower() or "machine learning" in result.lower()

    mock_llm_client.generate_json.assert_called_once()


@pytest.mark.asyncio
async def test_cluster_content(mock_llm_client, test_project):
    """Test content clustering."""
    # Create test notes first
    from advanced_memory.mcp.tools.content_manager import adn_content

    await mcp_fn(adn_content)(
        operation="write",
        identifier="Python Note",
        content="# Python\n\nPython programming.",
        folder="test",
    )

    # Mock LLM response
    mock_llm_client.generate_json = AsyncMock(
        return_value={
            "clusters": [
                {
                    "cluster_name": "Programming",
                    "theme": "Programming languages",
                    "notes": ["Python Note"],
                    "description": "Notes about programming",
                }
            ]
        }
    )

    result = await mcp_fn(adn_knowledge)(
        operation="cluster_content", filters={"query": "python"}, action={"num_clusters": 3}
    )
    assert "Content Clustering" in result
    assert "Programming" in result

    # Verify LLM was called
    mock_llm_client.generate_json.assert_called_once()


@pytest.mark.asyncio
async def test_extract_insights(mock_llm_client, test_project):
    """Test insight extraction."""
    # Create test notes first
    from advanced_memory.mcp.tools.content_manager import adn_content

    await mcp_fn(adn_content)(
        operation="write",
        identifier="Research Note",
        content="# Research\n\nKey finding: AI is important.",
        folder="test",
    )

    # Mock LLM response
    mock_llm_client.generate_json = AsyncMock(
        return_value={
            "insights": [
                {
                    "insight": "AI is becoming increasingly important",
                    "category": "finding",
                    "supporting_notes": ["Research Note"],
                    "importance": "high",
                }
            ]
        }
    )

    result = await mcp_fn(adn_knowledge)(operation="extract_insights", filters={"query": "research"})
    assert "Insight" in result
    mock_llm_client.generate_json.assert_called_once()


@pytest.mark.asyncio
async def test_suggest_relationships_missing_note_id(mock_llm_client):
    """Test suggest_relationships without note_id."""
    result = await mcp_fn(adn_knowledge)(operation="suggest_relationships", filters={})
    assert "Error" in result
    assert "note_id" in result.lower()


@pytest.mark.asyncio
async def test_find_gaps_missing_topics(mock_llm_client):
    """Test find_gaps without topics."""
    result = await mcp_fn(adn_knowledge)(operation="find_gaps", filters={})
    assert "Error" in result
    assert "topics" in result.lower()
