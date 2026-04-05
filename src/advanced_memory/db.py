import asyncio
import datetime
import sqlite3
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from enum import Enum, auto
from pathlib import Path

from alembic import command
from alembic.config import Config
from loguru import logger
from sqlalchemy import event, text
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_scoped_session,
    async_sessionmaker,
    create_async_engine,
)

from advanced_memory.config import AdvancedMemoryConfig, ConfigManager
from advanced_memory.repository.search_repository import SearchRepository


# Register sqlite3 adapters for Python 3.12+ compatibility
def _adapt_datetime_iso(val: datetime.datetime) -> str:
    return val.isoformat()


def _convert_datetime(val: bytes) -> datetime.datetime:
    return datetime.datetime.fromisoformat(val.decode())


sqlite3.register_adapter(datetime.datetime, _adapt_datetime_iso)
sqlite3.register_converter("timestamp", _convert_datetime)
sqlite3.register_converter("datetime", _convert_datetime)

# Module level state
_engine: AsyncEngine | None = None
_session_maker: async_sessionmaker[AsyncSession] | None = None
_migrations_completed: bool = False


class DatabaseType(Enum):
    """Types of supported databases."""

    MEMORY = auto()
    FILESYSTEM = auto()

    @classmethod
    def get_db_url(cls, db_path: Path, db_type: "DatabaseType") -> str:
        """Get SQLAlchemy URL for database path."""
        if db_type == cls.MEMORY:
            logger.info("Using in-memory SQLite database")
            return "sqlite+aiosqlite://"

        return f"sqlite+aiosqlite:///{db_path}"  # pragma: no cover


def get_scoped_session_factory(
    session_maker: async_sessionmaker[AsyncSession],
) -> async_scoped_session:
    """Create a scoped session factory scoped to current task."""
    return async_scoped_session(session_maker, scopefunc=asyncio.current_task)


@asynccontextmanager
async def scoped_session(
    session_maker: async_sessionmaker[AsyncSession],
) -> AsyncGenerator[AsyncSession, None]:
    """
    Get a scoped session with proper lifecycle management.

    Args:
        session_maker: Session maker to create scoped sessions from
    """
    factory = get_scoped_session_factory(session_maker)
    session = factory()
    try:
        await session.execute(text("PRAGMA foreign_keys=ON"))
        yield session
        await session.commit()
    except Exception:
        await session.rollback()
        raise
    finally:
        await session.close()
        await factory.remove()


def _create_engine_and_session(
    db_path: Path, db_type: DatabaseType = DatabaseType.FILESYSTEM
) -> tuple[AsyncEngine, async_sessionmaker[AsyncSession]]:
    """Internal helper to create engine and session maker."""
    db_url = DatabaseType.get_db_url(db_path, db_type)
    logger.debug(f"Creating engine for db_url: {db_url}")

    # Configure SQLite with timeout and WAL mode for better concurrency
    connect_args = {
        "check_same_thread": False,
        "timeout": 30.0,  # 30 second timeout prevents indefinite hanging
    }

    # Add connection pooling for better concurrency (not for SQLite databases)
    engine_kwargs = {"connect_args": connect_args, "pool_pre_ping": True}
    # SQLite (both MEMORY and FILESYSTEM) doesn't support pooling parameters
    # These parameters are only valid for PostgreSQL, MySQL, etc.
    # SQLite uses aiosqlite with NullPool which doesn't support pool_size/max_overflow

    engine = create_async_engine(db_url, **engine_kwargs)

    # Configure SQLite for better concurrency (WAL mode allows concurrent reads/writes)
    @event.listens_for(engine.sync_engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):  # type: ignore[misc]
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA journal_mode=WAL")  # Write-Ahead Logging for concurrency
        cursor.execute("PRAGMA busy_timeout=5000")  # Reduced to 5s since we have connection pooling
        cursor.execute("PRAGMA synchronous=NORMAL")  # Balance between safety and performance
        cursor.execute("PRAGMA cache_size=-64000")  # 64MB cache for better performance
        cursor.execute("PRAGMA temp_store=MEMORY")  # Keep temp tables in memory
        cursor.execute("PRAGMA mmap_size=268435456")  # 256MB memory-mapped I/O
        cursor.execute("PRAGMA wal_autocheckpoint=1000")  # Checkpoint every 1000 pages
        cursor.close()

    session_maker = async_sessionmaker(engine, expire_on_commit=False)
    return engine, session_maker


async def get_or_create_db(
    db_path: Path,
    db_type: DatabaseType = DatabaseType.FILESYSTEM,
    ensure_migrations: bool = True,
) -> tuple[AsyncEngine, async_sessionmaker[AsyncSession]]:  # pragma: no cover
    """Get or create database engine and session maker."""
    global _engine, _session_maker

    if _engine is None:
        _engine, _session_maker = _create_engine_and_session(db_path, db_type)

        # Run migrations automatically unless explicitly disabled
        if ensure_migrations:
            app_config = ConfigManager().config
            await run_migrations(app_config, db_type)

    # These checks should never fail since we just created the engine and session maker
    # if they were None, but we'll check anyway for the type checker
    if _engine is None:
        logger.error("Failed to create database engine", db_path=str(db_path))
        raise RuntimeError("Database engine initialization failed")

    if _session_maker is None:
        logger.error("Failed to create session maker", db_path=str(db_path))
        raise RuntimeError("Session maker initialization failed")

    return _engine, _session_maker


async def shutdown_db() -> None:  # pragma: no cover
    """Clean up database connections."""
    global _engine, _session_maker, _migrations_completed

    if _engine:
        await _engine.dispose()
        _engine = None
        _session_maker = None
        _migrations_completed = False


@asynccontextmanager
async def engine_session_factory(
    db_path: Path,
    db_type: DatabaseType = DatabaseType.MEMORY,
) -> AsyncGenerator[tuple[AsyncEngine, async_sessionmaker[AsyncSession]], None]:
    """Create engine and session factory.

    Note: This is primarily used for testing where we want a fresh database
    for each test. For production use, use get_or_create_db() instead.
    """

    global _engine, _session_maker, _migrations_completed

    db_url = DatabaseType.get_db_url(db_path, db_type)
    logger.debug(f"Creating engine for db_url: {db_url}")

    # Configure SQLite with timeout and WAL mode for better concurrency
    connect_args = {
        "check_same_thread": False,
        "timeout": 30.0,  # 30 second timeout prevents indefinite hanging
    }

    # Add connection pooling for better concurrency (not for in-memory databases)
    engine_kwargs = {"connect_args": connect_args, "pool_pre_ping": True}
    if db_type != DatabaseType.MEMORY:
        # Only add pool settings for file-based databases
        # In-memory databases use StaticPool which doesn't support these parameters
        engine_kwargs["pool_size"] = 5  # Keep 5 connections ready
        engine_kwargs["max_overflow"] = 10  # Allow 10 extra connections under load

    _engine = create_async_engine(db_url, **engine_kwargs)

    # Configure SQLite for better concurrency (WAL mode allows concurrent reads/writes)
    @event.listens_for(_engine.sync_engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):  # type: ignore[misc]
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA journal_mode=WAL")  # Write-Ahead Logging for concurrency
        cursor.execute("PRAGMA busy_timeout=5000")  # Reduced to 5s since we have connection pooling
        cursor.execute("PRAGMA synchronous=NORMAL")  # Balance between safety and performance
        cursor.execute("PRAGMA cache_size=-64000")  # 64MB cache for better performance
        cursor.execute("PRAGMA temp_store=MEMORY")  # Keep temp tables in memory
        cursor.execute("PRAGMA mmap_size=268435456")  # 256MB memory-mapped I/O
        cursor.execute("PRAGMA wal_autocheckpoint=1000")  # Checkpoint every 1000 pages
        cursor.close()

    try:
        _session_maker = async_sessionmaker(_engine, expire_on_commit=False)

        # Verify that engine and session maker are initialized
        if _engine is None:  # pragma: no cover
            logger.error("Database engine is None in engine_session_factory")
            raise RuntimeError("Database engine initialization failed")

        if _session_maker is None:  # pragma: no cover
            logger.error("Session maker is None in engine_session_factory")
            raise RuntimeError("Session maker initialization failed")

        yield _engine, _session_maker
    finally:
        if _engine:
            await _engine.dispose()
            _engine = None
            _session_maker = None
            _migrations_completed = False


async def run_migrations(
    app_config: AdvancedMemoryConfig,
    database_type: DatabaseType = DatabaseType.FILESYSTEM,
    force: bool = False,
) -> None:  # pragma: no cover
    """Run any pending alembic migrations."""
    global _migrations_completed

    # Skip if migrations already completed unless forced
    if _migrations_completed and not force:
        logger.debug("Migrations already completed in this session, skipping")
        return

    logger.info("Running database migrations...")
    try:
        # Get the absolute path to the alembic directory relative to this file
        alembic_dir = Path(__file__).parent / "alembic"
        config = Config()

        # Set required Alembic config options programmatically
        config.set_main_option("script_location", str(alembic_dir))
        config.set_main_option(
            "file_template",
            "%%(year)d_%%(month).2d_%%(day).2d_%%(hour).2d%%(minute).2d-%%(rev)s_%%(slug)s",
        )
        config.set_main_option("timezone", "UTC")
        config.set_main_option("revision_environment", "false")
        config.set_main_option(
            "sqlalchemy.url", DatabaseType.get_db_url(app_config.database_path, database_type)
        )

        command.upgrade(config, "head")
        logger.info("Migrations completed successfully")

        # Get session maker - ensure we don't trigger recursive migration calls
        if _session_maker is None:
            _, session_maker = _create_engine_and_session(app_config.database_path, database_type)
        else:
            session_maker = _session_maker

        # initialize the search Index schema
        # the project_id is not used for init_search_index, so we pass a dummy value
        await SearchRepository(session_maker, 1).init_search_index()

        # Mark migrations as completed
        _migrations_completed = True
    except Exception as e:  # pragma: no cover
        logger.error(f"Error running migrations: {e}")
        raise
