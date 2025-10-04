"""Command module for basic-memory sync operations."""

import asyncio
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import List, Dict

import typer
from loguru import logger
from rich.console import Console
from rich.tree import Tree

from basic_memory import db
from advanced_memory.cli.app import app
from advanced_memory.config import ConfigManager, get_project_config
from advanced_memory.markdown import EntityParser
from advanced_memory.markdown.markdown_processor import MarkdownProcessor
from advanced_memory.models import Project
from advanced_memory.repository import (
    EntityRepository,
    ObservationRepository,
    RelationRepository,
    ProjectRepository,
)
from advanced_memory.repository.search_repository import SearchRepository
from advanced_memory.services import EntityService, FileService
from advanced_memory.services.link_resolver import LinkResolver
from advanced_memory.services.search_service import SearchService
from advanced_memory.sync import SyncService
from advanced_memory.sync.sync_service import SyncReport

console = Console()


@dataclass
class ValidationIssue:
    file_path: str
    error: str


async def get_sync_service(project: Project) -> SyncService:  # pragma: no cover
    """Get sync service instance with all dependencies."""

    app_config = ConfigManager().config
    _, session_maker = await db.get_or_create_db(
        db_path=app_config.database_path, db_type=db.DatabaseType.FILESYSTEM
    )

    project_path = Path(project.path)
    entity_parser = EntityParser(project_path)
    markdown_processor = MarkdownProcessor(entity_parser)
    file_service = FileService(project_path, markdown_processor)

    # Initialize repositories
    entity_repository = EntityRepository(session_maker, project_id=project.id)
    observation_repository = ObservationRepository(session_maker, project_id=project.id)
    relation_repository = RelationRepository(session_maker, project_id=project.id)
    search_repository = SearchRepository(session_maker, project_id=project.id)

    # Initialize services
    search_service = SearchService(search_repository, entity_repository, file_service)
    link_resolver = LinkResolver(entity_repository, search_service)

    # Initialize services
    entity_service = EntityService(
        entity_parser,
        entity_repository,
        observation_repository,
        relation_repository,
        file_service,
        link_resolver,
    )

    # Create sync service
    sync_service = SyncService(
        app_config=app_config,
        entity_service=entity_service,
        entity_parser=entity_parser,
        entity_repository=entity_repository,
        relation_repository=relation_repository,
        search_service=search_service,
        file_service=file_service,
    )

    return sync_service


def group_issues_by_directory(issues: List[ValidationIssue]) -> Dict[str, List[ValidationIssue]]:
    """Group validation issues by directory."""
    grouped = defaultdict(list)
    for issue in issues:
        dir_name = Path(issue.file_path).parent.name
        grouped[dir_name].append(issue)
    return dict(grouped)


def display_sync_summary(knowledge: SyncReport):
    """Display a one-line summary of sync changes."""
    config = get_project_config()
    total_changes = knowledge.total
    project_name = config.project

    if total_changes == 0:
        console.print(f"[green]Project '{project_name}': Everything up to date[/green]")
        return

    # Format as: "Synced X files (A new, B modified, C moved, D deleted)"
    changes = []
    new_count = len(knowledge.new)
    mod_count = len(knowledge.modified)
    move_count = len(knowledge.moves)
    del_count = len(knowledge.deleted)

    if new_count:
        changes.append(f"[green]{new_count} new[/green]")
    if mod_count:
        changes.append(f"[yellow]{mod_count} modified[/yellow]")
    if move_count:
        changes.append(f"[blue]{move_count} moved[/blue]")
    if del_count:
        changes.append(f"[red]{del_count} deleted[/red]")

    console.print(f"Project '{project_name}': Synced {total_changes} files ({', '.join(changes)})")


def display_detailed_sync_results(knowledge: SyncReport):
    """Display detailed sync results with trees."""
    config = get_project_config()
    project_name = config.project

    if knowledge.total == 0:
        console.print(f"\n[green]Project '{project_name}': Everything up to date[/green]")
        return

    console.print(f"\n[bold]Sync Results for Project '{project_name}'[/bold]")

    if knowledge.total > 0:
        knowledge_tree = Tree("[bold]Knowledge Files[/bold]")
        if knowledge.new:
            created = knowledge_tree.add("[green]Created[/green]")
            for path in sorted(knowledge.new):
                checksum = knowledge.checksums.get(path, "")
                created.add(f"[green]{path}[/green] ({checksum[:8]})")
        if knowledge.modified:
            modified = knowledge_tree.add("[yellow]Modified[/yellow]")
            for path in sorted(knowledge.modified):
                checksum = knowledge.checksums.get(path, "")
                modified.add(f"[yellow]{path}[/yellow] ({checksum[:8]})")
        if knowledge.moves:
            moved = knowledge_tree.add("[blue]Moved[/blue]")
            for old_path, new_path in sorted(knowledge.moves.items()):
                checksum = knowledge.checksums.get(new_path, "")
                moved.add(f"[blue]{old_path}[/blue] → [blue]{new_path}[/blue] ({checksum[:8]})")
        if knowledge.deleted:
            deleted = knowledge_tree.add("[red]Deleted[/red]")
            for path in sorted(knowledge.deleted):
                deleted.add(f"[red]{path}[/red]")
        console.print(knowledge_tree)


async def run_sync(verbose: bool = False):
    """Run sync operation."""
    app_config = ConfigManager().config
    config = get_project_config()

    _, session_maker = await db.get_or_create_db(
        db_path=app_config.database_path, db_type=db.DatabaseType.FILESYSTEM
    )
    project_repository = ProjectRepository(session_maker)
    project = await project_repository.get_by_name(config.project)
    if not project:  # pragma: no cover
        raise Exception(f"Project '{config.project}' not found")

    import time

    start_time = time.time()

    logger.info(
        "Sync command started",
        project=config.project,
        verbose=verbose,
        directory=str(config.home),
    )

    sync_service = await get_sync_service(project)

    logger.info("Running one-time sync")
    knowledge_changes = await sync_service.sync(config.home, project_name=project.name)

    # Log results
    duration_ms = int((time.time() - start_time) * 1000)
    logger.info(
        "Sync command completed",
        project=config.project,
        total_changes=knowledge_changes.total,
        new_files=len(knowledge_changes.new),
        modified_files=len(knowledge_changes.modified),
        deleted_files=len(knowledge_changes.deleted),
        moved_files=len(knowledge_changes.moves),
        duration_ms=duration_ms,
    )

    # Display results
    if verbose:
        display_detailed_sync_results(knowledge_changes)
    else:
        display_sync_summary(knowledge_changes)  # pragma: no cover


@app.command()
def validate(
    fix: bool = typer.Option(
        False,
        "--fix",
        help="Attempt to fix simple YAML issues automatically.",
    ),
) -> None:
    """Validate YAML frontmatter in markdown files before syncing.

    Checks for malformed YAML that could break sync operations and provides
    detailed error messages to help fix issues.
    """
    config = get_project_config()

    try:
        typer.echo(f"Validating project: {config.project}")
        typer.echo(f"Project path: {config.home}")

        async def run_validation():
            app_config = ConfigManager().config
            _, session_maker = await db.get_or_create_db(
                db_path=app_config.database_path, db_type=db.DatabaseType.FILESYSTEM
            )
            project_repository = ProjectRepository(session_maker)
            project = await project_repository.get_by_name(config.project)
            if not project:
                raise Exception(f"Project '{config.project}' not found")

            sync_service = await get_sync_service(project)

            # Validate all files
            typer.echo("Scanning files for YAML frontmatter issues...")
            invalid_files = await sync_service.validate_project_files()

            if not invalid_files:
                typer.secho("All files passed validation!", fg=typer.colors.GREEN)
                return

            typer.secho(f"Found {len(invalid_files)} files with YAML issues:", fg=typer.colors.RED)
            typer.echo()

            for file_path, error in invalid_files.items():
                typer.secho(f"- {file_path}", fg=typer.colors.YELLOW)
                typer.echo(f"  Error: {error}")
                typer.echo()

            typer.echo("Tips to fix YAML issues:")
            typer.echo("   - Check for missing quotes around string values")
            typer.echo("   - Ensure proper YAML indentation (spaces, not tabs)")
            typer.echo("   - Fix malformed YAML aliases (&/*)")
            typer.echo("   - Validate YAML syntax with an online YAML validator")
            typer.echo()
            typer.echo("These files will be skipped during sync but won't break the process.")

        asyncio.run(run_validation())

    except Exception as e:  # pragma: no cover
        if not isinstance(e, typer.Exit):
            logger.exception(
                "Validate command failed",
                f"project={config.project},"
                f"error={str(e)},"
                f"error_type={type(e).__name__},"
                f"directory={str(config.home)}",
            )
            typer.secho(f"Error: {str(e)}", fg=typer.colors.RED)


@app.command()
def sync(
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-v",
        help="Show detailed sync information.",
    ),
) -> None:
    """Sync knowledge files with the database."""
    config = get_project_config()

    try:
        # Show which project we're syncing
        typer.echo(f"Syncing project: {config.project}")
        typer.echo(f"Project path: {config.home}")

        # Run sync
        asyncio.run(run_sync(verbose=verbose))

    except Exception as e:  # pragma: no cover
        if not isinstance(e, typer.Exit):
            logger.exception(
                "Sync command failed",
                f"project={config.project},"
                f"error={str(e)},"
                f"error_type={type(e).__name__},"
                f"directory={str(config.home)}",
            )
            typer.echo(f"Error during sync: {e}", err=True)
            raise typer.Exit(1)
        raise
