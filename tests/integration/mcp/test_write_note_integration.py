"""
Integration tests for adn_notes write operation (migrated from write_note MCP tool).

Comprehensive tests covering all scenarios including note creation, content formatting,
tag handling, error conditions, and edge cases from bug reports.
"""

import json
from textwrap import dedent

import pytest
from fastmcp import Client


def parse_write_response(mcp_result):
    """Parse the JSON text response from adn_notes write."""
    assert len(mcp_result.content) == 1
    assert mcp_result.content[0].type == "text"
    return json.loads(mcp_result.content[0].text)


async def read_note(client: Client, identifier: str) -> str:
    """Read a note back via adn_notes read and return the raw markdown content."""
    result = await client.call_tool(
        "adn_notes",
        {"op": {"operation": "read", "identifier": identifier}},
    )
    assert len(result.content) == 1
    parsed = json.loads(result.content[0].text)
    assert parsed["success"] is True
    return parsed["result"]["content"]


async def write_note(client: Client, title: str, folder: str, content: str, tags=None):
    """Helper: write a note through the adn_notes portmanteau."""
    op = {"operation": "write", "title": title, "folder": folder, "content": content}
    if tags is not None:
        op["tags"] = tags
    return await client.call_tool("adn_notes", {"op": op})


@pytest.mark.asyncio
async def test_write_note_basic_creation(mcp_server, app):
    """Test creating a simple note with basic content."""

    async with Client(mcp_server) as client:
        result = await write_note(
            client,
            "Simple Note",
            "basic",
            "# Simple Note\n\nThis is a simple note for testing.",
            "simple,test",
        )

        parsed = parse_write_response(result)

        assert parsed["success"] is True
        assert parsed["operation"] == "write"
        assert parsed["result"]["title"] == "Simple Note"
        assert parsed["result"]["folder"] == "basic"
        assert parsed["result"]["permalink"] == "basic/simple-note"
        assert parsed["result"]["tags"] == ["simple", "test"]


@pytest.mark.asyncio
async def test_write_note_no_tags(mcp_server, app):
    """Test creating a note without tags."""

    async with Client(mcp_server) as client:
        result = await write_note(
            client,
            "No Tags Note",
            "test",
            "Just some plain text without tags.",
        )

        parsed = parse_write_response(result)

        assert parsed["success"] is True
        assert parsed["result"]["title"] == "No Tags Note"
        assert parsed["result"]["folder"] == "test"
        assert parsed["result"]["permalink"] == "test/no-tags-note"
        # Should not have tags when no tags provided
        assert parsed["result"]["tags"] == []


@pytest.mark.asyncio
async def test_write_note_update_existing(mcp_server, app):
    """Test updating an existing note."""

    async with Client(mcp_server) as client:
        # Create initial note
        result1 = await write_note(
            client,
            "Update Test",
            "test",
            "# Update Test\n\nOriginal content.",
            "original",
        )

        assert parse_write_response(result1)["success"] is True

        # Update the same note
        result2 = await write_note(
            client,
            "Update Test",
            "test",
            "# Update Test\n\nUpdated content with changes.",
            "updated,modified",
        )

        parsed = parse_write_response(result2)

        assert parsed["success"] is True
        assert parsed["result"]["title"] == "Update Test"
        assert parsed["result"]["permalink"] == "test/update-test"
        assert parsed["result"]["tags"] == ["updated", "modified"]

        # Verify the update actually replaced the content
        content = await read_note(client, "test/update-test")
        assert "Updated content with changes." in content
        assert "Original content." not in content


@pytest.mark.asyncio
async def test_write_note_tag_array(mcp_server, app):
    """Test creating a note with tag array (Issue #38 regression test)."""

    async with Client(mcp_server) as client:
        # This reproduces the exact bug from Issue #38
        result = await write_note(
            client,
            "Array Tags Test",
            "test",
            "Testing tag array handling",
            ["python", "testing", "integration", "mcp"],
        )

        parsed = parse_write_response(result)

        assert parsed["success"] is True
        assert parsed["result"]["title"] == "Array Tags Test"
        assert parsed["result"]["folder"] == "test"
        assert parsed["result"]["permalink"] == "test/array-tags-test"
        assert parsed["result"]["tags"] == ["python", "testing", "integration", "mcp"]


@pytest.mark.asyncio
async def test_write_note_custom_permalink(mcp_server, app):
    """Test custom permalink handling (Issue #93 regression test)."""

    async with Client(mcp_server) as client:
        content_with_custom_permalink = dedent("""
            ---
            permalink: custom/my-special-permalink
            ---

            # Custom Permalink Note

            This note has a custom permalink in frontmatter.

            - [note] Testing custom permalink preservation
        """).strip()

        result = await write_note(
            client,
            "Custom Permalink Note",
            "notes",
            content_with_custom_permalink,
        )

        parsed = parse_write_response(result)

        assert parsed["success"] is True
        assert parsed["result"]["title"] == "Custom Permalink Note"
        # Custom permalink from frontmatter should be preserved
        assert parsed["result"]["permalink"] == "custom/my-special-permalink"

        # The note should be readable at the custom permalink
        content = await read_note(client, "custom/my-special-permalink")
        assert "# Custom Permalink Note" in content


@pytest.mark.asyncio
async def test_write_note_unicode_content(mcp_server, app):
    """Test handling unicode content including emojis."""

    async with Client(mcp_server) as client:
        unicode_content = (
            "# Unicode Test 🚀\n\nThis note has emoji 🎉 and unicode ♠♣♥♦\n\n- [note] Testing unicode handling 测试"
        )

        result = await write_note(
            client,
            "Unicode Test 🌟",
            "test",
            unicode_content,
            "unicode,emoji,测试",
        )

        parsed = parse_write_response(result)

        assert parsed["success"] is True
        assert parsed["result"]["folder"] == "test"
        # Permalink should be sanitized (emoji removed from title)
        assert parsed["result"]["permalink"] == "test/unicode-test"
        assert parsed["result"]["tags"] == ["unicode", "emoji", "测试"]

        # All unicode content should round-trip through read
        content = await read_note(client, "test/unicode-test")
        assert "🚀" in content
        assert "🎉" in content
        assert "♠♣♥♦" in content
        assert "测试" in content


@pytest.mark.asyncio
async def test_write_note_complex_content_with_observations_relations(mcp_server, app):
    """Test creating note with complex content including observations and relations."""

    async with Client(mcp_server) as client:
        complex_content = dedent("""
            # Complex Note

            This note demonstrates the full knowledge format.

            ## Observations
            - [tech] Uses Python and FastAPI
            - [design] Follows MCP protocol specification
            - [note] Integration tests are comprehensive

            ## Relations
            - implements [[MCP Protocol]]
            - depends_on [[FastAPI Framework]]
            - tested_by [[Integration Tests]]

            ## Additional Content

            Some more regular markdown content here.
        """).strip()

        result = await write_note(
            client,
            "Complex Knowledge Note",
            "knowledge",
            complex_content,
            "complex,knowledge,relations",
        )

        parsed = parse_write_response(result)

        assert parsed["success"] is True
        assert parsed["result"]["permalink"] == "knowledge/complex-knowledge-note"
        assert parsed["result"]["folder"] == "knowledge"
        # Should show observation and relation counts
        assert parsed["result"]["observations_count"] == 3
        assert parsed["result"]["relations_count"] == 3
        assert parsed["result"]["resolved_relations"] == 0
        assert parsed["result"]["unresolved_relations"] == 3

        # Structured content should be preserved in the note body
        content = await read_note(client, "knowledge/complex-knowledge-note")
        assert "## Observations" in content
        assert "## Relations" in content
        assert "[tech] Uses Python and FastAPI" in content
        assert "implements [[MCP Protocol]]" in content


@pytest.mark.asyncio
async def test_write_note_preserve_frontmatter(mcp_server, app):
    """Test that custom frontmatter is preserved when updating notes."""

    async with Client(mcp_server) as client:
        content_with_frontmatter = dedent("""
            ---
            title: Frontmatter Note
            type: note
            version: 1.0
            author: Test Author
            status: draft
            ---

            # Frontmatter Note

            This note has custom frontmatter that should be preserved.
        """).strip()

        result = await write_note(
            client,
            "Frontmatter Note",
            "test",
            content_with_frontmatter,
            "frontmatter,preservation",
        )

        parsed = parse_write_response(result)

        assert parsed["success"] is True
        assert parsed["result"]["permalink"] == "test/frontmatter-note"
        assert parsed["result"]["tags"] == ["frontmatter", "preservation"]

        # Custom frontmatter fields should be preserved in the stored note
        content = await read_note(client, "test/frontmatter-note")
        assert "author: Test Author" in content
        assert "status: draft" in content
        assert "version: 1.0" in content
