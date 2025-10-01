"""Tests for CLI status command."""

from unittest.mock import patch, AsyncMock

from typer.testing import CliRunner

from basic_memory.cli.app import app
from basic_memory.cli.commands.status import (
    add_files_to_tree,
    build_directory_summary,
    group_changes_by_directory,
    display_changes,
)
from basic_memory.sync.sync_service import SyncReport

# Set up CLI runner
runner = CliRunner()


def test_status_command():
    """Test CLI status command."""
    # Mock the async run_status function to avoid event loop issues
    with patch(
        "basic_memory.cli.commands.status.run_status", new_callable=AsyncMock
    ) as mock_run_status:
        # Mock successful execution (no return value needed since it just prints)
        mock_run_status.return_value = None

        # Should exit with code 0
        result = runner.invoke(app, ["status", "--verbose"])
        assert result.exit_code == 0

        # Verify the function was called with verbose=True
        mock_run_status.assert_called_once_with(True)


def test_status_command_error():
    """Test CLI status command error handling."""
    # Mock the async run_status function to raise an exception
    with patch(
        "basic_memory.cli.commands.status.run_status", new_callable=AsyncMock
    ) as mock_run_status:
        # Mock an error
        mock_run_status.side_effect = Exception("Database connection failed")

        # Should exit with code 1 when error occurs
        result = runner.invoke(app, ["status", "--verbose"])
        assert result.exit_code == 1
        assert "Error checking status: Database connection failed" in result.stderr


def test_display_changes_no_changes():
    """Test displaying no changes."""
    changes = SyncReport(set(), set(), set(), {}, {})
    display_changes("test", "Test", changes, verbose=True)
    display_changes("test", "Test", changes, verbose=False)


def test_display_changes_with_changes():
    """Test displaying various changes."""
    changes = SyncReport(
        new={"dir1/new.md"},
        modified={"dir1/mod.md"},
        deleted={"dir2/del.md"},
        moves={"old.md": "new.md"},
        checksums={"dir1/new.md": "abcd1234"},
    )
    display_changes("test", "Test", changes, verbose=True)
    display_changes("test", "Test", changes, verbose=False)


def test_build_directory_summary():
    """Test building directory change summary."""
    counts = {
        "new": 2,
        "modified": 1,
        "moved": 1,
        "deleted": 1,
    }
    summary = build_directory_summary(counts)
    assert "+2" in summary
    assert "~1" in summary
    assert "↔1" in summary
    assert "-1" in summary


def test_build_directory_summary_empty():
    """Test summary with no changes."""
    counts = {
        "new": 0,
        "modified": 0,
        "moved": 0,
        "deleted": 0,
    }
    summary = build_directory_summary(counts)
    assert summary == ""


def test_group_changes_by_directory():
    """Test grouping changes by directory."""
    changes = SyncReport(
        new={"dir1/new.md", "dir2/new2.md"},
        modified={"dir1/mod.md"},
        deleted={"dir2/del.md"},
        moves={"dir1/old.md": "dir2/new.md"},
        checksums={},
    )

    grouped = group_changes_by_directory(changes)

    assert grouped["dir1"]["new"] == 1
    assert grouped["dir1"]["modified"] == 1
    assert grouped["dir1"]["moved"] == 1

    assert grouped["dir2"]["new"] == 1
    assert grouped["dir2"]["deleted"] == 1
    assert grouped["dir2"]["moved"] == 1


def test_add_files_to_tree():
    """Test adding files to tree visualization."""
    from rich.tree import Tree

    # Test with various path patterns
    paths = {
        "dir1/file1.md",  # Normal nested file
        "dir1/file2.md",  # Another in same dir
        "dir2/subdir/file3.md",  # Deeper nesting
        "root.md",  # Root level file
    }

    # Test without checksums
    tree = Tree("Test")
    add_files_to_tree(tree, paths, "green")

    # Test with checksums
    checksums = {"dir1/file1.md": "abcd1234", "dir1/file2.md": "efgh5678"}

    tree = Tree("Test with checksums")
    add_files_to_tree(tree, paths, "green", checksums)
