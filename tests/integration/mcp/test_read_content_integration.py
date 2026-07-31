"""
Integration tests for content reading via adn_notes read (migrated from read_content MCP tool).

Comprehensive tests covering text files, error cases, and memory:// URL handling
via the complete MCP client-server flow.

NOTE: The standalone read_content tool (with raw file type/content_type/encoding
metadata) no longer exists on the wire surface. The adn_notes read operation
returns the raw markdown (with frontmatter) of the requested note, which covers
the same reading behaviors: by file path, by permalink, and by memory:// URL.
"""

import json

import pytest
from fastmcp import Client


def read_content(client: Client, path: str) -> str:
    """Read note content by identifier and return the raw markdown."""
    result = client.call_tool(
        "adn_notes",
        {"op": {"operation": "read", "identifier": path}},
    )
    return result


async def get_content_text(client: Client, path: str) -> str:
    """Helper: read content via adn_notes read and extract the markdown body."""
    read_result = await read_content(client, path)
    assert len(read_result.content) == 1
    assert read_result.content[0].type == "text"
    parsed = json.loads(read_result.content[0].text)
    assert parsed["success"] is True
    return parsed["result"]["content"]


@pytest.mark.asyncio
async def test_read_content_markdown_file(mcp_server, app):
    """Test reading a markdown file created by adn_notes write."""

    async with Client(mcp_server) as client:
        # First create a note
        await client.call_tool(
            "adn_notes",
            {
                "op": {
                    "operation": "write",
                    "title": "Content Test",
                    "folder": "test",
                    "content": "# Content Test\n\nThis is test content with **markdown**.",
                    "tags": "test,content",
                }
            },
        )

        # Then read the raw file content by file path
        content = await get_content_text(client, "test/Content_Test.md")

        # Should contain the raw markdown with frontmatter
        assert "# Content Test" in content
        assert "This is test content with **markdown**." in content
        assert "tags:" in content  # frontmatter
        assert "- test" in content  # tags are in YAML list format
        assert "- content" in content


@pytest.mark.asyncio
async def test_read_content_by_permalink(mcp_server, app):
    """Test reading content using permalink instead of file path."""

    async with Client(mcp_server) as client:
        # Create a note
        await client.call_tool(
            "adn_notes",
            {
                "op": {
                    "operation": "write",
                    "title": "Permalink Test",
                    "folder": "docs",
                    "content": "# Permalink Test\n\nTesting permalink-based content reading.",
                }
            },
        )

        # Read by permalink (without .md extension)
        content = await get_content_text(client, "docs/permalink-test")

        assert "# Permalink Test" in content
        assert "Testing permalink-based content reading." in content


@pytest.mark.asyncio
async def test_read_content_memory_url(mcp_server, app):
    """Test reading content using memory:// URL format."""

    async with Client(mcp_server) as client:
        # Create a note
        await client.call_tool(
            "adn_notes",
            {
                "op": {
                    "operation": "write",
                    "title": "Memory URL Test",
                    "folder": "test",
                    "content": "# Memory URL Test\n\nTesting memory:// URL handling.",
                    "tags": "memory,url",
                }
            },
        )

        # Read using memory:// URL
        content = await get_content_text(client, "memory://test/memory-url-test")

        assert "# Memory URL Test" in content
        assert "Testing memory:// URL handling." in content


@pytest.mark.asyncio
async def test_read_content_unicode_file(mcp_server, app):
    """Test reading content with unicode characters and emojis."""

    async with Client(mcp_server) as client:
        # Create a note with unicode content
        unicode_content = "# Unicode Test 🚀\n\nThis note has emoji 🎉 and unicode ♠♣♥♦\n\n测试中文内容"

        await client.call_tool(
            "adn_notes",
            {
                "op": {
                    "operation": "write",
                    "title": "Unicode Content Test",
                    "folder": "test",
                    "content": unicode_content,
                    "tags": "unicode,emoji",
                }
            },
        )

        # Read the content back
        content = await get_content_text(client, "test/Unicode_Content_Test.md")

        # All unicode content should be preserved
        assert "🚀" in content
        assert "🎉" in content
        assert "♠♣♥♦" in content
        assert "测试中文内容" in content


@pytest.mark.asyncio
async def test_read_content_complex_frontmatter(mcp_server, app):
    """Test reading content with complex frontmatter and markdown."""

    async with Client(mcp_server) as client:
        # Create a note with complex content
        complex_content = """---
title: Complex Note
type: document
version: 1.0
author: Test Author
metadata:
  status: draft
  priority: high
---

# Complex Note

This note has complex frontmatter and various markdown elements.

## Observations
- [tech] Uses YAML frontmatter
- [design] Structured content format

## Relations
- related_to [[Other Note]]
- depends_on [[Framework]]

Regular markdown content continues here."""

        await client.call_tool(
            "adn_notes",
            {
                "op": {
                    "operation": "write",
                    "title": "Complex Note",
                    "folder": "docs",
                    "content": complex_content,
                    "tags": "complex,frontmatter",
                }
            },
        )

        # Read the content back
        content = await get_content_text(client, "docs/Complex_Note.md")

        # Should preserve all frontmatter and content structure
        assert "version: 1.0" in content
        assert "author: Test Author" in content
        assert "status: draft" in content
        assert "[tech] Uses YAML frontmatter" in content
        assert "[[Other Note]]" in content


@pytest.mark.asyncio
async def test_read_content_missing_file(mcp_server, app):
    """Test reading a file that doesn't exist."""

    async with Client(mcp_server) as client:
        # Reading a missing file now returns a helpful "Note Not Found" message
        # (the old read_content tool raised a ToolError for missing files).
        read_result = await read_content(client, "nonexistent/file.md")

        assert len(read_result.content) == 1
        assert read_result.content[0].type == "text"
        parsed = json.loads(read_result.content[0].text)
        content = parsed["result"]["content"]

        # Should get an appropriate not-found message
        assert "Note Not Found" in content
        assert "nonexistent/file.md" in content


@pytest.mark.asyncio
async def test_read_content_empty_file(mcp_server, app):
    """Test reading a file with minimal content.

    NOTE: The new adn_notes write surface rejects truly empty ``content``
    (MISSING_PARAMS error), so the closest equivalent is a title-only note.
    The original intent - frontmatter (title/permalink) is always present in
    the read output - is preserved.
    """

    async with Client(mcp_server) as client:
        # Create a note with minimal content
        await client.call_tool(
            "adn_notes",
            {
                "op": {
                    "operation": "write",
                    "title": "Empty Test",
                    "folder": "test",
                    "content": "# Empty Test",  # Minimal content (empty content is rejected by the new surface)
                }
            },
        )

        # Read the content back
        content = await get_content_text(client, "test/Empty_Test.md")

        # Should still have frontmatter with title and permalink
        assert "title: Empty Test" in content
        assert "permalink: test/empty-test" in content


@pytest.mark.asyncio
async def test_read_content_large_file(mcp_server, app):
    """Test reading a file with substantial content."""

    async with Client(mcp_server) as client:
        # Create a note with substantial content
        large_content = "# Large Content Test\n\n"

        # Add multiple sections with substantial text
        for i in range(10):
            large_content += f"""
## Section {i + 1}

This is section {i + 1} with substantial content. Lorem ipsum dolor sit amet,
consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et
dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation.

- [note] This is observation {i + 1}
- related_to [[Section {i}]]

Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore
eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident.

"""

        await client.call_tool(
            "adn_notes",
            {
                "op": {
                    "operation": "write",
                    "title": "Large Content Note",
                    "folder": "test",
                    "content": large_content,
                    "tags": "large,content,test",
                }
            },
        )

        # Read the content back
        content = await get_content_text(client, "test/Large_Content_Note.md")

        # Should contain all sections
        assert "Section 1" in content
        assert "Section 10" in content
        assert "Lorem ipsum" in content
        assert len(content) > 1000  # Should be substantial


@pytest.mark.asyncio
async def test_read_content_special_characters_in_filename(mcp_server, app):
    """Test reading files with special characters in the filename."""

    async with Client(mcp_server) as client:
        # Create notes with special characters in titles
        test_cases = [
            ("File with spaces", "test"),
            ("File-with-dashes", "test"),
            ("File_with_underscores", "test"),
            ("File (with parentheses)", "test"),
            ("File & Symbols!", "test"),
        ]

        for title, folder in test_cases:
            await client.call_tool(
                "adn_notes",
                {
                    "op": {
                        "operation": "write",
                        "title": title,
                        "folder": folder,
                        "content": f"# {title}\n\nContent for {title}",
                    }
                },
            )

            # Read the content back using the exact filename
            content = await get_content_text(client, f"{folder}/{title}.md")

            assert f"# {title}" in content
            assert f"Content for {title}" in content
