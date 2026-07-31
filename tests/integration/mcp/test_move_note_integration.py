"""
Integration tests for adn_notes move operation (migrated from move_note MCP tool).

Tests the complete move note workflow: MCP client -> MCP server -> FastAPI -> database -> file system
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


async def move_note(client: Client, identifier: str, destination_path: str) -> str:
    """Move a note and return the markdown response text."""
    result = await client.call_tool(
        "adn_notes",
        {"op": {"operation": "move", "identifier": identifier, "destination": destination_path}},
    )
    assert len(result.content) == 1
    assert result.content[0].type == "text"
    return result.content[0].text


async def read_note(client: Client, identifier: str) -> str:
    """Read a note back and return the raw content (including Note Not Found bodies)."""
    result = await client.call_tool(
        "adn_notes",
        {"op": {"operation": "read", "identifier": identifier}},
    )
    assert len(result.content) == 1
    parsed = json.loads(result.content[0].text)
    return parsed["result"]["content"]


async def search(client: Client, query: str) -> str:
    """Run a text search and return the markdown response."""
    result = await client.call_tool(
        "adn_search",
        {"op": {"operation": "query", "text": query}},
    )
    assert len(result.content) == 1
    return result.content[0].text


@pytest.mark.asyncio
async def test_move_note_basic_operation(mcp_server, app):
    """Test basic move note operation to a new folder."""

    async with Client(mcp_server) as client:
        # Create a note to move
        await write_note(
            client,
            "Move Test Note",
            "source",
            "# Move Test Note\n\nThis note will be moved to a new location.",
            "test,move",
        )

        # Move the note to a new location
        move_text = await move_note(client, "Move Test Note", "destination/moved-note.md")

        # Should return successful move message
        assert "✅ Note moved successfully" in move_text
        assert "Move Test Note" in move_text
        assert "destination/moved-note.md" in move_text
        assert "📊 Database and search index updated" in move_text

        # Verify the note can be read from its new location
        content = await read_note(client, "destination/moved-note.md")
        assert "This note will be moved to a new location" in content

        # Verify the original location no longer works
        content_original = await read_note(client, "source/move-test-note.md")
        assert "Note Not Found" in content_original


@pytest.mark.asyncio
async def test_move_note_using_permalink(mcp_server, app):
    """Test moving a note using its permalink as identifier."""

    async with Client(mcp_server) as client:
        # Create a note to move
        await write_note(
            client,
            "Permalink Move Test",
            "test",
            "# Permalink Move Test\n\nMoving by permalink.",
            "test,permalink",
        )

        # Move using permalink
        move_text = await move_note(client, "test/permalink-move-test", "archive/permalink-moved.md")

        # Should successfully move
        assert "✅ Note moved successfully" in move_text
        assert "test/permalink-move-test" in move_text
        assert "archive/permalink-moved.md" in move_text

        # Verify accessibility at new location
        content = await read_note(client, "archive/permalink-moved.md")
        assert "Moving by permalink" in content


@pytest.mark.asyncio
async def test_move_note_with_observations_and_relations(mcp_server, app):
    """Test moving a note that contains observations and relations."""

    async with Client(mcp_server) as client:
        # Create complex note with observations and relations
        complex_content = """# Complex Note

This note has various structured content.

## Observations
- [feature] Has structured observations
- [tech] Uses markdown format
- [status] Ready for move testing

## Relations
- implements [[Auth System]]
- documented_in [[Move Guide]]
- depends_on [[File System]]

## Content
This note demonstrates moving complex content."""

        await write_note(
            client,
            "Complex Note",
            "complex",
            complex_content,
            "test,complex,move",
        )

        # Move the complex note
        move_text = await move_note(client, "Complex Note", "moved/complex-note.md")

        # Should successfully move
        assert "✅ Note moved successfully" in move_text
        assert "Complex Note" in move_text
        assert "moved/complex-note.md" in move_text

        # Verify content preservation including structured data
        content = await read_note(client, "moved/complex-note.md")
        assert "Has structured observations" in content
        assert "implements [[Auth System]]" in content
        assert "## Observations" in content
        assert "[feature]" in content  # Should show original markdown observations
        assert "## Relations" in content


@pytest.mark.asyncio
async def test_move_note_to_nested_directory(mcp_server, app):
    """Test moving a note to a deeply nested directory structure."""

    async with Client(mcp_server) as client:
        # Create a note
        await write_note(
            client,
            "Nested Move Test",
            "root",
            "# Nested Move Test\n\nThis will be moved deep.",
            "test,nested",
        )

        # Move to a deep nested structure
        move_text = await move_note(client, "Nested Move Test", "projects/2025/q2/work/nested-note.md")

        # Should successfully create directory structure and move
        assert "✅ Note moved successfully" in move_text
        assert "Nested Move Test" in move_text
        assert "projects/2025/q2/work/nested-note.md" in move_text

        # Verify accessibility
        content = await read_note(client, "projects/2025/q2/work/nested-note.md")
        assert "This will be moved deep" in content


@pytest.mark.asyncio
async def test_move_note_with_special_characters(mcp_server, app):
    """Test moving notes with special characters in titles and paths."""

    async with Client(mcp_server) as client:
        # Create note with special characters
        await write_note(
            client,
            "Special (Chars) & Symbols",
            "special",
            "# Special (Chars) & Symbols\n\nTesting special characters in move.",
            "test,special",
        )

        # Move to path with special characters
        move_text = await move_note(client, "Special (Chars) & Symbols", "archive/special-chars-note.md")

        # Should handle special characters properly
        assert "✅ Note moved successfully" in move_text
        assert "archive/special-chars-note.md" in move_text

        # Verify content preservation
        content = await read_note(client, "archive/special-chars-note.md")
        assert "Testing special characters in move" in content


@pytest.mark.asyncio
async def test_move_note_error_handling_note_not_found(mcp_server, app):
    """Test error handling when trying to move a non-existent note."""

    async with Client(mcp_server) as client:
        # Try to move a note that doesn't exist - should return error message
        move_text = await move_note(client, "Non-existent Note", "new/location.md")

        # Should contain error message about the failed operation
        assert "# Move Failed" in move_text
        assert "Non-existent Note" in move_text


@pytest.mark.asyncio
async def test_move_note_error_handling_invalid_destination(mcp_server, app):
    """Test error handling for invalid destination paths."""

    async with Client(mcp_server) as client:
        # Create a note to attempt moving
        await write_note(
            client,
            "Invalid Dest Test",
            "test",
            "# Invalid Dest Test\n\nThis move should fail.",
            "test,error",
        )

        # Try to move to absolute path (should fail) - should return error message
        move_text = await move_note(client, "Invalid Dest Test", "/absolute/path/note.md")

        # Should contain error message about the failed operation
        assert "# Move Failed" in move_text
        assert "/absolute/path/note.md" in move_text


@pytest.mark.asyncio
async def test_move_note_error_handling_destination_exists(mcp_server, app):
    """Test error handling when destination file already exists."""

    async with Client(mcp_server) as client:
        # Create source note
        await write_note(
            client,
            "Source Note",
            "source",
            "# Source Note\n\nThis is the source.",
            "test,source",
        )

        # Create destination note that already exists at the exact path we'll try to move to
        await write_note(
            client,
            "Existing Note",
            "destination",
            "# Existing Note\n\nThis already exists.",
            "test,existing",
        )

        # Try to move source to existing destination - should return error
        move_text = await move_note(client, "Source Note", "destination/Existing_Note.md")

        # Should return error message about destination existing
        assert "Move Failed" in move_text or "Destination already exists" in move_text
        assert "destination/Existing_Note.md" in move_text


@pytest.mark.asyncio
async def test_move_note_preserves_search_functionality(mcp_server, app):
    """Test that moved notes remain searchable after move operation."""

    async with Client(mcp_server) as client:
        # Create a note with searchable content
        await write_note(
            client,
            "Searchable Note",
            "original",
            """# Searchable Note

This note contains unique search terms:
- quantum mechanics
- artificial intelligence
- machine learning algorithms

## Features
- [technology] Advanced AI features
- [research] Quantum computing research

## Relations
- relates_to [[AI Research]]""",
            "search,test,move",
        )

        # Verify note is searchable before move
        search_before = await search(client, "quantum mechanics")
        assert "Searchable Note" in search_before

        # Move the note
        move_text = await move_note(client, "Searchable Note", "research/quantum-ai-note.md")
        assert "✅ Note moved successfully" in move_text

        # Verify note is still searchable after move
        search_after = await search(client, "quantum mechanics")
        assert "quantum mechanics" in search_after
        assert "research/quantum-ai-note.md" in search_after or "quantum-ai-note" in search_after

        # Verify search by new location works
        search_by_path = await search(client, "research/quantum")
        assert "No results found" not in search_by_path


@pytest.mark.asyncio
async def test_move_note_using_different_identifier_formats(mcp_server, app):
    """Test moving notes using different identifier formats (title, permalink, folder/title)."""

    async with Client(mcp_server) as client:
        # Create notes for different identifier tests
        await write_note(
            client,
            "Title ID Note",
            "test",
            "# Title ID Note\n\nMove by title.",
            "test,identifier",
        )

        await write_note(
            client,
            "Permalink ID Note",
            "test",
            "# Permalink ID Note\n\nMove by permalink.",
            "test,identifier",
        )

        await write_note(
            client,
            "Folder Title Note",
            "test",
            "# Folder Title Note\n\nMove by folder/title.",
            "test,identifier",
        )

        # Test moving by title
        move1 = await move_note(client, "Title ID Note", "moved/title-moved.md")  # by title
        assert "✅ Note moved successfully" in move1

        # Test moving by permalink
        move2 = await move_note(client, "test/permalink-id-note", "moved/permalink-moved.md")  # by permalink
        assert "✅ Note moved successfully" in move2

        # Test moving by folder/title format
        move3 = await move_note(client, "test/Folder Title Note", "moved/folder-title-moved.md")  # by folder/title
        assert "✅ Note moved successfully" in move3

        # Verify all notes can be accessed at their new locations
        content1 = await read_note(client, "moved/title-moved.md")
        assert "Move by title" in content1

        content2 = await read_note(client, "moved/permalink-moved.md")
        assert "Move by permalink" in content2

        content3 = await read_note(client, "moved/folder-title-moved.md")
        assert "Move by folder/title" in content3


@pytest.mark.asyncio
async def test_move_note_cross_project_detection(mcp_server, app):
    """Test cross-project move detection and helpful error messages."""

    async with Client(mcp_server) as client:
        # Create a test project to simulate cross-project scenario
        create_result = await client.call_tool(
            "adn_project",
            {"op": {"operation": "create", "name": "test-project-b", "path": "/tmp/test-project-b"}},
        )
        assert create_result.content[0].type == "text"

        # Create a note in the default project
        await write_note(
            client,
            "Cross Project Test Note",
            "source",
            "# Cross Project Test Note\n\nThis note is in the default project.",
            "test,cross-project",
        )

        # Try to move to a path that contains the other project name
        move_text = await move_note(client, "Cross Project Test Note", "test-project-b/moved-note.md")

        # Should detect cross-project attempt and provide helpful guidance
        assert "Cross-Project Move Not Supported" in move_text
        assert "test-project-b" in move_text
        assert "switch_project" in move_text
        assert "read_note" in move_text
        assert "write_note" in move_text


@pytest.mark.asyncio
async def test_move_note_normal_moves_still_work(mcp_server, app):
    """Test that normal within-project moves still work after cross-project detection."""

    async with Client(mcp_server) as client:
        # Create a note
        await write_note(
            client,
            "Normal Move Note",
            "source",
            "# Normal Move Note\n\nThis should move normally.",
            "test,normal-move",
        )

        # Try a normal move that should work
        move_text = await move_note(client, "Normal Move Note", "destination/normal-moved.md")

        # Should work normally
        assert "✅ Note moved successfully" in move_text
        assert "Normal Move Note" in move_text
        assert "destination/normal-moved.md" in move_text

        # Verify the note can be read from its new location
        content = await read_note(client, "destination/normal-moved.md")
        assert "This should move normally" in content
