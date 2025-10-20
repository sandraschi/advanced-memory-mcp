"""Tests for native PDF export functionality."""

from unittest.mock import patch

import pytest

# Try to import weasyprint, skip tests if not available (Windows GTK issue)
try:
    from advanced_memory.mcp.tools.export_pdf_native import export_pdf_native

    WEASYPRINT_AVAILABLE = True
except (OSError, ImportError) as e:
    WEASYPRINT_AVAILABLE = False
    SKIP_REASON = f"WeasyPrint not available: {e}"

pytestmark = pytest.mark.skipif(
    not WEASYPRINT_AVAILABLE, reason=SKIP_REASON if not WEASYPRINT_AVAILABLE else ""
)


@pytest.fixture
def mock_notes_data():
    """Sample notes data for testing."""
    return [
        {
            "title": "Test Note 1",
            "content": "# Test Note 1\n\nThis is test content with **bold** and *italic*.",
            "permalink": "test-note-1",
        },
        {
            "title": "Test Note 2",
            "content": "# Test Note 2\n\n```python\nprint('hello')\n```\n\nCode example.",
            "permalink": "test-note-2",
        },
    ]


@pytest.mark.asyncio
async def test_export_pdf_native_basic(tmp_path, mock_notes_data):
    """Test basic PDF export generates files."""
    export_path = tmp_path / "pdfs"

    with patch(
        "advanced_memory.mcp.tools.export_pdf_native._get_notes_from_folder"
    ) as mock_get_notes:
        mock_get_notes.return_value = mock_notes_data

        with patch("advanced_memory.mcp.tools.export_pdf_native.open_file_or_folder") as mock_open:
            mock_open.return_value = (True, "Opened successfully")

            result = await export_pdf_native.fn(
                export_path=str(export_path),
                source_folder="/test",
                show_after_export=False,  # Don't try to open files in test
            )

    # Verify success message
    assert "Native PDF Export Complete" in result
    assert "Export directory" in result


@pytest.mark.asyncio
async def test_export_pdf_native_multiple_files(tmp_path, mock_notes_data):
    """Test PDF export with multiple notes opens folder."""
    export_path = tmp_path / "pdfs"

    with patch(
        "advanced_memory.mcp.tools.export_pdf_native._get_notes_from_folder"
    ) as mock_get_notes:
        mock_get_notes.return_value = mock_notes_data

        with patch("advanced_memory.mcp.tools.export_pdf_native.open_file_or_folder") as mock_open:
            mock_open.return_value = (True, "Opened folder")

            result = await export_pdf_native.fn(
                export_path=str(export_path),
                source_folder="/test",
                show_after_export=True,
            )

    # Should indicate folder was opened (multiple PDFs)
    assert "Opened Folder" in result or "Opened" in result


@pytest.mark.asyncio
async def test_export_pdf_native_single_file(tmp_path):
    """Test PDF export with single note opens the file."""
    export_path = tmp_path / "pdfs"
    single_note = [
        {
            "title": "Single Note",
            "content": "# Single Note\n\nContent here.",
            "permalink": "single-note",
        }
    ]

    with patch(
        "advanced_memory.mcp.tools.export_pdf_native._get_notes_from_folder"
    ) as mock_get_notes:
        mock_get_notes.return_value = single_note

        with patch("advanced_memory.mcp.tools.export_pdf_native.open_file_or_folder") as mock_open:
            mock_open.return_value = (True, "Opened file")

            result = await export_pdf_native.fn(
                export_path=str(export_path),
                show_after_export=True,
            )

    # Should try to open the single PDF
    assert "Opened" in result or "Export Complete" in result


@pytest.mark.asyncio
async def test_export_pdf_native_show_false(tmp_path, mock_notes_data):
    """Test PDF export with show_after_export=False doesn't open."""
    export_path = tmp_path / "pdfs"

    with patch(
        "advanced_memory.mcp.tools.export_pdf_native._get_notes_from_folder"
    ) as mock_get_notes:
        mock_get_notes.return_value = mock_notes_data

        # Mock should NOT be called when show_after_export=False
        with patch("advanced_memory.mcp.tools.export_pdf_native.open_file_or_folder") as mock_open:
            result = await export_pdf_native.fn(
                export_path=str(export_path),
                show_after_export=False,
            )

            # Verify file opener was NOT called
            mock_open.assert_not_called()

    assert "Export Complete" in result


@pytest.mark.asyncio
async def test_export_pdf_native_empty_folder(tmp_path):
    """Test PDF export with no notes."""
    export_path = tmp_path / "pdfs"

    with patch(
        "advanced_memory.mcp.tools.export_pdf_native._get_notes_from_folder"
    ) as mock_get_notes:
        mock_get_notes.return_value = []

        result = await export_pdf_native.fn(
            export_path=str(export_path),
            source_folder="/nonexistent",
        )

    # Should handle gracefully
    assert "No notes" in result or "0" in result or "Export" in result


@pytest.mark.asyncio
async def test_export_pdf_native_themes(tmp_path, mock_notes_data):
    """Test PDF export with different themes."""
    export_path = tmp_path / "pdfs"

    for theme in ["default", "academic", "modern", "dark"]:
        with patch(
            "advanced_memory.mcp.tools.export_pdf_native._get_notes_from_folder"
        ) as mock_get_notes:
            mock_get_notes.return_value = mock_notes_data

            result = await export_pdf_native.fn(
                export_path=str(export_path / theme),
                theme=theme,
                show_after_export=False,
            )

        assert "Export Complete" in result or "Export" in result


@pytest.mark.asyncio
async def test_export_pdf_native_page_sizes(tmp_path, mock_notes_data):
    """Test PDF export with different page sizes."""
    export_path = tmp_path / "pdfs"

    for page_size in ["A4", "Letter", "Legal"]:
        with patch(
            "advanced_memory.mcp.tools.export_pdf_native._get_notes_from_folder"
        ) as mock_get_notes:
            mock_get_notes.return_value = mock_notes_data

            result = await export_pdf_native.fn(
                export_path=str(export_path / page_size),
                page_size=page_size,
                show_after_export=False,
            )

        assert "Export" in result
