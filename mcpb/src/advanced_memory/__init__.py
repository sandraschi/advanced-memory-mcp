"""advanced-memory - Independent local-first knowledge management system combining Zettelkasten with knowledge graphs, derived from Advanced Memory with significant enhancements"""

# Package version - updated by release automation
__version__ = "1.0.0b4"

# API version for FastAPI - independent of package version
__api_version__ = "v0"

# Import and re-export types from the types module
# Import and re-export logging utilities
from .logging_utils import setup_logging

# Import and re-export permalink utility function
from .permalink_utils import generate_permalink
from .types import FilePath, PathLike

__all__ = [
    "FilePath",
    "PathLike",
    "__api_version__",
    "__version__",
    "generate_permalink",
    "setup_logging",
]
