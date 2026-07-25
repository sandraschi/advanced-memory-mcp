"""FastAPI application for advanced-memory knowledge graph API."""

import asyncio
import traceback
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request
from fastapi.exception_handlers import http_exception_handler, request_validation_exception_handler
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from loguru import logger

from advanced_memory import __version__ as version
from advanced_memory import db
from advanced_memory.api.log_buffer import install_api_log_buffer_sink
from advanced_memory.api.routers import (
    directory_router,
    hardware_router,
    importer_router,
    knowledge,
    management,
    memory,
    project,
    prompt_router,
    resource,
    search,
    system_router,
    tests_router,
    wiki_router,
)
from advanced_memory.config import ConfigManager
from advanced_memory.services.initialization import initialize_app, initialize_file_sync
from advanced_memory.utils.task_logging import (
    attach_task_failure_logging,
    chain_asyncio_exception_handler,
)


@asynccontextmanager
async def lifespan(app: FastAPI):  # pragma: no cover
    """Lifecycle manager for the FastAPI app."""

    loop = asyncio.get_running_loop()
    prev_loop_exc_handler = loop.get_exception_handler()
    loop.set_exception_handler(chain_asyncio_exception_handler(prev_loop_exc_handler))

    # Setup logging for API (explicit call since config.py no longer does it automatically)
    from advanced_memory.config import setup_advanced_memory_logging

    setup_advanced_memory_logging()
    install_api_log_buffer_sink()

    app.state.sync_task = None
    app.state.watch_task = None
    try:
        app_config = ConfigManager().config
        # Initialize app and database
        logger.info("Starting Advanced Memory API")
        logger.debug(f"Configured projects: {app_config.projects}")
        await initialize_app(app_config)

        logger.info(f"Sync changes enabled: {app_config.sync_changes}")
        if app_config.sync_changes:
            sync_task = asyncio.create_task(
                initialize_file_sync(app_config),
                name="api_initialize_file_sync",
            )
            attach_task_failure_logging(sync_task, "api_initialize_file_sync")
            app.state.sync_task = sync_task
        else:
            logger.info("Sync changes disabled. Skipping file sync service.")

        yield
    finally:
        loop.set_exception_handler(prev_loop_exc_handler)

        logger.info("Shutting down Advanced Memory API")
        watch_task = getattr(app.state, "watch_task", None)
        if watch_task is not None and not watch_task.done():
            logger.info("Stopping management watch task...")
            watch_task.cancel()
            try:
                await watch_task
            except asyncio.CancelledError:
                logger.info("Watch task cancelled cleanly")
            except Exception:
                logger.exception("Watch task ended with error during shutdown")
            app.state.watch_task = None

        sync_task = getattr(app.state, "sync_task", None)
        if sync_task is not None and not sync_task.done():
            logger.info("Stopping file sync task...")
            sync_task.cancel()
            try:
                await sync_task
            except asyncio.CancelledError:
                logger.info("File sync task cancelled cleanly")
            except Exception:
                logger.exception("File sync task ended with error during shutdown")

        await db.shutdown_db()


from fastapi.middleware.cors import CORSMiddleware

# Initialize FastAPI app
app = FastAPI(
    title="Advanced Memory API",
    description="Knowledge graph API for advanced-memory",
    version=version,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers

app.include_router(hardware_router.router, prefix="/api/v1")
app.include_router(hardware_router.model_router, prefix="/api/v1")
app.include_router(importer_router.router, prefix="/api/v1")

# Project-scoped routers under /api/v1/{project}
app.include_router(knowledge.router, prefix="/api/v1/{project}")
app.include_router(memory.router, prefix="/api/v1/{project}")
app.include_router(resource.router, prefix="/api/v1/{project}")
app.include_router(search.router, prefix="/api/v1/{project}")
app.include_router(project.project_router, prefix="/api/v1/{project}")
app.include_router(directory_router.router, prefix="/api/v1/{project}")
app.include_router(prompt_router.router, prefix="/api/v1/{project}")

# Non-project specific routers
app.include_router(project.project_resource_router, prefix="/api/v1")
app.include_router(management.router, prefix="/api/v1")
app.include_router(system_router.router, prefix="/api/v1")
app.include_router(tests_router.router, prefix="/api/v1")
app.include_router(wiki_router.router)

# Auth routes are handled by FastMCP automatically when auth is enabled


@app.get("/api/v1/health")
async def health_check():
    return {"status": "ok"}


@app.exception_handler(RequestValidationError)
async def request_validation_handler(  # pragma: no cover
    request: Request, exc: RequestValidationError
):
    return await request_validation_exception_handler(request, exc)


@app.exception_handler(HTTPException)
async def http_exception_handler_route(request: Request, exc: HTTPException):  # pragma: no cover
    return await http_exception_handler(request, exc)


@app.exception_handler(Exception)
async def exception_handler(request: Request, exc: Exception):  # pragma: no cover
    """Log full traceback; return a safe JSON body (detail is not the raw exception string)."""
    tb = "".join(traceback.format_exception(type(exc), exc, exc.__traceback__))
    logger.error(
        "API unhandled exception method={} path={} client={} type={}: {}\n{}",
        request.method,
        request.url.path,
        request.client.host if request.client else None,
        type(exc).__name__,
        exc,
        tb,
    )
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "error_type": type(exc).__name__,
        },
    )
