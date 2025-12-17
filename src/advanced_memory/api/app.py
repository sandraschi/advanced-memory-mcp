"""FastAPI application for advanced-memory knowledge graph API."""

import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.exception_handlers import http_exception_handler
from loguru import logger

from advanced_memory import __version__ as version
from advanced_memory import db
from advanced_memory.api.routers import (
    directory_router,
    importer_router,
    knowledge,
    management,
    memory,
    project,
    prompt_router,
    resource,
    search,
)
from advanced_memory.config import ConfigManager
from advanced_memory.services.initialization import initialize_app, initialize_file_sync


@asynccontextmanager
async def lifespan(app: FastAPI):  # pragma: no cover
    """Lifecycle manager for the FastAPI app."""

    # Setup logging for API (explicit call since config.py no longer does it automatically)
    from advanced_memory.config import setup_advanced_memory_logging
    setup_advanced_memory_logging()

    app_config = ConfigManager().config
    # Initialize app and database
    logger.info("Starting Advanced Memory API")
    logger.debug(f"Configured projects: {app_config.projects}")
    await initialize_app(app_config)

    logger.info(f"Sync changes enabled: {app_config.sync_changes}")
    if app_config.sync_changes:
        # start file sync task in background
        app.state.sync_task = asyncio.create_task(initialize_file_sync(app_config))
    else:
        logger.info("Sync changes disabled. Skipping file sync service.")

    # proceed with startup
    yield

    logger.info("Shutting down Advanced Memory API")
    if app.state.sync_task:
        logger.info("Stopping sync...")
        app.state.sync_task.cancel()  # pyright: ignore

    await db.shutdown_db()


# Initialize FastAPI app
app = FastAPI(
    title="Advanced Memory API",
    description="Knowledge graph API for advanced-memory",
    version=version,
    lifespan=lifespan,
)


# Include routers
app.include_router(knowledge.router, prefix="/{project}")
app.include_router(memory.router, prefix="/{project}")
app.include_router(resource.router, prefix="/{project}")
app.include_router(search.router, prefix="/{project}")
app.include_router(project.project_router, prefix="/{project}")
app.include_router(directory_router.router, prefix="/{project}")
app.include_router(prompt_router.router, prefix="/{project}")
app.include_router(importer_router.router, prefix="/{project}")

# Project resource router works accross projects
app.include_router(project.project_resource_router)
app.include_router(management.router)

# Auth routes are handled by FastMCP automatically when auth is enabled


@app.exception_handler(Exception)
async def exception_handler(request, exc):  # pragma: no cover
    logger.exception(
        "API unhandled exception",
        url=str(request.url),
        method=request.method,
        client=request.client.host if request.client else None,
        path=request.url.path,
        error_type=type(exc).__name__,
        error=str(exc),
    )
    return await http_exception_handler(request, HTTPException(status_code=500, detail=str(exc)))
