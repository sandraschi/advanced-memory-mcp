"""Safe file operations with trash and logging support.

This module provides safe alternatives to standard file operations that:
1. Move files to a trash directory instead of deleting them
2. Include extensive logging
3. Perform safety checks
4. Support recovery of deleted files
"""

import shutil
from datetime import datetime
from fnmatch import fnmatch
from pathlib import Path

from loguru import logger

# Type aliases
FilePath = str | Path


class FileSafetyError(Exception):
    """Base exception for file safety operations."""

    pass


class FileSafety:
    """Safe file operations with trash and logging."""

    # Directories that should never be deleted
    PROTECTED_DIRS = {
        ".git",
        ".hg",
        ".svn",
        ".trash",  # Don't delete the trash!
    }

    # File patterns that should never be deleted
    PROTECTED_PATTERNS = {
        ".gitignore",
        ".gitmodules",
        "README.md",
        "LICENSE*",
    }

    # Maximum file size to move to trash (in bytes)
    MAX_TRASH_SIZE = 100 * 1024 * 1024  # 100MB

    def __init__(self, base_path: FilePath, trash_dir: FilePath | None = None):
        """Initialize with base path and optional trash directory.

        Args:
            base_path: Base path for all operations (must be absolute)
            trash_dir: Custom trash directory (default: .trash in base_path)
        """
        self.base_path = Path(base_path).resolve()

        # Set up trash directory
        self.trash_dir = Path(trash_dir) if trash_dir else self.base_path / ".trash"
        self._ensure_trash_dir()

        # Set up logging
        self.setup_logging()

    def _ensure_trash_dir(self) -> None:
        """Ensure the trash directory exists."""
        if not self.trash_dir.exists():
            self.trash_dir.mkdir(parents=True, exist_ok=True)
            logger.info(f"Created trash directory: {self.trash_dir}")

    def setup_logging(self) -> None:
        """Set up file operation logging."""
        self.log_file = self.trash_dir / "file_operations.log"

        # Configure loguru logger for this module
        logger.add(
            self.log_file,
            rotation="10 MB",
            retention="30 days",
            level="INFO",
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {message}",
            enqueue=True,
        )

    def is_safe_to_delete(self, path: FilePath) -> bool:
        """Check if path is safe to delete.

        Args:
            path: Path to check

        Returns:
            True if path is safe to delete, False otherwise
        """
        path_obj = Path(path).resolve()

        # Check against protected directories
        for protected in self.PROTECTED_DIRS:
            if protected in path_obj.parts:
                return False

        # Check against protected patterns
        name = path_obj.name
        for pattern in self.PROTECTED_PATTERNS:
            if fnmatch(name, pattern):
                return False

        # Check if it's within base_path
        try:
            path_obj.relative_to(self.base_path)
        except ValueError:
            return False

        return True

    def safe_delete(self, path: FilePath) -> Path:
        """Move file to trash.

        Args:
            path: Path to file to delete

        Returns:
            Path where the file was moved in trash

        Raises:
            FileSafetyError: If deletion is unsafe or fails
        """
        path_obj = Path(path).resolve()

        if not path_obj.exists():
            raise FileSafetyError(f"File not found: {path_obj}")

        if not self.is_safe_to_delete(path_obj):
            raise FileSafetyError(f"Safety check failed for: {path_obj}")

        # Check file size
        if path_obj.is_file() and path_obj.stat().st_size > self.MAX_TRASH_SIZE:
            logger.warning(
                f"Moving large file to trash: {path_obj} ({path_obj.stat().st_size} bytes)"
            )

        # Generate unique trash path
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        trash_name = f"{path_obj.name}.{timestamp}"
        trash_path = self.trash_dir / trash_name

        try:
            shutil.move(str(path_obj), str(trash_path))
            logger.info(f"Moved to trash: {path_obj} -> {trash_path}")
            return trash_path
        except Exception as e:
            raise FileSafetyError(f"Failed to move to trash: {e}") from e

    def recover_from_trash(self, trash_path: FilePath, destination: FilePath) -> Path:
        """Recover a file from trash.

        Args:
            trash_path: Path in trash
            destination: Where to recover to

        Returns:
            Path to recovered file
        """
        trash_obj = Path(trash_path).resolve()
        dest_obj = Path(destination).resolve()

        if not trash_obj.exists():
            raise FileSafetyError(f"Trash file not found: {trash_obj}")

        try:
            shutil.move(str(trash_obj), str(dest_obj))
            logger.info(f"Recovered from trash: {trash_obj} -> {dest_obj}")
            return dest_obj
        except Exception as e:
            raise FileSafetyError(f"Failed to recover from trash: {e}") from e


# Global instance for convenience
# Use user's home directory as base to allow operations on user files
# Use a specific directory for trash to avoid permission issues and clutter
file_safety = FileSafety(
    base_path=Path.home(),
    trash_dir=Path.home() / ".advanced-memory-mcp" / "trash",
)
