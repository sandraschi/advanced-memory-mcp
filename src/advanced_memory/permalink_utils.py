"""Permalink generation utilities for basic-memory."""

import os
import re
import unicodedata
from pathlib import Path
from typing import Any, Union

def generate_permalink(file_path: Union[Path, str, Any]) -> str:
    """
    Generate a permalink from a file path.

    Returns:
        Normalized permalink that matches validation rules. Converts spaces and underscores
        to hyphens for consistency. Preserves non-ASCII characters like Chinese.

    Examples:
        >>> generate_permalink("docs/My Feature.md")
        'docs/my-feature'
        >>> generate_permalink("specs/API_v2.md")
        'specs/api-v2'
        >>> generate_permalink("design/unified_model_refactor.md")
        'design/unified-model-refactor'
        >>> generate_permalink("中文/测试文档.md")
        '中文/测试文档'
    """
    # Convert Path to string if needed
    path_str = str(file_path)

    # Normalize path separators to forward slashes early
    path_str = path_str.replace("\\", "/")

    # Remove extension
    base = os.path.splitext(path_str)[0]

    # Create a transliteration mapping for specific characters
    transliteration_map = {
        "ø": "o",  # Handle Søren -> soren
        "å": "a",  # Handle Kierkegård -> kierkegard
        "ü": "u",  # Handle Müller -> muller
        "é": "e",  # Handle Café -> cafe
        "è": "e",  # Handle Mère -> mere
        "ê": "e",  # Handle Fête -> fete
        "à": "a",  # Handle À la mode -> a la mode
        "ç": "c",  # Handle Façade -> facade
        "ñ": "n",  # Handle Niño -> nino
        "ö": "o",  # Handle Björk -> bjork
        "ä": "a",  # Handle Häagen -> haagen
        # Add more mappings as needed
    }

    # Process character by character, transliterating Latin characters with diacritics
    result = ""
    for char in base:
        # Direct mapping for known characters
        if char.lower() in transliteration_map:
            result += transliteration_map[char.lower()]
        # General case using Unicode normalization
        else:
            # Normalize the character (NFD splits accented characters into base + diacritic)
            normalized = unicodedata.normalize('NFD', char)
            # Keep only the base character, discarding diacritics
            base_char = ''.join(c for c in normalized if not unicodedata.combining(c))
            result += base_char

    # Insert hyphens before uppercase letters that follow lowercase letters (camelCase)
    result = re.sub(r'([a-z])([A-Z])', r'\1-\2', result)

    # Convert to lowercase and replace spaces/underscores with hyphens
    clean_text = (
        result.lower()
        .replace(" ", "-")
        .replace("_", "-")
    )

    # Remove any remaining non-word characters except slashes and hyphens
    clean_text = re.sub(r"[^\w\-/]", "", clean_text)

    # Replace multiple hyphens with a single one
    clean_text = re.sub(r"-+", "-", clean_text)

    # Clean each path segment
    segments = clean_text.split("/")
    clean_segments = [s.strip("-") for s in segments]

    return "/".join(clean_segments)


def sanitize_filename(title: str) -> str:
    """
    Sanitize a note title for use as a filename.

    This function ensures that note titles can be safely used as filenames by:
    - Converting colons (:) to dashes (-) for timestamps
    - Removing dots (.) to prevent filename issues
    - Keeping only alphanumeric characters, spaces, underscores, and hyphens
    - Replacing unsafe characters with underscores

    Args:
        title: The note title to sanitize

    Returns:
        A sanitized string safe for use as a filename (without extension)

    Examples:
        >>> sanitize_filename("Meeting: 2024-01-15 14:30")
        'Meeting-_2024-01-15_14-30'
        >>> sanitize_filename("Version 2.1 Release Notes")
        'Version_2_1_Release_Notes'
        >>> sanitize_filename("Project Alpha/Beta")
        'Project_Alpha_Beta'
    """
    if not title:
        return "untitled"

    # Check if string is only whitespace
    if not title.strip():
        return "untitled"

    # Convert colons to dashes (for timestamps)
    title = title.replace(":", "-")

    # Replace dots with underscores (to prevent filename issues)
    title = title.replace(".", "_")

    # Replace unsafe characters with underscores
    # Keep alphanumeric and dashes, replace spaces and other unsafe chars
    title = re.sub(r"[^\w\-]", "_", title)

    # Replace multiple underscores with single ones
    title = re.sub(r"_+", "_", title)

    # Don't collapse dash-underscore combinations - keep them as is

    # Trim underscores from start and end
    title = title.strip("_")

    # Ensure we have a valid filename (not empty)
    if not title:
        return "untitled"

    # Limit length to prevent filesystem issues
    if len(title) > 100:
        title = title[:100].rstrip("_")

    return title
