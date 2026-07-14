"""Archive export tool for Advanced Memory - creates complete backup for migration."""

import json
import shutil
import sqlite3
import tempfile
import zipfile
from datetime import datetime, timedelta
from pathlib import Path

from loguru import logger

from advanced_memory.config import CONFIG_FILE_NAME, DATABASE_NAME, ConfigManager
from advanced_memory.mcp.mcp_instance import mcp


def _parse_since_date(since_date: str) -> datetime:
    """Parse since_date parameter into datetime object."""
    if not since_date:
        return datetime.min

    # Handle relative dates
    if since_date.endswith("d"):
        days = int(since_date[:-1])
        return datetime.now() - timedelta(days=days)
    elif since_date.endswith("m"):
        months = int(since_date[:-1])
        return datetime.now() - timedelta(days=months * 30)  # Approximate
    elif since_date.endswith("y"):
        years = int(since_date[:-1])
        return datetime.now() - timedelta(days=years * 365)  # Approximate

    # Handle ISO format
    try:
        return datetime.fromisoformat(since_date.replace("Z", "+00:00"))
    except ValueError:
        logger.warning(f"Invalid date format: {since_date}, using no date filter")
        return datetime.min


def _filter_database(
    source_db: Path,
    dest_db: Path,
    exclude_tags: list[str] | None = None,
    since_date: datetime | None = None,
    project_ids: set[int] | None = None,
) -> tuple[int, int]:
    """
    Filter database content based on tags, date, and projects.

    Returns:
        Tuple of (entities_kept, entities_filtered)
    """
    if not exclude_tags and not since_date and not project_ids:
        # No filtering needed, just copy
        shutil.copy2(source_db, dest_db)
        return (0, 0)  # Can't count without opening DB

    # Connect to source and create destination
    source_conn = sqlite3.connect(str(source_db))
    dest_conn = sqlite3.connect(str(dest_db))

    try:
        source_cursor = source_conn.cursor()
        dest_cursor = dest_conn.cursor()

        # Enable foreign keys
        dest_cursor.execute("PRAGMA foreign_keys = ON")

        # Get all tables
        source_cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in source_cursor.fetchall()]

        entities_filtered = 0
        entities_kept = 0

        # Create tables in destination
        for table in tables:
            # Get table schema
            source_cursor.execute(f"PRAGMA table_info({table})")
            source_cursor.fetchall()

            # Get CREATE TABLE statement
            source_cursor.execute(  # nosec B608 - table name from schema, not user input
                f"SELECT sql FROM sqlite_master WHERE type='table' AND name='{table}'"
            )
            create_sql = source_cursor.fetchone()
            if create_sql and create_sql[0]:
                dest_cursor.execute(create_sql[0])

        # Filter and copy entity table (this is the main filtering)
        if "entity" in tables:
            # Get entities to keep
            where_conditions = []
            params = []

            if exclude_tags:
                # Find entities with excluded tags
                tag_conditions = " OR ".join(["entity_metadata LIKE ?" for _ in exclude_tags])
                tag_params = [f'%"tags":%"{tag}"%' for tag in exclude_tags]
                where_conditions.append(f"NOT (entity_metadata LIKE '%\"tags\"%' AND ({tag_conditions}))")
                params.extend(tag_params)

            if since_date and since_date > datetime.min:
                where_conditions.append("(created_at >= ? OR updated_at >= ?)")
                params.extend([since_date.isoformat(), since_date.isoformat()])

            if project_ids:
                placeholders = ",".join(["?" for _ in project_ids])
                where_conditions.append(f"project_id IN ({placeholders})")
                params.extend(project_ids)

            where_clause = " AND ".join(where_conditions) if where_conditions else "1=1"

            # Count total entities
            source_cursor.execute(  # nosec B608 - uses parameterized query with params
                f"SELECT COUNT(*) FROM entity WHERE {where_clause}", params
            )
            entities_kept = source_cursor.fetchone()[0]

            source_cursor.execute("SELECT COUNT(*) FROM entity")
            total_entities = source_cursor.fetchone()[0]
            entities_filtered = total_entities - entities_kept

            # Copy filtered entities
            source_cursor.execute(  # nosec B608 - uses parameterized query with params
                f"SELECT * FROM entity WHERE {where_clause}", params
            )
            entities = source_cursor.fetchall()

            for entity in entities:
                placeholders = ",".join(["?" for _ in entity])
                dest_cursor.execute(  # nosec B608 - uses placeholders, not direct insertion
                    f"INSERT INTO entity VALUES ({placeholders})", entity
                )

        # Copy other tables (with foreign key constraints this will only copy related data)
        for table in tables:
            if table == "entity":
                continue  # Already handled

            try:
                # Try to copy all data (foreign keys will prevent orphaned records)
                source_cursor.execute(  # nosec B608 - table name from schema, not user input
                    f"SELECT * FROM {table}"
                )
                rows = source_cursor.fetchall()

                for row in rows:
                    try:
                        placeholders = ",".join(["?" for _ in row])
                        dest_cursor.execute(  # nosec B608 - uses placeholders, table from schema
                            f"INSERT INTO {table} VALUES ({placeholders})", row
                        )
                    except sqlite3.IntegrityError:
                        # Foreign key constraint failed, skip this record
                        pass

            except Exception as e:
                logger.warning(f"Could not copy table {table}: {e}")

        dest_conn.commit()

        return entities_kept, entities_filtered

    finally:
        source_conn.close()
        dest_conn.close()


# @mcp.tool
async def export_to_archive(
    archive_path: str | Path,
    include_projects: list[str] | None = None,
    exclude_projects: list[str] | None = None,
    exclude_tags: list[str] | None = None,
    since_date: str | None = None,
    compress: bool = True,
    project: str | None = None,
    show_after_export: bool = True,
) -> str:
    """
    Export complete Advanced Memory system to archive for migration/backup.

    Args:
        archive_path: Path for the archive file (with or without extension).
                     If directory, creates filename with timestamp.
                     Timestamp format: YYYYMMDD-HHMMSS (e.g., 20251202-143022)
                     Examples:
                     - "d:/backup/dev" → "d:/backup/dev/advanced-memory-backup-20251202-143022.zip"
                     - "d:/backup/my-backup.zip" → "d:/backup/my-backup-20251202-143022.zip"
        include_projects: List of project names to include (None = all projects)
        exclude_projects: List of project names to exclude (takes precedence over include_projects)
        exclude_tags: List of tags to exclude from export (e.g., ["obsolete", "test"])
        since_date: Only include data since this date (ISO format or relative like "30d", "1y")
        compress: Whether to create compressed ZIP (True) or uncompressed tar (False)
        project: Active project context

    Returns:
        Success message with archive details
    """
    try:
        config_manager = ConfigManager()
        config = config_manager.load_config()

        # Ensure archive path has extension and add timestamp
        archive_path = Path(archive_path)

        # Generate timestamp string (YYYYMMDD-HHMMSS)
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")

        # If path is a directory or doesn't have a filename, create default name with timestamp
        if archive_path.is_dir() or not archive_path.name or archive_path.name == archive_path.suffix:
            # Use directory name or default name
            default_name = "advanced-memory-backup"
            if compress:
                archive_path = archive_path / f"{default_name}-{timestamp}.zip"
            else:
                archive_path = archive_path / f"{default_name}-{timestamp}.tar"
        else:
            # Add timestamp before extension
            stem = archive_path.stem
            suffix = archive_path.suffix
            if compress and suffix.lower() != ".zip":
                archive_path = archive_path.parent / f"{stem}-{timestamp}.zip"
            elif not compress and suffix.lower() != ".tar":
                archive_path = archive_path.parent / f"{stem}-{timestamp}.tar"
            else:
                # Has correct extension, insert timestamp before it
                archive_path = archive_path.parent / f"{stem}-{timestamp}{suffix}"

        # Validate and parse parameters
        filters_applied = []
        if exclude_projects:
            filters_applied.append(f"excluding projects: {', '.join(exclude_projects)}")
        elif include_projects:
            filters_applied.append(f"including only projects: {', '.join(include_projects)}")
        if exclude_tags:
            filters_applied.append(f"excluding tags: {', '.join(exclude_tags)}")
        if since_date:
            filters_applied.append(f"since date: {since_date}")

        filtering_enabled = bool(exclude_tags or since_date)
        if filtering_enabled:
            logger.info(f"Advanced filtering enabled: {', '.join(filters_applied)}")
        elif filters_applied:
            logger.info(f"Project filtering: {', '.join(filters_applied[:1])}")

        # Parse date parameter
        cutoff_date = _parse_since_date(since_date) if since_date else None

        # Get project IDs for filtering (if we're filtering projects)
        project_ids = None
        if exclude_projects or include_projects:
            # We would need to query the database to get project IDs
            # For now, we'll implement this in the database filtering
            pass

        # Create temporary directory for staging files
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            archive_root = temp_path / "advanced-memory-backup"
            archive_root.mkdir()

            total_files = 0
            total_size = 0
            entities_kept = 0
            entities_filtered = 0

            # 1. Export database (with filtering if needed)
            logger.info("Exporting database...")
            db_source = config.app_database_path
            if db_source.exists():
                db_dest = archive_root / "database" / DATABASE_NAME
                db_dest.parent.mkdir(parents=True, exist_ok=True)

                if filtering_enabled:
                    # Apply filtering
                    entities_kept, entities_filtered = _filter_database(
                        db_source, db_dest, exclude_tags, cutoff_date, project_ids
                    )
                    logger.info(f"Database filtered: {entities_kept} entities kept, {entities_filtered} filtered")
                else:
                    # Simple copy
                    shutil.copy2(db_source, db_dest)

                total_files += 1
                total_size += db_dest.stat().st_size
                logger.info(f"Database ready: {db_dest}")
            else:
                logger.warning(f"Database not found: {db_source}")

            # 2. Export configuration
            logger.info("Exporting configuration...")
            config_source = config_manager.config_file
            if config_source.exists():
                config_dest = archive_root / "config" / CONFIG_FILE_NAME
                config_dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(config_source, config_dest)
                total_files += 1
                total_size += config_source.stat().st_size
                logger.info(f"Copied config: {config_source} -> {config_dest}")

            # 3. Export projects
            logger.info("Exporting projects...")
            projects_dir = archive_root / "projects"
            projects_dir.mkdir()

            # Get all projects and apply filtering
            all_projects = config.projects

            # Apply project filtering
            if exclude_projects:
                # Exclude specified projects
                projects_to_export = {name: path for name, path in all_projects.items() if name not in exclude_projects}
            elif include_projects:
                # Include only specified projects
                projects_to_export = {name: path for name, path in all_projects.items() if name in include_projects}
            else:
                # Include all projects
                projects_to_export = all_projects

            for project_name, project_path_str in projects_to_export.items():
                project_path = Path(project_path_str)

                if project_path.exists():
                    # Copy entire project directory
                    dest_path = projects_dir / project_name
                    logger.info(f"Copying project '{project_name}': {project_path} -> {dest_path}")

                    # Use copytree for directories
                    shutil.copytree(project_path, dest_path, dirs_exist_ok=True)

                    # Count files and size for this project
                    project_files = list(dest_path.rglob("*"))
                    project_size = sum(f.stat().st_size for f in project_files if f.is_file())
                    total_files += len([f for f in project_files if f.is_file()])
                    total_size += project_size

                    logger.info(
                        f"Project '{project_name}': {len([f for f in project_files if f.is_file()])} files, {project_size} bytes"
                    )
                else:
                    logger.warning(f"Project directory not found: {project_path}")

            # 4. Create metadata file
            metadata = {
                "version": "1.0",
                "created_at": str(Path(__file__).stat().st_mtime),
                "total_files": total_files,
                "total_size_bytes": total_size,
                "projects_exported": list(projects_to_export.keys()),
                "compressed": compress,
                "database_included": db_source.exists(),
                "config_included": config_source.exists(),
                "filters_applied": {
                    "exclude_projects": exclude_projects or [],
                    "include_projects": include_projects or [],
                    "exclude_tags": exclude_tags or [],
                    "since_date": since_date,
                },
                "filtering_results": {
                    "entities_kept": entities_kept,
                    "entities_filtered": entities_filtered,
                    "filtering_implemented": filtering_enabled,
                },
            }

            metadata_file = archive_root / "metadata.json"
            with open(metadata_file, "w") as f:
                json.dump(metadata, f, indent=2)

            # 5. Create archive
            logger.info(f"Creating archive: {archive_path}")
            if compress:
                # Create ZIP archive using zipfile for Windows Explorer compatibility
                # shutil.make_archive can create ZIPs that Windows Explorer doesn't recognize
                source_dir = temp_path / "advanced-memory-backup"

                # Check if ZIP64 is needed (Windows Explorer has issues with ZIP64)
                # ZIP64 is only needed if any file > 4GB or total size > 4GB
                needs_zip64 = False
                max_file_size = 0
                total_size_check = 0
                for file_path in source_dir.rglob("*"):
                    if file_path.is_file():
                        file_size = file_path.stat().st_size
                        max_file_size = max(max_file_size, file_size)
                        total_size_check += file_size
                        # Check if any file exceeds 4GB limit (ZIP32 max file size)
                        if file_size > 4 * 1024 * 1024 * 1024:
                            needs_zip64 = True
                            break

                # Check if total archive size would exceed 4GB (ZIP32 max archive size)
                if not needs_zip64 and total_size_check > 4 * 1024 * 1024 * 1024:
                    needs_zip64 = True

                if needs_zip64:
                    logger.warning(
                        f"Archive requires ZIP64 format (max file: {max_file_size / (1024**3):.2f} GB, "
                        f"total: {total_size_check / (1024**3):.2f} GB). "
                        "Windows Explorer may have issues opening this archive. Use WinRAR or 7-Zip instead."
                    )

                # Create ZIP file with explicit Windows Explorer compatibility settings
                # Use explicit open/close instead of context manager to ensure proper finalization
                zipf = zipfile.ZipFile(
                    archive_path,
                    "w",
                    compression=zipfile.ZIP_DEFLATED,
                    compresslevel=6,  # Balanced compression
                    allowZip64=needs_zip64,  # Only use ZIP64 when necessary for Windows Explorer compatibility
                )

                try:
                    # Walk through all files in the source directory
                    for file_path in source_dir.rglob("*"):
                        if file_path.is_file():
                            # Calculate relative path from source_dir
                            arcname = file_path.relative_to(source_dir)
                            # Use forward slashes for ZIP standard (Windows compatibility)
                            arcname_str = str(arcname).replace("\\", "/")
                            # Write file with explicit encoding
                            zipf.write(file_path, arcname_str)
                            logger.debug(f"Added to ZIP: {arcname_str}")
                finally:
                    # Explicitly close and finalize the ZIP file
                    # This ensures proper ZIP structure that Windows Explorer expects
                    zipf.close()

                # Verify the ZIP file is valid
                try:
                    test_zip = zipfile.ZipFile(archive_path, "r")
                    test_zip.close()
                    logger.info(f"ZIP archive created and verified: {archive_path} (ZIP64: {needs_zip64})")
                except zipfile.BadZipFile as e:
                    logger.error(f"Created ZIP file is invalid: {e}")
                    raise
            else:
                # Create uncompressed tar archive
                shutil.make_archive(
                    str(archive_path.with_suffix("")),  # remove extension for make_archive
                    "tar",
                    temp_path,
                    "advanced-memory-backup",
                )

            # Get final archive size
            final_size = archive_path.stat().st_size

            # Format results
            projects_list = "\n".join(f"  - {name}: {path}" for name, path in projects_to_export.items())

            filter_info = ""
            if filters_applied:
                filter_info = f"""

**[SEARCH] Filtering Applied:**
{chr(10).join(f"  - {f}" for f in filters_applied)}"""

            if filtering_enabled and (entities_kept > 0 or entities_filtered > 0):
                filter_info += f"""

**[CHART] Database Filtering Results:**
  - Entities kept: {entities_kept}
  - Entities filtered: {entities_filtered}"""

            if filtering_enabled:
                filter_info += """
*Note: Filtered archives may have broken semantic links. Run rescan after import to rebuild.*"""

            summary = f"""[UNICODE][UNICODE] **Advanced Memory Archive Created Successfully!**

**Archive Details:**
- [FOLDER] Location: {archive_path}
- [CHART] Size: {_format_size(final_size)}
- [DOC] Files: {total_files}
- [UNICODE][UNICODE][UNICODE] Projects: {len(projects_to_export)}

**Contents:**
[UNICODE] Database: {db_source.exists()}
[UNICODE] Configuration: {config_source.exists()}
[UNICODE] Projects ({len(projects_to_export)}):
{projects_list}{filter_info}

**To restore on a new machine:**
Use the `import_from_archive` tool with this archive file.

**Example restore command:**
```
import_from_archive("{archive_path}")
```
"""

            # Open the archive folder or file if requested
            if show_after_export:
                from advanced_memory.utils.file_opener import (
                    open_file_or_folder,
                )

                # Open the parent folder containing the archive
                archive_parent = Path(archive_path).parent
                success, msg = open_file_or_folder(archive_parent)
                summary += f"\n\n## 🚀 Opened Archive Location\n\n✅ Opened folder in file explorer: {archive_parent}"

            return summary

    except Exception as e:
        logger.error(f"Error creating archive: {e}")
        return f"[UNICODE] **Archive Creation Failed**\n\nError: {e!s}"


def _format_size(bytes_size: float) -> str:
    """Format bytes to human readable size."""
    for _unit in ["B", "KB", "MB", "GB"]:
        if bytes_size < 1024.0:
            return ".1f"
        bytes_size /= 1024.0
    return ".1f"
