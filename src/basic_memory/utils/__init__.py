"""Utility modules for Basic Memory.

This package contains various utility modules that provide common functionality
across the Basic Memory application, including file operations, logging, and more.
"""

# Import types from the main types module
from basic_memory.types import PathLike, FilePath

# Import file safety utilities
from .file_safety import FileSafety, FileSafetyError, file_safety

# Import setup_logging from the logging_utils module
from basic_memory.logging_utils import setup_logging

# Import generate_permalink and sanitize_filename from the permalink_utils module
from basic_memory.permalink_utils import generate_permalink, sanitize_filename

# Import parse_tags from tag_utils
from basic_memory.tag_utils import parse_tags

# Import from path_utils
from basic_memory.utils.path_utils import validate_project_path

__all__ = [
    'FileSafety',
    'FileSafetyError',
    'file_safety',
    'FilePath',
    'PathLike',
    'setup_logging',
    'generate_permalink',
    'sanitize_filename',
    'parse_tags',
    'validate_project_path',
]
