"""Service for file operations with checksum tracking and safety features."""

import mimetypes
import shutil
import time
from datetime import datetime
from os import stat_result, stat
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union, TypeVar

# Import file utilities with explicit module path to avoid type checking issues
import basic_memory.file_utils as file_utils
from basic_memory.markdown.markdown_processor import MarkdownProcessor
from basic_memory.models import Entity as EntityModel
from basic_memory.schemas import Entity as EntitySchema
from basic_memory.services.exceptions import FileOperationError
from basic_memory.utils import file_safety
from loguru import logger

# Type alias for file paths that can be either a string or a Path object
FilePath = Union[str, Path]


class FileService:
    """Service for handling file operations.

    All paths are handled as Path objects internally. Strings are converted to
    Path objects when passed in. Relative paths are assumed to be relative to
    base_path.

    Features:
    - Consistent file writing with checksums
    - Frontmatter management
    - Atomic operations
    - Error handling
    """

    def __init__(
        self,
        base_path: Path,
        markdown_processor: MarkdownProcessor,
    ):
        self.base_path = base_path.resolve()  # Get absolute path
        self.markdown_processor = markdown_processor

    def get_entity_path(self, entity: Union[EntityModel, EntitySchema]) -> Path:
        """Generate absolute filesystem path for entity.

        Args:
            entity: Entity model or schema with file_path attribute

        Returns:
            Absolute Path to the entity file
        """
        return self.base_path / entity.file_path

    async def read_entity_content(self, entity: EntityModel) -> str:
        """Get entity's content without frontmatter or structured sections.

        Used to index for search. Returns raw content without frontmatter,
        observations, or relations.

        Args:
            entity: Entity to read content for

        Returns:
            Raw content string without metadata sections
        """
        logger.debug(f"Reading entity content, entity_id={entity.id}, permalink={entity.permalink}")

        file_path = self.get_entity_path(entity)
        markdown = await self.markdown_processor.read_file(file_path)
        return markdown.content or ""

    async def delete_entity_file(self, entity: EntityModel, force: bool = False) -> bool:
        """Safely delete an entity's file from the filesystem.

        Args:
            entity: Entity model whose file should be deleted
            force: If True, bypass safety checks (use with caution!)

        Returns:
            bool: True if file was deleted, False if it didn't exist

        Raises:
            FileOperationError: If deletion fails or is not allowed
        """
        path = self.get_entity_path(entity)
        return await self.delete_file(path, force=force)

    async def exists(self, path: FilePath) -> bool:
        """Check if file exists at the provided path.

        If path is relative, it is assumed to be relative to base_path.

        Args:
            path: Path to check (Path or string)

        Returns:
            True if file exists, False otherwise

        Raises:
            FileOperationError: If check fails
        """
        try:
            # Convert string to Path if needed
            path_obj = self.base_path / path if isinstance(path, str) else path
            logger.debug(f"Checking file existence: path={path_obj}")
            if path_obj.is_absolute():
                return path_obj.exists()
            else:
                return (self.base_path / path_obj).exists()
        except Exception as e:
            logger.error("Failed to check file existence", path=str(path), error=str(e))
            raise FileOperationError(f"Failed to check file existence: {e}")

    async def write_file(self, path: FilePath, content: str, overwrite: bool = True) -> str:
        """Safely write content to file and return checksum.

        Handles both absolute and relative paths. Relative paths are resolved
        against base_path. Creates backup of existing file if overwriting.

        Args:
            path: Where to write (Path or string)
            content: Content to write
            overwrite: If False, raise error if file exists

        Returns:
            Checksum of written content

        Raises:
            FileOperationError: If write fails or file exists and overwrite=False
        """
        # Convert string to Path if needed
        path_obj = Path(path) if isinstance(path, str) else path
        full_path = path_obj if path_obj.is_absolute() else self.base_path / path_obj

        try:
            # Check if file exists and handle accordingly
            if full_path.exists():
                if not overwrite:
                    raise FileOperationError(f"File already exists and overwrite=False: {full_path}")
                
                # Create backup before overwriting
                backup_path = full_path.with_suffix(f".{datetime.now().strftime('%Y%m%d_%H%M%S')}.bak")
            # Ensure the parent directory exists
            parent_dir = full_path.parent
            await file_utils.ensure_directory(parent_dir)
            
            # Create a backup if the file exists and we're not forcing overwrite
            if full_path.exists() and not overwrite:
                backup_path = full_path.with_suffix(f".{int(time.time())}.bak")
                shutil.copy2(str(full_path), str(backup_path))
                logger.info(f"Created backup at {backup_path}")
            
            # Log the write operation
            logger.info(
                f"Writing file: {full_path.relative_to(self.base_path)}, "
                f"is_markdown={full_path.suffix.lower() == '.md'}"
            )

            # Use atomic write to prevent partial writes
            await file_utils.write_file_atomic(full_path, content)

            # Compute and return checksum
            checksum = await file_utils.compute_checksum(content)
            logger.debug(f"File write completed: {full_path}, checksum={checksum}")
            return checksum

        except Exception as e:
            error_msg = f"Failed to write file {full_path}: {str(e)}"
            logger.error(error_msg, exc_info=True)
            raise FileOperationError(error_msg) from e

    # TODO remove read_file
    async def read_file(self, path: FilePath) -> Tuple[str, str]:
        """Safely read file and compute checksum.

        Handles both absolute and relative paths. Relative paths are resolved
        against base_path. Includes safety checks and logging.

        Args:
            path: Path to read (Path or string)

        Returns:
            Tuple of (content, checksum)

        Raises:
            FileOperationError: If read fails or file is not safe to read
        """
        # Convert string to Path if needed
        path_obj = Path(path) if isinstance(path, str) else path
        full_path = path_obj if path_obj.is_absolute() else self.base_path / path_obj

        try:
            # Check if file exists and is accessible
            if not full_path.exists():
                raise FileOperationError(f"File does not exist: {full_path}")
                
            if not full_path.is_file():
                raise FileOperationError(f"Path is not a file: {full_path}")
                
            # Check file size to prevent reading extremely large files
            file_size = full_path.stat().st_size
            MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
            if file_size > MAX_FILE_SIZE:
                raise FileOperationError(
                    f"File too large ({file_size/1024/1024:.1f}MB > {MAX_FILE_SIZE/1024/1024}MB): {full_path}"
                )

            logger.debug(f"Reading file: {full_path.relative_to(self.base_path)}")
            
            # Read file with explicit encoding
            try:
                content = full_path.read_text(encoding="utf-8")
            except UnicodeDecodeError as ude:
                # Try with different encodings if UTF-8 fails
                try:
                    content = full_path.read_text(encoding="latin-1")
                    logger.warning(f"Read file with latin-1 encoding: {full_path}")
                except Exception as e:
                    raise FileOperationError(f"Failed to decode file {full_path}: {str(e)}") from ude
            
            # Compute checksum of the file content
            checksum = await file_utils.compute_checksum(content)
            logger.debug(
                f"File read completed: {full_path.relative_to(self.base_path)}, "
                f"size={len(content)} bytes, checksum={checksum}"
            )
            
            return content, checksum

        except FileOperationError:
            raise  # Re-raise our own exceptions
            
        except Exception as e:
            error_msg = f"Failed to read file {full_path}: {str(e)}"
            logger.error(error_msg, exc_info=True)
            raise FileOperationError(error_msg) from e

    async def delete_file(self, path: FilePath, force: bool = False) -> bool:
        """Safely delete a file by moving it to trash.

        Handles both absolute and relative paths. Relative paths are resolved
        against base_path.

        Args:
            path: Path to delete (Path or string)
            force: If True, bypass safety checks (use with caution!)

        Returns:
            bool: True if file was deleted, False if it didn't exist

        Raises:
            FileOperationError: If deletion fails or is not allowed
        """
        # Convert string to Path if needed
        path_obj = Path(path) if isinstance(path, str) else path
        full_path = path_obj if path_obj.is_absolute() else self.base_path / path_obj

        if not full_path.exists():
            logger.debug(f"File does not exist, nothing to delete: {full_path}")
            return False

        try:
            # Log the deletion attempt
            file_size = full_path.stat().st_size if full_path.is_file() else 0
            logger.info(
                f"Deleting {'directory' if full_path.is_dir() else 'file'}: "
                f"{full_path.relative_to(self.base_path)} (size: {file_size/1024:.1f} KB)"
            )

            # Use the file_safety module to handle the deletion
            if force:
                # Bypass safety checks (dangerous!)
                if full_path.is_dir():
                    shutil.rmtree(full_path)
                else:
                    full_path.unlink()
                logger.warning(f"Force deleted (bypassed safety checks): {full_path}")
            else:
                # Use safe deletion (moves to trash)
                file_safety.safe_delete(full_path)
                logger.info(f"Moved to trash: {full_path}")

            return True

        except Exception as e:
            error_msg = f"Failed to delete {full_path}: {str(e)}"
            logger.error(error_msg, exc_info=True)
            raise FileOperationError(error_msg) from e

    async def update_frontmatter(self, path: FilePath, updates: Dict[str, Any]) -> str:
        """
        Update frontmatter fields in a file while preserving all content.

        Args:
            path: Path to the file (Path or string)
            updates: Dictionary of frontmatter fields to update

        Returns:
            Checksum of updated file
        """
        # Convert string to Path if needed
        path_obj = self.base_path / path if isinstance(path, str) else path
        full_path = path_obj if path_obj.is_absolute() else self.base_path / path_obj
        return await file_utils.update_frontmatter(full_path, updates)

    async def compute_checksum(self, path: FilePath) -> str:
        """Compute checksum for a file.

        Args:
            path: Path to the file (Path or string)

        Returns:
            Checksum of the file content

        Raises:
            FileError: If checksum computation fails
        """
        # Convert string to Path if needed
        path_obj = self.base_path / path if isinstance(path, str) else path
        full_path = path_obj if path_obj.is_absolute() else self.base_path / path_obj

        try:
            if self.is_markdown(path):
                # read str
                content = full_path.read_text(encoding="utf-8")
            else:
                # read bytes
                content = full_path.read_bytes()
            return await file_utils.compute_checksum(content)

        except Exception as e:  # pragma: no cover
            logger.error("Failed to compute checksum", path=str(full_path), error=str(e))
            raise file_utils.FileError(f"Failed to compute checksum for {path}: {e}")

    def file_stats(self, path: FilePath) -> stat_result:
        """Return file stats for a given path.

        Args:
            path: Path to the file (Path or string)

        Returns:
            File statistics
        """
        # Convert string to Path if needed
        path_obj = self.base_path / path if isinstance(path, str) else path
        full_path = path_obj if path_obj.is_absolute() else self.base_path / path_obj
        # get file timestamps
        return full_path.stat()

    def content_type(self, path: FilePath) -> str:
        """Return content_type for a given path.

        Args:
            path: Path to the file (Path or string)

        Returns:
            MIME type of the file
        """
        # Convert string to Path if needed
        path_obj = self.base_path / path if isinstance(path, str) else path
        full_path = path_obj if path_obj.is_absolute() else self.base_path / path_obj
        # get file timestamps
        mime_type, _ = mimetypes.guess_type(full_path.name)

        # .canvas files are json
        if full_path.suffix == ".canvas":
            mime_type = "application/json"

        content_type = mime_type or "text/plain"
        return content_type

    def is_markdown(self, path: FilePath) -> bool:
        """Check if a file is a markdown file.

        Args:
            path: Path to the file (Path or string)

        Returns:
            True if the file is a markdown file, False otherwise
        """
        return self.content_type(path) == "text/markdown"
