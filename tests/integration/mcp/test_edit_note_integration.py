"""
Integration tests for adn_notes edit operation (migrated from edit_note MCP tool).

Tests the complete edit note workflow: MCP client -> MCP server -> FastAPI -> database
"""

import json

import pytest
from fastmcp import Client


def parse_text(result) -> dict:
    """Parse a JSON text response."""
    assert len(result.content) == 1
    assert result.content[0].type == "text"
    return json.loads(result.content[0].text)


async def write_note(client: Client, title: str, folder: str, content: str, tags: str | None = None):
    """Helper: write a note through the adn_notes portmanteau."""
    op = {"operation": "write", "title": title, "folder": folder, "content": content}
    if tags is not None:
        op["tags"] = tags
    await client.call_tool("adn_notes", {"op": op})


async def edit_note(client: Client, identifier: str, mode: str, content: str, section=None, find_text=None):
    """Helper: edit a note through the adn_notes portmanteau."""
    op = {"operation": "edit", "identifier": identifier, "mode": mode, "content": content}
    if section is not None:
        op["section"] = section
    if find_text is not None:
        op["find_text"] = find_text
    return await client.call_tool("adn_notes", {"op": op})


async def read_note(client: Client, identifier: str) -> str:
    """Read a note back and return the raw markdown content."""
    result = await client.call_tool(
        "adn_notes",
        {"op": {"operation": "read", "identifier": identifier}},
    )
    parsed = parse_text(result)
    assert parsed["success"] is True
    return parsed["result"]["content"]


@pytest.mark.asyncio
async def test_edit_note_append_operation(mcp_server, app):
    """Test appending content to an existing note."""

    async with Client(mcp_server) as client:
        # First create a note
        await write_note(
            client,
            "Append Test Note",
            "test",
            "# Append Test Note\n\nOriginal content here.",
            "test,append",
        )

        # Test appending content
        edit_result = await edit_note(
            client,
            "Append Test Note",
            "append",
            "\n\n## New Section\n\nThis content was appended.",
        )

        # Should return successful edit summary
        parsed = parse_text(edit_result)
        assert parsed["success"] is True
        assert "Edited note (append)" in parsed["summary"]
        assert "lines to end of note" in parsed["summary"]
        assert parsed["permalink"] == "test/append-test-note"

        # Verify the content was actually appended
        content = await read_note(client, "Append Test Note")
        assert "Original content here." in content
        assert "## New Section" in content
        assert "This content was appended." in content


@pytest.mark.asyncio
async def test_edit_note_prepend_operation(mcp_server, app):
    """Test prepending content to an existing note."""

    async with Client(mcp_server) as client:
        # Create a note
        await write_note(
            client,
            "Prepend Test Note",
            "test",
            "# Prepend Test Note\n\nExisting content.",
            "test,prepend",
        )

        # Test prepending content
        edit_result = await edit_note(
            client,
            "test/prepend-test-note",
            "prepend",
            "## Important Update\n\nThis was added at the top.\n\n",
        )

        # Should return successful edit summary
        parsed = parse_text(edit_result)
        assert parsed["success"] is True
        assert "Edited note (prepend)" in parsed["summary"]
        assert "lines to beginning of note" in parsed["summary"]

        # Verify the content was prepended after frontmatter
        content = await read_note(client, "test/prepend-test-note")
        assert "## Important Update" in content
        assert "This was added at the top." in content
        assert "Existing content." in content
        # Check that prepended content comes before existing content
        prepend_pos = content.find("Important Update")
        existing_pos = content.find("Existing content")
        assert prepend_pos < existing_pos


@pytest.mark.asyncio
async def test_edit_note_find_replace_operation(mcp_server, app):
    """Test find and replace operation on an existing note.

    NOTE: The new adn_notes edit surface (NotesEditOp) has no
    ``expected_replacements`` field, and the server default of 1 makes
    find_replace fail validation when the text occurs multiple times. The
    original test replaced 3 occurrences of v1.0.0; the closest equivalent on
    the new surface is a note with exactly one occurrence, which verifies the
    same find-and-replace behavior end to end.
    """

    async with Client(mcp_server) as client:
        # Create a note with content to replace (single occurrence)
        await write_note(
            client,
            "Find Replace Test",
            "test",
            """# Find Replace Test

This is version v1.0.0 of the system.

## Notes
- Next version will be v1.1.0""",
            "test,version",
        )

        # Test find and replace operation
        edit_result = await edit_note(
            client,
            "Find Replace Test",
            "find_replace",
            "v1.2.0",
            find_text="v1.0.0",
        )

        # Should return successful edit summary
        parsed = parse_text(edit_result)
        assert parsed["success"] is True
        assert "Edited note (find_replace)" in parsed["summary"]
        assert "Find and replace operation completed" in parsed["summary"]

        # Verify the replacement was made
        content = await read_note(client, "Find Replace Test")
        assert "v1.2.0" in content
        assert "v1.0.0" not in content  # Should be completely replaced


@pytest.mark.asyncio
async def test_edit_note_replace_section_operation(mcp_server, app):
    """Test replacing content under a specific section header."""

    async with Client(mcp_server) as client:
        # Create a note with sections
        await write_note(
            client,
            "Section Replace Test",
            "test",
            """# Section Replace Test

## Overview
Original overview content.

## Implementation
Old implementation details here.
This will be replaced.

## Future Work
Some future work notes.""",
            "test,section",
        )

        # Test replacing section content
        edit_result = await edit_note(
            client,
            "test/section-replace-test",
            "replace_section",
            """New implementation approach using microservices.

- Service A handles authentication
- Service B manages data processing
- Service C provides API endpoints

All services communicate via message queues.""",
            section="## Implementation",
        )

        # Should return successful edit summary
        parsed = parse_text(edit_result)
        assert parsed["success"] is True
        assert "Edited note (replace_section)" in parsed["summary"]
        assert "Replaced content under section" in parsed["summary"]

        # Verify the section was replaced
        content = await read_note(client, "Section Replace Test")
        assert "New implementation approach using microservices" in content
        assert "Old implementation details here" not in content
        assert "Service A handles authentication" in content
        # Other sections should remain unchanged
        assert "Original overview content" in content
        assert "Some future work notes" in content


@pytest.mark.asyncio
async def test_edit_note_with_observations_and_relations(mcp_server, app):
    """Test editing a note that has observations and relations, and verify they're updated."""

    async with Client(mcp_server) as client:
        # Create a complex note with observations and relations
        complex_content = """# API Documentation

The API provides REST endpoints for data access.

## Observations
- [feature] User authentication endpoints
- [tech] Built with FastAPI framework
- [status] Currently in beta testing

## Relations
- implements [[Authentication System]]
- documented_in [[API Guide]]
- depends_on [[Database Schema]]

## Endpoints
Current endpoints include user management."""

        await write_note(
            client,
            "API Documentation",
            "docs",
            complex_content,
            "api,docs",
        )

        # Add new content with observations and relations
        new_content = """
## New Features
- [feature] Added payment processing endpoints
- [feature] Implemented rate limiting
- [security] Added OAuth2 authentication

## Additional Relations
- integrates_with [[Payment Gateway]]
- secured_by [[OAuth2 Provider]]"""

        edit_result = await edit_note(
            client,
            "API Documentation",
            "append",
            new_content,
        )

        # Should return edit summary with observation and relation counts
        parsed = parse_text(edit_result)
        assert parsed["success"] is True
        assert "Edited note (append)" in parsed["summary"]
        assert "## Observations" in parsed["summary"]
        assert "## Relations" in parsed["summary"]
        # Should have feature, tech, status, security categories
        assert "- feature:" in parsed["summary"]
        assert "- security:" in parsed["summary"]
        assert "- tech:" in parsed["summary"]
        assert "- status:" in parsed["summary"]

        # Verify the content was added and processed
        content = await read_note(client, "API Documentation")
        assert "Added payment processing endpoints" in content
        assert "integrates_with [[Payment Gateway]]" in content


@pytest.mark.asyncio
async def test_edit_note_error_handling_note_not_found(mcp_server, app):
    """Test error handling when trying to edit a non-existent note."""

    async with Client(mcp_server) as client:
        # Try to edit a note that doesn't exist
        edit_result = await edit_note(
            client,
            "Non-existent Note",
            "append",
            "Some content to add",
        )

        # Should return helpful error message (structured error dict)
        parsed = parse_text(edit_result)
        assert parsed["success"] is False
        assert "Edit Failed" in parsed["message"]
        assert "Non-existent Note" in parsed["message"]
        assert "search_notes(" in parsed["message"]


@pytest.mark.asyncio
async def test_edit_note_error_handling_text_not_found(mcp_server, app):
    """Test error handling when find_text is not found in the note."""

    async with Client(mcp_server) as client:
        # Create a note
        await write_note(
            client,
            "Error Test Note",
            "test",
            "# Error Test Note\n\nThis note has specific content.",
            "test,error",
        )

        # Try to replace text that doesn't exist
        edit_result = await edit_note(
            client,
            "Error Test Note",
            "find_replace",
            "replacement text",
            find_text="non-existent text",
        )

        # Should return helpful error message (structured error dict)
        parsed = parse_text(edit_result)
        assert parsed["success"] is False
        assert "Edit Failed - Text Not Found" in parsed["message"]
        assert "non-existent text" in parsed["message"]
        assert "Error Test Note" in parsed["message"]
        assert "read_note(" in parsed["message"]


@pytest.mark.asyncio
async def test_edit_note_error_handling_wrong_replacement_count(mcp_server, app):
    """Test error handling when actual occurrences don't match the expected count.

    NOTE: The new adn_notes edit surface (NotesEditOp) has no
    ``expected_replacements`` field, so the server always validates against the
    default of 1. The note below contains 3 occurrences of "test", so the edit
    fails with a count mismatch - the same validation behavior, with the
    expected count now fixed at 1.
    """

    async with Client(mcp_server) as client:
        # Create a note with specific repeated text
        await write_note(
            client,
            "Count Test Note",
            "test",
            """# Count Test Note

The word "test" appears here.
This is another test sentence.
Final test of the content.""",
            "test,count",
        )

        # Try to replace "test" - 3 occurrences found, server expects 1
        edit_result = await edit_note(
            client,
            "Count Test Note",
            "find_replace",
            "example",
            find_text="test",
        )

        # Should return helpful error message about count mismatch
        parsed = parse_text(edit_result)
        assert parsed["success"] is False
        assert "Edit Failed - Wrong Replacement Count" in parsed["message"]
        assert "Expected 1 occurrences" in parsed["message"]
        assert "test" in parsed["message"]
        assert "expected_replacements=" in parsed["message"]


@pytest.mark.asyncio
async def test_edit_note_invalid_operation(mcp_server, app):
    """Test error handling for invalid operation parameter."""

    async with Client(mcp_server) as client:
        # Create a note
        await write_note(
            client,
            "Invalid Op Test",
            "test",
            "# Invalid Op Test\n\nSome content.",
            "test",
        )

        # Try to use an invalid mode - the new surface validates the mode
        # Literal at the schema boundary, so this raises a ToolError
        with pytest.raises(Exception) as exc_info:
            await edit_note(
                client,
                "Invalid Op Test",
                "invalid_operation",
                "Some content",
            )

        # Should contain information about invalid operation
        error_message = str(exc_info.value)
        assert "invalid_operation" in error_message
        # The Literal validation message lists the valid modes
        assert "append" in error_message
        assert "prepend" in error_message


@pytest.mark.asyncio
async def test_edit_note_missing_required_parameters(mcp_server, app):
    """Test error handling when required parameters are missing."""

    async with Client(mcp_server) as client:
        # Create a note
        await write_note(
            client,
            "Param Test Note",
            "test",
            "# Param Test Note\n\nContent here.",
            "test",
        )

        # Try find_replace without find_text parameter
        edit_result = await edit_note(
            client,
            "Param Test Note",
            "find_replace",
            "replacement",
            # Missing find_text parameter
        )

        # Should return helpful error message
        parsed = parse_text(edit_result)
        assert parsed["success"] is False
        assert "find_text" in parsed["message"]
        assert "find_replace" in parsed["message"]


@pytest.mark.asyncio
async def test_edit_note_special_characters_in_content(mcp_server, app):
    """Test editing notes with special characters, Unicode, and markdown formatting."""

    async with Client(mcp_server) as client:
        # Create a note
        await write_note(
            client,
            "Special Chars Test",
            "test",
            "# Special Chars Test\n\nBasic content here.",
            "test,unicode",
        )

        # Add content with special characters and Unicode
        special_content = """
## Unicode Section 🚀

This section contains:
- Emojis: 🎉 💡 ⚡ 🔥
- Languages: 测试中文 Tëst Übër
- Math symbols: ∑∏∂∇∆Ω ≠≤≥ ∞
- Special markdown: `code` **bold** *italic*
- URLs: https://example.com/path?param=value&other=123
- Code blocks:
```python
def test_function():
    return "Hello, 世界!"
```

## Observations
- [unicode] Unicode characters preserved ✓
- [markdown] Formatting maintained 📝

## Relations
- documented_in [[Unicode Standards]]"""

        edit_result = await edit_note(
            client,
            "Special Chars Test",
            "append",
            special_content,
        )

        # Should successfully handle special characters
        parsed = parse_text(edit_result)
        assert parsed["success"] is True
        assert "Edited note (append)" in parsed["summary"]
        assert "## Observations" in parsed["summary"]
        assert "- unicode:" in parsed["summary"]
        assert "- markdown:" in parsed["summary"]

        # Verify the special content was added correctly
        content = await read_note(client, "Special Chars Test")
        assert "🚀" in content
        assert "测试中文" in content
        assert "∑∏∂∇∆Ω" in content
        assert "def test_function():" in content
        assert "[[Unicode Standards]]" in content


@pytest.mark.asyncio
async def test_edit_note_using_different_identifiers(mcp_server, app):
    """Test editing notes using different identifier formats (title, permalink, folder/title)."""

    async with Client(mcp_server) as client:
        # Create a note
        await write_note(
            client,
            "Identifier Test Note",
            "docs",
            "# Identifier Test Note\n\nOriginal content.",
            "test,identifier",
        )

        # Test editing by title
        edit_result1 = await edit_note(
            client,
            "Identifier Test Note",  # by title
            "append",
            "\n\nEdited by title.",
        )
        assert parse_text(edit_result1)["success"] is True

        # Test editing by permalink
        edit_result2 = await edit_note(
            client,
            "docs/identifier-test-note",  # by permalink
            "append",
            "\n\nEdited by permalink.",
        )
        assert parse_text(edit_result2)["success"] is True

        # Test editing by folder/title format
        edit_result3 = await edit_note(
            client,
            "docs/Identifier Test Note",  # by folder/title
            "append",
            "\n\nEdited by folder/title.",
        )
        assert parse_text(edit_result3)["success"] is True

        # Verify all edits were applied
        content = await read_note(client, "docs/identifier-test-note")
        assert "Edited by title." in content
        assert "Edited by permalink." in content
        assert "Edited by folder/title." in content
