"""Tests for management router API endpoints."""

from unittest.mock import MagicMock, patch

import pytest
from fastapi import FastAPI

from advanced_memory.api.routers.management_router import (
    WatchStatusResponse,
    get_watch_status,
    start_watch_service,
    stop_watch_service,
)


class MockRequest:
    """Mock FastAPI request with app state."""

    def __init__(self, app):
        self.app = app


@pytest.fixture
def mock_app():
    """Create a mock FastAPI app with state.

    Uses app.state.sync_task, not watch_task: the real watcher started at
    boot in api/app.py's lifespan is app.state.sync_task (initialize_file_sync).
    app.state.watch_task was a separate, unrelated variable nothing else in
    the app ever set - these tests originally asserted against it, which is
    exactly how a real, live bug (Start/Stop watch always 422'd; Status
    always read "stopped" regardless of the real watcher) went unnoticed.
    """
    app = MagicMock(spec=FastAPI)
    app.state = MagicMock(spec=["sync_task"])
    app.state.sync_task = None
    return app


@pytest.mark.asyncio
async def test_get_watch_status_not_running(mock_app):
    """Test getting watch status when watch service is not running."""
    mock_app.state.sync_task = None
    mock_request = MockRequest(mock_app)

    response = await get_watch_status(mock_request)

    assert isinstance(response, WatchStatusResponse)
    assert response.running is False


@pytest.mark.asyncio
async def test_get_watch_status_running(mock_app):
    """Test getting watch status when watch service is running."""
    mock_task = MagicMock()
    mock_task.done.return_value = False
    mock_app.state.sync_task = mock_task
    mock_request = MockRequest(mock_app)

    response = await get_watch_status(mock_request)

    assert isinstance(response, WatchStatusResponse)
    assert response.running is True


@pytest.mark.asyncio
async def test_start_watch_service_when_not_running(mock_app):
    """Test starting watch service when it's not running."""
    mock_app.state.sync_task = None
    mock_request = MockRequest(mock_app)

    with (
        patch("advanced_memory.services.initialization.initialize_file_sync") as mock_init_sync,
        patch("advanced_memory.utils.task_logging.attach_task_failure_logging"),
        patch("asyncio.create_task") as mock_create_task,
    ):
        mock_task = MagicMock()
        mock_task.done.return_value = False
        mock_create_task.return_value = mock_task

        response = await start_watch_service(mock_request)

        assert isinstance(response, WatchStatusResponse)
        assert response.running is True
        # start_watch_service calls initialize_file_sync(app_config) to build
        # the coroutine it hands to asyncio.create_task
        assert mock_init_sync.called
        assert mock_create_task.called
        assert mock_app.state.sync_task is mock_task


@pytest.mark.asyncio
async def test_start_watch_service_already_running(mock_app):
    """Test starting watch service when it's already running."""
    mock_task = MagicMock()
    mock_task.done.return_value = False
    mock_app.state.sync_task = mock_task
    mock_request = MockRequest(mock_app)

    with patch("asyncio.create_task") as mock_create_task:
        response = await start_watch_service(mock_request)

        assert isinstance(response, WatchStatusResponse)
        assert response.running is True
        # Already running - must not spawn a second, competing sync task
        assert not mock_create_task.called
        assert mock_app.state.sync_task is mock_task


@pytest.mark.asyncio
async def test_stop_watch_service_not_running(mock_app):
    """Test stopping the watch service when it's not running."""
    mock_app.state.sync_task = None
    mock_request = MockRequest(mock_app)

    response = await stop_watch_service(mock_request)

    assert isinstance(response, WatchStatusResponse)
    assert response.running is False


@pytest.mark.asyncio
async def test_stop_watch_service_already_done(mock_app):
    """Test stopping the watch service when it's already done."""
    mock_task = MagicMock()
    mock_task.done.return_value = True
    mock_app.state.sync_task = mock_task
    mock_request = MockRequest(mock_app)

    response = await stop_watch_service(mock_request)

    assert isinstance(response, WatchStatusResponse)
    assert response.running is False


@pytest.mark.asyncio
async def test_stop_watch_service_when_running(mock_app):
    """Test stopping the watch service when it's running - task is cancelled and awaited."""
    import asyncio

    async def _never_ending():
        await asyncio.sleep(3600)

    real_task = asyncio.create_task(_never_ending())
    mock_app.state.sync_task = real_task
    mock_request = MockRequest(mock_app)

    response = await stop_watch_service(mock_request)

    assert isinstance(response, WatchStatusResponse)
    assert response.running is False
    assert real_task.cancelled()
    assert mock_app.state.sync_task is None
