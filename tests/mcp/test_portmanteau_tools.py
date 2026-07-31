"""Test portmanteau tools for Advanced Memory MCP.

This module tests the consolidated portmanteau tools that reduce the MCP tool count
from 40+ individual tools to just 8 consolidated tools for Cursor IDE compatibility.

Tests verify:
- Tool registration and signatures
- Structured response format (FastMCP 2.14.3 compliance)
- Error handling with recovery options
- Parameter validation
"""

import pytest

# Import tool callables from defining modules (package __init__ may not re-export all names).
from advanced_memory.mcp.tools.adn_export import adn_export
from advanced_memory.mcp.tools.adn_import import adn_import
from advanced_memory.mcp.tools.adn_llm import adn_llm
from advanced_memory.mcp.tools.adn_navigation import adn_nav
from advanced_memory.mcp.tools.adn_search import adn_search
from advanced_memory.mcp.tools.content_manager import (
    adn_content,
    adn_corpus_qc,
    adn_note_ai,
    adn_notes,
)
from advanced_memory.mcp.tools.portmanteau_knowledge import adn_knowledge
from advanced_memory.mcp.tools.portmanteau_project import adn_project

# Note: adn_editor is deprecated and only available in FULL_TOOLS_MODE

# Extract the actual functions from FunctionTool objects (FastMCP may return fn or Tool)
adn_content_fn = getattr(adn_content, "fn", adn_content)
adn_notes_fn = getattr(adn_notes, "fn", adn_notes)
adn_note_ai_fn = getattr(adn_note_ai, "fn", adn_note_ai)
adn_corpus_qc_fn = getattr(adn_corpus_qc, "fn", adn_corpus_qc)
adn_project_fn = getattr(adn_project, "fn", adn_project)
adn_export_fn = getattr(adn_export, "fn", adn_export)
adn_import_fn = getattr(adn_import, "fn", adn_import)
adn_search_fn = getattr(adn_search, "fn", adn_search)
adn_knowledge_fn = getattr(adn_knowledge, "fn", adn_knowledge)
adn_nav_fn = getattr(adn_nav, "fn", adn_nav)
adn_llm_fn = getattr(adn_llm, "fn", adn_llm)


class TestPortmanteauToolRegistration:
    """Test that all portmanteau tools are properly registered."""

    def test_adn_content_registration(self):
        """Test adn_content tool registration."""
        if hasattr(adn_content, "name"):
            assert adn_content.name == "adn_content"
        assert callable(adn_content_fn)
        assert adn_content_fn.__name__ == "adn_content"

    def test_adn_notes_registration(self):
        """Split portmanteau: note CRUD/capture."""
        assert callable(adn_notes_fn)
        assert adn_notes_fn.__name__ == "adn_notes"

    def test_adn_note_ai_registration(self):
        """Split portmanteau: LLM note ops."""
        assert callable(adn_note_ai_fn)
        assert adn_note_ai_fn.__name__ == "adn_note_ai"

    def test_adn_corpus_qc_registration(self):
        """Split portmanteau: corpus quality sweeps."""
        assert callable(adn_corpus_qc_fn)
        assert adn_corpus_qc_fn.__name__ == "adn_corpus_qc"

    def test_adn_project_registration(self):
        """Test adn_project tool registration."""
        if hasattr(adn_project, "name"):
            assert adn_project.name == "adn_project"
        assert callable(adn_project_fn)
        assert adn_project_fn.__name__ == "adn_project"

    def test_adn_export_registration(self):
        """Test adn_export tool registration."""
        if hasattr(adn_export, "name"):
            assert adn_export.name == "adn_export"
        assert callable(adn_export_fn)
        assert adn_export_fn.__name__ == "adn_export"

    def test_adn_import_registration(self):
        """Test adn_import tool registration."""
        if hasattr(adn_import, "name"):
            assert adn_import.name == "adn_import"
        assert callable(adn_import_fn)

    def test_adn_search_registration(self):
        """Test adn_search tool registration."""
        if hasattr(adn_search, "name"):
            assert adn_search.name == "adn_search"
        assert callable(adn_search_fn)
        assert adn_search_fn.__name__ == "adn_search"

    def test_adn_knowledge_registration(self):
        """Test adn_knowledge tool registration."""
        if hasattr(adn_knowledge, "name"):
            assert adn_knowledge.name == "adn_knowledge"
        assert callable(adn_knowledge_fn)

    def test_adn_nav_registration(self):
        """Test adn_nav tool registration."""
        if hasattr(adn_nav, "name"):
            assert adn_nav.name == "adn_nav"
        assert callable(adn_nav_fn)

    def test_adn_llm_registration(self):
        """Test adn_llm tool registration."""
        if hasattr(adn_llm, "name"):
            assert adn_llm.name == "adn_llm"
        assert callable(adn_llm_fn)

    @pytest.mark.skip(reason="adn_editor is deprecated and only available in FULL_TOOLS_MODE")
    def test_adn_editor_registration(self):
        """Test adn_editor tool registration."""
        # Note: adn_editor is deprecated, skip this test
        pass


class TestPortmanteauToolSignatures:
    """Test that all portmanteau tools have correct signatures."""

    def test_adn_content_signature(self):
        """Test adn_content function signature."""
        import inspect

        sig = inspect.signature(adn_content_fn)
        params = list(sig.parameters.keys())
        assert "operation" in params
        assert "identifier" in params
        assert "content" in params
        assert "folder" in params

    def test_adn_project_signature(self):
        """Test adn_project function signature."""
        import inspect

        sig = inspect.signature(adn_project_fn)
        params = list(sig.parameters.keys())
        assert "operation" in params
        assert "project_name" in params
        assert "project_path" in params

    def test_adn_export_signature(self):
        """Test adn_export function signature."""
        import inspect

        sig = inspect.signature(adn_export_fn)
        params = list(sig.parameters.keys())
        assert "operation" in params
        assert "export_path" in params
        assert "format_type" in params

    def test_adn_import_signature(self):
        """Test adn_import function signature."""
        import inspect

        sig = inspect.signature(adn_import_fn)
        params = list(sig.parameters.keys())
        assert "operation" in params
        assert "source_path" in params
        assert "destination_folder" in params

    def test_adn_search_signature(self):
        """Test adn_search function signature (model-based op dispatch)."""
        import inspect

        sig = inspect.signature(adn_search_fn)
        params = list(sig.parameters.keys())
        assert "op" in params

    def test_adn_knowledge_signature(self):
        """Test adn_knowledge function signature."""
        import inspect

        sig = inspect.signature(adn_knowledge_fn)
        params = list(sig.parameters.keys())
        assert "operation" in params
        assert "identifier" in params
        assert "query" in params

    def test_adn_nav_signature(self):
        """Test adn_nav function signature (model-based op dispatch)."""
        import inspect

        sig = inspect.signature(adn_nav_fn)
        params = list(sig.parameters.keys())
        assert "op" in params

    def test_adn_llm_signature(self):
        """Test adn_llm function signature."""
        import inspect

        sig = inspect.signature(adn_llm_fn)
        params = list(sig.parameters.keys())
        assert "operation" in params
        assert "provider" in params
        assert "model" in params

    @pytest.mark.skip(reason="adn_editor is deprecated and only available in FULL_TOOLS_MODE")
    def test_adn_editor_signature(self):
        """Test adn_editor function signature."""
        # Note: adn_editor is deprecated, skip this test
        pass


class TestAdnContentBasic:
    """Test basic adn_content portmanteau tool functionality."""

    def test_adn_content_invalid_operation(self):
        """Test adn_content with invalid operation."""
        import asyncio

        result = asyncio.run(adn_content_fn(operation="invalid"))
        assert isinstance(result, dict)
        assert result["success"] is False
        assert "error" in result
        assert "error_code" in result
        assert "message" in result
        assert "recovery_options" in result
        msg = result["message"]
        assert (
            "Invalid operation" in msg
            or "Unknown operation" in msg
            or "Unknown project operation" in msg
            or "not supported" in msg.lower()
        )

    def test_adn_content_missing_parameters(self):
        """Test adn_content with missing required parameters."""
        import asyncio

        result = asyncio.run(adn_content_fn(operation="write"))
        assert isinstance(result, dict)
        assert result["success"] is False
        assert "error" in result
        assert "error_code" in result
        assert "message" in result
        assert "recovery_options" in result
        assert "requires" in result["message"]


class TestAdnProjectBasic:
    """Test basic adn_project portmanteau tool functionality."""

    def test_adn_project_invalid_operation(self):
        """Test adn_project with invalid operation."""
        import asyncio

        result = asyncio.run(adn_project_fn(operation="invalid"))
        assert isinstance(result, dict)
        assert result["success"] is False
        assert "error" in result
        assert "error_code" in result
        assert "message" in result
        assert "recovery_options" in result
        msg = result["message"]
        assert (
            "Invalid operation" in msg
            or "Unknown operation" in msg
            or "Unknown project operation" in msg
            or "not supported" in msg.lower()
        )

    def test_adn_project_missing_parameters(self):
        """Test adn_project with missing required parameters."""
        import asyncio

        result = asyncio.run(adn_project_fn(operation="create"))
        assert isinstance(result, dict)
        assert result["success"] is False
        assert "error" in result
        assert "error_code" in result
        assert "message" in result
        assert "recovery_options" in result
        assert "requires" in result["message"]


class TestAdnExportBasic:
    """Test basic adn_export portmanteau tool functionality."""

    def test_adn_export_invalid_operation(self):
        """Test adn_export with invalid operation."""
        import asyncio

        result = asyncio.run(adn_export_fn(operation="invalid", export_path="/tmp/test"))
        assert isinstance(result, dict)
        assert result["success"] is False
        assert "error" in result
        assert "error_code" in result
        assert "message" in result
        assert "recovery_options" in result
        msg = result["message"]
        assert (
            "Invalid operation" in msg
            or "Unknown operation" in msg
            or "Unknown project operation" in msg
            or "not supported" in msg.lower()
        )

    @pytest.mark.skip(reason="FunctionTool API changed - needs test refactor")
    def test_adn_export_missing_parameters(self):
        """Test adn_export with missing required parameters."""
        import asyncio

        with pytest.raises(TypeError, match="missing 1 required positional argument"):
            asyncio.run(adn_export_fn(operation="pandoc"))


class TestAdnImportBasic:
    """Test basic adn_import portmanteau tool functionality."""

    def test_adn_import_invalid_operation(self):
        """Test adn_import with invalid operation."""
        import asyncio

        result = asyncio.run(adn_import_fn(operation="invalid", source_path="/tmp/test"))
        assert isinstance(result, dict)
        assert result["success"] is False
        assert "error" in result
        assert "error_code" in result
        assert "message" in result
        assert "recovery_options" in result
        msg = result["message"]
        assert (
            "Invalid operation" in msg
            or "Unknown operation" in msg
            or "Unknown project operation" in msg
            or "not supported" in msg.lower()
        )

    def test_adn_import_missing_parameters(self):
        """Test adn_import with missing required parameters."""
        import asyncio

        with pytest.raises(TypeError, match="missing 1 required positional argument"):
            asyncio.run(adn_import_fn(operation="obsidian"))


class TestAdnSearchBasic:
    """Test basic adn_search portmanteau tool functionality."""

    def test_adn_search_invalid_operation(self):
        """Test adn_search rejects invalid operation (model-based op dispatch)."""
        import asyncio

        with pytest.raises((TypeError, ValueError)):
            asyncio.run(adn_search_fn(operation="invalid", query="test"))

    def test_adn_search_missing_parameters(self):
        """Test adn_search with missing required parameters."""
        import asyncio

        with pytest.raises((TypeError, ValueError)):
            asyncio.run(adn_search_fn(operation="notes"))


class TestAdnKnowledgeBasic:
    """Test basic adn_knowledge portmanteau tool functionality."""

    def test_adn_knowledge_invalid_operation(self):
        """Test adn_knowledge with invalid operation."""
        import asyncio

        result = asyncio.run(adn_knowledge_fn(operation="invalid"))
        assert isinstance(result, dict)
        assert result["success"] is False
        assert "error" in result
        assert "error_code" in result
        assert "message" in result
        assert "recovery_options" in result
        msg = result["message"]
        assert (
            "Invalid operation" in msg
            or "Unknown operation" in msg
            or "Unknown project operation" in msg
            or "not supported" in msg.lower()
        )


class TestAdnNavigationBasic:
    """Test basic adn_nav portmanteau tool functionality."""

    def test_adn_nav_invalid_operation(self):
        """Test adn_nav rejects invalid operation (model-based op dispatch)."""
        import asyncio

        with pytest.raises((TypeError, ValueError)):
            asyncio.run(adn_nav_fn(operation="invalid"))


class TestAdnEditorBasic:
    """Test basic adn_editor portmanteau tool functionality."""

    @pytest.mark.skip(reason="adn_editor is deprecated and only available in FULL_TOOLS_MODE")
    def test_adn_editor_invalid_operation(self):
        """Test adn_editor with invalid operation."""
        # Note: adn_editor is deprecated, skip this test
        pass


class TestStructuredResponses:
    """Test FastMCP 2.14.3 structured response format compliance.

    All portmanteau tools must return structured dict responses with:
    - success: bool
    - operation: str (for successful operations)
    - summary: str (for successful operations)
    - result: dict (for successful operations)
    - error: str (for failed operations)
    - error_code: str (for failed operations)
    - message: str (for failed operations)
    - recovery_options: list (for failed operations)
    """

    def _assert_success_response(self, result: dict, expected_operation: str):
        """Assert that a response follows the success format."""
        assert isinstance(result, dict), f"Response should be dict, got {type(result)}"
        assert result["success"] is True, f"Success should be True, got {result.get('success')}"
        assert "operation" in result, "Success response should have 'operation' field"
        assert result["operation"] == expected_operation, f"Operation should be '{expected_operation}'"
        assert "summary" in result, "Success response should have 'summary' field"
        assert "result" in result, "Success response should have 'result' field"
        assert isinstance(result["result"], dict), "Result field should be a dict"

    def _assert_error_response(self, result: dict):
        """Assert that a response follows the error format."""
        assert isinstance(result, dict), f"Response should be dict, got {type(result)}"
        assert result["success"] is False, f"Success should be False, got {result.get('success')}"
        assert "error" in result, "Error response should have 'error' field"
        assert "error_code" in result, "Error response should have 'error_code' field"
        assert "message" in result, "Error response should have 'message' field"
        assert "recovery_options" in result, "Error response should have 'recovery_options' field"
        assert isinstance(result["recovery_options"], list), "recovery_options should be a list"

    async def _test_tool_error_response(self, tool_fn, **kwargs):
        """Helper to test error response format."""
        result = await tool_fn(**kwargs)
        self._assert_error_response(result)
        return result

    def test_adn_content_structured_error_responses(self):
        """Test adn_content returns structured error responses."""
        import asyncio

        # Test invalid operation
        result = asyncio.run(self._test_tool_error_response(adn_content_fn, operation="invalid_operation"))
        msg = result["message"]
        assert (
            "Invalid operation" in msg
            or "Unknown operation" in msg
            or "Unknown project operation" in msg
            or "not supported" in msg.lower()
        )

        # Test missing parameters
        result = asyncio.run(self._test_tool_error_response(adn_content_fn, operation="write"))
        assert "requires" in result["message"]

    def test_adn_project_structured_error_responses(self):
        """Test adn_project returns structured error responses."""
        import asyncio

        # Test invalid operation
        result = asyncio.run(self._test_tool_error_response(adn_project_fn, operation="invalid_operation"))
        msg = result["message"]
        assert (
            "Invalid operation" in msg
            or "Unknown operation" in msg
            or "Unknown project operation" in msg
            or "not supported" in msg.lower()
        )

        # Test missing parameters
        result = asyncio.run(self._test_tool_error_response(adn_project_fn, operation="create"))
        assert "requires" in result["message"]

    def test_adn_export_structured_error_responses(self):
        """Test adn_export returns structured error responses."""
        import asyncio

        # Test invalid operation
        result = asyncio.run(
            self._test_tool_error_response(adn_export_fn, operation="invalid_operation", export_path="/tmp/test")
        )
        msg = result["message"]
        assert (
            "Invalid operation" in msg
            or "Unknown operation" in msg
            or "Unknown project operation" in msg
            or "not supported" in msg.lower()
        )

    def test_adn_import_structured_error_responses(self):
        """Test adn_import returns structured error responses."""
        import asyncio

        # Test invalid operation
        result = asyncio.run(
            self._test_tool_error_response(adn_import_fn, operation="invalid_operation", source_path="/tmp/test")
        )
        msg = result["message"]
        assert (
            "Invalid operation" in msg
            or "Unknown operation" in msg
            or "Unknown project operation" in msg
            or "not supported" in msg.lower()
        )

    def test_adn_search_structured_error_responses(self):
        """Test adn_search rejects invalid operations via model validation."""
        import asyncio

        with pytest.raises((TypeError, ValueError)):
            asyncio.run(self._test_tool_error_response(adn_search_fn, operation="invalid_operation", query="test"))

    def test_adn_knowledge_structured_error_responses(self):
        """Test adn_knowledge returns structured error responses."""
        import asyncio

        # Test invalid operation
        result = asyncio.run(self._test_tool_error_response(adn_knowledge_fn, operation="invalid_operation"))
        msg = result["message"]
        assert (
            "Invalid operation" in msg
            or "Unknown operation" in msg
            or "Unknown project operation" in msg
            or "not supported" in msg.lower()
        )

    def test_adn_nav_structured_error_responses(self):
        """Test adn_nav rejects invalid operations via model validation."""
        import asyncio

        with pytest.raises((TypeError, ValueError)):
            asyncio.run(self._test_tool_error_response(adn_nav_fn, operation="invalid_operation"))

    def test_all_tools_return_dict_responses(self):
        """Test that kwargs-dispatch tools return dict responses (not strings)."""
        import asyncio

        tools_to_test = [
            (adn_content_fn, {"operation": "invalid"}),
            (adn_project_fn, {"operation": "invalid"}),
            (adn_export_fn, {"operation": "invalid", "export_path": "/tmp"}),
            (adn_import_fn, {"operation": "invalid", "source_path": "/tmp"}),
            (adn_knowledge_fn, {"operation": "invalid"}),
            (adn_llm_fn, {"operation": "invalid"}),
        ]

        for tool_fn, kwargs in tools_to_test:
            result = asyncio.run(tool_fn(**kwargs))
            assert isinstance(result, dict), f"{tool_fn.__name__} should return dict, got {type(result)}"
            assert "success" in result, f"{tool_fn.__name__} response should have 'success' field"
