"""Tests for search MCP tools."""

from datetime import datetime, timedelta
from unittest.mock import patch

import pytest

from advanced_memory.mcp.tools import write_note
from advanced_memory.mcp.tools.search import _format_search_error_response, search_notes
from advanced_memory.schemas.search import SearchResponse


@pytest.mark.asyncio
async def test_search_text(client):
    """Test basic search functionality."""
    # Create a test note
    result = await write_note.fn(
        title="Test Search Note",
        folder="test",
        content="# Test\nThis is a searchable test note",
        tags=["test", "search"],
    )
    assert result

    # Search for it
    response = await search_notes.fn(query="searchable")

    # Verify results - handle both success and error cases
    if isinstance(response, SearchResponse):
        # Success case - verify SearchResponse
        assert len(response.results) > 0
        assert any(r.permalink == "test/test-search-note" for r in response.results)
    else:
        # If search failed and returned error message, test should fail with informative message
        pytest.fail(f"Search failed with error: {response}")


@pytest.mark.asyncio
async def test_search_title(client):
    """Test basic search functionality."""
    # Create a test note
    result = await write_note.fn(
        title="Test Search Note",
        folder="test",
        content="# Test\nThis is a searchable test note",
        tags=["test", "search"],
    )
    assert result

    # Search for it
    response = await search_notes.fn(query="Search Note", search_type="title")

    # Verify results - handle both success and error cases
    if isinstance(response, str):
        # If search failed and returned error message, test should fail with informative message
        pytest.fail(f"Search failed with error: {response}")
    else:
        # Success case - verify SearchResponse
        assert len(response.results) > 0
        assert any(r.permalink == "test/test-search-note" for r in response.results)


@pytest.mark.asyncio
async def test_search_permalink(client):
    """Test basic search functionality."""
    # Create a test note
    result = await write_note.fn(
        title="Test Search Note",
        folder="test",
        content="# Test\nThis is a searchable test note",
        tags=["test", "search"],
    )
    assert result

    # Search for it
    response = await search_notes.fn(query="test/test-search-note", search_type="permalink")

    # Verify results - handle both success and error cases
    if isinstance(response, SearchResponse):
        # Success case - verify SearchResponse
        assert len(response.results) > 0
        assert any(r.permalink == "test/test-search-note" for r in response.results)
    else:
        # If search failed and returned error message, test should fail with informative message
        pytest.fail(f"Search failed with error: {response}")


@pytest.mark.asyncio
async def test_search_permalink_match(client):
    """Test basic search functionality."""
    # Create a test note
    result = await write_note.fn(
        title="Test Search Note",
        folder="test",
        content="# Test\nThis is a searchable test note",
        tags=["test", "search"],
    )
    assert result

    # Search for it
    response = await search_notes.fn(query="test/test-search-*", search_type="permalink")

    # Verify results - handle both success and error cases
    if isinstance(response, SearchResponse):
        # Success case - verify SearchResponse
        assert len(response.results) > 0
        assert any(r.permalink == "test/test-search-note" for r in response.results)
    else:
        # If search failed and returned error message, test should fail with informative message
        pytest.fail(f"Search failed with error: {response}")


@pytest.mark.asyncio
async def test_search_pagination(client):
    """Test basic search functionality."""
    # Create a test note
    result = await write_note.fn(
        title="Test Search Note",
        folder="test",
        content="# Test\nThis is a searchable test note",
        tags=["test", "search"],
    )
    assert result

    # Search for it
    response = await search_notes.fn(query="searchable", page=1, results_per_page=1)

    # Verify results - handle both success and error cases
    if isinstance(response, SearchResponse):
        # Success case - verify SearchResponse
        assert len(response.results) == 1
        assert any(r.permalink == "test/test-search-note" for r in response.results)
    else:
        # If search failed and returned error message, test should fail with informative message
        pytest.fail(f"Search failed with error: {response}")


@pytest.mark.asyncio
async def test_search_with_type_filter(client):
    """Test search with entity type filter."""
    # Create test content
    await write_note.fn(
        title="Entity Type Test",
        folder="test",
        content="# Test\nFiltered by type",
    )

    # Search with type filter
    response = await search_notes.fn(query="type", types=["note"])

    # Verify results - handle both success and error cases
    if isinstance(response, SearchResponse):
        # Success case - verify all results are entities
        assert all(r.type == "entity" for r in response.results)
    else:
        # If search failed and returned error message, test should fail with informative message
        pytest.fail(f"Search failed with error: {response}")


@pytest.mark.asyncio
async def test_search_with_entity_type_filter(client):
    """Test search with entity type filter."""
    # Create test content
    await write_note.fn(
        title="Entity Type Test",
        folder="test",
        content="# Test\nFiltered by type",
    )

    # Search with entity type filter
    response = await search_notes.fn(query="type", entity_types=["entity"])

    # Verify results - handle both success and error cases
    if isinstance(response, SearchResponse):
        # Success case - verify all results are entities
        assert all(r.type == "entity" for r in response.results)
    else:
        # If search failed and returned error message, test should fail with informative message
        pytest.fail(f"Search failed with error: {response}")


@pytest.mark.asyncio
async def test_search_with_date_filter(client):
    """Test search with date filter."""
    # Create test content
    await write_note.fn(
        title="Recent Note",
        folder="test",
        content="# Test\nRecent content",
    )

    # Search with date filter
    one_hour_ago = datetime.now() - timedelta(hours=1)
    response = await search_notes.fn(query="recent", after_date=one_hour_ago.isoformat())

    # Verify results - handle both success and error cases
    if isinstance(response, SearchResponse):
        # Success case - verify we get results within timeframe
        assert len(response.results) > 0
    else:
        # If search failed and returned error message, test should fail with informative message
        pytest.fail(f"Search failed with error: {response}")


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
async def test_search_all_projects(client):
    """Test search across all projects."""
    # Create test notes in current project
    await write_note.fn(
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
                ).model_dump()
            ),  # Project2 search
        ]

        with patch("advanced_memory.mcp.tools.search.get_active_project") as mock_get_project:
            mock_project = MagicMock()
            mock_project.project_url = "http://test"
            mock_get_project.return_value = mock_project

            response = await search_notes.fn(query="multi-project", search_all_projects=True)

            # Verify response
            assert isinstance(response, SearchResponse)
            assert len(response.results) == 2
            # Results should have project prefix
            assert any("[project1]" in str(r.title) for r in response.results)
            assert any("[project2]" in str(r.title) for r in response.results)


@pytest.mark.asyncio
async def test_search_all_projects_conflict_with_project_param(client):
    """Test that search_all_projects conflicts with project parameter."""
    result = await search_notes.fn(
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
                ).model_dump()
            ),
            Exception("Project access denied"),  # Failing project
        ]

        with patch("advanced_memory.mcp.tools.search.get_active_project") as mock_get_project:
            mock_project = MagicMock()
            mock_project.project_url = "http://test"
            mock_get_project.return_value = mock_project

            response = await search_notes.fn(query="test", search_all_projects=True)

            # Should still succeed with results from working project
            assert isinstance(response, SearchResponse)
            assert len(response.results) == 1


class TestSearchToolErrorHandling:
    """Test search tool exception handling."""

    @pytest.mark.asyncio
    async def test_search_notes_exception_handling(self):
        """Test exception handling in search_notes."""
        with patch("advanced_memory.mcp.tools.search.get_active_project") as mock_get_project:
            mock_get_project.return_value.project_url = "http://test"

            with patch(
                "advanced_memory.mcp.tools.search.call_post", side_effect=Exception("syntax error")
            ):
                result = await search_notes.fn("test query")

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
                result = await search_notes.fn("test query")

                assert isinstance(result, str)
                assert "# Search Failed - Access Error" in result
