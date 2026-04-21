"""Tests for discussion context MCP tool."""

from datetime import datetime

import pytest

from tests.mcp.tool_invoker import mcp_fn
from mcp.server.fastmcp.exceptions import ToolError

from advanced_memory.mcp.tools.build_context import build_context
from advanced_memory.schemas.memory import (
    GraphContext,
)


@pytest.mark.asyncio
async def test_get_basic_discussion_context(client, test_graph):
    """Test getting basic discussion context."""
    context = await mcp_fn(build_context)(url="memory://test/root")

    assert isinstance(context, GraphContext)
    assert len(context.results) == 1
    assert context.results[0].primary_result.permalink == "test/root"
    assert len(context.results[0].related_results) > 0

    # Verify metadata
    assert context.metadata.uri == "test/root"
    assert context.metadata.depth == 1  # default depth
    assert context.metadata.timeframe is not None
    assert isinstance(context.metadata.generated_at, datetime)
    assert context.metadata.primary_count == 1
    assert context.metadata.related_count > 0


@pytest.mark.asyncio
async def test_get_discussion_context_pattern(client, test_graph):
    """Test getting context with pattern matching."""
    context = await mcp_fn(build_context)(url="memory://test/*", depth=1)

    assert isinstance(context, GraphContext)
    assert len(context.results) > 1  # Should match multiple test/* paths
    assert all("test/" in item.primary_result.permalink for item in context.results)
    assert context.metadata.depth == 1


@pytest.mark.asyncio
async def test_get_discussion_context_timeframe(client, test_graph):
    """Test timeframe parameter filtering."""
    # Get recent context
    recent_context = await mcp_fn(build_context)(
        url="memory://test/root",
        timeframe="1d",  # Last 24 hours
    )

    # Get older context
    older_context = await mcp_fn(build_context)(
        url="memory://test/root",
        timeframe="30d",  # Last 30 days
    )

    # Calculate total related items
    total_recent_related = (
        sum(len(item.related_results) for item in recent_context.results) if recent_context.results else 0
    )
    total_older_related = (
        sum(len(item.related_results) for item in older_context.results) if older_context.results else 0
    )

    assert total_older_related >= total_recent_related


@pytest.mark.asyncio
async def test_get_discussion_context_not_found(client):
    """Test handling of non-existent URIs."""
    context = await mcp_fn(build_context)(url="memory://test/does-not-exist")

    assert isinstance(context, GraphContext)
    assert len(context.results) == 0
    assert context.metadata.primary_count == 0
    assert context.metadata.related_count == 0


# Test data for different timeframe formats
valid_timeframes = [
    "7d",  # Standard format
    "yesterday",  # Natural language
    "0d",  # Zero duration
]

invalid_timeframes = [
    "invalid",  # Nonsense string
    "tomorrow",  # Future date
]


@pytest.mark.asyncio
async def test_build_context_timeframe_formats(client, test_graph):
    """Test that build_context accepts various timeframe formats."""
    test_url = "memory://specs/test"

    # Test each valid timeframe
    for timeframe in valid_timeframes:
        try:
            result = await mcp_fn(build_context)(url=test_url, timeframe=timeframe, page=1, page_size=10, max_related=10)
            assert result is not None
        except Exception as e:
            pytest.fail(f"Failed with valid timeframe '{timeframe}': {e!s}")

    # Test invalid timeframes should raise ValidationError
    for timeframe in invalid_timeframes:
        with pytest.raises(ToolError):
            await mcp_fn(build_context)(url=test_url, timeframe=timeframe)
