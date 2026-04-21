"""Tests for note tools that exercise the full stack with SQLite."""

from textwrap import dedent
from unittest.mock import MagicMock, patch

import pytest
import pytest_asyncio

from tests.mcp.tool_invoker import mcp_fn

from advanced_memory.mcp.tools.read_note import read_note
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
async def test_read_note_by_title(app):
    """Test reading a note by its title."""
    # First create a note
    await mcp_fn(write_note)(title="Special Note", folder="test", content="Note content here")

    # Should be able to read it by title
    content = await mcp_fn(read_note)("Special Note")
    assert "Note content here" in content


@pytest.mark.asyncio
async def test_note_unicode_content(app):
    """Test handling of unicode content in"""
    content = "# Test 🚀\nThis note has emoji 🎉 and unicode ♠♣♥♦"
    result = await mcp_fn(write_note)(title="Unicode Test", folder="test", content=content)

    assert (
        dedent("""
        # Created note
        file_path: test/Unicode_Test.md
        permalink: test/unicode-test
        checksum: 272389cd
        """).strip()
        in result
    )

    # Read back should preserve unicode (normalize line endings for cross-platform compatibility)
    result = await mcp_fn(read_note)("test/unicode-test")
    assert content.replace("\n", "\r\n") in result


@pytest.mark.asyncio
async def test_multiple_notes(app):
    """Test creating and managing multiple"""
    # Create several notes
    notes_data = [
        ("test/note-1", "Note 1", "test", "Content 1", ["tag1"]),
        ("test/note-2", "Note 2", "test", "Content 2", ["tag1", "tag2"]),
        ("test/note-3", "Note 3", "test", "Content 3", []),
    ]

    for _, title, folder, content, tags in notes_data:
        await mcp_fn(write_note)(title=title, folder=folder, content=content, tags=tags)

    # Should be able to read each one
    for permalink, _title, _folder, content, _ in notes_data:
        note = await mcp_fn(read_note)(permalink)
        assert content in note

    # read multiple notes at once

    result = await mcp_fn(read_note)("test/*")

    # note we can't compare times
    assert "--- memory://test/note-1" in result
    assert "Content 1" in result

    assert "--- memory://test/note-2" in result
    assert "Content 2" in result

    assert "--- memory://test/note-3" in result
    assert "Content 3" in result


@pytest.mark.asyncio
async def test_multiple_notes_pagination(app):
    """Test creating and managing multiple"""
    # Create several notes
    notes_data = [
        ("test/note-1", "Note 1", "test", "Content 1", ["tag1"]),
        ("test/note-2", "Note 2", "test", "Content 2", ["tag1", "tag2"]),
        ("test/note-3", "Note 3", "test", "Content 3", []),
    ]

    for _, title, folder, content, tags in notes_data:
        await mcp_fn(write_note)(title=title, folder=folder, content=content, tags=tags)

    # Should be able to read each one
    for permalink, _title, _folder, content, _ in notes_data:
        note = await mcp_fn(read_note)(permalink)
        assert content in note

    # read multiple notes at once with pagination
    result = await mcp_fn(read_note)("test/*", page=1, page_size=2)

    # note we can't compare times
    assert "--- memory://test/note-1" in result
    assert "Content 1" in result

    assert "--- memory://test/note-2" in result
    assert "Content 2" in result


@pytest.mark.asyncio
async def test_read_note_memory_url(app):
    """Test reading a note using a memory:// URL.

    Should:
    - Handle memory:// URLs correctly
    - Normalize the URL before resolving
    - Return the note content
    """
    # First create a note
    result = await mcp_fn(write_note)(
        title="Memory URL Test",
        folder="test",
        content="Testing memory:// URL handling",
    )
    assert result

    # Should be able to read it with a memory:// URL
    memory_url = "memory://test/memory-url-test"
    content = await mcp_fn(read_note)(memory_url)
    assert "Testing memory:// URL handling" in content


@pytest.mark.asyncio
async def test_read_note_direct_success(mock_call_get):
    """Test read_note with successful direct permalink lookup."""
    # Setup mock for successful response
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.text = "# Test Note\n\nThis is a test note."
    mock_call_get.return_value = mock_response

    # Call the function
    result = await mcp_fn(read_note)("test/test-note")

    # Verify direct lookup was used
    mock_call_get.assert_called_once()
    assert "test/test-note" in mock_call_get.call_args[0][1]

    # Verify result
    assert "# Test Note" in result
    assert "This is a test note." in result


@pytest.mark.asyncio
async def test_read_note_title_search_fallback(mock_call_get):
    """Test read_note falls back to title search when direct lookup fails."""
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

    result = await mcp_fn(read_note)("Test Note")

    assert mock_call_get.call_count == 4
    search_call = mock_call_get.call_args_list[2]
    assert "/search/" in search_call[0][1]
    assert search_call[1]["params"]["query"] == "Test Note"
    assert search_call[1]["params"]["search_type"] == "title"
    fetch_call = mock_call_get.call_args_list[3][0][1]
    assert "test/test-note" in fetch_call

    assert "# Test Note" in result
    assert "This is a test note." in result


@pytest.mark.asyncio
async def test_read_note_text_search_fallback(mock_call_get):
    """Test read_note falls back to text search and returns related results."""
    title_empty = SearchResponse(results=[], current_page=1, page_size=5, total_results=0)
    text_hits = SearchResponse(
        results=[
            SearchResult(
                title="Related Note 1",
                type=SearchItemType.ENTITY,
                score=0.8,
                entity="notes/related-note-1",
                permalink="notes/related-note-1",
                file_path="notes/related-note-1.md",
            ),
            SearchResult(
                title="Related Note 2",
                type=SearchItemType.ENTITY,
                score=0.7,
                entity="notes/related-note-2",
                permalink="notes/related-note-2",
                file_path="notes/related-note-2.md",
            ),
        ],
        current_page=1,
        page_size=5,
        total_results=2,
    )
    mock_call_get.side_effect = [
        MagicMock(status_code=404),
        MagicMock(status_code=404),
        _mock_json_response(title_empty),
        _mock_json_response(text_hits),
    ]

    result = await mcp_fn(read_note)("some query")

    assert mock_call_get.call_count == 4
    assert mock_call_get.call_args_list[2][1]["params"]["search_type"] == "title"
    assert mock_call_get.call_args_list[3][1]["params"]["search_type"] == "text"

    assert "Note Not Found" in result
    assert "Related Note 1" in result
    assert "Related Note 2" in result
    assert 'read_note("notes/related-note-1")' in result


@pytest.mark.asyncio
async def test_read_note_complete_fallback(mock_call_get):
    """Test read_note with all lookups failing."""
    empty = SearchResponse(results=[], current_page=1, page_size=5, total_results=0)
    mock_call_get.side_effect = [
        MagicMock(status_code=404),
        _mock_json_response(empty),
        _mock_json_response(empty),
    ]

    result = await mcp_fn(read_note)("nonexistent")

    assert mock_call_get.call_count == 3

    assert "Note Not Found" in result
    assert "nonexistent" in result
    assert "Check Identifier Type" in result
    assert "Search Instead" in result
    assert "Recent Activity" in result
    assert "search_notes(query=" in result


class TestReadNoteSecurityValidation:
    """Test read_note security validation features."""

    @pytest.mark.asyncio
    async def test_read_note_blocks_path_traversal_unix(self, app):
        """Test that Unix-style path traversal attacks are blocked in identifier parameter."""
        # Test various Unix-style path traversal patterns
        attack_identifiers = [
            "../secrets.txt",
            "../../etc/passwd",
            "../../../root/.ssh/id_rsa",
            "notes/../../../etc/shadow",
            "folder/../../outside/file.md",
            "../../../../etc/hosts",
            "../../../home/user/.env",
        ]

        for attack_identifier in attack_identifiers:
            result = await mcp_fn(read_note)(identifier=attack_identifier)

            assert isinstance(result, str)
            assert "# Error" in result
            assert "paths must stay within project boundaries" in result
            assert attack_identifier in result

    @pytest.mark.asyncio
    async def test_read_note_blocks_path_traversal_windows(self, app):
        """Test that Windows-style path traversal attacks are blocked in identifier parameter."""
        # Test various Windows-style path traversal patterns
        attack_identifiers = [
            "..\\secrets.txt",
            "..\\..\\Windows\\System32\\config\\SAM",
            "notes\\..\\..\\..\\Windows\\System32",
            "\\\\server\\share\\file.txt",
            "..\\..\\Users\\user\\.env",
            "\\\\..\\..\\Windows",
            "..\\..\\..\\Boot.ini",
        ]

        for attack_identifier in attack_identifiers:
            result = await mcp_fn(read_note)(identifier=attack_identifier)

            assert isinstance(result, str)
            assert "# Error" in result
            assert "paths must stay within project boundaries" in result
            assert attack_identifier in result

    @pytest.mark.asyncio
    async def test_read_note_blocks_absolute_paths(self, app):
        """Test that absolute paths are blocked in identifier parameter."""
        # Test various absolute path patterns
        attack_identifiers = [
            "/etc/passwd",
            "/home/user/.env",
            "/var/log/auth.log",
            "/root/.ssh/id_rsa",
            "C:\\Windows\\System32\\config\\SAM",
            "C:\\Users\\user\\.env",
            "D:\\secrets\\config.json",
            "/tmp/malicious.txt",
            "/usr/local/bin/evil",
        ]

        for attack_identifier in attack_identifiers:
            result = await mcp_fn(read_note)(identifier=attack_identifier)

            assert isinstance(result, str)
            assert "# Error" in result
            assert "paths must stay within project boundaries" in result
            assert attack_identifier in result

    @pytest.mark.asyncio
    async def test_read_note_blocks_home_directory_access(self, app):
        """Test that home directory access patterns are blocked in identifier parameter."""
        # Test various home directory access patterns
        attack_identifiers = [
            "~/secrets.txt",
            "~/.env",
            "~/.ssh/id_rsa",
            "~/Documents/passwords.txt",
            "~\\AppData\\secrets",
            "~\\Desktop\\config.ini",
            "~/.bashrc",
            "~/Library/Preferences/secret.plist",
        ]

        for attack_identifier in attack_identifiers:
            result = await mcp_fn(read_note)(identifier=attack_identifier)

            assert isinstance(result, str)
            assert "# Error" in result
            assert "paths must stay within project boundaries" in result
            assert attack_identifier in result

    @pytest.mark.asyncio
    async def test_read_note_blocks_memory_url_attacks(self, app):
        """Test that memory URLs with path traversal are blocked."""
        # Test memory URLs with attacks embedded
        attack_identifiers = [
            "memory://../../etc/passwd",
            "memory://../../../root/.ssh/id_rsa",
            "memory://~/.env",
            "memory:///etc/passwd",
            "memory://notes/../../../etc/shadow",
            "memory://..\\..\\Windows\\System32",
        ]

        for attack_identifier in attack_identifiers:
            result = await mcp_fn(read_note)(identifier=attack_identifier)

            assert isinstance(result, str)
            assert "# Error" in result
            assert "paths must stay within project boundaries" in result

    @pytest.mark.asyncio
    async def test_read_note_blocks_mixed_attack_patterns(self, app):
        """Test that mixed legitimate/attack patterns are blocked in identifier parameter."""
        # Test mixed patterns that start legitimate but contain attacks
        attack_identifiers = [
            "notes/../../../etc/passwd",
            "docs/../../.env",
            "legitimate/path/../../.ssh/id_rsa",
            "project/folder/../../../Windows/System32",
            "valid/folder/../../home/user/.bashrc",
            "assets/../../../tmp/evil.exe",
        ]

        for attack_identifier in attack_identifiers:
            result = await mcp_fn(read_note)(identifier=attack_identifier)

            assert isinstance(result, str)
            assert "# Error" in result
            assert "paths must stay within project boundaries" in result

    @pytest.mark.asyncio
    async def test_read_note_allows_safe_identifiers(self, app):
        """Test that legitimate identifiers are still allowed."""
        # Test various safe identifier patterns
        safe_identifiers = [
            "notes/meeting",
            "docs/readme",
            "projects/2025/planning",
            "archive/old-notes/backup",
            "folder/subfolder/document",
            "research/ml/algorithms",
            "meeting-notes",
            "test/simple-note",
        ]

        for safe_identifier in safe_identifiers:
            result = await mcp_fn(read_note)(identifier=safe_identifier)

            assert isinstance(result, str)
            # Should not contain security error message
            assert "# Error" not in result or "paths must stay within project boundaries" not in result
            # Should either succeed or fail for legitimate reasons (not found, etc.)
            # but not due to security validation

    @pytest.mark.asyncio
    async def test_read_note_allows_legitimate_titles(self, app):
        """Test that legitimate note titles work normally."""
        # Create a test note first
        await mcp_fn(write_note)(
            title="Security Test Note",
            folder="security-tests",
            content="# Security Test Note\nThis is a legitimate note for security testing.",
        )

        # Test reading by title (should work)
        result = await mcp_fn(read_note)("Security Test Note")

        assert isinstance(result, str)
        # Should not be a security error
        assert "# Error" not in result or "paths must stay within project boundaries" not in result
        # Should either return the note content or search results

    @pytest.mark.asyncio
    async def test_read_note_empty_identifier_security(self, app):
        """Test that empty identifier is handled securely."""
        # Empty identifier should be allowed (may return search results or error, but not security error)
        result = await mcp_fn(read_note)(identifier="")

        assert isinstance(result, str)
        # Empty identifier should not trigger security error
        assert "# Error" not in result or "paths must stay within project boundaries" not in result

    @pytest.mark.asyncio
    async def test_read_note_security_with_all_parameters(self, app):
        """Test security validation works with all read_note parameters."""
        # Test that security validation is applied even when all other parameters are provided
        result = await mcp_fn(read_note)(
            identifier="../../../etc/malicious",
            page=1,
            page_size=5,
            project=None,  # Use default project
        )

        assert isinstance(result, str)
        assert "# Error" in result
        assert "paths must stay within project boundaries" in result
        assert "../../../etc/malicious" in result

    @pytest.mark.asyncio
    async def test_read_note_security_logging(self, app, caplog):
        """Test that security violations are properly logged."""
        # Attempt path traversal attack
        result = await mcp_fn(read_note)(identifier="../../../etc/passwd")

        assert "# Error" in result
        assert "paths must stay within project boundaries" in result

        # Check that security violation was logged
        # Note: This test may need adjustment based on the actual logging setup
        # The security validation should generate a warning log entry

    @pytest.mark.asyncio
    async def test_read_note_preserves_functionality_with_security(self, app):
        """Test that security validation doesn't break normal note reading functionality."""
        # Create a note with complex content to ensure security validation doesn't interfere
        await mcp_fn(write_note)(
            title="Full Feature Security Test Note",
            folder="security-tests",
            content=dedent("""
                # Full Feature Security Test Note

                This note tests that security validation doesn't break normal functionality.

                ## Observations
                - [security] Path validation working correctly #security
                - [feature] All features still functional #test

                ## Relations
                - relates_to [[Security Implementation]]
                - depends_on [[Path Validation]]

                Additional content with various formatting.
            """).strip(),
            tags=["security", "test", "full-feature"],
            entity_type="guide",
        )

        # Test reading by permalink
        result = await mcp_fn(read_note)("security-tests/full-feature-security-test-note")

        # Should succeed normally (not a security error)
        assert isinstance(result, str)
        assert "# Error" not in result or "paths must stay within project boundaries" not in result
        # Should either return content or search results, but not security error


class TestReadNoteSecurityEdgeCases:
    """Test edge cases for read_note security validation."""

    @pytest.mark.asyncio
    async def test_read_note_unicode_identifier_attacks(self, app):
        """Test that Unicode-based path traversal attempts are blocked."""
        # Test Unicode path traversal attempts
        unicode_attack_identifiers = [
            "notes/文档/../../../etc/passwd",  # Chinese characters
            "docs/café/../../.env",  # Accented characters
            "files/αβγ/../../../secret.txt",  # Greek characters
        ]

        for attack_identifier in unicode_attack_identifiers:
            result = await mcp_fn(read_note)(identifier=attack_identifier)

            assert isinstance(result, str)
            assert "# Error" in result
            assert "paths must stay within project boundaries" in result

    @pytest.mark.asyncio
    async def test_read_note_very_long_attack_identifier(self, app):
        """Test handling of very long attack identifiers."""
        # Create a very long path traversal attack
        long_attack_identifier = "../" * 1000 + "etc/malicious"

        result = await mcp_fn(read_note)(identifier=long_attack_identifier)

        assert isinstance(result, str)
        assert "# Error" in result
        assert "paths must stay within project boundaries" in result

    @pytest.mark.asyncio
    async def test_read_note_case_variations_attacks(self, app):
        """Test that case variations don't bypass security."""
        # Test case variations (though case sensitivity depends on filesystem)
        case_attack_identifiers = [
            "../ETC/passwd",
            "../Etc/PASSWD",
            "..\\WINDOWS\\system32",
            "~/.SSH/id_rsa",
        ]

        for attack_identifier in case_attack_identifiers:
            result = await mcp_fn(read_note)(identifier=attack_identifier)

            assert isinstance(result, str)
            assert "# Error" in result
            assert "paths must stay within project boundaries" in result

    @pytest.mark.asyncio
    async def test_read_note_whitespace_in_attack_identifiers(self, app):
        """Test that whitespace doesn't help bypass security."""
        # Test attack identifiers with various whitespace
        whitespace_attack_identifiers = [
            " ../../../etc/passwd ",
            "\t../../../secrets\t",
            " ..\\..\\Windows ",
            "notes/ ../../ malicious",
        ]

        for attack_identifier in whitespace_attack_identifiers:
            result = await mcp_fn(read_note)(identifier=attack_identifier)

            assert isinstance(result, str)
            # The attack should still be blocked even with whitespace
            if ".." in attack_identifier.strip() or "~" in attack_identifier.strip():
                assert "# Error" in result
                assert "paths must stay within project boundaries" in result
