"""
Integration tests for adn_search query operation (migrated from search_notes MCP tool).

Comprehensive tests covering search functionality using the complete
MCP client-server flow with real databases.
"""

import pytest
from fastmcp import Client


async def write_note(client: Client, title: str, folder: str, content: str, tags: str | None = None):
    """Helper: write a note through the adn_notes portmanteau."""
    op = {"operation": "write", "title": title, "folder": folder, "content": content}
    if tags is not None:
        op["tags"] = tags
    await client.call_tool("adn_notes", {"op": op})


async def search(client: Client, query: str, search_type: str = "text", page: int = 1, page_size: int = 10) -> str:
    """Helper: run a text search through the adn_search portmanteau."""
    result = await client.call_tool(
        "adn_search",
        {"op": {"operation": "query", "text": query, "search_type": search_type, "page": page, "page_size": page_size}},
    )
    assert len(result.content) == 1
    assert result.content[0].type == "text"
    return result.content[0].text


@pytest.mark.asyncio
async def test_search_basic_text_search(mcp_server, app):
    """Test basic text search functionality."""

    async with Client(mcp_server) as client:
        # Create test notes for searching
        await write_note(
            client,
            "Python Programming Guide",
            "docs",
            "# Python Programming Guide\n\nThis guide covers Python basics and advanced topics.",
            "python,programming",
        )

        await write_note(
            client,
            "Flask Web Development",
            "docs",
            "# Flask Web Development\n\nBuilding web applications with Python Flask framework.",
            "python,flask,web",
        )

        await write_note(
            client,
            "JavaScript Basics",
            "docs",
            "# JavaScript Basics\n\nIntroduction to JavaScript programming language.",
            "javascript,programming",
        )

        # Search for Python-related content
        result_text = await search(client, "Python")

        assert "Python Programming Guide" in result_text
        assert "Flask Web Development" in result_text
        assert "JavaScript Basics" not in result_text


@pytest.mark.asyncio
async def test_search_boolean_operators(mcp_server, app):
    """Test boolean search operators (AND, OR, NOT)."""

    async with Client(mcp_server) as client:
        # Create test notes
        await write_note(
            client,
            "Python Flask Tutorial",
            "tutorials",
            "# Python Flask Tutorial\n\nLearn Python web development with Flask.",
            "python,flask,tutorial",
        )

        await write_note(
            client,
            "Python Django Guide",
            "tutorials",
            "# Python Django Guide\n\nBuilding web apps with Python Django framework.",
            "python,django,web",
        )

        await write_note(
            client,
            "React JavaScript",
            "tutorials",
            "# React JavaScript\n\nBuilding frontend applications with React.",
            "javascript,react,frontend",
        )

        # Test AND operator
        result_text = await search(client, "Python AND Flask")
        assert "Python Flask Tutorial" in result_text
        assert "Python Django Guide" not in result_text
        assert "React JavaScript" not in result_text

        # Test OR operator
        result_text = await search(client, "Flask OR Django")
        assert "Python Flask Tutorial" in result_text
        assert "Python Django Guide" in result_text
        assert "React JavaScript" not in result_text

        # Test NOT operator
        result_text = await search(client, "Python NOT Django")
        assert "Python Flask Tutorial" in result_text
        assert "Python Django Guide" not in result_text


@pytest.mark.asyncio
async def test_search_title_only(mcp_server, app):
    """Test searching in titles only."""

    async with Client(mcp_server) as client:
        # Create test notes
        await write_note(
            client,
            "Database Design",
            "docs",
            "# Database Design\n\nThis covers SQL and database concepts.",
            "database,sql",
        )

        await write_note(
            client,
            "Web Development",
            "docs",
            "# Web Development\n\nDatabase integration in web applications.",
            "web,development",
        )

        # Search for "database" in titles only
        result_text = await search(client, "Database", search_type="title")

        assert "Database Design" in result_text
        assert "Web Development" not in result_text  # Has "database" in content but not title


@pytest.mark.asyncio
async def test_search_permalink_exact(mcp_server, app):
    """Test exact permalink search."""

    async with Client(mcp_server) as client:
        # Create test notes
        await write_note(
            client,
            "API Documentation",
            "api",
            "# API Documentation\n\nComplete API reference guide.",
            "api,docs",
        )

        await write_note(
            client,
            "API Testing",
            "testing",
            "# API Testing\n\nHow to test REST APIs.",
            "api,testing",
        )

        # Search for exact permalink
        result_text = await search(client, "api/api-documentation", search_type="permalink")

        assert "API Documentation" in result_text
        assert "API Testing" not in result_text


@pytest.mark.asyncio
async def test_search_permalink_pattern(mcp_server, app):
    """Test permalink pattern search with wildcards."""

    async with Client(mcp_server) as client:
        # Create test notes in different folders
        await write_note(
            client,
            "Meeting Notes January",
            "meetings",
            "# Meeting Notes January\n\nJanuary team meeting notes.",
            "meetings,january",
        )

        await write_note(
            client,
            "Meeting Notes February",
            "meetings",
            "# Meeting Notes February\n\nFebruary team meeting notes.",
            "meetings,february",
        )

        await write_note(
            client,
            "Project Notes",
            "projects",
            "# Project Notes\n\nGeneral project documentation.",
            "projects,notes",
        )

        # Search for all meeting notes using pattern
        result_text = await search(client, "meetings/*", search_type="permalink")

        assert "Meeting Notes January" in result_text
        assert "Meeting Notes February" in result_text
        assert "Project Notes" not in result_text


@pytest.mark.asyncio
async def test_search_entity_type_filter(mcp_server, app):
    """Test filtering search results by entity type."""

    async with Client(mcp_server) as client:
        # Create a note with observations and relations
        content_with_observations = """# Development Process

This describes our development workflow.

## Observations
- [process] We use Git for version control
- [tool] We use VS Code as our editor

## Relations
- uses [[Git]]
- part_of [[Development Workflow]]

Regular content about development practices."""

        await write_note(
            client,
            "Development Process",
            "processes",
            content_with_observations,
            "development,process",
        )

        # NOTE: The new adn_search surface (SearchQueryOp) exposes only
        # text/search_type/page/page_size. The old `entity_types` filter is not
        # part of the new wire schema, so this searches full text instead.
        # The main entity is still found for the query term.
        result_text = await search(client, "development")

        # Should find the main entity
        assert "Development Process" in result_text


@pytest.mark.asyncio
async def test_search_pagination(mcp_server, app):
    """Test search result pagination."""

    async with Client(mcp_server) as client:
        # Create multiple notes to test pagination
        for i in range(15):
            await write_note(
                client,
                f"Test Note {i + 1:02d}",
                "test",
                f"# Test Note {i + 1:02d}\n\nThis is test content for pagination testing.",
                "test,pagination",
            )

        # Search with pagination (page 1, page_size 5)
        result_text = await search(client, "test", page=1, page_size=5)

        # Should contain pagination info
        assert "**Page:** 1 of 3" in result_text

        # Search page 2
        result_text = await search(client, "test", page=2, page_size=5)

        assert "**Page:** 2 of 3" in result_text


@pytest.mark.asyncio
async def test_search_no_results(mcp_server, app):
    """Test search with no matching results."""

    async with Client(mcp_server) as client:
        # Create a test note
        await write_note(
            client,
            "Sample Note",
            "test",
            "# Sample Note\n\nThis is a sample note for testing.",
            "sample,test",
        )

        # Search for something that doesn't exist
        result_text = await search(client, "nonexistent")

        assert "No results found for your query." in result_text


@pytest.mark.asyncio
async def test_search_complex_boolean_query(mcp_server, app):
    """Test complex boolean queries with grouping."""

    async with Client(mcp_server) as client:
        # Create test notes
        await write_note(
            client,
            "Python Web Development",
            "tutorials",
            "# Python Web Development\n\nLearn Python for web development using Flask and Django.",
            "python,web,development",
        )

        await write_note(
            client,
            "Python Data Science",
            "tutorials",
            "# Python Data Science\n\nData analysis and machine learning with Python.",
            "python,data,science",
        )

        await write_note(
            client,
            "JavaScript Web Development",
            "tutorials",
            "# JavaScript Web Development\n\nBuilding web applications with JavaScript and React.",
            "javascript,web,development",
        )

        # Complex boolean query: (Python OR JavaScript) AND web
        result_text = await search(client, "(Python OR JavaScript) AND web")

        assert "Python Web Development" in result_text
        assert "JavaScript Web Development" in result_text
        assert "Python Data Science" not in result_text  # Has Python but not web


@pytest.mark.asyncio
async def test_search_case_insensitive(mcp_server, app):
    """Test that search is case insensitive."""

    async with Client(mcp_server) as client:
        # Create test note
        await write_note(
            client,
            "Machine Learning Guide",
            "guides",
            "# Machine Learning Guide\n\nIntroduction to MACHINE LEARNING concepts.",
            "ML,AI",
        )

        # Search with different cases
        search_cases = ["machine", "MACHINE", "Machine", "learning", "LEARNING"]

        for search_term in search_cases:
            result_text = await search(client, search_term)
            assert "Machine Learning Guide" in result_text, f"Failed for search term: {search_term}"
