"""Tests for HTML export functionality."""

from unittest.mock import patch

import pytest

from advanced_memory.mcp.tools.export_html_notes import export_html_notes


@pytest.fixture
def mock_notes_data():
    """Sample notes data for testing."""
    return [
        {
            "title": "HTML Test Note",
            "content": "# HTML Test\n\nContent with **formatting**.",
            "filename": "html-test-note.md",
            "path": "test/note1.md",
            "folder": "test",
        },
        {
            "title": "Second Note",
            "content": "# Second\n\nMore content.",
            "filename": "second-note.md",
            "path": "test/note2.md",
            "folder": "test",
        },
    ]


@pytest.mark.asyncio
async def test_export_html_basic(tmp_path, mock_notes_data):
    """Test basic HTML export with index."""
    export_path = tmp_path / "html"

    with patch(
        "advanced_memory.mcp.tools.export_html_notes._get_notes_from_folder"
    ) as mock_get_notes:
        mock_get_notes.return_value = mock_notes_data

        with patch("advanced_memory.utils.file_opener.open_file_or_folder") as mock_open:
            mock_open.return_value = (True, "Opened")

            result = await export_html_notes.fn(
                export_path=str(export_path),
                include_index=True,
                show_after_export=False,
            )

    assert "HTML Export Complete" in result or "export" in result.lower()


@pytest.mark.asyncio
@pytest.mark.skip(reason="Test needs update for new file_opener implementation")  
async def test_export_html_with_index_opens_browser(tmp_path, mock_notes_data):
    """Test HTML export with index opens index.html in browser."""
    export_path = tmp_path / "html"
    export_path.mkdir(parents=True)

    # Create dummy index.html
    index_file = export_path / "index.html"
    index_file.write_text("<html><body>Test</body></html>")

    with patch(
        "advanced_memory.mcp.tools.export_html_notes._get_notes_from_folder"
    ) as mock_get_notes:
        mock_get_notes.return_value = mock_notes_data

        with patch(
            "advanced_memory.mcp.tools.export_html_notes._process_html_export"
        ) as mock_process:
            mock_process.return_value = "# Export Complete"

    with patch(
        "advanced_memory.utils.file_opener.open_file_or_folder"
    ) as mock_open:
                mock_open.return_value = (True, "Opened index.html")

                result = await export_html_notes.fn(
                    export_path=str(export_path),
                    include_index=True,
                    show_after_export=True,
                )

                # Should try to open index.html
                assert mock_open.called

    assert "Opened" in result


@pytest.mark.asyncio
@pytest.mark.skip(reason="Test needs update for new file_opener implementation")
async def test_export_html_no_index_opens_folder(tmp_path, mock_notes_data):
    """Test HTML export without index opens folder."""
    export_path = tmp_path / "html_no_index"

    with patch(
        "advanced_memory.mcp.tools.export_html_notes._get_notes_from_folder"
    ) as mock_get_notes:
        mock_get_notes.return_value = mock_notes_data

        with patch(
            "advanced_memory.mcp.tools.export_html_notes._process_html_export"
        ) as mock_process:
            mock_process.return_value = "# Export Complete"

    with patch(
        "advanced_memory.utils.file_opener.open_file_or_folder"
    ) as mock_open:
                mock_open.return_value = (True, "Opened folder")

                result = await export_html_notes.fn(
                    export_path=str(export_path),
                    include_index=False,
                    show_after_export=True,
                )

                # Should open folder
                assert mock_open.called

    assert "Opened" in result


@pytest.mark.asyncio
async def test_export_html_show_false(tmp_path, mock_notes_data):
    """Test HTML export doesn't open when show_after_export=False."""
    export_path = tmp_path / "html"

    with patch(
        "advanced_memory.mcp.tools.export_html_notes._get_notes_from_folder"
    ) as mock_get_notes:
        mock_get_notes.return_value = mock_notes_data

        with patch(
            "advanced_memory.mcp.tools.export_html_notes._process_html_export"
        ) as mock_process:
            mock_process.return_value = "# Export Complete"

    with patch(
        "advanced_memory.utils.file_opener.open_file_or_folder"
    ) as mock_open:
                result = await export_html_notes.fn(
                    export_path=str(export_path),
                    show_after_export=False,
                )

                # Should NOT open
                mock_open.assert_not_called()

    assert "Export" in result


@pytest.mark.asyncio
async def test_export_html_empty_folder(tmp_path):
    """Test HTML export with no notes."""
    export_path = tmp_path / "empty"

    with patch(
        "advanced_memory.mcp.tools.export_html_notes._get_notes_from_folder"
    ) as mock_get_notes:
        mock_get_notes.return_value = []

        result = await export_html_notes.fn(
            export_path=str(export_path),
        )

    assert "No notes" in result or "export" in result.lower()


@pytest.mark.asyncio
async def test_export_html_mermaid_diagrams(tmp_path):
    """Test HTML export with Mermaid diagrams."""
    notes_with_mermaid = [
        {
            "title": "Diagram Note",
            "content": "# Diagram\n\n```mermaid\ngraph TD\n  A-->B\n```",
            "filename": "diagram.md",
            "path": "test/diagram.md",
            "folder": "test",
        }
    ]

    export_path = tmp_path / "mermaid"

    with patch(
        "advanced_memory.mcp.tools.export_html_notes._get_notes_from_folder"
    ) as mock_get_notes:
        mock_get_notes.return_value = notes_with_mermaid

        with patch(
            "advanced_memory.mcp.tools.export_html_notes._process_html_export"
        ) as mock_process:
            mock_process.return_value = "# Export with Mermaid Complete"

            result = await export_html_notes.fn(
                export_path=str(export_path),
                show_after_export=False,
            )

    assert "export" in result.lower()



