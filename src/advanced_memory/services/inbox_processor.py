"""Inbox processor service for handling files dropped into zettelkasten/inbox/

This service monitors the inbox directory, processes dropped files (markdown or documents),
converts them as needed, and triggers sync to add them to the knowledge base.
"""

import asyncio
import shutil
from pathlib import Path
from typing import Any

from loguru import logger

from advanced_memory import db
from advanced_memory.config import ConfigManager
from advanced_memory.repository import ProjectRepository
from advanced_memory.services.document_converter import DocumentConverter

# from advanced_memory.deps import get_sync_service (moved to method to break circularity)


class InboxProcessor:
    """Process files dropped into the zettelkasten inbox"""

    def __init__(self, inbox_dir: Path | None = None, converted_dir: Path | None = None):
        """Initialize inbox processor

        Args:
            inbox_dir: Inbox directory to monitor. Defaults to zettelkasten/inbox/
            converted_dir: Directory to store converted files. Defaults to zettelkasten/converted/
        """
        self.config = ConfigManager().config
        self.inbox_dir = inbox_dir or self._get_inbox_dir()
        self.converted_dir = converted_dir or self._get_converted_dir()
        self.converter = DocumentConverter()

        logger.info("InboxProcessor initialized:")
        logger.info(f"  Inbox: {self.inbox_dir}")
        logger.info(f"  Converted: {self.converted_dir}")

    def _get_inbox_dir(self) -> Path:
        """Get default inbox directory"""
        # Try repo root first
        repo_root = Path(__file__).parent.parent.parent.parent
        inbox = repo_root / "zettelkasten" / "inbox"
        if inbox.exists():
            return inbox

        # Fall back to config project path
        project_path = Path(self.config.get_project_path(self.config.default_project))
        inbox = project_path / "inbox"
        inbox.mkdir(parents=True, exist_ok=True)
        return inbox

    def _get_converted_dir(self) -> Path:
        """Get default converted directory"""
        # Try repo root first
        repo_root = Path(__file__).parent.parent.parent.parent
        converted = repo_root / "zettelkasten" / "converted"
        if converted.exists():
            return converted

        # Fall back to config project path
        project_path = Path(self.config.get_project_path(self.config.default_project))
        converted = project_path / "converted"
        converted.mkdir(parents=True, exist_ok=True)
        return converted

    async def process_file(self, file_path: Path) -> dict[str, Any]:
        """Process a single file from the inbox

        Args:
            file_path: Path to file in inbox

        Returns:
            Processing result with status, output_path, etc.
        """
        logger.info(f"Processing inbox file: {file_path.name}")

        if not file_path.exists():
            return {"status": "error", "message": f"File not found: {file_path}"}

        # Skip hidden files, README, and .gitkeep
        if file_path.name.startswith(".") or file_path.name in ["README.md", ".gitkeep"]:
            logger.debug(f"Skipping system file: {file_path.name}")
            return {"status": "skipped", "message": "System file"}

        try:
            # Determine file type and processing strategy
            suffix = file_path.suffix.lower()

            if suffix == ".md":
                # Markdown: move directly to project
                return await self._process_markdown(file_path)

            elif suffix in [".docx", ".doc"]:
                # Word doc: convert to markdown
                return await self._process_document(file_path, "docx")

            elif suffix == ".html":
                # HTML: convert to markdown
                return await self._process_document(file_path, "html")

            elif suffix == ".pdf":
                # PDF: extract text to markdown
                return await self._process_document(file_path, "pdf")

            elif suffix == ".txt":
                # Plain text: convert to markdown
                return await self._process_text(file_path)

            else:
                logger.warning(f"Unsupported file type: {suffix}")
                return {
                    "status": "unsupported",
                    "message": f"File type {suffix} not supported",
                    "supported_types": [".md", ".docx", ".html", ".pdf", ".txt"],
                }

        except Exception as e:
            logger.error(f"Error processing {file_path.name}: {e}")
            return {"status": "error", "message": str(e), "file": str(file_path)}

    async def _process_markdown(self, file_path: Path) -> dict[str, Any]:
        """Process markdown file - move to project and trigger sync

        Args:
            file_path: Path to markdown file

        Returns:
            Processing result
        """
        logger.info(f"Processing markdown: {file_path.name}")

        # Get target directory (project path)
        project_path = Path(self.config.get_project_path(self.config.default_project))
        target_path = project_path / file_path.name

        # Avoid overwriting existing files
        counter = 1
        while target_path.exists():
            stem = file_path.stem
            target_path = project_path / f"{stem}_{counter}.md"
            counter += 1

        # Move file to project
        shutil.move(str(file_path), str(target_path))
        logger.info(f"Moved {file_path.name} → {target_path}")

        # Trigger sync
        await self._trigger_sync(target_path)

        return {
            "status": "success",
            "action": "moved",
            "source": str(file_path),
            "target": str(target_path),
            "message": "Markdown file moved to project and synced",
        }

    async def _process_document(self, file_path: Path, doc_type: str) -> dict[str, Any]:
        """Convert document to markdown, save to converted/, move to project, sync

        Args:
            file_path: Path to document
            doc_type: Document type (docx, html, pdf)

        Returns:
            Processing result
        """
        logger.info(f"Converting {doc_type.upper()}: {file_path.name}")

        # Convert to markdown
        markdown_content = await self.converter.convert(file_path, doc_type)

        if not markdown_content:
            return {
                "status": "error",
                "message": f"Conversion failed for {file_path.name}",
            }

        # Save converted file
        md_filename = file_path.stem + ".md"
        converted_path = self.converted_dir / md_filename
        converted_path.write_text(markdown_content, encoding="utf-8")

        logger.info(f"Saved converted markdown: {converted_path}")

        # Move original to converted/ (preserve for reference)
        original_backup = self.converted_dir / file_path.name
        counter = 1
        while original_backup.exists():
            original_backup = self.converted_dir / f"{file_path.stem}_{counter}{file_path.suffix}"
            counter += 1

        shutil.move(str(file_path), str(original_backup))

        # Move converted markdown to project
        project_path = Path(self.config.get_project_path(self.config.default_project))
        target_path = project_path / md_filename

        counter = 1
        while target_path.exists():
            target_path = project_path / f"{file_path.stem}_{counter}.md"
            counter += 1

        shutil.copy(str(converted_path), str(target_path))

        # Trigger sync
        await self._trigger_sync(target_path)

        return {
            "status": "success",
            "action": "converted",
            "source": str(file_path),
            "converted": str(converted_path),
            "target": str(target_path),
            "original_backup": str(original_backup),
            "message": f"{doc_type.upper()} converted to markdown and synced",
        }

    async def _process_text(self, file_path: Path) -> dict[str, Any]:
        """Convert plain text to markdown

        Args:
            file_path: Path to text file

        Returns:
            Processing result
        """
        logger.info(f"Processing text file: {file_path.name}")

        # Read content
        content = file_path.read_text(encoding="utf-8")

        # Create simple markdown wrapper
        title = file_path.stem.replace("_", " ").replace("-", " ").title()
        markdown_content = f"# {title}\n\n{content}\n"

        # Save as markdown
        md_filename = file_path.stem + ".md"
        project_path = Path(self.config.get_project_path(self.config.default_project))
        target_path = project_path / md_filename

        counter = 1
        while target_path.exists():
            target_path = project_path / f"{file_path.stem}_{counter}.md"
            counter += 1

        target_path.write_text(markdown_content, encoding="utf-8")

        # Remove original from inbox
        file_path.unlink()

        # Trigger sync
        await self._trigger_sync(target_path)

        return {
            "status": "success",
            "action": "converted",
            "source": str(file_path),
            "target": str(target_path),
            "message": "Text file converted to markdown and synced",
        }

    async def _trigger_sync(self, file_path: Path) -> None:
        """Trigger sync for newly added file

        Args:
            file_path: Absolute path to the moved/converted file
        """
        logger.info(f"Triggering sync for processed file: {file_path.name}")

        try:
            # 1. Get database session
            app_config = ConfigManager().config
            _, session_maker = await db.get_or_create_db(
                db_path=app_config.database_path, db_type=db.DatabaseType.FILESYSTEM
            )

            # 2. Get project from config
            from advanced_memory.config import get_project_config

            project_config = get_project_config()

            async with session_maker() as session:
                project_repo = ProjectRepository(session)
                project = await project_repo.get_by_name(project_config.project)

                if not project:
                    logger.error(f"Project '{project_config.project}' not found during sync trigger")
                    return

                # 3. Initialize SyncService and sync the file
                from advanced_memory.sync.sync_service import get_sync_service

                sync_service = await get_sync_service(project)

                # Calculate relative path for sync_service
                project_base = Path(project.path)
                try:
                    rel_path = file_path.relative_to(project_base)
                    # Normalize for database consistency
                    normalized_path = str(rel_path).replace("\\", "/")

                    logger.info(f"Syncing file: {normalized_path}")
                    await sync_service.sync_file(normalized_path, new=True)

                    # Also resolve relations in case this file links to others or others link to it
                    await sync_service.resolve_relations()

                    logger.info(f"Successfully indexed {file_path.name}")
                except ValueError:
                    logger.error(f"File {file_path} is not within project path {project_base}")

        except Exception as e:
            logger.exception(f"Failed to trigger auto-sync for {file_path.name}: {e}")

    async def process_inbox(self) -> list[dict[str, Any]]:
        """Process all files currently in the inbox

        Returns:
            List of processing results
        """
        logger.info("Processing inbox...")

        if not self.inbox_dir.exists():
            logger.warning(f"Inbox directory does not exist: {self.inbox_dir}")
            return []

        # Get all files in inbox (not subdirectories)
        files = [f for f in self.inbox_dir.iterdir() if f.is_file()]

        if not files:
            logger.info("Inbox is empty")
            return []

        logger.info(f"Found {len(files)} file(s) in inbox")

        # Process each file
        results = []
        for file_path in files:
            result = await self.process_file(file_path)
            results.append(result)

        successful = sum(1 for r in results if r["status"] == "success")
        logger.info(f"Inbox processing complete: {successful}/{len(results)} successful")

        return results

    async def watch_inbox(self) -> None:
        """Watch inbox for new files and process them automatically

        This method runs indefinitely, checking for new files every few seconds.
        Suitable for use in a background task or separate process.
        """
        logger.info("Starting inbox watcher...")

        processed_files = set()

        while True:
            try:
                if not self.inbox_dir.exists():
                    logger.warning(f"Inbox directory missing: {self.inbox_dir}")
                    await asyncio.sleep(5)
                    continue

                # Get current files
                current_files = {f for f in self.inbox_dir.iterdir() if f.is_file()}

                # Find new files (not yet processed)
                new_files = current_files - processed_files

                if new_files:
                    logger.info(f"Detected {len(new_files)} new file(s) in inbox")

                    for file_path in new_files:
                        # Skip if file is still being written (size changing)
                        initial_size = file_path.stat().st_size if file_path.exists() else 0
                        await asyncio.sleep(0.5)

                        if not file_path.exists():
                            continue

                        current_size = file_path.stat().st_size

                        if current_size != initial_size:
                            logger.debug(f"File still being written: {file_path.name}")
                            continue

                        # Process file
                        result = await self.process_file(file_path)

                        if result["status"] in ["success", "skipped"]:
                            processed_files.add(file_path)

                # Clean up processed_files set if files no longer exist
                processed_files = {f for f in processed_files if f.exists()}

                # Wait before next check
                await asyncio.sleep(2)

            except Exception as e:
                logger.error(f"Error in inbox watcher: {e}")
                await asyncio.sleep(5)


# Singleton instance
_inbox_processor: InboxProcessor | None = None


def get_inbox_processor() -> InboxProcessor:
    """Get singleton inbox processor instance

    Returns:
        InboxProcessor instance
    """
    global _inbox_processor
    if _inbox_processor is None:
        _inbox_processor = InboxProcessor()
    return _inbox_processor
