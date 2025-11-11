"""Tests for search MCP tools."""

from datetime import datetime, timedelta
from unittest.mock import patch

import pytest

from advanced_memory.mcp.tools import adn_content
from advanced_memory.mcp.tools.search import _format_search_error_response, search_notes
from advanced_memory.schemas.search import SearchResponse


async def create_note(
    title: str,
    folder: str,
    content: str,
    tags: list[str] | None = None,
) -> str:
    """Helper to create notes via the adn_content portmanteau tool."""
    return await adn_content.fn(
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

    response = await search_notes.fn(query="tag:important")

    assert isinstance(response, SearchResponse)
    assert any(r.permalink == "search-tags/important-inline-tag-note" for r in response.results)
    assert not any(r.permalink == "search-tags/non-matching-tag-note" for r in response.results)


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

    response = await search_notes.fn(query="tag:important status")

    assert isinstance(response, SearchResponse)
    assert any(r.permalink == "search-tags/important-status-update" for r in response.results)
    assert not any(r.permalink == "search-tags/important-without-keyword" for r in response.results)


@pytest.mark.asyncio
async def test_search_tag_parameter_filter(client):
    """Search notes using the tags parameter."""
    await create_note(
        title="Priority Review Note",
        folder="search-tags",
        content="# Review\nThis note requires review.",
        tags=["priority", "important"],
    )

    response = await search_notes.fn(query="review", tags=["priority"])

    assert isinstance(response, SearchResponse)
    assert any(r.permalink == "search-tags/priority-review-note" for r in response.results)

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
    result = await create_note(
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
    result = await create_note(
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
    result = await create_note(
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
    await create_note(
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
    await create_note(
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
    await create_note(
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
    create_result = await adn_content.fn(
        operation="write",
        identifier=title,
        folder=folder,
        content=content,
        tags=tags,
    )
    assert "Created note" in create_result

    # Search by title
    title_response = await search_notes.fn(query="Butterfly Lifecycle Notes", search_type="title")
    assert isinstance(title_response, SearchResponse)
    assert any(r.permalink.endswith("butterfly-lifecycle-notes") for r in title_response.results)

    # Search by content keyword
    content_response = await search_notes.fn(query="metamorphosis")
    assert isinstance(content_response, SearchResponse)
    assert any("Butterfly Lifecycle" in r.title for r in content_response.results)

    # Search by tag
    tag_response = await search_notes.fn(query="tag:butterfly")
    assert isinstance(tag_response, SearchResponse)
    assert any("Butterfly Lifecycle" in r.title for r in tag_response.results)

    # Delete the note
    delete_result = await adn_content.fn(operation="delete", identifier=title)
    assert delete_result is True

    # Confirm no results
    post_delete_response = await search_notes.fn(query="Butterfly Lifecycle Notes", search_type="title")
    assert isinstance(post_delete_response, SearchResponse)
    assert not any(r.permalink.endswith("butterfly-lifecycle-notes") for r in post_delete_response.results)


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
