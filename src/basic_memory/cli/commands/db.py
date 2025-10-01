"""Database management commands."""

import asyncio

import typer
from loguru import logger

from basic_memory import db
from basic_memory.cli.app import app
from basic_memory.config import ConfigManager, BasicMemoryConfig, save_basic_memory_config


@app.command()
def reset(
    reindex: bool = typer.Option(False, "--reindex", help="Rebuild db index from filesystem"),
):  # pragma: no cover
    """Reset database (drop all tables and recreate)."""
    if typer.confirm("This will delete all data in your db. Are you sure?"):
        logger.info("Resetting database...")
        config_manager = ConfigManager()
        app_config = config_manager.config
        # Get database path
        db_path = app_config.app_database_path

        # Delete the database file if it exists
        if db_path.exists():
            db_path.unlink()
            logger.info(f"Database file deleted: {db_path}")

        # Reset project configuration
        config = BasicMemoryConfig()
        save_basic_memory_config(config_manager.config_file, config)
        logger.info("Project configuration reset to default")

        # Create a new empty database
        asyncio.run(db.run_migrations(app_config))
        logger.info("Database reset complete")

        if reindex:
            # Import and run sync
            from basic_memory.cli.commands.sync import sync

            logger.info("Rebuilding search index from filesystem...")
            sync(watch=False)  # pyright: ignore
