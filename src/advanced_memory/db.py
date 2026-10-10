import asyncio
import datetime
import json
import os
import sqlite3
import time
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
from sqlalchemy.pool import NullPool

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


# Single-writer enforcement (SPEC_SINGLE_WRITER rule 4, BUG-048). One SQLite
# vault, one writer process. The lock below is held by the OS on an open file
# descriptor kept for process lifetime: a second writer fails LOUDLY at engine
# creation instead of contending silently (write timeouts, phantom index
# entries). A crashed holder releases the lock via the OS itself, so the lock
# can never go stale from a dead process - the only failure mode is a loud
# startup error naming the live holder, never silent corruption.
_WRITER_LOCK_FDS: dict[str, object] = {}
_WRITER_LOCK_NAME = ".writer.lock"


def _pid_alive(pid: int) -> bool:
    """Best-effort process liveness check (for error messages only)."""
    try:
        import psutil

        return psutil.pid_exists(pid)
    except ImportError:  # pragma: no cover
        pass
    try:  # Windows stdlib fallback, no extra deps
        import ctypes

        kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
        handle = kernel32.OpenProcess(0x00100000, False, pid)  # SYNCHRONIZE
        if not handle:
            return False
        kernel32.CloseHandle(handle)
        return True
    except Exception:  # pragma: no cover
        return True  # fail-safe: assume alive, die loudly, never risk two writers


def _read_lock_owner(fh) -> dict:
    # Owner record is an append-only claim log (one JSON object per line);
    # the live holder is the last valid entry. Never overwrite it in place:
    # any write() to this file drops the MSVCRT region lock (verified
    # 2026-10-05: lock-then-write lets a second process lock - silent
    # two-writer corruption, exactly what this lock exists to prevent).
    try:
        fh.seek(0)
        raw = fh.read()
        if isinstance(raw, bytes):
            raw = raw.decode("utf-8", errors="ignore")
        owner: dict = {}
        for line in raw.splitlines():
            try:
                parsed = json.loads(line)
                if isinstance(parsed, dict):
                    owner = parsed
            except ValueError:
                continue
        return owner
    except Exception:
        return {}


def _raise_locked(lock_path: Path, owner: dict) -> None:
    holder = owner.get("pid", "unknown")
    since = owner.get("started", "unknown time")
    alive = _pid_alive(holder) if isinstance(holder, int) else "unknown"
    raise RuntimeError(
        f"advanced-memory vault is already opened for writing by PID {holder} "
        f"(since {since}, alive={alive}). Two writers corrupt the index (BUG-048). "
        f"If that process is a stale memops stdio server, kill it - every stdio "
        f"client must proxy the daemon (SPEC_SINGLE_WRITER). Lock: {lock_path}"
    )


def claim_writer_lock(db_path: Path, db_type: "DatabaseType") -> None:
    """Claim exclusive writer ownership of the vault holding db_path.

    No-ops for in-memory DBs and read-only mode (readers never take the lock).
    Reentrant within one process (engine created twice keeps one lock).
    Raises RuntimeError naming the live holder when another writer owns it.
    """
    from advanced_memory.readonly import IS_READONLY

    if db_type != DatabaseType.FILESYSTEM or IS_READONLY:
        return
    lock_path = Path(db_path).resolve().parent / _WRITER_LOCK_NAME
    key = os.path.normcase(str(lock_path))
    if key in _WRITER_LOCK_FDS:
        return  # same process already holds it

    try:
        fh = open(lock_path, "a+b")
    except OSError as e:
        raise RuntimeError(f"advanced-memory: cannot open writer lock {lock_path}: {e}") from e

    # Stamp our claim BEFORE locking (append-only; a racer may append after us
    # but only one process wins the region lock below). Writes must never
    # happen after locking - any write() drops the MSVCRT region lock.
    try:
        with open(lock_path, "ab") as stamp:
            stamp.write(
                (json.dumps({"pid": os.getpid(), "started": time.strftime("%Y-%m-%d %H:%M:%S")}) + "\n").encode("utf-8")
            )
    except OSError as e:
        fh.close()
        raise RuntimeError(f"advanced-memory: cannot stamp writer lock {lock_path}: {e}") from e

    try:
        # CRITICAL: seek(0) first. MSVCRT locking() locks at the CURRENT file
        # position, and "a+b" opens positioned at EOF: without this, parent and
        # child lock different offsets on any non-empty file and both "succeed"
        # (14-case matrix verified 2026-10-05 - silent two-writer corruption).
        # Everybody locks byte [0,1), always.
        fh.seek(0)
        if os.name == "nt":
            import msvcrt

            msvcrt.locking(fh.fileno(), msvcrt.LK_NBLCK, 1)
        else:  # pragma: no cover - POSIX fallback
            import fcntl

            fcntl.flock(fh.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
    except OSError:
        owner = _read_lock_owner(fh)
        fh.close()
        _raise_locked(lock_path, owner)

    # The lock fd is never written or closed for process lifetime. fh stays in
    # _WRITER_LOCK_FDS so the descriptor (and the OS lock on it) survives.
    _WRITER_LOCK_FDS[key] = fh
    logger.info(f"Claimed vault writer lock: {lock_path} (pid {os.getpid()})")


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
    from advanced_memory.readonly import IS_READONLY

    db_url = DatabaseType.get_db_url(db_path, db_type)

    # In read-only mode, open the SQLite file with ?mode=ro so any write attempt
    # raises an OperationalError immediately rather than silently corrupting state.
    if IS_READONLY and db_type == DatabaseType.FILESYSTEM:
        db_url = f"sqlite+aiosqlite:///file:{db_path}?mode=ro&uri=true"

    # Single writer per vault (SPEC_SINGLE_WRITER rule 4): die loudly here if
    # another writer owns it, instead of contending silently downstream.
    claim_writer_lock(db_path, db_type)

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

    # NullPool for filesystem SQLite: without it, SQLAlchemy's async engine defaults
    # to AsyncAdaptedQueuePool, which reuses connections across requests. A connection
    # checked out by a cancelled asyncio task (client disconnect, MCP session teardown)
    # never gets returned to that pool - it sits there holding an open SQLite read
    # transaction indefinitely, which blocks WAL checkpointing for every other process
    # sharing this db file until the whole thing looks like a readonly/locked database.
    # NullPool opens and closes a real connection per checkout, so there is nothing to
    # leak. Does not apply to MEMORY (in-memory db_type used by tests), where NullPool
    # would silently reset to an empty database on every new connection.
    if db_type == DatabaseType.FILESYSTEM:
        engine_kwargs["poolclass"] = NullPool

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
    # Same single-writer claim as _create_engine_and_session (covers the
    # explicit-FILESYSTEM test path; MEMORY stays lock-free).
    claim_writer_lock(db_path, db_type)
    logger.debug(f"Creating engine for db_url: {db_url}")

    # Configure SQLite with timeout and WAL mode for better concurrency
    connect_args = {
        "check_same_thread": False,
        "timeout": 30.0,  # 30 second timeout prevents indefinite hanging
    }

    # Add connection pooling for better concurrency (not for in-memory databases)
    engine_kwargs = {"connect_args": connect_args, "pool_pre_ping": True}
    if db_type != DatabaseType.MEMORY:
        # NullPool, not a sized QueuePool: see the matching comment in
        # _create_engine_and_session for why - a pooled connection checked out
        # by a cancelled asyncio task never gets returned, and ends up holding
        # a stale SQLite read transaction that blocks WAL checkpoints fleet-wide.
        engine_kwargs["poolclass"] = NullPool

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
        config.set_main_option("sqlalchemy.url", DatabaseType.get_db_url(app_config.database_path, database_type))

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
