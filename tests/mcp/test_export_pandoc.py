"""Tests for Pandoc export functionality."""

import inspect
from unittest.mock import AsyncMock, patch

import pytest

from tests.mcp.tool_invoker import mcp_fn

from advanced_memory.mcp.tools.export_pandoc import _build_pandoc_command, export_pandoc


@pytest.fixture
def mock_notes_data():
    """Sample notes data for testing."""
    return [
        {
            "id": "1",
            "title": "Research Note",
            "file_path": "research/note1.md",
            "content": "# Research Note\n\nContent here.",
        },
        {
            "id": "2",
            "title": "Meeting Minutes",
            "file_path": "meetings/note2.md",
            "content": "# Meeting Minutes\n\n- Action item 1\n- Action item 2",
        },
    ]


@pytest.mark.asyncio
async def test_export_pandoc_docx(tmp_path, mock_notes_data):
    """Test DOCX export via Pandoc."""
    export_path = tmp_path / "docx"

    with patch("advanced_memory.mcp.tools.export_pandoc._get_notes_from_folder") as mock_get_notes:
        mock_get_notes.return_value = mock_notes_data

        with patch("advanced_memory.mcp.tools.export_pandoc.get_pandoc_command") as mock_pandoc:
            mock_pandoc.return_value = ["pandoc"]  # Returns list, not string

            with patch("advanced_memory.mcp.tools.export_pandoc.asyncio.create_subprocess_exec") as mock_exec:
                # Mock successful subprocess
                mock_process = AsyncMock()
                mock_process.communicate.return_value = (b"", b"")
                mock_process.returncode = 0
                mock_exec.return_value = mock_process

                with patch("advanced_memory.utils.file_opener.open_file_or_folder") as mock_open:
                    mock_open.return_value = (True, "Opened")

                    result = await mcp_fn(export_pandoc)(
                        export_path=str(export_path),
                        format_type="docx",
                        show_after_export=False,
                    )

    assert "export" in result.lower() or "pandoc" in result.lower()


@pytest.mark.asyncio
async def test_export_pandoc_epub(tmp_path, mock_notes_data):
    """Test EPUB export via Pandoc."""
    export_path = tmp_path / "epub"

    with patch("advanced_memory.mcp.tools.export_pandoc._get_notes_from_folder") as mock_get_notes:
        mock_get_notes.return_value = mock_notes_data

        with patch("advanced_memory.mcp.tools.export_pandoc.get_pandoc_command") as mock_pandoc:
            mock_pandoc.return_value = ["pandoc"]  # Returns list, not string

            with patch("advanced_memory.mcp.tools.export_pandoc.asyncio.create_subprocess_exec") as mock_exec:
                mock_process = AsyncMock()
                mock_process.communicate.return_value = (b"", b"")
                mock_process.returncode = 0
                mock_exec.return_value = mock_process

                result = await mcp_fn(export_pandoc)(
                    export_path=str(export_path),
                    format_type="epub",
                    show_after_export=False,
                )

    assert "export" in result.lower() or "pandoc" in result.lower()


@pytest.mark.asyncio
async def test_export_pandoc_html(tmp_path, mock_notes_data):
    """Test HTML export via Pandoc."""
    export_path = tmp_path / "html"

    with patch("advanced_memory.mcp.tools.export_pandoc._get_notes_from_folder") as mock_get_notes:
        mock_get_notes.return_value = mock_notes_data

        with patch("advanced_memory.mcp.tools.export_pandoc.get_pandoc_command") as mock_pandoc:
            mock_pandoc.return_value = ["pandoc"]  # Returns list, not string

            with patch("advanced_memory.mcp.tools.export_pandoc.asyncio.create_subprocess_exec") as mock_exec:
                mock_process = AsyncMock()
                mock_process.communicate.return_value = (b"", b"")
                mock_process.returncode = 0
                mock_exec.return_value = mock_process

                result = await mcp_fn(export_pandoc)(
                    export_path=str(export_path),
                    format_type="html",
                    show_after_export=False,
                )

    assert "export" in result.lower() or "pandoc" in result.lower()


@pytest.mark.asyncio
async def test_export_pandoc_show_after_export(tmp_path, mock_notes_data):
    """Test Pandoc export opens files when show_after_export=True."""
    export_path = tmp_path / "output"

    with patch("advanced_memory.mcp.tools.export_pandoc._get_notes_from_folder") as mock_get_notes:
        mock_get_notes.return_value = mock_notes_data[:1]  # Single note

        with patch("advanced_memory.mcp.tools.export_pandoc.get_pandoc_command") as mock_pandoc:
            mock_pandoc.return_value = ["pandoc"]  # Returns list, not string

            with patch("advanced_memory.mcp.tools.export_pandoc.asyncio.create_subprocess_exec") as mock_exec:
                mock_process = AsyncMock()
                mock_process.communicate.return_value = (b"", b"")
                mock_process.returncode = 0
                mock_exec.return_value = mock_process

                with patch("advanced_memory.utils.file_opener.open_file_or_folder") as mock_open:
                    mock_open.return_value = (True, "Opened file")

                    result = await mcp_fn(export_pandoc)(
                        export_path=str(export_path),
                        format_type="docx",
                        show_after_export=True,
                    )

                    # Verify opener was called
                    assert mock_open.called

    assert "Opened" in result


@pytest.mark.asyncio
async def test_export_pandoc_no_show(tmp_path, mock_notes_data):
    """Test Pandoc export doesn't open when show_after_export=False."""
    export_path = tmp_path / "output"

    with patch("advanced_memory.mcp.tools.export_pandoc._get_notes_from_folder") as mock_get_notes:
        mock_get_notes.return_value = mock_notes_data

        with patch("advanced_memory.mcp.tools.export_pandoc.get_pandoc_command") as mock_pandoc:
            mock_pandoc.return_value = ["pandoc"]  # Returns list, not string

            with patch("advanced_memory.mcp.tools.export_pandoc.asyncio.create_subprocess_exec") as mock_exec:
                mock_process = AsyncMock()
                mock_process.communicate.return_value = (b"", b"")
                mock_process.returncode = 0
                mock_exec.return_value = mock_process

                with patch("advanced_memory.utils.file_opener.open_file_or_folder") as mock_open:
                    result = await mcp_fn(export_pandoc)(
                        export_path=str(export_path),
                        format_type="docx",
                        show_after_export=False,
                    )

                    # Verify opener was NOT called
                    mock_open.assert_not_called()

    assert "export" in result.lower()


@pytest.mark.asyncio
async def test_export_pandoc_empty_folder(tmp_path):
    """Test Pandoc export with no notes."""
    export_path = tmp_path / "empty"

    with patch("advanced_memory.mcp.tools.export_pandoc._get_notes_from_folder") as mock_get_notes:
        mock_get_notes.return_value = []

        result = await mcp_fn(export_pandoc)(
            export_path=str(export_path),
            format_type="pdf",
        )

    # Should handle gracefully
    assert "export" in result.lower() or "no notes" in result.lower()


@pytest.mark.asyncio
async def test_export_pandoc_error_handling(tmp_path, mock_notes_data):
    """Test Pandoc export handles errors gracefully."""
    export_path = tmp_path / "error"

    with patch("advanced_memory.mcp.tools.export_pandoc._get_notes_from_folder") as mock_get_notes:
        mock_get_notes.return_value = mock_notes_data

        with patch("advanced_memory.mcp.tools.export_pandoc.get_pandoc_command") as mock_pandoc:
            mock_pandoc.return_value = ["pandoc"]

            with patch("advanced_memory.mcp.tools.export_pandoc.asyncio.create_subprocess_exec") as mock_exec:
                # Mock failed subprocess
                mock_process = AsyncMock()
                mock_process.communicate.return_value = (b"", b"Error: conversion failed")
                mock_process.returncode = 1
                mock_exec.return_value = mock_process

                result = await mcp_fn(export_pandoc)(
                    export_path=str(export_path),
                    format_type="pdf",
                    show_after_export=False,
                )

    # Should report errors
    assert "export" in result.lower()


class TestPdfEngineDefaults:
    """Test PDF engine configuration and defaults."""

    def test_default_pdf_engine_is_weasyprint(self):
        """Test that the default pdf_engine is weasyprint (pure Python, no external deps)."""
        sig = inspect.signature(mcp_fn(export_pandoc))
        pdf_engine_param = sig.parameters.get("pdf_engine")

        assert pdf_engine_param is not None, "pdf_engine parameter not found"
        assert pdf_engine_param.default == "weasyprint", (
            f"Expected default pdf_engine to be 'weasyprint' (pure Python), but got '{pdf_engine_param.default}'"
        )

    def test_default_self_contained_is_true(self):
        """Test that self_contained defaults to True for embedded resources."""
        sig = inspect.signature(mcp_fn(export_pandoc))
        self_contained_param = sig.parameters.get("self_contained")

        assert self_contained_param is not None
        assert self_contained_param.default is True

    def test_build_pandoc_command_weasyprint(self):
        """Test that _build_pandoc_command correctly handles weasyprint engine."""
        with patch("advanced_memory.mcp.tools.export_pandoc.get_pandoc_command") as mock_pandoc:
            mock_pandoc.return_value = ["pandoc"]

            cmd = _build_pandoc_command(
                input_path="input.md",
                output_path="output.pdf",
                format_type="pdf",
                pdf_engine="weasyprint",
                template_path=None,
                css_path=None,
                toc=False,
                highlight_style="tango",
                standalone=True,
                self_contained=False,
            )

            assert "--pdf-engine" in cmd
            assert "weasyprint" in cmd
            # Should include CSS for weasyprint
            assert "--css" in cmd

    def test_build_pandoc_command_html_embed_resources(self):
        """Test that HTML export uses --embed-resources for self-contained output."""
        with patch("advanced_memory.mcp.tools.export_pandoc.get_pandoc_command") as mock_pandoc:
            mock_pandoc.return_value = ["pandoc"]

            cmd = _build_pandoc_command(
                input_path="input.md",
                output_path="output.html",
                format_type="html",
                pdf_engine="weasyprint",  # Ignored for HTML
                template_path=None,
                css_path=None,
                toc=False,
                highlight_style="tango",
                standalone=True,
                self_contained=True,
            )

            assert "--embed-resources" in cmd
            # Should include default CSS
            assert "--css" in cmd
            assert "water.css" in " ".join(cmd)

    def test_build_pandoc_command_with_toc(self):
        """Test that TOC options are correctly added."""
        with patch("advanced_memory.mcp.tools.export_pandoc.get_pandoc_command") as mock_pandoc:
            mock_pandoc.return_value = ["pandoc"]

            cmd = _build_pandoc_command(
                input_path="input.md",
                output_path="output.html",
                format_type="html",
                pdf_engine="weasyprint",
                template_path=None,
                css_path=None,
                toc=True,
                highlight_style="tango",
                standalone=True,
                self_contained=False,
            )

            assert "--toc" in cmd
            assert "--toc-depth" in cmd
            assert "3" in cmd
