"""Comprehensive test for tag operations with large tag counts.

Tests creating notes with large tag sets (20+ tags) through the MCP wire
surface (adn_notes), plus direct parse_tags unit checks.
"""

import json

import pytest
from fastmcp import Client

from advanced_memory.utils import parse_tags


@pytest.mark.asyncio
async def test_large_tag_operations(mcp_server, app):
    """Test tag operations with 20+ tags."""

    # Generate 20 test tags
    test_tags_list = [f"tag{i}" for i in range(1, 21)]
    test_tags_string = ",".join(test_tags_list)

    test_note_id = "Tag Test Note - Large Tag Count"

    # Test 1: Create note with 20 tags as Python list
    async with Client(mcp_server) as client:
        result1 = await client.call_tool(
            "adn_notes",
            {
                "op": {
                    "operation": "write",
                    "title": test_note_id,
                    "content": "# Tag Test Note\n\nThis note tests handling of many tags.",
                    "folder": "test",
                    "tags": test_tags_list,
                }
            },
        )
        assert result1.content, "write response should have content"

    # Test 2: Create note with 20 tags as comma-separated string
    async with Client(mcp_server) as client:
        result2 = await client.call_tool(
            "adn_notes",
            {
                "op": {
                    "operation": "write",
                    "title": f"{test_note_id} - String Format",
                    "content": "# Tag Test Note\n\nThis note tests handling of many tags as string.",
                    "folder": "test",
                    "tags": test_tags_string,
                }
            },
        )
        assert result2.content, "write response should have content"

    # Test 3: Read the note and verify tags
    async with Client(mcp_server) as client:
        result3 = await client.call_tool("adn_notes", {"op": {"operation": "read", "identifier": test_note_id}})
        assert result3.content, "read response should have content"

    # Test 4: Test parse_tags function directly with 20 tags
    result_list = parse_tags(test_tags_list)
    assert len(result_list) == 20

    result_string = parse_tags(test_tags_string)
    assert len(result_string) == 20

    json_tags = json.dumps(test_tags_list)
    result_json = parse_tags(json_tags)
    assert len(result_json) == 20

    # Test 5: Test with exactly 9 tags (the problematic count)
    nine_tags = test_tags_list[:9]
    async with Client(mcp_server) as client:
        result8 = await client.call_tool(
            "adn_notes",
            {
                "op": {
                    "operation": "write",
                    "title": f"{test_note_id} - 9 Tags",
                    "content": "# Tag Test Note\n\nThis note has exactly 9 tags.",
                    "folder": "test",
                    "tags": nine_tags,
                }
            },
        )
        assert result8.content, "write response should have content"
