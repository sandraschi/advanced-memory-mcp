"""Service for syncing files between filesystem and database."""

import asyncio
import os
import time
from collections.abc import Sequence
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

from loguru import logger
from sqlalchemy.exc import IntegrityError

from advanced_memory.config import AdvancedMemoryConfig
from advanced_memory.file_utils import has_frontmatter, parse_frontmatter
from advanced_memory.markdown import EntityParser
from advanced_memory.models import Entity
from advanced_memory.repository import EntityRepository, RelationRepository
from advanced_memory.services import EntityService, FileService
from advanced_memory.services.search_service import SearchService
from advanced_memory.services.sync_status_service import SyncStatus, sync_status_tracker


def normalize_file_path(path: str) -> str:
    """Normalize file path for consistent database storage.

    Ensures paths use forward slashes and are properly resolved.
    This helps prevent duplicate path issues due to different path formats.
    """
    # Convert backslashes to forward slashes for consistency
    normalized = path.replace("\\", "/")
    # Remove any duplicate slashes
    while "//" in normalized:
        normalized = normalized.replace("//", "/")
    # Ensure it doesn't start with /
    if normalized.startswith("/"):
        normalized = normalized[1:]
    return normalized


# Common directories to ignore during file scanning and sync
IGNORE_PATTERNS = {
    # Node.js
    "node_modules",
    # Build outputs
    "dist",
    "build",
    "target",
    "out",
    ".next",
    ".nuxt",
    # Python
    "__pycache__",
    ".pytest_cache",
    ".tox",
    "venv",
    ".venv",
    # Other package managers / build tools
    "vendor",
    ".gradle",
    ".cargo",
    "coverage",
    # IDE and editor files
    ".vscode",
    ".idea",
    # OS files
    ".DS_Store",
    "Thumbs.db",
}

# Patterns for archived/obsolete content that should be preserved but not indexed
ARCHIVE_PATTERNS = {
    # Backup folders (timestamped)
    "-backup-",
    ".backup",
    "_backup",
    # Obsolete markers
    ".obsolete",
    "-obsolete",
    "_obsolete",
    # Archive folders
    ".archived",
    "-archived",
    "_archived",
}


@dataclass
class SyncReport:
    """Report of file changes found compared to database state.

    Attributes:
        total: Total number of files in directory being synced
        new: Files that exist on disk but not in database
        modified: Files that exist in both but have different checksums
        deleted: Files that exist in database but not on disk
        moves: Files that have been moved from one location to another
        checksums: Current checksums for files on disk
    """

    # We keep paths as strings in sets/dicts for easier serialization
    new: set[str] = field(default_factory=set)
    modified: set[str] = field(default_factory=set)
    deleted: set[str] = field(default_factory=set)
    moves: dict[str, str] = field(default_factory=dict)  # old_path -> new_path
    checksums: dict[str, str] = field(default_factory=dict)  # path -> checksum

    @property
    def total(self) -> int:
        """Total number of changes."""
        return len(self.new) + len(self.modified) + len(self.deleted) + len(self.moves)


@dataclass
class ScanResult:
    """Result of scanning a directory."""

    # file_path -> checksum
    files: dict[str, str] = field(default_factory=dict)

    # checksum -> file_path
    checksums: dict[str, str] = field(default_factory=dict)

    # file_path -> error message
    errors: dict[str, str] = field(default_factory=dict)


class SyncService:
    """Syncs documents and knowledge files with database."""

    def __init__(
        self,
        app_config: AdvancedMemoryConfig,
        entity_service: EntityService,
        entity_parser: EntityParser,
        entity_repository: EntityRepository,
        relation_repository: RelationRepository,
        search_service: SearchService,
        file_service: FileService,
    ):
        self.app_config = app_config
        self.entity_service = entity_service
        self.entity_parser = entity_parser
        self.entity_repository = entity_repository
        self.relation_repository = relation_repository
        self.search_service = search_service
        self.file_service = file_service

    async def sync(self, directory: Path, project_name: str | None = None) -> SyncReport:
        """Sync all files with database."""

        start_time = time.time()
        logger.info(f"Sync operation started for directory: {directory}")

        # Start tracking sync for this project if project name provided
        if project_name:
            sync_status_tracker.start_project_sync(project_name)

        # initial paths from db to sync
        # path -> checksum
        report = await self.scan(directory)

        # Update progress with file counts
        if project_name:
            sync_status_tracker.update_project_progress(
                project_name=project_name,
                status=SyncStatus.SYNCING,
                message="Processing file changes",
                files_total=report.total,
                files_processed=0,
            )

        # order of sync matters to resolve relations effectively
        logger.info(
            f"Sync changes detected: new_files={len(report.new)}, modified_files={len(report.modified)}, "
            + f"deleted_files={len(report.deleted)}, moved_files={len(report.moves)}"
        )

        files_processed = 0

        # sync moves first
        for old_path, new_path in report.moves.items():
            try:
                # in the case where a file has been deleted and replaced by another file
                # it will show up in the move and modified lists, so handle it in modified
                if new_path in report.modified:
                    report.modified.remove(new_path)
                    logger.debug(
                        f"File marked as moved and modified: old_path={old_path}, new_path={new_path}"
                    )
                else:
                    await self.handle_move(old_path, new_path)
            except Exception as e:  # pragma: no cover
                logger.error(
                    f"Unexpected error moving file {old_path} -> {new_path}: {type(e).__name__}: {e}"
                )
                # Continue with other files

            files_processed += 1
            if project_name:
                sync_status_tracker.update_project_progress(  # pragma: no cover
                    project_name=project_name,
                    status=SyncStatus.SYNCING,
                    message="Processing moves",
                    files_processed=files_processed,
                )

        # deleted next
        for path in report.deleted:
            try:
                await self.handle_delete(path)
            except Exception as e:  # pragma: no cover
                logger.error(f"Unexpected error deleting file {path}: {type(e).__name__}: {e}")
                # Continue with other files
            files_processed += 1
            if project_name:
                sync_status_tracker.update_project_progress(  # pragma: no cover
                    project_name=project_name,
                    status=SyncStatus.SYNCING,
                    message="Processing deletions",
                    files_processed=files_processed,
                )

        # then new and modified
        for path in report.new:
            try:
                entity, checksum = await self.sync_file(path, new=True)
                if entity is None:
                    logger.warning(f"Skipped new file due to errors: {path}")
            except Exception as e:  # pragma: no cover
                logger.error(f"Unexpected error syncing new file {path}: {type(e).__name__}: {e}")
                # Continue with other files
            files_processed += 1
            if project_name:
                sync_status_tracker.update_project_progress(
                    project_name=project_name,
                    status=SyncStatus.SYNCING,
                    message="Processing new files",
                    files_processed=files_processed,
                )

        for path in report.modified:
            try:
                entity, checksum = await self.sync_file(path, new=False)
                if entity is None:
                    logger.warning(f"Skipped modified file due to errors: {path}")
            except Exception as e:  # pragma: no cover
                logger.error(
                    f"Unexpected error syncing modified file {path}: {type(e).__name__}: {e}"
                )
                # Continue with other files
            files_processed += 1
            if project_name:
                sync_status_tracker.update_project_progress(  # pragma: no cover
                    project_name=project_name,
                    status=SyncStatus.SYNCING,
                    message="Processing modified files",
                    files_processed=files_processed,
                )

        await self.resolve_relations()

        # Mark sync as completed
        if project_name:
            sync_status_tracker.complete_project_sync(project_name)

        duration_ms = int((time.time() - start_time) * 1000)
        logger.info(
            f"Sync operation completed: directory={directory}, total_changes={report.total}, duration_ms={duration_ms}"
        )

        return report

    async def scan(self, directory: Path) -> SyncReport:
        """Scan directory for changes compared to database state."""

        db_paths = await self.get_db_file_state()
        logger.info(f"Scanning directory {directory}. Found {len(db_paths)} db paths")

        # Track potentially moved files by checksum
        scan_result = await self.scan_directory(directory)
        report = SyncReport()

        # First find potential new files and record checksums
        # if a path is not present in the db, it could be new or could be the destination of a move
        for file_path, checksum in scan_result.files.items():
            if file_path not in db_paths:
                report.new.add(file_path)
                report.checksums[file_path] = checksum

        # Now detect moves and deletions
        for db_path, db_checksum in db_paths.items():
            local_checksum_for_db_path = scan_result.files.get(db_path)

            # file not modified
            if db_checksum == local_checksum_for_db_path:
                pass

            # if checksums don't match for the same path, its modified
            if local_checksum_for_db_path and db_checksum != local_checksum_for_db_path:
                report.modified.add(db_path)
                report.checksums[db_path] = local_checksum_for_db_path

            # check if it's moved or deleted
            if not local_checksum_for_db_path:
                # if we find the checksum in another file, it's a move
                if db_checksum in scan_result.checksums:
                    new_path = scan_result.checksums[db_checksum]
                    report.moves[db_path] = new_path

                    # Remove from new files if present
                    if new_path in report.new:
                        report.new.remove(new_path)

                # deleted
                else:
                    report.deleted.add(db_path)
        logger.info(f"Completed scan for directory {directory}, found {report.total} changes.")
        return report

    async def get_db_file_state(self) -> dict[str, str]:
        """Get file_path and checksums from database.
        Args:
            db_records: database records
        Returns:
            Dict mapping file paths to FileState
            :param db_records: the data from the db
        """
        db_records: Sequence[Entity] = await self.entity_repository.find_all()
        logger.info(f"Found {len(db_records)} db records")
        return {r.file_path: r.checksum or "" for r in db_records}

    async def sync_file(self, path: str, new: bool = True) -> tuple[Entity | None, str | None]:
        """Sync a single file.

        Args:
            path: Path to file to sync
            new: Whether this is a new file

        Returns:
            Tuple of (entity, checksum) or (None, None) if sync fails
        """
        try:
            logger.debug(
                f"Syncing file path={path} is_new={new} is_markdown={self.file_service.is_markdown(path)}"
            )

            if self.file_service.is_markdown(path):
                entity, checksum = await self.sync_markdown_file(path, new)
            else:
                entity, checksum = await self.sync_regular_file(path, new)

            if entity is not None:
                await self.search_service.index_entity(entity)

                logger.debug(
                    f"File sync completed, path={path}, entity_id={entity.id}, checksum={checksum[:8]}"
                )
            return entity, checksum

        except Exception as e:  # pragma: no cover
            error_msg = str(e)
            error_type = type(e).__name__

            # Provide more specific error messages for common issues
            if "mapping values are not allowed" in error_msg:
                logger.warning(f"Malformed YAML frontmatter in {path}: {error_msg}")
                logger.info(
                    f"File {path} will be skipped due to invalid YAML frontmatter. Fix the YAML syntax to include this file in sync."
                )
            elif "scanning an alias" in error_msg or "alias" in error_msg.lower():
                logger.warning(f"Invalid YAML alias in {path}: {error_msg}")
                logger.info(
                    f"File {path} will be skipped due to malformed YAML aliases. Check for invalid &/* syntax."
                )
            elif "yaml" in error_msg.lower() or "yamlload" in error_type.lower():
                logger.warning(f"YAML parsing error in {path}: {error_msg}")
                logger.info(
                    f"File {path} will be skipped due to YAML syntax error. The file may still be processed with empty frontmatter."
                )
            else:
                logger.error(
                    f"Failed to sync file: path={path}, error_type={error_type}, error={error_msg}"
                )

            # Return None to indicate sync failure, but don't crash the entire process
            return None, None

    async def validate_file_frontmatter(self, path: str) -> tuple[bool, str | None]:
        """Validate YAML frontmatter in a markdown file.

        Args:
            path: Path to the file to validate

        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            if not self.file_service.is_markdown(path):
                return True, None

            absolute_path = self.entity_parser.base_path / path
            if not absolute_path.exists():
                return False, f"File does not exist: {path}"

            # Check file size before reading
            file_size = absolute_path.stat().st_size
            if file_size > 10 * 1024 * 1024:  # 10MB limit
                return False, f"File too large ({file_size / 1024 / 1024:.2f} MB)"

            # Try to read file with encoding error handling
            try:
                content = absolute_path.read_text(encoding="utf-8")
            except UnicodeDecodeError as e:
                return False, f"Invalid UTF-8 encoding: {e}"

            if not has_frontmatter(content):
                return True, None  # No frontmatter to validate

            # Try to parse frontmatter - parse_frontmatter handles YAML errors gracefully
            parse_frontmatter(content)

            # Additional validation could go here (e.g., required fields, data types)

            return True, None

        except Exception as e:
            error_msg = f"Failed to validate frontmatter in {path}: {str(e)}"
            logger.warning(error_msg)
            return False, error_msg

    async def validate_project_files(self, paths: set[str] | None = None) -> dict[str, str]:
        """Validate frontmatter in multiple files.

        Args:
            paths: Specific paths to validate, or None for all project files

        Returns:
            Dict mapping file paths to error messages for invalid files
        """
        invalid_files = {}

        if paths is None:
            # Get all markdown files in project
            all_files = []
            # Get project path from entity parser's base path
            project_path = self.entity_parser.base_path
            for root, dirs, files in os.walk(project_path):
                # Skip ignored directories
                dirs[:] = [d for d in dirs if d not in IGNORE_PATTERNS]

                for file in files:
                    if file.endswith(".md"):
                        rel_path = os.path.relpath(os.path.join(root, file), project_path)
                        rel_path = normalize_file_path(rel_path)
                        all_files.append(rel_path)
            paths = set(all_files)

        for path in paths:
            is_valid, error_msg = await self.validate_file_frontmatter(path)
            if not is_valid and error_msg:
                invalid_files[path] = error_msg

        return invalid_files

    async def sync_markdown_file(self, path: str, new: bool = True) -> tuple[Entity | None, str]:
        """Sync a markdown file with full processing.

        Args:
            path: Path to markdown file
            new: Whether this is a new file

        Returns:
            Tuple of (entity, checksum)
        """
        # Parse markdown first to get any existing permalink
        logger.debug(f"Parsing markdown file, path: {path}, new: {new}")

        file_path = self.entity_parser.base_path / path

        # Run blocking file I/O in thread pool - prevents sync from blocking event loop
        # so API writes can complete without hanging
        def _read_file() -> str:
            try:
                return file_path.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                logger.warning(f"UTF-8 decode failed for {path}, trying with error handling")
                return file_path.read_text(encoding="utf-8", errors="replace")

        def _stat_size() -> int:
            return file_path.stat().st_size

        try:
            file_size = await asyncio.to_thread(_stat_size)
            if file_size > 10 * 1024 * 1024:  # 10MB limit
                logger.warning(f"File too large to sync: {path} ({file_size / 1024 / 1024:.2f} MB)")
                raise ValueError(f"File exceeds 10MB limit: {path}")
        except OSError as e:
            logger.error(f"Cannot access file: {path}, error: {e}")
            raise

        try:
            file_content = await asyncio.to_thread(_read_file)
        except Exception as e:
            logger.error(f"Cannot read file {path}: {e}")
            raise ValueError(f"File is unreadable: {path}") from e

        file_contains_frontmatter = has_frontmatter(file_content)

        # entity markdown will always contain front matter, so it can be used up create/update the entity
        # Wrap parser in try/except to handle corrupt markdown
        try:
            entity_markdown = await self.entity_parser.parse_file(path)
        except Exception as e:
            logger.error(f"Failed to parse markdown file {path}: {type(e).__name__}: {e}")
            raise ValueError(f"Markdown parsing failed for {path}: {e}") from e

        # if the file contains frontmatter, resolve a permalink
        if file_contains_frontmatter:
            # Resolve permalink - this handles all the cases including conflicts
            permalink = await self.entity_service.resolve_permalink(path, markdown=entity_markdown)

            # If permalink changed, update the file
            if permalink != entity_markdown.frontmatter.permalink:
                logger.info(
                    f"Updating permalink for path: {path}, old_permalink: {entity_markdown.frontmatter.permalink}, new_permalink: {permalink}"
                )

                entity_markdown.frontmatter.metadata["permalink"] = permalink
                await self.file_service.update_frontmatter(path, {"permalink": permalink})

        # if the file is new, create an entity
        if new:
            # Create entity with final permalink
            logger.debug(f"Creating new entity from markdown, path={path}")
            await self.entity_service.create_entity_from_markdown(Path(path), entity_markdown)

        # otherwise we need to update the entity and observations
        else:
            logger.debug(f"Updating entity from markdown, path={path}")
            await self.entity_service.update_entity_and_observations(Path(path), entity_markdown)

        # Update relations and search index
        entity = await self.entity_service.update_entity_relations(path, entity_markdown)

        # After updating relations, we need to compute the checksum again
        # This is necessary for files with wikilinks to ensure consistent checksums
        # after relation processing is complete
        final_checksum = await self.file_service.compute_checksum(path)

        # set checksum
        await self.entity_repository.update(entity.id, {"checksum": final_checksum})

        logger.debug(
            f"Markdown sync completed: path={path}, entity_id={entity.id}, "
            f"observation_count={len(entity.observations)}, relation_count={len(entity.relations)}, "
            f"checksum={final_checksum[:8]}"
        )

        # Return the final checksum to ensure everything is consistent
        return entity, final_checksum

    async def sync_regular_file(self, path: str, new: bool = True) -> tuple[Entity | None, str]:
        """Sync a non-markdown file with basic tracking.

        Args:
            path: Path to file
            new: Whether this is a new file

        Returns:
            Tuple of (entity, checksum)
        """
        checksum = await self.file_service.compute_checksum(path)
        if new:
            # Generate permalink from path
            await self.entity_service.resolve_permalink(path)

            # get file timestamps
            file_stats = self.file_service.file_stats(path)
            created = datetime.fromtimestamp(file_stats.st_ctime)
            modified = datetime.fromtimestamp(file_stats.st_mtime)

            # get mime type
            content_type = self.file_service.content_type(path)

            file_path = Path(path)
            normalized_path = normalize_file_path(path)
            try:
                entity = await self.entity_repository.add(
                    Entity(
                        entity_type="file",
                        file_path=normalized_path,
                        checksum=checksum,
                        title=file_path.name,
                        created_at=created,
                        updated_at=modified,
                        content_type=content_type,
                    )
                )
                return entity, checksum
            except IntegrityError as e:
                # Handle race condition where entity was created by another process
                if "UNIQUE constraint failed: entity.file_path" in str(e):
                    logger.info(
                        f"Entity already exists for file_path={path}, updating instead of creating"
                    )
                    # Treat as update instead of create
                    entity = await self.entity_repository.get_by_file_path(path)
                    if entity is None:  # pragma: no cover
                        logger.error(f"Entity not found after constraint violation, path={path}")
                        raise ValueError(
                            f"Entity not found after constraint violation: {path}"
                        ) from e

                    updated = await self.entity_repository.update(
                        entity.id, {"file_path": path, "checksum": checksum}
                    )

                    if updated is None:  # pragma: no cover
                        logger.error(f"Failed to update entity, entity_id={entity.id}, path={path}")
                        raise ValueError(f"Failed to update entity with ID {entity.id}") from e

                    return updated, checksum
                else:
                    # Re-raise if it's a different integrity error
                    raise
        else:
            entity: Entity | None = await self.entity_repository.get_by_file_path(path)
            if entity is None:  # pragma: no cover
                logger.error(f"Entity not found for existing file, path={path}")
                raise ValueError(f"Entity not found for existing file: {path}")

            normalized_path = normalize_file_path(path)
            try:
                updated = await self.entity_repository.update(
                    entity.id, {"file_path": normalized_path, "checksum": checksum}
                )

                if updated is None:  # pragma: no cover
                    logger.error(f"Failed to update entity, entity_id={entity.id}, path={path}")
                    raise ValueError(f"Failed to update entity with ID {entity.id}")
            except IntegrityError as e:
                if "UNIQUE constraint failed: entity.file_path" in str(e):
                    logger.warning(
                        f"File path conflict during update: {path} already exists. "
                        f"This may indicate duplicate files or path normalization issues. "
                        f"Entity ID: {entity.id}"
                    )
                    # Try to find the conflicting entity and log details
                    conflicting_entity = await self.entity_repository.get_by_file_path(path)
                    if conflicting_entity:
                        logger.warning(
                            f"Conflicting entity: ID={conflicting_entity.id}, "
                            f"type={conflicting_entity.entity_type}, "
                            f"project={conflicting_entity.project_id}"
                        )
                    # Don't raise - let the sync continue but log the issue
                    return entity, checksum
                else:
                    raise

            return updated, checksum

    async def handle_delete(self, file_path: str) -> None:
        """Handle complete entity deletion including search index cleanup."""

        # First get entity to get permalink before deletion
        entity = await self.entity_repository.get_by_file_path(file_path)
        if entity:
            logger.info(
                f"Deleting entity with file_path={file_path}, entity_id={entity.id}, permalink={entity.permalink}"
            )

            # Delete from db (this cascades to observations/relations)
            await self.entity_service.delete_entity_by_file_path(file_path)

            # Clean up search index
            permalinks = (
                [entity.permalink]
                + [o.permalink for o in entity.observations]
                + [r.permalink for r in entity.relations]
            )

            logger.debug(
                f"Cleaning up search index for entity_id={entity.id}, file_path={file_path}, "
                f"index_entries={len(permalinks)}"
            )

            for permalink in permalinks:
                if permalink:
                    await self.search_service.delete_by_permalink(permalink)
                else:
                    await self.search_service.delete_by_entity_id(entity.id)

    async def handle_move(self, old_path: str, new_path: str) -> None:
        logger.debug("Moving entity", old_path=old_path, new_path=new_path)

        entity = await self.entity_repository.get_by_file_path(old_path)
        if entity:
            # Update file_path in all cases (normalized)
            normalized_new_path = normalize_file_path(new_path)
            updates = {"file_path": normalized_new_path}

            # If configured, also update permalink to match new path
            if self.app_config.update_permalinks_on_move and self.file_service.is_markdown(
                normalized_new_path
            ):
                # generate new permalink value
                new_permalink = await self.entity_service.resolve_permalink(normalized_new_path)

                # write to file and get new checksum
                new_checksum = await self.file_service.update_frontmatter(
                    new_path, {"permalink": new_permalink}
                )

                updates["permalink"] = new_permalink
                updates["checksum"] = new_checksum

                logger.info(
                    f"Updating permalink on move,old_permalink={entity.permalink}"
                    f"new_permalink={new_permalink}"
                    f"new_checksum={new_checksum}"
                )

            try:
                updated = await self.entity_repository.update(entity.id, updates)

                if updated is None:  # pragma: no cover
                    logger.error(
                        "Failed to update entity path"
                        f"entity_id={entity.id}"
                        f"old_path={old_path}"
                        f"new_path={new_path}"
                    )
                    raise ValueError(f"Failed to update entity path for ID {entity.id}")
            except IntegrityError as e:
                if "UNIQUE constraint failed: entity.file_path" in str(e):
                    logger.warning(
                        f"File path conflict during move: {new_path} already exists. "
                        f"Cannot move {old_path} to {new_path}. "
                        f"Entity ID: {entity.id}"
                    )
                    # Don't update the entity - leave it as-is
                    return
                else:
                    raise

            logger.debug(
                "Entity path updated"
                f"entity_id={entity.id} "
                f"permalink={entity.permalink} "
                f"old_path={old_path} "
                f"new_path={new_path} "
            )

            # update search index
            await self.search_service.index_entity(updated)

    async def resolve_relations(self) -> None:
        """Try to resolve any unresolved relations"""

        unresolved_relations = await self.relation_repository.find_unresolved_relations()

        logger.info("Resolving forward references", count=len(unresolved_relations))

        for relation in unresolved_relations:
            logger.trace(
                "Attempting to resolve relation "
                f"relation_id={relation.id} "
                f"from_id={relation.from_id} "
                f"to_name={relation.to_name}"
            )

            resolved_entity = await self.entity_service.link_resolver.resolve_link(relation.to_name)

            # ignore reference to self
            if resolved_entity and resolved_entity.id != relation.from_id:
                logger.debug(
                    "Resolved forward reference "
                    f"relation_id={relation.id} "
                    f"from_id={relation.from_id} "
                    f"to_name={relation.to_name} "
                    f"resolved_id={resolved_entity.id} "
                    f"resolved_title={resolved_entity.title}",
                )
                try:
                    await self.relation_repository.update(
                        relation.id,
                        {
                            "to_id": resolved_entity.id,
                            "to_name": resolved_entity.title,
                        },
                    )
                except IntegrityError:  # pragma: no cover
                    logger.debug(
                        "Ignoring duplicate relation "
                        f"relation_id={relation.id} "
                        f"from_id={relation.from_id} "
                        f"to_name={relation.to_name}"
                    )

                # update search index
                await self.search_service.index_entity(resolved_entity)

    async def scan_directory(self, directory: Path) -> ScanResult:
        """
        Scan directory for markdown files and their checksums.

        Args:
            directory: Directory to scan

        Returns:
            ScanResult containing found files and any errors
        """
        start_time = time.time()

        logger.debug(f"Scanning directory {directory}")
        result = ScanResult()

        skipped_folders = set()

        for root, dirnames, filenames in os.walk(str(directory)):
            # Track which directories are being skipped
            original_dirnames = dirnames.copy()

            # Skip dot directories, ignore patterns, and archive patterns in-place
            dirnames[:] = [
                d
                for d in dirnames
                if not d.startswith(".")
                and d not in IGNORE_PATTERNS
                and not any(pattern in d.lower() for pattern in ARCHIVE_PATTERNS)
            ]

            # Log skipped directories for debugging
            for d in original_dirnames:
                if d not in dirnames:
                    skipped_folders.add(d)
                    logger.debug(f"Skipping ignored directory: {d}")

            for filename in filenames:
                # Skip dot files and files in ignore patterns
                if filename.startswith(".") or filename in IGNORE_PATTERNS:
                    logger.trace(f"Skipping ignored file: {filename}")
                    continue

                # If index_all_files is False, only index markdown files
                if not self.app_config.index_all_files and not filename.endswith(".md"):
                    logger.trace(f"Skipping non-markdown file (index_all_files=False): {filename}")
                    continue

                path = Path(root) / filename
                rel_path = str(path.relative_to(directory))
                checksum = await self.file_service.compute_checksum(rel_path)
                result.files[rel_path] = checksum
                result.checksums[checksum] = rel_path

                logger.trace(f"Found file, path={rel_path}, checksum={checksum}")

        duration_ms = int((time.time() - start_time) * 1000)

        if len(result.files) == 0:
            logger.warning(
                f"No files found in {directory}. "
                f"Skipped {len(skipped_folders)} folders. "
                f"Ensure files are not in ignored folders: {IGNORE_PATTERNS}"
            )

        logger.debug(
            f"{directory} scan completed "
            f"directory={str(directory)} "
            f"files_found={len(result.files)} "
            f"duration_ms={duration_ms}"
        )

        return result
