"""Tests for file_opener utility."""

import platform
from unittest.mock import patch

from advanced_memory.utils.file_opener import (
    format_open_result,
    open_file_or_folder,
    open_url_in_browser,
)


def test_open_file_or_folder_nonexistent():
    """Test opening non-existent path returns error."""
    success, msg = open_file_or_folder("/nonexistent/path/file.txt")

    assert success is False
    assert "does not exist" in msg.lower()


def test_open_file_or_folder_existing_file(tmp_path):
    """Test opening existing file."""
    test_file = tmp_path / "test.txt"
    test_file.write_text("test content")

    system = platform.system()

    if system == "Windows":
        with patch("os.startfile") as mock_start:
            success, msg = open_file_or_folder(test_file)

            assert success is True
            assert mock_start.called
    elif system == "Darwin":
        with patch("subprocess.run") as mock_run:
            success, msg = open_file_or_folder(test_file)

            assert success is True
            assert mock_run.called
    elif system == "Linux":
        with patch("subprocess.run") as mock_run:
            success, msg = open_file_or_folder(test_file)

            assert success is True
            assert mock_run.called


def test_open_file_or_folder_existing_folder(tmp_path):
    """Test opening existing folder."""
    test_folder = tmp_path / "test_folder"
    test_folder.mkdir()

    system = platform.system()

    if system == "Windows":
        with patch("os.startfile") as mock_start:
            success, msg = open_file_or_folder(test_folder)

            assert success is True
            assert mock_start.called
    elif system == "Darwin":
        with patch("subprocess.run") as mock_run:
            success, msg = open_file_or_folder(test_folder)

            assert success is True
            assert mock_run.called
    elif system == "Linux":
        with patch("subprocess.run") as mock_run:
            success, msg = open_file_or_folder(test_folder)

            assert success is True
            assert mock_run.called


def test_open_url_in_browser_success():
    """Test opening URL in browser."""
    with patch("webbrowser.open") as mock_browser:
        success, msg = open_url_in_browser("http://localhost:3211")

        assert success is True
        assert mock_browser.called
        assert "localhost:3211" in msg


def test_open_url_in_browser_failure():
    """Test browser open failure."""
    with patch("webbrowser.open") as mock_browser:
        mock_browser.side_effect = Exception("Browser not available")

        success, msg = open_url_in_browser("http://test.com")

        assert success is False
        assert "Failed" in msg


def test_format_open_result_success():
    """Test formatting successful open result."""
    result = format_open_result(True, "File opened successfully", "/path/to/file.pdf")

    assert "Opened After Export" in result
    assert "✅" in result
    assert "opened successfully" in result.lower()


def test_format_open_result_failure_with_file():
    """Test formatting failed open result with file path."""
    result = format_open_result(False, "Failed to open", "/path/to/file.pdf")

    assert "Auto-Open Failed" in result
    assert "⚠️" in result
    assert "Failed" in result
    assert "Open manually" in result
    assert "file.pdf" in result


def test_format_open_result_failure_with_folder():
    """Test formatting failed open result with folder path."""
    result = format_open_result(False, "Failed to open", "/path/to/folder")

    assert "Auto-Open Failed" in result
    assert "Open manually" in result
    assert "file explorer" in result.lower()


def test_format_open_result_failure_no_path():
    """Test formatting failed open result without path."""
    result = format_open_result(False, "Something went wrong")

    assert "Auto-Open Failed" in result
    assert "Something went wrong" in result
    # Should not have manual open instructions without path













