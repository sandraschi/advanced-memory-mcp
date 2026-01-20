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

from advanced_memory.mcp.tools import (
    adn_content,
    adn_export,
    adn_import,
    adn_knowledge,
    adn_llm,
    adn_navigation,
    adn_project,
    adn_search,
)

# Note: adn_editor is deprecated and only available in FULL_TOOLS_MODE

# Extract the actual functions from FunctionTool objects
adn_content_fn = adn_content.fn
adn_project_fn = adn_project.fn
adn_export_fn = adn_export.fn
adn_import_fn = adn_import.fn
adn_search_fn = adn_search.fn
adn_knowledge_fn = adn_knowledge.fn
adn_navigation_fn = adn_navigation.fn
adn_llm_fn = adn_llm.fn


class TestPortmanteauToolRegistration:
    """Test that all portmanteau tools are properly registered."""

    def test_adn_content_registration(self):
        """Test adn_content tool registration."""
        assert hasattr(adn_content, "name")
        assert adn_content.name == "adn_content"
        assert hasattr(adn_content, "fn")
        assert callable(adn_content.fn)

    def test_adn_project_registration(self):
        """Test adn_project tool registration."""
        assert hasattr(adn_project, "name")
        assert adn_project.name == "adn_project"
        assert hasattr(adn_project, "fn")
        assert callable(adn_project.fn)

    def test_adn_export_registration(self):
        """Test adn_export tool registration."""
        assert hasattr(adn_export, "name")
        assert adn_export.name == "adn_export"
        assert hasattr(adn_export, "fn")
        assert callable(adn_export.fn)

    def test_adn_import_registration(self):
        """Test adn_import tool registration."""
        assert hasattr(adn_import, "name")
        assert adn_import.name == "adn_import"
        assert hasattr(adn_import, "fn")
        assert callable(adn_import.fn)

    def test_adn_search_registration(self):
        """Test adn_search tool registration."""
        assert hasattr(adn_search, "name")
        assert adn_search.name == "adn_search"
        assert hasattr(adn_search, "fn")
        assert callable(adn_search.fn)

    def test_adn_knowledge_registration(self):
        """Test adn_knowledge tool registration."""
        assert hasattr(adn_knowledge, "name")
        assert adn_knowledge.name == "adn_knowledge"
        assert hasattr(adn_knowledge, "fn")
        assert callable(adn_knowledge.fn)

    def test_adn_navigation_registration(self):
        """Test adn_navigation tool registration."""
        assert hasattr(adn_navigation, "name")
        assert adn_navigation.name == "adn_navigation"
        assert hasattr(adn_navigation, "fn")
        assert callable(adn_navigation.fn)

    def test_adn_llm_registration(self):
        """Test adn_llm tool registration."""
        assert hasattr(adn_llm, "name")
        assert adn_llm.name == "adn_llm"
        assert hasattr(adn_llm, "fn")
        assert callable(adn_llm.fn)

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
        """Test adn_search function signature."""
        import inspect

        sig = inspect.signature(adn_search_fn)
        params = list(sig.parameters.keys())
        assert "operation" in params
        assert "query" in params
        assert "source_path" in params

    def test_adn_knowledge_signature(self):
        """Test adn_knowledge function signature."""
        import inspect

        sig = inspect.signature(adn_knowledge_fn)
        params = list(sig.parameters.keys())
        assert "operation" in params
        assert "filters" in params
        assert "action" in params

    def test_adn_navigation_signature(self):
        """Test adn_navigation function signature."""
        import inspect

        sig = inspect.signature(adn_navigation_fn)
        params = list(sig.parameters.keys())
        assert "operation" in params
        assert "url" in params
        assert "dir_name" in params

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
        assert "Invalid operation" in result["message"]

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
        assert "Invalid operation" in result["message"]

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
        assert "Invalid operation" in result["message"]

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
        assert "Invalid operation" in result["message"]

    def test_adn_import_missing_parameters(self):
        """Test adn_import with missing required parameters."""
        import asyncio

        with pytest.raises(TypeError, match="missing 1 required positional argument"):
            asyncio.run(adn_import_fn(operation="obsidian"))


class TestAdnSearchBasic:
    """Test basic adn_search portmanteau tool functionality."""

    def test_adn_search_invalid_operation(self):
        """Test adn_search with invalid operation."""
        import asyncio

        result = asyncio.run(adn_search_fn(operation="invalid", query="test"))
        assert isinstance(result, dict)
        assert result["success"] is False
        assert "error" in result
        assert "error_code" in result
        assert "message" in result
        assert "recovery_options" in result
        assert "Invalid operation" in result["message"]

    def test_adn_search_missing_parameters(self):
        """Test adn_search with missing required parameters."""
        import asyncio

        with pytest.raises(TypeError, match="missing 1 required positional argument"):
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
        assert "Invalid operation" in result["message"]


class TestAdnNavigationBasic:
    """Test basic adn_navigation portmanteau tool functionality."""

    def test_adn_navigation_invalid_operation(self):
        """Test adn_navigation with invalid operation."""
        import asyncio

        result = asyncio.run(adn_navigation_fn(operation="invalid"))
        assert isinstance(result, dict)
        assert result["success"] is False
        assert "error" in result
        assert "error_code" in result
        assert "message" in result
        assert "recovery_options" in result
        assert "Invalid operation" in result["message"]


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
        assert result["operation"] == expected_operation, (
            f"Operation should be '{expected_operation}'"
        )
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
        result = asyncio.run(
            self._test_tool_error_response(adn_content_fn, operation="invalid_operation")
        )
        assert "Invalid operation" in result["message"]

        # Test missing parameters
        result = asyncio.run(self._test_tool_error_response(adn_content_fn, operation="write"))
        assert "requires" in result["message"]

    def test_adn_project_structured_error_responses(self):
        """Test adn_project returns structured error responses."""
        import asyncio

        # Test invalid operation
        result = asyncio.run(
            self._test_tool_error_response(adn_project_fn, operation="invalid_operation")
        )
        assert "Invalid operation" in result["message"]

        # Test missing parameters
        result = asyncio.run(self._test_tool_error_response(adn_project_fn, operation="create"))
        assert "requires" in result["message"]

    def test_adn_export_structured_error_responses(self):
        """Test adn_export returns structured error responses."""
        import asyncio

        # Test invalid operation
        result = asyncio.run(
            self._test_tool_error_response(
                adn_export_fn, operation="invalid_operation", export_path="/tmp/test"
            )
        )
        assert "Invalid operation" in result["message"]

    def test_adn_import_structured_error_responses(self):
        """Test adn_import returns structured error responses."""
        import asyncio

        # Test invalid operation
        result = asyncio.run(
            self._test_tool_error_response(
                adn_import_fn, operation="invalid_operation", source_path="/tmp/test"
            )
        )
        assert "Invalid operation" in result["message"]

    def test_adn_search_structured_error_responses(self):
        """Test adn_search returns structured error responses."""
        import asyncio

        # Test invalid operation
        result = asyncio.run(
            self._test_tool_error_response(
                adn_search_fn, operation="invalid_operation", query="test"
            )
        )
        assert "Invalid operation" in result["message"]

    def test_adn_knowledge_structured_error_responses(self):
        """Test adn_knowledge returns structured error responses."""
        import asyncio

        # Test invalid operation
        result = asyncio.run(
            self._test_tool_error_response(adn_knowledge_fn, operation="invalid_operation")
        )
        assert "Invalid operation" in result["message"]

    def test_adn_navigation_structured_error_responses(self):
        """Test adn_navigation returns structured error responses."""
        import asyncio

        # Test invalid operation
        result = asyncio.run(
            self._test_tool_error_response(adn_navigation_fn, operation="invalid_operation")
        )
        assert "Invalid operation" in result["message"]

    def test_all_tools_return_dict_responses(self):
        """Test that all tools return dict responses (not strings)."""
        import asyncio

        tools_to_test = [
            (adn_content_fn, {"operation": "invalid"}),
            (adn_project_fn, {"operation": "invalid"}),
            (adn_export_fn, {"operation": "invalid", "export_path": "/tmp"}),
            (adn_import_fn, {"operation": "invalid", "source_path": "/tmp"}),
            (adn_search_fn, {"operation": "invalid", "query": "test"}),
            (adn_knowledge_fn, {"operation": "invalid"}),
            (adn_navigation_fn, {"operation": "invalid"}),
            (adn_llm_fn, {"operation": "invalid"}),
        ]

        for tool_fn, kwargs in tools_to_test:
            result = asyncio.run(tool_fn(**kwargs))
            assert isinstance(result, dict), (
                f"{tool_fn.__name__} should return dict, got {type(result)}"
            )
            assert "success" in result, f"{tool_fn.__name__} response should have 'success' field"
