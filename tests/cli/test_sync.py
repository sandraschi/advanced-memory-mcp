"""Tests for CLI sync command."""

import pytest
from typer.testing import CliRunner

from basic_memory.cli.app import app
from basic_memory.cli.commands.sync import (
    display_sync_summary,
    display_detailed_sync_results,
    run_sync,
    group_issues_by_directory,
    ValidationIssue,
)
from basic_memory.config import get_project_config
from basic_memory.sync.sync_service import SyncReport

# Set up CLI runner
runner = CliRunner()


def test_group_issues_by_directory():
    """Test grouping validation issues by directory."""
    issues = [
        ValidationIssue("dir1/file1.md", "error1"),
        ValidationIssue("dir1/file2.md", "error2"),
        ValidationIssue("dir2/file3.md", "error3"),
    ]

    grouped = group_issues_by_directory(issues)

    assert len(grouped["dir1"]) == 2
    assert len(grouped["dir2"]) == 1
    assert grouped["dir1"][0].error == "error1"
    assert grouped["dir2"][0].error == "error3"


def test_display_sync_summary_no_changes():
    """Test displaying sync summary with no changes."""
    changes = SyncReport(set(), set(), set(), {}, {})
    display_sync_summary(changes)


def test_display_sync_summary_with_changes():
    """Test displaying sync summary with various changes."""
    changes = SyncReport(
        new={"new.md"},
        modified={"mod.md"},
        deleted={"del.md"},
        moves={"old.md": "new.md"},
        checksums={"new.md": "abcd1234"},
    )
    display_sync_summary(changes)


def test_display_detailed_sync_results_no_changes():
    """Test displaying detailed results with no changes."""
    changes = SyncReport(set(), set(), set(), {}, {})
    display_detailed_sync_results(changes)


def test_display_detailed_sync_results_with_changes():
    """Test displaying detailed results with various changes."""
    changes = SyncReport(
        new={"new.md"},
        modified={"mod.md"},
        deleted={"del.md"},
        moves={"old.md": "new.md"},
        checksums={"new.md": "abcd1234", "mod.md": "efgh5678"},
    )
    display_detailed_sync_results(changes)


@pytest.mark.asyncio
async def test_run_sync_basic(sync_service, project_config, test_project):
    """Test basic sync operation."""
    # Set up test environment
    config = get_project_config()
    config.home = project_config.home
    config.name = test_project.name

    # Create test files
    test_file = project_config.home / "test.md"
    test_file.write_text("""---
title: Test
---
# Test
Some content""")

    # Run sync - should detect new file
    await run_sync(verbose=True)


def test_sync_command():
    """Test the sync command."""
    from unittest.mock import patch, AsyncMock

    # Mock the async run_sync function to avoid event loop issues
    with patch("basic_memory.cli.commands.sync.run_sync", new_callable=AsyncMock) as mock_run_sync:
        # Mock successful execution (no return value needed since it just prints)
        mock_run_sync.return_value = None

        # Mock config values that the sync command prints
        result = runner.invoke(app, ["sync", "--verbose"])
        assert result.exit_code == 0

        # Verify output contains project info
        assert "Syncing project: test-project" in result.stdout

        # Verify the function was called with verbose=True
        mock_run_sync.assert_called_once_with(verbose=True)


def test_sync_command_error():
    """Test the sync command error handling."""
    from unittest.mock import patch, AsyncMock

    # Mock the async run_sync function to raise an exception
    with patch("basic_memory.cli.commands.sync.run_sync", new_callable=AsyncMock) as mock_run_sync:
        # Mock an error
        mock_run_sync.side_effect = Exception("Sync failed")

        result = runner.invoke(app, ["sync", "--verbose"])
        assert result.exit_code == 1
        assert "Error during sync: Sync failed" in result.stderr
