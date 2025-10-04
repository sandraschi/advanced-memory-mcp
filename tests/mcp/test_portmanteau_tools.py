"""Test portmanteau tools for Advanced Memory MCP.

This module tests the consolidated portmanteau tools that reduce the MCP tool count
from 40+ individual tools to just 8 consolidated tools for Cursor IDE compatibility.
"""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from advanced_memory.mcp.tools import (
    adn_content, adn_project, adn_export, adn_import, 
    adn_search, adn_knowledge, adn_navigation, adn_editor
)

# Extract the actual functions from FunctionTool objects
adn_content_fn = adn_content.fn
adn_project_fn = adn_project.fn
adn_export_fn = adn_export.fn
adn_import_fn = adn_import.fn
adn_search_fn = adn_search.fn
adn_knowledge_fn = adn_knowledge.fn
adn_navigation_fn = adn_navigation.fn
adn_editor_fn = adn_editor.fn


class TestPortmanteauToolRegistration:
    """Test that all portmanteau tools are properly registered."""
    
    def test_adn_content_registration(self):
        """Test adn_content tool registration."""
        assert hasattr(adn_content, 'name')
        assert adn_content.name == "adn_content"
        assert hasattr(adn_content, 'fn')
        assert callable(adn_content.fn)
    
    def test_adn_project_registration(self):
        """Test adn_project tool registration."""
        assert hasattr(adn_project, 'name')
        assert adn_project.name == "adn_project"
        assert hasattr(adn_project, 'fn')
        assert callable(adn_project.fn)
    
    def test_adn_export_registration(self):
        """Test adn_export tool registration."""
        assert hasattr(adn_export, 'name')
        assert adn_export.name == "adn_export"
        assert hasattr(adn_export, 'fn')
        assert callable(adn_export.fn)
    
    def test_adn_import_registration(self):
        """Test adn_import tool registration."""
        assert hasattr(adn_import, 'name')
        assert adn_import.name == "adn_import"
        assert hasattr(adn_import, 'fn')
        assert callable(adn_import.fn)
    
    def test_adn_search_registration(self):
        """Test adn_search tool registration."""
        assert hasattr(adn_search, 'name')
        assert adn_search.name == "adn_search"
        assert hasattr(adn_search, 'fn')
        assert callable(adn_search.fn)
    
    def test_adn_knowledge_registration(self):
        """Test adn_knowledge tool registration."""
        assert hasattr(adn_knowledge, 'name')
        assert adn_knowledge.name == "adn_knowledge"
        assert hasattr(adn_knowledge, 'fn')
        assert callable(adn_knowledge.fn)
    
    def test_adn_navigation_registration(self):
        """Test adn_navigation tool registration."""
        assert hasattr(adn_navigation, 'name')
        assert adn_navigation.name == "adn_navigation"
        assert hasattr(adn_navigation, 'fn')
        assert callable(adn_navigation.fn)
    
    def test_adn_editor_registration(self):
        """Test adn_editor tool registration."""
        assert hasattr(adn_editor, 'name')
        assert adn_editor.name == "adn_editor"
        assert hasattr(adn_editor, 'fn')
        assert callable(adn_editor.fn)


class TestPortmanteauToolSignatures:
    """Test that all portmanteau tools have correct signatures."""
    
    def test_adn_content_signature(self):
        """Test adn_content function signature."""
        import inspect
        sig = inspect.signature(adn_content_fn)
        params = list(sig.parameters.keys())
        assert 'operation' in params
        assert 'identifier' in params
        assert 'content' in params
        assert 'folder' in params
    
    def test_adn_project_signature(self):
        """Test adn_project function signature."""
        import inspect
        sig = inspect.signature(adn_project_fn)
        params = list(sig.parameters.keys())
        assert 'operation' in params
        assert 'project_name' in params
        assert 'project_path' in params
    
    def test_adn_export_signature(self):
        """Test adn_export function signature."""
        import inspect
        sig = inspect.signature(adn_export_fn)
        params = list(sig.parameters.keys())
        assert 'operation' in params
        assert 'export_path' in params
        assert 'format_type' in params
    
    def test_adn_import_signature(self):
        """Test adn_import function signature."""
        import inspect
        sig = inspect.signature(adn_import_fn)
        params = list(sig.parameters.keys())
        assert 'operation' in params
        assert 'source_path' in params
        assert 'destination_folder' in params
    
    def test_adn_search_signature(self):
        """Test adn_search function signature."""
        import inspect
        sig = inspect.signature(adn_search_fn)
        params = list(sig.parameters.keys())
        assert 'operation' in params
        assert 'query' in params
        assert 'source_path' in params
    
    def test_adn_knowledge_signature(self):
        """Test adn_knowledge function signature."""
        import inspect
        sig = inspect.signature(adn_knowledge_fn)
        params = list(sig.parameters.keys())
        assert 'operation' in params
        assert 'filters' in params
        assert 'action' in params
    
    def test_adn_navigation_signature(self):
        """Test adn_navigation function signature."""
        import inspect
        sig = inspect.signature(adn_navigation_fn)
        params = list(sig.parameters.keys())
        assert 'operation' in params
        assert 'url' in params
        assert 'dir_name' in params
    
    def test_adn_editor_signature(self):
        """Test adn_editor function signature."""
        import inspect
        sig = inspect.signature(adn_editor_fn)
        params = list(sig.parameters.keys())
        assert 'operation' in params
        assert 'note_identifier' in params
        assert 'workspace_path' in params


class TestAdnContentBasic:
    """Test basic adn_content portmanteau tool functionality."""
    
    def test_adn_content_invalid_operation(self):
        """Test adn_content with invalid operation."""
        import asyncio
        result = asyncio.run(adn_content_fn(operation="invalid"))
        assert "Error" in result
        assert "Invalid operation" in result
    
    def test_adn_content_missing_parameters(self):
        """Test adn_content with missing required parameters."""
        import asyncio
        result = asyncio.run(adn_content_fn(operation="write"))
        assert "Error" in result
        assert "requires" in result


class TestAdnProjectBasic:
    """Test basic adn_project portmanteau tool functionality."""
    
    def test_adn_project_invalid_operation(self):
        """Test adn_project with invalid operation."""
        import asyncio
        result = asyncio.run(adn_project_fn(operation="invalid"))
        assert "Error" in result
        assert "Invalid operation" in result
    
    def test_adn_project_missing_parameters(self):
        """Test adn_project with missing required parameters."""
        import asyncio
        result = asyncio.run(adn_project_fn(operation="create"))
        assert "Error" in result
        assert "requires" in result


class TestAdnExportBasic:
    """Test basic adn_export portmanteau tool functionality."""
    
    def test_adn_export_invalid_operation(self):
        """Test adn_export with invalid operation."""
        import asyncio
        result = asyncio.run(adn_export_fn(operation="invalid", export_path="/tmp/test"))
        assert "Error" in result
        assert "Invalid operation" in result
    
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
        assert "Error" in result
        assert "Invalid operation" in result
    
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
        assert "Error" in result
        assert "Invalid operation" in result
    
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
        assert "Error" in result
        assert "Invalid operation" in result


class TestAdnNavigationBasic:
    """Test basic adn_navigation portmanteau tool functionality."""
    
    def test_adn_navigation_invalid_operation(self):
        """Test adn_navigation with invalid operation."""
        import asyncio
        result = asyncio.run(adn_navigation_fn(operation="invalid"))
        assert "Error" in result
        assert "Invalid operation" in result


class TestAdnEditorBasic:
    """Test basic adn_editor portmanteau tool functionality."""
    
    def test_adn_editor_invalid_operation(self):
        """Test adn_editor with invalid operation."""
        import asyncio
        result = asyncio.run(adn_editor_fn(operation="invalid"))
        assert "Error" in result
        assert "Invalid operation" in result