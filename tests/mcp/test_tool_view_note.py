"""Tests for view_note tool that exercise the full stack with SQLite."""

from textwrap import dedent
from unittest.mock import MagicMock, patch

import pytest
import pytest_asyncio

from tests.mcp.tool_invoker import mcp_fn

from advanced_memory.mcp.tools.view_note import view_note
from advanced_memory.mcp.tools.write_note import write_note
from advanced_memory.schemas.search import SearchItemType, SearchResponse, SearchResult


@pytest_asyncio.fixture
async def mock_call_get():
    """Mock for call_get to simulate different responses."""
    with patch("advanced_memory.mcp.tools.read_note.call_get") as mock:
        # Default to 404 - not found
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock.return_value = mock_response
        yield mock


def _mock_json_response(model: SearchResponse) -> MagicMock:
    m = MagicMock(status_code=200)
    m.json.return_value = model.model_dump()
    return m


@pytest.mark.asyncio
async def test_view_note_basic_functionality(app):
    """Test viewing a note creates an artifact."""
    # First create a note
    await mcp_fn(write_note)(
        title="Test View Note",
        folder="test",
        content="# Test View Note\n\nThis is test content for viewing.",
    )

    # View the note
    result = await mcp_fn(view_note)("Test View Note")

    # Should contain artifact XML
    assert '<artifact identifier="note-' in result
    assert 'type="text/markdown"' in result
    assert 'title="Test View Note"' in result
    assert "</artifact>" in result

    # Should contain the note content within the artifact
    assert "# Test View Note" in result
    assert "This is test content for viewing." in result

    # Should have confirmation message
    assert "[UNICODE] Note displayed as artifact" in result


@pytest.mark.asyncio
async def test_view_note_with_frontmatter_title(app):
    """Test viewing a note extracts title from frontmatter."""
    # Create note with frontmatter
    content = dedent("""
        ---
        title: "Frontmatter Title"
        tags: [test]
        ---

        # Frontmatter Title

        Content with frontmatter title.
    """).strip()

    await mcp_fn(write_note)(title="Frontmatter Title", folder="test", content=content)

    # View the note
    result = await mcp_fn(view_note)("Frontmatter Title")

    # Should extract title from frontmatter
    assert 'title="Frontmatter Title"' in result
    assert "[UNICODE] Note displayed as artifact: **Frontmatter Title**" in result


@pytest.mark.asyncio
async def test_view_note_with_heading_title(app):
    """Test viewing a note extracts title from first heading when no frontmatter."""
    # Create note with heading but no frontmatter title
    content = "# Heading Title\n\nContent with heading title."

    await mcp_fn(write_note)(title="Heading Title", folder="test", content=content)

    # View the note
    result = await mcp_fn(view_note)("Heading Title")

    # Should extract title from heading
    assert 'title="Heading Title"' in result
    assert "[UNICODE] Note displayed as artifact: **Heading Title**" in result


@pytest.mark.asyncio
async def test_view_note_unicode_content(app):
    """Test viewing a note with Unicode content."""
    content = "# Unicode Test 🚀\n\nThis note has emoji 🎉 and unicode ♠♣♥♦"

    await mcp_fn(write_note)(title="Unicode Test 🚀", folder="test", content=content)

    # View the note
    result = await mcp_fn(view_note)("Unicode Test 🚀")

    # Should handle Unicode properly
    assert "🚀" in result
    assert "🎉" in result
    assert "♠♣♥♦" in result
    assert '<artifact identifier="note-' in result


@pytest.mark.asyncio
async def test_view_note_by_permalink(app):
    """Test viewing a note by its permalink."""
    await mcp_fn(write_note)(title="Permalink Test", folder="test", content="Content for permalink test.")

    # View by permalink
    result = await mcp_fn(view_note)("test/permalink-test")

    # Should work with permalink
    assert '<artifact identifier="note-' in result
    assert "Content for permalink test." in result
    assert "[UNICODE] Note displayed as artifact" in result


@pytest.mark.asyncio
async def test_view_note_with_memory_url(app):
    """Test viewing a note using a memory:// URL."""
    await mcp_fn(write_note)(
        title="Memory URL Test",
        folder="test",
        content="Testing memory:// URL handling in view_note",
    )

    # View with memory:// URL
    result = await mcp_fn(view_note)("memory://test/memory-url-test")

    # Should work with memory:// URL
    assert '<artifact identifier="note-' in result
    assert "Testing memory:// URL handling in view_note" in result
    assert "[UNICODE] Note displayed as artifact" in result


@pytest.mark.asyncio
async def test_view_note_not_found(app):
    """Test viewing a non-existent note returns error without artifact."""
    # Try to view non-existent note
    result = await mcp_fn(view_note)("NonExistent Note")

    # Should return error message without artifact
    assert "# Note Not Found:" in result
    assert "NonExistent Note" in result
    assert "<artifact" not in result  # No artifact for errors
    assert "Check Identifier Type" in result
    assert "Search Instead" in result


@pytest.mark.asyncio
async def test_view_note_pagination(app):
    """Test viewing a note with pagination parameters."""
    await mcp_fn(write_note)(title="Pagination Test", folder="test", content="Content for pagination test.")

    # View with pagination
    result = await mcp_fn(view_note)("Pagination Test", page=1, page_size=5)

    # Should work with pagination
    assert '<artifact identifier="note-' in result
    assert "Content for pagination test." in result
    assert "[UNICODE] Note displayed as artifact" in result


@pytest.mark.asyncio
async def test_view_note_project_parameter(app):
    """Test viewing a note with project parameter."""
    await mcp_fn(write_note)(title="Project Test", folder="test", content="Content for project test.")

    # View with explicit project (None uses current)
    result = await mcp_fn(view_note)("Project Test", project=None)

    # Should work with project parameter
    assert '<artifact identifier="note-' in result
    assert "Content for project test." in result
    assert "[UNICODE] Note displayed as artifact" in result


@pytest.mark.asyncio
async def test_view_note_artifact_identifier_unique(app):
    """Test that different notes get different artifact identifiers."""
    # Create two notes
    await mcp_fn(write_note)(title="Note One", folder="test", content="Content one")
    await mcp_fn(write_note)(title="Note Two", folder="test", content="Content two")

    # View both notes
    result1 = await mcp_fn(view_note)("Note One")
    result2 = await mcp_fn(view_note)("Note Two")

    # Should have different artifact identifiers
    import re

    id1_match = re.search(r'identifier="(note-\d+)"', result1)
    id2_match = re.search(r'identifier="(note-\d+)"', result2)

    assert id1_match is not None
    assert id2_match is not None
    assert id1_match.group(1) != id2_match.group(1)


@pytest.mark.asyncio
async def test_view_note_fallback_identifier_as_title(app):
    """Test that view_note uses identifier as title when no title is extractable."""
    # Create a note with no clear title structure
    await mcp_fn(write_note)(
        title="Simple Note",
        folder="test",
        content="Just plain content with no headings or frontmatter title",
    )

    # View the note
    result = await mcp_fn(view_note)("Simple Note")

    # Should use identifier as fallback title
    assert 'title="Simple Note"' in result
    assert "[UNICODE] Note displayed as artifact: **Simple Note**" in result


@pytest.mark.asyncio
async def test_view_note_direct_success(mock_call_get):
    """Test view_note with successful direct permalink lookup."""
    # Setup mock for successful response with frontmatter
    note_content = dedent("""
        ---
        title: "Test Note"
        ---
        # Test Note

        This is a test note.
    """).strip()

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.text = note_content
    mock_call_get.return_value = mock_response

    # Call the function
    result = await mcp_fn(view_note)("test/test-note")

    # Verify direct lookup was used
    mock_call_get.assert_called_once()
    assert "test/test-note" in mock_call_get.call_args[0][1]

    # Verify result contains artifact
    assert '<artifact identifier="note-' in result
    assert 'title="Test Note"' in result
    assert "This is a test note." in result
    assert "[UNICODE] Note displayed as artifact: **Test Note**" in result


@pytest.mark.asyncio
async def test_view_note_title_search_fallback(mock_call_get):
    """Test view_note falls back to title search when direct lookup fails."""
    title_hits = SearchResponse(
        results=[
            SearchResult(
                title="Test Note",
                type=SearchItemType.ENTITY,
                score=1.0,
                entity="test/test-note",
                permalink="test/test-note",
                file_path="test/test-note.md",
            )
        ],
        current_page=1,
        page_size=1,
        total_results=1,
    )
    mock_call_get.side_effect = [
        MagicMock(status_code=404),
        MagicMock(status_code=404),
        _mock_json_response(title_hits),
        MagicMock(status_code=200, text="# Test Note\n\nThis is a test note."),
    ]

    result = await mcp_fn(view_note)("Test Note")

    assert mock_call_get.call_count == 4
    assert mock_call_get.call_args_list[2][1]["params"]["search_type"] == "title"

    assert '<artifact identifier="note-' in result
    assert 'title="Test Note"' in result
    assert "This is a test note." in result
    assert "[UNICODE] Note displayed as artifact: **Test Note**" in result
