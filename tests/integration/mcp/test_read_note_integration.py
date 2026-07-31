"""
Integration tests for adn_notes read operation (migrated from read_note MCP tool).

Tests the full flow: MCP client -> MCP server -> FastAPI -> database
"""

import json

import pytest
from fastmcp import Client


@pytest.mark.asyncio
async def test_read_note_after_write(mcp_server, app):
    """Test read after write using real database."""

    async with Client(mcp_server) as client:
        # First write a note
        write_result = await client.call_tool(
            "adn_notes",
            {
                "op": {
                    "operation": "write",
                    "title": "Test Note",
                    "folder": "test",
                    "content": "# Test Note\n\nThis is test content.",
                    "tags": "test,integration",
                }
            },
        )

        assert len(write_result.content) == 1
        assert write_result.content[0].type == "text"
        write_parsed = json.loads(write_result.content[0].text)
        assert write_parsed["success"] is True
        assert write_parsed["result"]["permalink"] == "test/test-note"

        # Then read it back
        read_result = await client.call_tool(
            "adn_notes",
            {
                "op": {"operation": "read", "identifier": "Test Note"},
            },
        )

        assert len(read_result.content) == 1
        assert read_result.content[0].type == "text"
        read_parsed = json.loads(read_result.content[0].text)

        assert read_parsed["success"] is True
        content = read_parsed["result"]["content"]

        # Should contain the note content and metadata
        assert "# Test Note" in content
        assert "This is test content." in content
        assert "test/test-note" in content  # permalink
