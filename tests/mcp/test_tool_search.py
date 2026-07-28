"""Tests for search MCP tools."""

from datetime import datetime, timedelta
from unittest.mock import patch

import pytest

from advanced_memory.mcp.tools.content_manager import adn_content
from advanced_memory.mcp.tools.search import _format_search_error_response, search_notes
from advanced_memory.schemas.search import SearchResponse
from tests.mcp.tool_invoker import mcp_fn


def _assert_search_md(md: str, *substrings: str) -> None:
    """search_notes returns rendered markdown on success."""
    assert isinstance(md, str), type(md)
    assert "# Search Failed" not in md[:1200], md[:1200]
    for s in substrings:
        assert s in md, (s, md[:2000])


async def create_note(
    title: str,
    folder: str,
    content: str,
    tags: list[str] | None = None,
) -> str:
    """Helper to create notes via the adn_content portmanteau tool."""
    return await mcp_fn(adn_content)(
        operation="write",
        identifier=title,
        folder=folder,
        content=content,
        tags=tags,
    )


@pytest.mark.asyncio
async def test_search_text(client):
    """Test basic search functionality."""
    # Create a test note
    result = await create_note(
        title="Test Search Note",
        folder="test",
        content="# Test\nThis is a searchable test note",
        tags=["test", "search"],
    )
    assert result

    # Search for it
    response = await mcp_fn(search_notes)(query="searchable")
    _assert_search_md(response, "test/test-search-note", "Test Search Note")


@pytest.mark.asyncio
async def test_search_tag_filter_inline(client):
    """Search notes using inline tag: syntax."""
    # Create notes with and without the target tag
    await create_note(
        title="Important Inline Tag Note",
        folder="search-tags",
        content="# Tag Inline\nThis note should match inline tag filters.",
        tags=["important", "search"],
    )
    await create_note(
        title="Non Matching Tag Note",
        folder="search-tags",
        content="# Tag Inline\nThis note should not match inline tag filters.",
        tags=["optional"],
    )

    response = await mcp_fn(search_notes)(query="tag:important")
    _assert_search_md(response, "important-inline-tag-note")
    assert "non-matching-tag-note" not in response


@pytest.mark.asyncio
async def test_search_tag_filter_with_text(client):
    """Search notes using inline tag filter combined with text criteria."""
    await create_note(
        title="Important Status Update",
        folder="search-tags",
        content="# Weekly Status\nStatus update and planning notes.",
        tags=["important", "meeting"],
    )
    await create_note(
        title="Important Without Keyword",
        folder="search-tags",
        content="# Random\nThis note lacks the keyword.",
        tags=["important", "random"],
    )

    response = await mcp_fn(search_notes)(query="tag:important status")
    _assert_search_md(response, "important-status-update")
    assert "important-without-keyword" not in response


@pytest.mark.asyncio
async def test_search_tag_parameter_filter(client):
    """Search notes using the tags parameter."""
    await create_note(
        title="Priority Review Note",
        folder="search-tags",
        content="# Review\nThis note requires review.",
        tags=["priority", "important"],
    )

    response = await mcp_fn(search_notes)(query="review", tags=["priority"])
    _assert_search_md(response, "priority-review-note")


@pytest.mark.asyncio
async def test_search_title(client):
    """Test basic search functionality."""
    # Create a test note
    result = await create_note(
        title="Test Search Note",
        folder="test",
        content="# Test\nThis is a searchable test note",
        tags=["test", "search"],
    )
    assert result

    # Search for it
    response = await mcp_fn(search_notes)(query="Search Note", search_type="title")
    _assert_search_md(response, "test/test-search-note", "Test Search Note")


@pytest.mark.asyncio
async def test_search_permalink(client):
    """Test basic search functionality."""
    # Create a test note
    result = await create_note(
        title="Test Search Note",
        folder="test",
        content="# Test\nThis is a searchable test note",
        tags=["test", "search"],
    )
    assert result

    # Search for it
    response = await mcp_fn(search_notes)(query="test/test-search-note", search_type="permalink")
    _assert_search_md(response, "test/test-search-note")


@pytest.mark.asyncio
async def test_search_permalink_match(client):
    """Test basic search functionality."""
    # Create a test note
    result = await create_note(
        title="Test Search Note",
        folder="test",
        content="# Test\nThis is a searchable test note",
        tags=["test", "search"],
    )
    assert result

    # Search for it
    response = await mcp_fn(search_notes)(query="test/test-search-*", search_type="permalink")
    _assert_search_md(response, "test/test-search-note")


@pytest.mark.asyncio
async def test_search_pagination(client):
    """Test basic search functionality."""
    # Create a test note
    result = await create_note(
        title="Test Search Note",
        folder="test",
        content="# Test\nThis is a searchable test note",
        tags=["test", "search"],
    )
    assert result

    # Search for it
    response = await mcp_fn(search_notes)(query="searchable", page=1, results_per_page=1)
    _assert_search_md(response, "test/test-search-note")


@pytest.mark.asyncio
async def test_search_with_type_filter(client):
    """Test search with entity type filter."""
    # Create test content
    await create_note(
        title="Entity Type Test",
        folder="test",
        content="# Test\nFiltered by type",
    )

    # Search with type filter
    response = await mcp_fn(search_notes)(query="type", types=["note"])
    _assert_search_md(response, "**Type:** entity")


@pytest.mark.asyncio
async def test_search_with_entity_type_filter(client):
    """Test search with entity type filter."""
    # Create test content
    await create_note(
        title="Entity Type Test",
        folder="test",
        content="# Test\nFiltered by type",
    )

    # Search with entity type filter
    response = await mcp_fn(search_notes)(query="type", entity_types=["entity"])
    _assert_search_md(response, "**Type:** entity")


@pytest.mark.asyncio
async def test_search_with_date_filter(client):
    """Test search with date filter."""
    # Create test content
    await create_note(
        title="Recent Note",
        folder="test",
        content="# Test\nRecent content",
    )

    # Search with date filter
    one_hour_ago = datetime.now() - timedelta(hours=1)
    response = await mcp_fn(search_notes)(query="recent", after_date=one_hour_ago.isoformat())
    _assert_search_md(response, "Recent Note")


class TestSearchErrorFormatting:
    """Test search error formatting for better user experience."""

    def test_format_search_error_fts5_syntax(self):
        """Test formatting for FTS5 syntax errors."""
        result = _format_search_error_response("syntax error in FTS5", "test query(")

        assert "# Search Failed - Invalid Syntax" in result
        assert "The search query 'test query(' contains invalid syntax" in result
        assert "Special characters" in result
        assert "test query" in result  # Clean query without special chars

    def test_format_search_error_no_results(self):
        """Test formatting for no results found."""
        result = _format_search_error_response("no results found", "very specific query")

        assert "# Search Complete - No Results Found" in result
        assert "No content found matching 'very specific query'" in result
        assert "Broaden your search" in result
        assert "very" in result  # Simplified query

    def test_format_search_error_server_error(self):
        """Test formatting for server errors."""
        result = _format_search_error_response("internal server error", "test query")

        assert "# Search Failed - Server Error" in result
        assert "The search service encountered an error while processing 'test query'" in result
        assert "Try again" in result
        assert "Check project status" in result

    def test_format_search_error_permission_denied(self):
        """Test formatting for permission errors."""
        result = _format_search_error_response("permission denied", "test query")

        assert "# Search Failed - Access Error" in result
        assert "You don't have permission to search" in result
        assert "Check your project access" in result

    def test_format_search_error_project_not_found(self):
        """Test formatting for project not found errors."""
        result = _format_search_error_response("current project not found", "test query")

        assert "# Search Failed - Project Not Found" in result
        assert "The current project is not accessible" in result
        assert "Check available projects" in result

    def test_format_search_error_generic(self):
        """Test formatting for generic errors."""
        result = _format_search_error_response("unknown error", "test query")

        assert "# Search Failed" in result
        assert "Error searching for 'test query': unknown error" in result
        assert "## Troubleshooting steps:" in result


@pytest.mark.asyncio
async def test_search_e2e_write_search_delete(client):
    """End-to-end write → search → delete flow with butterfly tags."""
    title = "Butterfly Lifecycle Notes"
    folder = "z-tests/butterflies"
    content = "\n".join(
        [
            "# Butterfly Lifecycle",
            "",
            "Butterflies undergo complete metamorphosis.",
            "",
            "## Stages",
            "- Egg",
            "- Larva",
            "- Pupa",
            "- Adult butterfly",
        ]
    )
    tags = ["insect", "butterfly"]

    # Write note and verify creation
    create_result = await mcp_fn(adn_content)(
        operation="write",
        identifier=title,
        folder=folder,
        content=content,
        tags=tags,
    )
    if isinstance(create_result, dict):
        assert create_result.get("success") is True
    else:
        assert "Created note" in str(create_result)

    # Search by title
    title_response = await mcp_fn(search_notes)(query="Butterfly Lifecycle Notes", search_type="title")
    _assert_search_md(title_response, "butterfly-lifecycle-notes")

    content_response = await mcp_fn(search_notes)(query="metamorphosis")
    _assert_search_md(content_response, "Butterfly Lifecycle")

    tag_response = await mcp_fn(search_notes)(query="tag:butterfly")
    _assert_search_md(tag_response, "Butterfly Lifecycle")

    # Delete the note
    delete_result = await mcp_fn(adn_content)(operation="delete", identifier=title)
    delete_ok = delete_result is True or (isinstance(delete_result, dict) and delete_result.get("success") is True)
    if not delete_ok and isinstance(delete_result, str):
        delete_ok = "delete" in delete_result.lower()
    assert delete_ok, delete_result

    # Confirm no results
    post_delete_response = await mcp_fn(search_notes)(query="Butterfly Lifecycle Notes", search_type="title")
    assert isinstance(post_delete_response, str)
    assert "butterfly-lifecycle-notes" not in post_delete_response


@pytest.mark.asyncio
async def test_search_all_projects(client):
    """Test search across all projects."""
    # Create test notes in current project
    await create_note(
        title="Multi-Project Test Note",
        folder="test",
        content="# Test\nThis should be found across projects",
        tags=["test", "multi-project"],
    )

    # Mock the projects list and search responses
    from unittest.mock import MagicMock

    from advanced_memory.schemas.project_info import ProjectItem, ProjectList
    from advanced_memory.schemas.search import SearchItemType, SearchResult

    mock_projects = ProjectList(
        projects=[
            ProjectItem(name="project1", path="/tmp/p1", is_default=False),
            ProjectItem(name="project2", path="/tmp/p2", is_default=False),
        ],
        current_project="project1",
        default_project="project1",
    )

    with patch("advanced_memory.mcp.tools.search.call_post") as mock_call_post:
        # First call returns project list
        # Subsequent calls return search results for each project
        mock_call_post.side_effect = [
            MagicMock(json=lambda: mock_projects.model_dump()),  # Project list
            MagicMock(
                json=lambda: SearchResponse(
                    results=[
                        SearchResult(
                            title="Result from project1",
                            type=SearchItemType.ENTITY,
                            score=1.0,
                            permalink="test/note1",
                            file_path="test/note1.md",
                        )
                    ],
                    current_page=1,
                    page_size=10,
                    total_results=1,
                ).model_dump()
            ),  # Project1 search
            MagicMock(
                json=lambda: SearchResponse(
                    results=[
                        SearchResult(
                            title="Result from project2",
                            type=SearchItemType.ENTITY,
                            score=1.0,
                            permalink="test/note2",
                            file_path="test/note2.md",
                        )
                    ],
                    current_page=1,
                    page_size=10,
                    total_results=1,
                ).model_dump()
            ),  # Project2 search
        ]

        with patch("advanced_memory.mcp.tools.search.get_active_project") as mock_get_project:
            mock_project = MagicMock()
            mock_project.project_url = "http://test"
            mock_get_project.return_value = mock_project

            response = await mcp_fn(search_notes)(query="multi-project", search_all_projects=True)

            assert isinstance(response, str)
            assert "[project1]" in response
            assert "[project2]" in response


@pytest.mark.asyncio
async def test_search_all_projects_conflict_with_project_param(client):
    """Test that search_all_projects conflicts with project parameter."""
    result = await mcp_fn(search_notes)(
        query="test",
        project="specific-project",
        search_all_projects=True,
    )

    # Should return error message
    assert isinstance(result, str)
    assert "Error" in result
    assert "Cannot use both" in result


@pytest.mark.asyncio
async def test_search_all_projects_handles_project_errors(client):
    """Test that search_all_projects gracefully handles errors in individual projects."""
    from unittest.mock import MagicMock

    from advanced_memory.schemas.project_info import ProjectItem, ProjectList
    from advanced_memory.schemas.search import SearchItemType, SearchResult

    mock_projects = ProjectList(
        projects=[
            ProjectItem(name="working-project", path="/tmp/p1", is_default=False),
            ProjectItem(name="failing-project", path="/tmp/p2", is_default=False),
        ],
        current_project="working-project",
        default_project="working-project",
    )

    with patch("advanced_memory.mcp.tools.search.call_post") as mock_call_post:
        # First call returns project list
        # Second call succeeds (working project)
        # Third call fails (failing project)
        mock_call_post.side_effect = [
            MagicMock(json=lambda: mock_projects.model_dump()),
            MagicMock(
                json=lambda: SearchResponse(
                    results=[
                        SearchResult(
                            title="Working result",
                            type=SearchItemType.ENTITY,
                            score=1.0,
                            permalink="test/note1",
                            file_path="test/note1.md",
                        )
                    ],
                    current_page=1,
                    page_size=10,
                    total_results=1,
                ).model_dump()
            ),
            Exception("Project access denied"),  # Failing project
        ]

        with patch("advanced_memory.mcp.tools.search.get_active_project") as mock_get_project:
            mock_project = MagicMock()
            mock_project.project_url = "http://test"
            mock_get_project.return_value = mock_project

            response = await mcp_fn(search_notes)(query="test", search_all_projects=True)

            assert isinstance(response, str)
            assert "Working result" in response


class TestSearchToolErrorHandling:
    """Test search tool exception handling."""

    @pytest.mark.asyncio
    async def test_search_notes_exception_handling(self):
        """Test exception handling in search_notes."""
        with patch("advanced_memory.mcp.tools.search.get_active_project") as mock_get_project:
            mock_get_project.return_value.project_url = "http://test"

            with patch("advanced_memory.mcp.tools.search.call_post", side_effect=Exception("syntax error")):
                result = await mcp_fn(search_notes)("test query")

                assert isinstance(result, str)
                assert "# Search Failed - Invalid Syntax" in result

    @pytest.mark.asyncio
    async def test_search_notes_permission_error(self):
        """Test search_notes with permission error."""
        with patch("advanced_memory.mcp.tools.search.get_active_project") as mock_get_project:
            mock_get_project.return_value.project_url = "http://test"

            with patch(
                "advanced_memory.mcp.tools.search.call_post",
                side_effect=Exception("permission denied"),
            ):
                result = await mcp_fn(search_notes)("test query")

                assert isinstance(result, str)
                assert "# Search Failed - Access Error" in result
