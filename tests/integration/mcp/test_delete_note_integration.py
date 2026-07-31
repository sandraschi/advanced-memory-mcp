"""
Integration tests for adn_notes delete operation (migrated from delete_note MCP tool).

Tests the complete delete note workflow: MCP client -> MCP server -> FastAPI -> database
"""

import json

import pytest
from fastmcp import Client


async def write_note(client: Client, title: str, folder: str, content: str, tags: str | None = None):
    """Helper: write a note through the adn_notes portmanteau."""
    op = {"operation": "write", "title": title, "folder": folder, "content": content}
    if tags is not None:
        op["tags"] = tags
    await client.call_tool("adn_notes", {"op": op})


async def read_note(client: Client, identifier: str) -> str:
    """Read a note back and return the raw content (including Note Not Found bodies)."""
    result = await client.call_tool(
        "adn_notes",
        {"op": {"operation": "read", "identifier": identifier}},
    )
    assert len(result.content) == 1
    assert result.content[0].type == "text"
    parsed = json.loads(result.content[0].text)
    return parsed["result"]["content"]


async def delete_note(client: Client, identifier: str) -> str:
    """Delete a note and return the markdown response text."""
    result = await client.call_tool(
        "adn_notes",
        {"op": {"operation": "delete", "identifier": identifier}},
    )
    assert len(result.content) == 1
    assert result.content[0].type == "text"
    return result.content[0].text


async def search(client: Client, query: str) -> str:
    """Run a text search and return the markdown response."""
    result = await client.call_tool(
        "adn_search",
        {"op": {"operation": "query", "text": query}},
    )
    assert len(result.content) == 1
    assert result.content[0].type == "text"
    return result.content[0].text


@pytest.mark.asyncio
async def test_delete_note_by_title(mcp_server, app):
    """Test deleting a note by its title."""

    async with Client(mcp_server) as client:
        # First create a note
        await write_note(
            client,
            "Note to Delete",
            "test",
            "# Note to Delete\n\nThis note will be deleted.",
            "test,delete",
        )

        # Verify the note exists by reading it
        content = await read_note(client, "Note to Delete")
        assert "Note to Delete" in content

        # Delete the note by title
        delete_text = await delete_note(client, "Note to Delete")

        # Should return a successful deletion message
        assert "# Delete Complete" in delete_text

        # Verify the note no longer exists
        content_after = await read_note(client, "Note to Delete")

        # Should return helpful "Note Not Found" message instead of the actual note
        assert "Note Not Found" in content_after
        assert "Note to Delete" in content_after


@pytest.mark.asyncio
async def test_delete_note_by_permalink(mcp_server, app):
    """Test deleting a note by its permalink."""

    async with Client(mcp_server) as client:
        # Create a note
        await write_note(
            client,
            "Permalink Delete Test",
            "tests",
            "# Permalink Delete Test\n\nTesting deletion by permalink.",
            "test,permalink",
        )

        # Delete the note by permalink
        delete_text = await delete_note(client, "tests/permalink-delete-test")

        # Should return a successful deletion message
        assert "# Delete Complete" in delete_text

        # Verify the note no longer exists by searching
        result_text = await search(client, "Permalink Delete Test")

        # Should have no results
        assert "No results found for your query." in result_text


@pytest.mark.asyncio
async def test_delete_note_with_observations_and_relations(mcp_server, app):
    """Test deleting a note that has observations and relations."""

    async with Client(mcp_server) as client:
        # Create a complex note with observations and relations
        complex_content = """# Project Management System

This is a comprehensive project management system.

## Observations
- [feature] Task tracking functionality
- [feature] User authentication system
- [tech] Built with Python and Flask
- [status] Currently in development

## Relations
- depends_on [[Database Schema]]
- implements [[User Stories]]
- part_of [[Main Application]]

The system handles multiple projects and users."""

        await write_note(
            client,
            "Project Management System",
            "projects",
            complex_content,
            "project,management,system",
        )

        # Verify the note exists and has content
        content = await read_note(client, "Project Management System")
        assert "Task tracking functionality" in content
        assert "depends_on" in content

        # Delete the complex note
        delete_text = await delete_note(client, "projects/project-management-system")

        # Should return a successful deletion message
        assert "# Delete Complete" in delete_text

        # Verify the note is deleted
        content_after = await read_note(client, "Project Management System")

        # Should return "Note Not Found" message
        assert "Note Not Found" in content_after
        assert "Project Management System" in content_after


@pytest.mark.asyncio
async def test_delete_note_special_characters_in_title(mcp_server, app):
    """Test deleting notes with special characters in the title."""

    async with Client(mcp_server) as client:
        # Create notes with special characters
        special_titles = [
            "Note with spaces",
            "Note-with-dashes",
            "Note_with_underscores",
            "Note (with parentheses)",
            "Note & Symbols!",
        ]

        # Create all the notes
        for title in special_titles:
            await write_note(
                client,
                title,
                "special",
                f"# {title}\n\nContent for {title}",
                "special,characters",
            )

        # Delete each note by title
        for title in special_titles:
            delete_text = await delete_note(client, title)

            # Each deletion should be successful
            assert "# Delete Complete" in delete_text, f"Failed to delete note: {title}"

            # Verify the note is deleted
            content_after = await read_note(client, title)

            # Should return "Note Not Found" message
            assert "Note Not Found" in content_after
            assert title in content_after


@pytest.mark.asyncio
async def test_delete_nonexistent_note(mcp_server, app):
    """Test attempting to delete a note that doesn't exist."""

    async with Client(mcp_server) as client:
        # Try to delete a note that doesn't exist
        delete_text = await delete_note(client, "Nonexistent Note")

        # Should return a helpful failure message
        assert "# Delete Failed" in delete_text
        assert "Nonexistent Note" in delete_text


@pytest.mark.asyncio
async def test_delete_note_by_file_path(mcp_server, app):
    """Test deleting a note using its file path."""

    async with Client(mcp_server) as client:
        # Create a note
        await write_note(
            client,
            "File Path Delete",
            "docs",
            "# File Path Delete\n\nTesting deletion by file path.",
            "test,filepath",
        )

        # Try to delete using the file path (should work as an identifier)
        delete_text = await delete_note(client, "docs/File_Path_Delete.md")

        # Should return a successful deletion message
        assert "# Delete Complete" in delete_text

        # Verify deletion
        content_after = await read_note(client, "File Path Delete")

        # Should return "Note Not Found" message
        assert "Note Not Found" in content_after
        assert "File Path Delete" in content_after


@pytest.mark.asyncio
async def test_delete_note_case_insensitive(mcp_server, app):
    """Test that note deletion is case insensitive for titles."""

    async with Client(mcp_server) as client:
        # Create a note with mixed case
        await write_note(
            client,
            "CamelCase Note Title",
            "test",
            "# CamelCase Note Title\n\nTesting case sensitivity.",
            "test,case",
        )

        # Try to delete with different case
        delete_text = await delete_note(client, "camelcase note title")

        # Should return a successful deletion message
        assert "# Delete Complete" in delete_text


@pytest.mark.asyncio
async def test_delete_multiple_notes_sequentially(mcp_server, app):
    """Test deleting multiple notes in sequence."""

    async with Client(mcp_server) as client:
        # Create multiple notes
        note_titles = [
            "First Note",
            "Second Note",
            "Third Note",
            "Fourth Note",
            "Fifth Note",
        ]

        for title in note_titles:
            await write_note(
                client,
                title,
                "batch",
                f"# {title}\n\nContent for {title}",
                "batch,test",
            )

        # Delete all notes sequentially
        for title in note_titles:
            delete_text = await delete_note(client, title)

            # Each deletion should be successful
            assert "# Delete Complete" in delete_text, f"Failed to delete {title}"

        # Verify all notes are deleted by searching
        result_text = await search(client, "batch")

        # Should have no results
        assert "No results found for your query." in result_text


@pytest.mark.asyncio
async def test_delete_note_with_unicode_content(mcp_server, app):
    """Test deleting notes with Unicode content."""

    async with Client(mcp_server) as client:
        # Create a note with Unicode content
        unicode_content = """# Unicode Test Note 🚀

This note contains various Unicode characters:
- Emojis: 🎉 🔥 ⚡ 💡
- Languages: 测试中文 Tëst Übër
- Symbols: ♠♣♥♦ ←→↑↓ ∞≠≤≥
- Math: ∑∏∂∇∆Ω

## Observations
- [test] Unicode characters preserved ✓
- [note] Emoji support working 🎯

## Relations
- supports [[Unicode Standards]]
- tested_with [[Various Languages]]"""

        await write_note(
            client,
            "Unicode Test Note",
            "unicode",
            unicode_content,
            "unicode,test,emoji",
        )

        # Delete the Unicode note
        delete_text = await delete_note(client, "Unicode Test Note")

        # Should return a successful deletion message
        assert "# Delete Complete" in delete_text

        # Verify deletion
        content_after = await read_note(client, "Unicode Test Note")

        # Should return "Note Not Found" message
        assert "Note Not Found" in content_after
        assert "Unicode Test Note" in content_after
