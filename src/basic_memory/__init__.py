"""advanced-memory - Enhanced local-first knowledge management combining Zettelkasten with knowledge graphs"""

# Package version - updated by release automation
__version__ = "0.14.4"

# API version for FastAPI - independent of package version
__api_version__ = "v0"

# Import and re-export types from the types module
from .types import PathLike, FilePath

# Import and re-export permalink utility function
from .permalink_utils import generate_permalink

# Import and re-export logging utilities
from .logging_utils import setup_logging

__all__ = [
    'PathLike',
    'FilePath',
    'setup_logging',
    'generate_permalink',
    '__version__',
    '__api_version__',
]
