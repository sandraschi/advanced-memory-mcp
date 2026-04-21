"""Comprehensive Project CRUD tests for adn_project portmanteau tool.

This module tests the full lifecycle of project management via the adn_project tool,
ensuring regression testing for the validation errors and context injection issues.
"""

from unittest.mock import AsyncMock

import pytest
from fastmcp import Context

from advanced_memory.mcp.tools.portmanteau_project import adn_project

# Extract the actual function from FunctionTool object
adn_project_fn = getattr(adn_project, "fn", adn_project)


class MockContext(Context):
    """Mock FastMCP Context for testing."""

    def __init__(self):
        self.info = AsyncMock()
        self.warn = AsyncMock()
        self.error = AsyncMock()
        self.debug = AsyncMock()


@pytest.fixture
def mock_ctx():
    return MockContext()


class TestAdnProjectCRUD:
    """Test suite for adn_project CRUD operations."""

    @pytest.mark.asyncio
    async def test_adn_project_create_success(self, mock_ctx, config_home):
        """Test successful project creation."""
        project_name = "new-test-project"
        project_path = str(config_home / "new-project")

        result = await adn_project_fn(
            operation="create",
            project_name=project_name,
            project_path=project_path,
            ctx=mock_ctx,
        )

        assert result["success"] is True, f"Operation failed: {result.get('message')}"
        assert result["operation"] == "create"
        assert "Created" in result["technical_summary"] or "added successfully" in result["technical_summary"]
        assert project_name in result["technical_summary"]

        mock_ctx.info.assert_called()

    @pytest.mark.asyncio
    async def test_adn_project_list(self, mock_ctx, test_project):
        """Test listing projects."""
        result = await adn_project_fn(operation="list", ctx=mock_ctx)

        assert result["success"] is True, f"Operation failed: {result.get('message')}"
        assert result["operation"] == "list"
        names = [p["name"] for p in result["result"]["projects"]]
        assert test_project.name in names

    @pytest.mark.asyncio
    async def test_adn_project_current(self, mock_ctx, test_project):
        """Test getting current project."""
        result = await adn_project_fn(operation="get_current", ctx=mock_ctx)

        assert result["success"] is True, f"Operation failed: {result.get('message')}"
        assert result["operation"] == "get_current"
        assert test_project.name in result["technical_summary"]

    @pytest.mark.asyncio
    async def test_adn_project_switch_success(self, mock_ctx, test_project, config_home):
        """Test successful project switching."""
        other_name = "other-project"
        other_path = str(config_home / "other")
        created = await adn_project_fn(
            operation="create",
            project_name=other_name,
            project_path=other_path,
            ctx=mock_ctx,
        )
        assert created["success"] is True, created

        result = await adn_project_fn(operation="switch", project_name=other_name, ctx=mock_ctx)

        assert result["success"] is True, f"Operation failed: {result.get('message')}"
        assert result["operation"] == "switch"
        assert (
            f"Switched to project: {other_name}" in result["technical_summary"]
            or f"to {other_name} project" in result["technical_summary"]
            or "switched" in result["technical_summary"].lower()
        )

    @pytest.mark.asyncio
    async def test_adn_project_delete_success(self, mock_ctx, config_home, project_repository):
        """Test successful project deletion."""
        del_name = "to-delete"
        del_path = str(config_home / "delete-me")

        await adn_project_fn(operation="create", project_name=del_name, project_path=del_path, ctx=mock_ctx)

        result = await adn_project_fn(operation="delete", project_name=del_name, ctx=mock_ctx)

        assert result["success"] is True, f"Operation failed: {result.get('message')}"
        assert result["operation"] == "delete"
        assert (
            f"Deleted project: {del_name}" in result["technical_summary"]
            or "removed successfully" in result["technical_summary"]
            or "removed" in result["technical_summary"].lower()
        )

    @pytest.mark.asyncio
    async def test_adn_project_status(self, mock_ctx, test_project):
        """Test project status operation."""
        result = await adn_project_fn(operation="status", project_name=test_project.name, ctx=mock_ctx)

        assert result["success"] is True, f"Operation failed: {result.get('message')}"
        assert result["operation"] == "status"
        assert "status" in result["technical_summary"].lower()

    @pytest.mark.asyncio
    async def test_adn_project_sync(self, mock_ctx, test_project):
        """Test project sync operation."""
        result = await adn_project_fn(operation="sync", project_name=test_project.name, ctx=mock_ctx)

        assert result["success"] is True, f"Operation failed: {result.get('message')}"
        assert result["operation"] == "sync"
        assert "Sync" in result["technical_summary"] or "Indexing" in result["technical_summary"] or "sync" in result["technical_summary"].lower()
