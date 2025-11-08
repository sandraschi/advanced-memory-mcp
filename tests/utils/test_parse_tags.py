"""Tests for parse_tags utility function."""

import pytest

from advanced_memory.utils import parse_tags


@pytest.mark.parametrize(
    "input_tags,expected",
    [
        # Basic functionality
        (None, []),
        ([], []),
        (["tag1", "tag2"], ["tag1", "tag2"]),
        ("tag1,tag2", ["tag1", "tag2"]),
        # Whitespace and empty handling
        ("tag1, ,tag2", ["tag1", "tag2"]),  # Empty filtered, whitespace stripped
        (["tag1 ", " tag2"], ["tag1", "tag2"]),  # Trimmed
        # Hash stripping
        ("#tag1,##tag2", ["tag1", "tag2"]),
        (["#tag1", "tag2"], ["tag1", "tag2"]),
    ],
)
def test_parse_tags(input_tags: list[str] | str | None, expected: list[str]) -> None:
    """Test tag parsing with various input formats."""
    result = parse_tags(input_tags)
    assert result == expected
