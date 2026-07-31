"""Tests for the initialization service."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from advanced_memory.services.initialization import (
    ensure_initialization,
    initialize_database,
    initialize_file_sync,
    reconcile_projects_with_config,
)


@pytest.mark.asyncio
@patch("advanced_memory.services.initialization.db.get_or_create_db")
async def test_initialize_database(mock_get_or_create_db, app_config):
    """Test initializing the database."""
    mock_get_or_create_db.return_value = (MagicMock(), MagicMock())
    await initialize_database(app_config)
    mock_get_or_create_db.assert_called_once_with(app_config.database_path)


@pytest.mark.asyncio
@patch("advanced_memory.services.initialization.db.get_or_create_db")
async def test_initialize_database_error(mock_get_or_create_db, app_config):
    """Test handling errors during database initialization."""
    mock_get_or_create_db.side_effect = Exception("Test error")
    with pytest.raises(Exception, match="Test error"):
        await initialize_database(app_config)
    mock_get_or_create_db.assert_called_once_with(app_config.database_path)


@patch("advanced_memory.services.initialization.asyncio.run")
def test_ensure_initialization(mock_run, project_config):
    """Test synchronous initialization wrapper."""
    ensure_initialization(project_config)
    mock_run.assert_called_once()


@pytest.mark.asyncio
@patch("advanced_memory.services.initialization.db.get_or_create_db")
async def test_reconcile_projects_with_config(mock_get_db, app_config):
    """Test reconciling projects from config with database using ProjectService."""
    # Setup mocks
    mock_session_maker = AsyncMock()
    mock_get_db.return_value = (None, mock_session_maker)

    mock_repository = AsyncMock()
    mock_project_service = AsyncMock()
    mock_project_service.synchronize_projects = AsyncMock()

    # Mock the repository and project service
    with (
        patch("advanced_memory.services.initialization.ProjectRepository") as mock_repo_class,
        patch(
            "advanced_memory.services.project_service.ProjectService",
            return_value=mock_project_service,
        ),
    ):
        mock_repo_class.return_value = mock_repository

        # Set up app_config projects as a dictionary
        app_config.projects = {"test_project": "/path/to/project", "new_project": "/path/to/new"}
        app_config.default_project = "test_project"

        # Run the function
        await reconcile_projects_with_config(app_config)

        # Assertions
        mock_get_db.assert_called_once()
        mock_repo_class.assert_called_once_with(mock_session_maker)
        mock_project_service.synchronize_projects.assert_called_once()

        # We should no longer be calling these directly since we're using the service
        mock_repository.find_all.assert_not_called()
        mock_repository.set_as_default.assert_not_called()


@pytest.mark.asyncio
@patch("advanced_memory.services.initialization.db.get_or_create_db")
async def test_reconcile_projects_with_error_handling(mock_get_db, app_config):
    """Test error handling during project synchronization."""
    # Setup mocks
    mock_session_maker = AsyncMock()
    mock_get_db.return_value = (None, mock_session_maker)

    mock_repository = AsyncMock()
    mock_project_service = AsyncMock()
    mock_project_service.synchronize_projects = AsyncMock(side_effect=ValueError("Project synchronization error"))

    # Mock the repository and project service
    with (
        patch("advanced_memory.services.initialization.ProjectRepository") as mock_repo_class,
        patch(
            "advanced_memory.services.project_service.ProjectService",
            return_value=mock_project_service,
        ),
        patch("advanced_memory.services.initialization.logger") as mock_logger,
    ):
        mock_repo_class.return_value = mock_repository

        # Set up app_config projects as a dictionary
        app_config.projects = {"test_project": "/path/to/project"}
        app_config.default_project = "missing_project"

        # Run the function which now has error handling
        await reconcile_projects_with_config(app_config)

        # Assertions
        mock_get_db.assert_called_once()
        mock_repo_class.assert_called_once_with(mock_session_maker)
        mock_project_service.synchronize_projects.assert_called_once()

        # Verify error was logged
        mock_logger.exception.assert_called_once_with(
            "Project synchronization failed — continuing startup; some projects may be missing"
        )


@pytest.mark.asyncio
@patch("advanced_memory.services.initialization.db.get_or_create_db")
@patch("advanced_memory.sync.WatchService")
async def test_initialize_file_sync_sequential(mock_watch_service_class, mock_get_db, app_config):
    """Test file sync initialization starts the watch service in the background."""
    # Setup mocks
    mock_session_maker = AsyncMock()
    mock_get_db.return_value = (None, mock_session_maker)

    mock_watch_service = AsyncMock()
    mock_watch_service.run = AsyncMock()
    mock_watch_service_class.return_value = mock_watch_service

    mock_repository = AsyncMock()

    # Mock the repository
    with patch("advanced_memory.services.initialization.ProjectRepository") as mock_repo_class:
        mock_repo_class.return_value = mock_repository

        # Run the function
        result = await initialize_file_sync(app_config)

        # Assertions
        mock_get_db.assert_called_once()
        mock_repo_class.assert_called_once_with(mock_session_maker)

        # Should construct the watch service with the app config and repository
        mock_watch_service_class.assert_called_once_with(
            app_config=app_config,
            project_repository=mock_repository,
            quiet=True,
        )

        # Should start the watch service in the background
        mock_watch_service.run.assert_called_once()

        # Should return None
        assert result is None
