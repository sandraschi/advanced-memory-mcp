"""Test filename sanitization for note titles."""

import pytest

from advanced_memory.utils import sanitize_filename


@pytest.mark.parametrize(
    "input_title, expected",
    [
        # Basic cases
        ("Simple Title", "Simple_Title"),
        ("", "untitled"),
        ("   ", "untitled"),

        # Colon replacement (timestamps)
        ("Meeting: 2024-01-15 14:30", "Meeting-_2024-01-15_14-30"),
        ("Call: 10:00 AM", "Call-_10-00_AM"),

        # Dot replacement
        ("Version 2.1 Release Notes", "Version_2_1_Release_Notes"),
        ("File.txt Notes", "File_txt_Notes"),
        ("v1.0.0-alpha", "v1_0_0-alpha"),

        # Unsafe character replacement
        ("Project Alpha/Beta", "Project_Alpha_Beta"),
        ("Test & Special", "Test_Special"),
        ("Question?", "Question"),
        ("File@#$%^&*()", "File"),

        # Multiple unsafe characters
        ("File: v1.2/test&more", "File-_v1_2_test_more"),

        # Length limits
        ("A" * 150, "A" * 100),  # Should be truncated to 100 chars

        # Unicode and special cases
        ("Café Menu", "Café_Menu"),
        ("北京 Notes", "北京_Notes"),
        ("Müller Report", "Müller_Report"),

        # Mixed safe/unsafe
        ("Meeting_2024-01-15_14:30_v2.1", "Meeting_2024-01-15_14-30_v2_1"),

        # Edge cases
        ("___leading_underscores", "leading_underscores"),
        ("trailing_underscores___", "trailing_underscores"),
        ("___both___", "both"),
        ("_single_", "single"),
    ],
)
def test_sanitize_filename(input_title, expected):
    """Test that titles are properly sanitized for filename use."""
    result = sanitize_filename(input_title)
    assert result == expected


def test_sanitize_filename_basic_examples():
    """Test the examples from the docstring."""
    assert sanitize_filename("Meeting: 2024-01-15 14:30") == "Meeting-_2024-01-15_14-30"
    assert sanitize_filename("Version 2.1 Release Notes") == "Version_2_1_Release_Notes"
    assert sanitize_filename("Project Alpha/Beta") == "Project_Alpha_Beta"
