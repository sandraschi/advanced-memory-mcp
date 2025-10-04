"""advanced-memory - Independent local-first knowledge management system combining Zettelkasten with knowledge graphs, derived from Basic Memory with significant enhancements"""

# Package version - updated by release automation
__version__ = "1.0.0b1"

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
