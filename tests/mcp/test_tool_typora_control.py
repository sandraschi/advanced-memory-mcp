"""
Tests for Typora control via json_rpc plugin.

Note: These tests require Typora with json_rpc plugin running on port 8888.
For CI/CD, these would be integration tests that require Typora setup.
"""

from unittest.mock import AsyncMock, patch

import pytest

from advanced_memory.mcp.tools.typora_control import (
    TyporaRPCClient,
    check_typora_connection,
    get_typora_status,
    typora_control,
)
from tests.mcp.tool_invoker import mcp_fn


class TestTyporaRPCClient:
    """Test the TyporaRPCClient class."""

    @pytest.fixture
    def client(self):
        """Create a test client."""
        return TyporaRPCClient()

    @pytest.mark.asyncio
    async def test_successful_call(self, client):
        """Test successful JSON-RPC call."""

        with patch("websockets.connect") as mock_connect:
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
        with patch("websockets.connect") as mock_connect:
            mock_ws = AsyncMock()
            mock_ws.send = AsyncMock()
            mock_ws.recv = AsyncMock(
                return_value='{"jsonrpc": "2.0", "id": 1, "error": {"code": -32601, "message": "Method not found"}}'
            )
            mock_connect.return_value.__aenter__.return_value = mock_ws

            result = await client.call("invalidMethod")

            assert result["success"] is False
            assert "Method not found" in result["error"]

    @pytest.mark.asyncio
    async def test_connection_failure(self, client):
        """Test connection failure handling."""
        with patch("websockets.connect", side_effect=Exception("Connection refused")):
            result = await client.call("getContent")

            assert result["success"] is False
            assert "Connection failed" in result["error"]


class TestTyporaControlOperations:
    """Test individual typora_control operations."""

    @pytest.fixture
    def mock_client(self):
        """Mock the global typora_client."""
        with patch("advanced_memory.mcp.tools.typora_control.typora_client") as mock_client:
            yield mock_client

    @pytest.mark.asyncio
    async def test_export_operation(self, mock_client):
        """Test export operation."""
        mock_client.call = AsyncMock(return_value={"success": True, "result": None})

        result = await mcp_fn(typora_control)("export", format="pdf", output_path="/test/file.pdf")

        assert "[UNICODE] **Document Exported Successfully!**" in result
        # Check that export was called with the expected parameters
        mock_client.call.assert_called_once()
        call_args = mock_client.call.call_args
        assert call_args[0][0] == "export"
        params = call_args[0][1]
        assert params["format"] == "pdf"
        assert params["outputPath"].endswith("test\\file.pdf")  # Windows path separator
        assert params["includeImages"] is True
        assert params["embedStyles"] is True
        assert params["embedImages"] is True
        assert params["keepSource"] is False
        # PDF-specific options
        assert params["pageSize"] == "A4"
        assert params["margins"] == "1cm"
        assert params["printBackground"] is True

    @pytest.mark.asyncio
    async def test_get_content_operation(self, mock_client):
        """Test get_content operation."""
        mock_client.call = AsyncMock(return_value={"success": True, "result": "# Test Content\n\nSome content"})

        result = await mcp_fn(typora_control)("get_content")

        assert "[DOC] **Document Content Retrieved**" in result
        assert "Test Content" in result

    @pytest.mark.asyncio
    async def test_set_content_operation(self, mock_client):
        """Test set_content operation."""
        mock_client.call = AsyncMock(return_value={"success": True, "result": None})

        result = await mcp_fn(typora_control)("set_content", content="New content")

        assert "[UNICODE] **Document Content Updated**" in result
        mock_client.call.assert_called_once_with("setContent", {"content": "New content"})

    @pytest.mark.asyncio
    async def test_insert_text_operation(self, mock_client):
        """Test insert_text operation."""
        mock_client.call = AsyncMock(return_value={"success": True, "result": None})

        result = await mcp_fn(typora_control)("insert_text", text="New text")

        assert "[UNICODE] **Text Inserted Successfully**" in result
        mock_client.call.assert_called_once_with("insertText", {"text": "New text"})

    @pytest.mark.asyncio
    async def test_open_file_operation(self, mock_client, tmp_path):
        """Test open_file operation."""
        # Create a test file that exists
        test_file = tmp_path / "test.md"
        test_file.write_text("# Test file")

        mock_client.call = AsyncMock(return_value={"success": True, "result": None})

        result = await mcp_fn(typora_control)("open_file", file_path=str(test_file))

        assert "[UNICODE] **File Opened in Typora**" in result
        mock_client.call.assert_called_once_with("openFile", {"path": str(test_file)})

    @pytest.mark.asyncio
    async def test_batch_export_operation(self, mock_client):
        """Test batch_export operation."""
        # Mock file opening and export calls
        mock_client.call = AsyncMock(
            side_effect=[
                {"success": True},  # openFile call 1
                {"success": True},  # export call 1
                {"success": True},  # openFile call 2
                {"success": True},  # export call 2
            ]
        )

        files = ["/test/file1.md", "/test/file2.md"]
        result = await mcp_fn(typora_control)("batch_export", files=files, format="html", output_path="/exports")

        assert "[UNICODE][UNICODE] **Batch Export Completed**" in result
        assert "**Files Processed**: 2" in result
        assert "**Successful Exports**: 2" in result

    @pytest.mark.asyncio
    async def test_template_apply_operation(self, mock_client):
        """Test template_apply operation."""
        mock_client.call = AsyncMock(return_value={"success": True, "result": None})

        result = await mcp_fn(typora_control)("template_apply", template_name="research_note")

        assert "[UNICODE] **Template Applied Successfully**" in result
        assert "research_note" in result

        # Check that setContent was called with template content
        call_args = mock_client.call.call_args
        assert call_args[0][0] == "setContent"
        assert "# Research Note" in call_args[0][1]["content"]

    @pytest.mark.asyncio
    async def test_unknown_operation(self, mock_client):
        """Test unknown operation handling."""
        result = await mcp_fn(typora_control)("unknown_operation")

        assert "[UNICODE] **Unknown Operation**: unknown_operation" in result
        assert "**Available Operations**:" in result
        assert "export" in result

    @pytest.mark.asyncio
    async def test_content_analysis_operation(self, mock_client):
        """Test content_analysis operation."""
        mock_client.call = AsyncMock(
            return_value={
                "success": True,
                "result": "# Heading 1\n\nSome content\n\n## Heading 2\n\n[Link](url)\n\n```code\nblock\n```",
            }
        )

        result = await mcp_fn(typora_control)("content_analysis")

        assert "[CHART] **Document Analysis**" in result
        assert "Headings: 2" in result
        assert "Links: 1" in result
        assert "Code Blocks: 1" in result


class TestUtilityFunctions:
    """Test utility functions."""

    @pytest.mark.asyncio
    async def test_check_typora_connection_success(self):
        """Test successful connection check."""
        with patch("advanced_memory.mcp.tools.typora_control.typora_client") as mock_client:
            mock_client.call = AsyncMock(return_value={"success": True})

            result = await check_typora_connection()
            assert result is True

    @pytest.mark.asyncio
    async def test_check_typora_connection_failure(self):
        """Test failed connection check."""
        with patch("advanced_memory.mcp.tools.typora_control.typora_client") as mock_client:
            mock_client.call.side_effect = Exception("Connection failed")

            result = await check_typora_connection()
            assert result is False

    @pytest.mark.asyncio
    async def test_get_typora_status_connected(self):
        """Test getting Typora status when connected."""
        with (
            patch(
                "advanced_memory.mcp.tools.typora_control.check_typora_connection",
                return_value=True,
            ),
            patch("advanced_memory.mcp.tools.typora_control.typora_client") as mock_client,
        ):
            mock_client.call = AsyncMock(
                side_effect=[
                    {
                        "success": True,
                        "result": {"filePath": "/test/file.md", "title": "Test"},
                    },  # metadata
                    {
                        "success": True,
                        "result": {"current": "dark", "themes": ["light", "dark"]},
                    },  # themes
                ]
            )

            status = await get_typora_status()

            assert status["connection"] is True
            assert status["current_file"] == "/test/file.md"
            assert status["theme"] == "dark"

    @pytest.mark.asyncio
    async def test_get_typora_status_disconnected(self):
        """Test getting Typora status when disconnected."""
        with patch("advanced_memory.mcp.tools.typora_control.check_typora_connection", return_value=False):
            status = await get_typora_status()

            assert status["connection"] is False
            assert status["current_file"] is None
            assert status["theme"] is None


class TestErrorHandling:
    """Test error handling scenarios."""

    @pytest.mark.asyncio
    async def test_export_missing_format(self):
        """Test export operation with missing format."""
        result = await mcp_fn(typora_control)("export", output_path="/test/file.pdf")
        assert "[UNICODE] Export requires 'format' parameter" in result

    @pytest.mark.asyncio
    async def test_export_missing_output_path(self):
        """Test export operation with missing output path."""
        result = await mcp_fn(typora_control)("export", format="pdf")
        assert "[UNICODE] Export requires 'output_path' parameter" in result

    @pytest.mark.asyncio
    async def test_set_content_missing_content(self):
        """Test set_content operation with missing content."""
        result = await mcp_fn(typora_control)("set_content")
        assert "[UNICODE] set_content requires 'content' parameter" in result

    @pytest.mark.asyncio
    async def test_insert_text_missing_text(self):
        """Test insert_text operation with missing text."""
        result = await mcp_fn(typora_control)("insert_text")
        assert "[UNICODE] insert_text requires 'text' parameter" in result

    @pytest.mark.asyncio
    async def test_open_file_missing_path(self):
        """Test open_file operation with missing file path."""
        result = await mcp_fn(typora_control)("open_file")
        assert "[UNICODE] open_file requires 'file_path' parameter" in result

    @pytest.mark.asyncio
    async def test_batch_export_missing_files(self):
        """Test batch_export operation with missing files."""
        result = await mcp_fn(typora_control)("batch_export", format="pdf")
        assert "[UNICODE] batch_export requires 'files' parameter" in result

    @pytest.mark.asyncio
    async def test_template_apply_missing_name(self):
        """Test template_apply operation with missing template name."""
        result = await mcp_fn(typora_control)("template_apply")
        assert "[UNICODE] template_apply requires 'template_name' parameter" in result

    @pytest.mark.asyncio
    async def test_template_apply_unknown_template(self):
        """Test template_apply operation with unknown template."""
        result = await mcp_fn(typora_control)("template_apply", template_name="unknown")
        assert "[UNICODE] **Unknown Template**" in result
        assert "**Available Templates**:" in result
