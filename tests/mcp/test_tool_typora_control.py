"""
Tests for Typora control via json_rpc plugin.

Note: These tests require Typora with json_rpc plugin running on port 8888.
For CI/CD, these would be integration tests that require Typora setup.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from advanced_memory.mcp.tools.typora_control import (
    typora_control,
    TyporaRPCClient,
    check_typora_connection,
    get_typora_status
)


class TestTyporaRPCClient:
    """Test the TyporaRPCClient class."""

    @pytest.fixture
    def client(self):
        """Create a test client."""
        return TyporaRPCClient()

    @pytest.mark.asyncio
    async def test_successful_call(self, client):
        """Test successful JSON-RPC call."""
        mock_response = {
            "jsonrpc": "2.0",
            "id": 1,
            "result": {"content": "test content"}
        }

        with patch('websockets.connect') as mock_connect:
            mock_ws = AsyncMock()
            mock_ws.send = AsyncMock()
            mock_ws.recv = AsyncMock(return_value='{"jsonrpc": "2.0", "id": 1, "result": {"content": "test content"}}')
            mock_connect.return_value.__aenter__.return_value = mock_ws

            result = await client.call("getContent")

            assert result["success"] is True
            assert result["result"]["content"] == "test content"

    @pytest.mark.asyncio
    async def test_error_response(self, client):
        """Test handling of JSON-RPC error response."""
        with patch('websockets.connect') as mock_connect:
            mock_ws = AsyncMock()
            mock_ws.send = AsyncMock()
            mock_ws.recv = AsyncMock(return_value='{"jsonrpc": "2.0", "id": 1, "error": {"code": -32601, "message": "Method not found"}}')
            mock_connect.return_value.__aenter__.return_value = mock_ws

            result = await client.call("invalidMethod")

            assert result["success"] is False
            assert "Method not found" in result["error"]

    @pytest.mark.asyncio
    async def test_connection_failure(self, client):
        """Test connection failure handling."""
        with patch('websockets.connect', side_effect=Exception("Connection refused")):
            result = await client.call("getContent")

            assert result["success"] is False
            assert "Connection failed" in result["error"]


class TestTyporaControlOperations:
    """Test individual typora_control operations."""

    @pytest.fixture
    def mock_client(self):
        """Mock the global typora_client."""
        with patch('basic_memory.mcp.tools.typora_control.typora_client') as mock_client:
            yield mock_client

    @pytest.mark.asyncio
    async def test_export_operation(self, mock_client):
        """Test export operation."""
        mock_client.call.return_value = {"success": True, "result": None}

        result = await typora_control("export", format="pdf", output_path="/test/file.pdf")

        assert "✅ **Document Exported Successfully!**" in result
        mock_client.call.assert_called_once_with("export", {
            "format": "pdf",
            "outputPath": "/test/file.pdf",
            "includeImages": True,
            "embedStyles": True,
            "embedImages": True,
            "keepSource": False
        })

    @pytest.mark.asyncio
    async def test_get_content_operation(self, mock_client):
        """Test get_content operation."""
        mock_client.call.return_value = {"success": True, "result": "# Test Content\n\nSome content"}

        result = await typora_control("get_content")

        assert "📄 **Document Content Retrieved**" in result
        assert "Test Content" in result

    @pytest.mark.asyncio
    async def test_set_content_operation(self, mock_client):
        """Test set_content operation."""
        mock_client.call.return_value = {"success": True, "result": None}

        result = await typora_control("set_content", content="New content")

        assert "✅ **Document Content Updated**" in result
        mock_client.call.assert_called_once_with("setContent", {"content": "New content"})

    @pytest.mark.asyncio
    async def test_insert_text_operation(self, mock_client):
        """Test insert_text operation."""
        mock_client.call.return_value = {"success": True, "result": None}

        result = await typora_control("insert_text", text="New text")

        assert "✅ **Text Inserted Successfully**" in result
        mock_client.call.assert_called_once_with("insertText", {"text": "New text"})

    @pytest.mark.asyncio
    async def test_open_file_operation(self, mock_client):
        """Test open_file operation."""
        mock_client.call.return_value = {"success": True, "result": None}

        result = await typora_control("open_file", file_path="/test/file.md")

        assert "✅ **File Opened in Typora**" in result
        mock_client.call.assert_called_once_with("openFile", {"path": "/test/file.md"})

    @pytest.mark.asyncio
    async def test_batch_export_operation(self, mock_client):
        """Test batch_export operation."""
        # Mock file opening and export calls
        mock_client.call.side_effect = [
            {"success": True},  # openFile call 1
            {"success": True},  # export call 1
            {"success": True},  # openFile call 2
            {"success": True},  # export call 2
        ]

        files = ["/test/file1.md", "/test/file2.md"]
        result = await typora_control("batch_export", files=files, format="html", output_path="/exports")

        assert "📦 **Batch Export Completed**" in result
        assert "Files Processed: 2" in result
        assert "Successful Exports: 2" in result

    @pytest.mark.asyncio
    async def test_template_apply_operation(self, mock_client):
        """Test template_apply operation."""
        mock_client.call.return_value = {"success": True, "result": None}

        result = await typora_control("template_apply", template_name="research_note")

        assert "✅ **Template Applied Successfully**" in result
        assert "research_note" in result

        # Check that setContent was called with template content
        call_args = mock_client.call.call_args
        assert call_args[0][0] == "setContent"
        assert "# Research Note" in call_args[0][1]["content"]

    @pytest.mark.asyncio
    async def test_unknown_operation(self, mock_client):
        """Test unknown operation handling."""
        result = await typora_control("unknown_operation")

        assert "❌ **Unknown Operation**: unknown_operation" in result
        assert "Available Operations:" in result
        assert "export" in result

    @pytest.mark.asyncio
    async def test_content_analysis_operation(self, mock_client):
        """Test content_analysis operation."""
        mock_client.call.return_value = {
            "success": True,
            "result": "# Heading 1\n\nSome content\n\n## Heading 2\n\n[Link](url)\n\n```code\nblock\n```"
        }

        result = await typora_control("content_analysis")

        assert "📊 **Document Analysis**" in result
        assert "Headings: 2" in result
        assert "Links: 1" in result
        assert "Code Blocks: 1" in result


class TestUtilityFunctions:
    """Test utility functions."""

    @pytest.mark.asyncio
    async def test_check_typora_connection_success(self):
        """Test successful connection check."""
        with patch('basic_memory.mcp.tools.typora_control.typora_client') as mock_client:
            mock_client.call.return_value = {"success": True}

            result = await check_typora_connection()
            assert result is True

    @pytest.mark.asyncio
    async def test_check_typora_connection_failure(self):
        """Test failed connection check."""
        with patch('basic_memory.mcp.tools.typora_control.typora_client') as mock_client:
            mock_client.call.side_effect = Exception("Connection failed")

            result = await check_typora_connection()
            assert result is False

    @pytest.mark.asyncio
    async def test_get_typora_status_connected(self):
        """Test getting Typora status when connected."""
        with patch('basic_memory.mcp.tools.typora_control.check_typora_connection', return_value=True), \
             patch('basic_memory.mcp.tools.typora_control.typora_client') as mock_client:

            mock_client.call.side_effect = [
                {"success": True, "result": {"filePath": "/test/file.md", "title": "Test"}},  # metadata
                {"success": True, "result": {"current": "dark", "themes": ["light", "dark"]}}  # themes
            ]

            status = await get_typora_status()

            assert status["connection"] is True
            assert status["current_file"] == "/test/file.md"
            assert status["theme"] == "dark"

    @pytest.mark.asyncio
    async def test_get_typora_status_disconnected(self):
        """Test getting Typora status when disconnected."""
        with patch('basic_memory.mcp.tools.typora_control.check_typora_connection', return_value=False):
            status = await get_typora_status()

            assert status["connection"] is False
            assert status["current_file"] is None
            assert status["theme"] is None


class TestErrorHandling:
    """Test error handling scenarios."""

    @pytest.mark.asyncio
    async def test_export_missing_format(self):
        """Test export operation with missing format."""
        result = await typora_control("export", output_path="/test/file.pdf")
        assert "❌ Export requires 'format' parameter" in result

    @pytest.mark.asyncio
    async def test_export_missing_output_path(self):
        """Test export operation with missing output path."""
        result = await typora_control("export", format="pdf")
        assert "❌ Export requires 'output_path' parameter" in result

    @pytest.mark.asyncio
    async def test_set_content_missing_content(self):
        """Test set_content operation with missing content."""
        result = await typora_control("set_content")
        assert "❌ set_content requires 'content' parameter" in result

    @pytest.mark.asyncio
    async def test_insert_text_missing_text(self):
        """Test insert_text operation with missing text."""
        result = await typora_control("insert_text")
        assert "❌ insert_text requires 'text' parameter" in result

    @pytest.mark.asyncio
    async def test_open_file_missing_path(self):
        """Test open_file operation with missing file path."""
        result = await typora_control("open_file")
        assert "❌ open_file requires 'file_path' parameter" in result

    @pytest.mark.asyncio
    async def test_batch_export_missing_files(self):
        """Test batch_export operation with missing files."""
        result = await typora_control("batch_export", format="pdf")
        assert "❌ batch_export requires 'files' parameter" in result

    @pytest.mark.asyncio
    async def test_template_apply_missing_name(self):
        """Test template_apply operation with missing template name."""
        result = await typora_control("template_apply")
        assert "❌ template_apply requires 'template_name' parameter" in result

    @pytest.mark.asyncio
    async def test_template_apply_unknown_template(self):
        """Test template_apply operation with unknown template."""
        result = await typora_control("template_apply", template_name="unknown")
        assert "❌ **Unknown Template**" in result
        assert "Available Templates:" in result
