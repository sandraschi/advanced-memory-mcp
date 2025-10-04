"""Type definitions for Basic Memory.

This module contains type definitions used throughout the application to avoid circular imports.
"""

from pathlib import Path
from typing import Union, TypeVar, Any, Optional

# Define PathLike and FilePath types
PathLike = Union[str, Path]
FilePath = TypeVar('FilePath', str, Path)

__all__ = [
    'PathLike',
    'FilePath',
]
