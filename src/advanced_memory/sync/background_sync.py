import asyncio

from loguru import logger

from advanced_memory.config import get_project_config
from advanced_memory.sync import SyncService, WatchService
from advanced_memory.utils.task_logging import attach_task_failure_logging


async def sync_and_watch(sync_service: SyncService, watch_service: WatchService) -> None:  # pragma: no cover
    """Run sync and watch service."""

    config = get_project_config()
    logger.info(f"Starting watch service to sync file changes in dir: {config.home}")
    # full sync
    await sync_service.sync(config.home)

    # watch changes
    await watch_service.run()


async def create_background_sync_task(sync_service: SyncService, watch_service: WatchService):  # pragma: no cover
    task = asyncio.create_task(
        sync_and_watch(sync_service, watch_service),
        name="management_sync_and_watch",
    )
    attach_task_failure_logging(task, "management_sync_and_watch")
    return task
