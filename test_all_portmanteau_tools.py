#!/usr/bin/env python3
"""Test script for all portmanteau tools to verify import, registration, and signatures."""

import sys
import os

# Add src to path
sys.path.insert(0, 'src')

def test_tool_imports():
    """Test that all portmanteau tools can be imported."""
    try:
        from advanced_memory.mcp.tools import (
            adn_content, adn_project, adn_export, adn_import, 
            adn_search, adn_knowledge, adn_navigation, adn_editor
        )
        
        print("[PASS] All portmanteau tools imported successfully")
        return True
    except Exception as e:
        print(f"[FAIL] Tool import failed: {e}")
        return False

def test_tool_registration():
    """Test that tools are properly registered with MCP."""
    try:
        from advanced_memory.mcp.tools import (
            adn_content, adn_project, adn_export, adn_import, 
            adn_search, adn_knowledge, adn_navigation, adn_editor
        )
        
        tools = [adn_content, adn_project, adn_export, adn_import, 
                adn_search, adn_knowledge, adn_navigation, adn_editor]
        
        for tool in tools:
            assert hasattr(tool, 'name'), f"{tool} missing name attribute"
            
        expected_names = ["adn_content", "adn_project", "adn_export", "adn_import", 
                         "adn_search", "adn_knowledge", "adn_navigation", "adn_editor"]
        
        for tool, expected_name in zip(tools, expected_names):
            assert tool.name == expected_name, f"{tool} has wrong name: {tool.name}"
        
        print("[PASS] All portmanteau tools properly registered with MCP")
        return True
    except Exception as e:
        print(f"[FAIL] Tool registration test failed: {e}")
        return False

def test_tool_signatures():
    """Test that tools have expected signatures."""
    try:
        from advanced_memory.mcp.tools import (
            adn_content, adn_project, adn_export, adn_import, 
            adn_search, adn_knowledge, adn_navigation, adn_editor
        )
        import inspect
        
        # Test adn_content signature
        content_manager_fn = adn_content.fn
        sig = inspect.signature(content_manager_fn)
        params = list(sig.parameters.keys())
        
        expected_params = ['operation', 'identifier', 'content', 'folder', 'tags']
        for param in expected_params:
            assert param in params, f"adn_content missing parameter: {param}"
        
        # Test adn_project signature
        project_manager_fn = adn_project.fn
        sig = inspect.signature(project_manager_fn)
        params = list(sig.parameters.keys())
        
        expected_params = ['operation', 'project_name', 'project_path', 'set_default']
        for param in expected_params:
            assert param in params, f"adn_project missing parameter: {param}"
        
        # Test adn_export signature
        export_fn = adn_export.fn
        sig = inspect.signature(export_fn)
        params = list(sig.parameters.keys())
        
        expected_params = ['operation', 'export_path', 'format_type']
        for param in expected_params:
            assert param in params, f"adn_export missing parameter: {param}"
        
        # Test adn_import signature
        import_fn = adn_import.fn
        sig = inspect.signature(import_fn)
        params = list(sig.parameters.keys())
        
        expected_params = ['operation', 'source_path', 'destination_folder']
        for param in expected_params:
            assert param in params, f"adn_import missing parameter: {param}"
        
        # Test adn_search signature
        search_fn = adn_search.fn
        sig = inspect.signature(search_fn)
        params = list(sig.parameters.keys())
        
        expected_params = ['operation', 'query', 'source_path']
        for param in expected_params:
            assert param in params, f"adn_search missing parameter: {param}"
        
        # Test adn_knowledge signature
        knowledge_fn = adn_knowledge.fn
        sig = inspect.signature(knowledge_fn)
        params = list(sig.parameters.keys())
        
        expected_params = ['operation', 'filters', 'action', 'topic']
        for param in expected_params:
            assert param in params, f"adn_knowledge missing parameter: {param}"
        
        # Test adn_navigation signature
        navigation_fn = adn_navigation.fn
        sig = inspect.signature(navigation_fn)
        params = list(sig.parameters.keys())
        
        expected_params = ['operation', 'url', 'dir_name', 'depth']
        for param in expected_params:
            assert param in params, f"adn_navigation missing parameter: {param}"
        
        # Test adn_editor signature
        editor_fn = adn_editor.fn
        sig = inspect.signature(editor_fn)
        params = list(sig.parameters.keys())
        
        expected_params = ['operation', 'note_identifier', 'workspace_path']
        for param in expected_params:
            assert param in params, f"adn_editor missing parameter: {param}"
        
        print("[PASS] All portmanteau tools have correct signatures")
        return True
    except Exception as e:
        print(f"[FAIL] Tool signature test failed: {e}")
        return False

def test_tool_count():
    """Test that we have exactly 8 portmanteau tools."""
    try:
        from advanced_memory.mcp.tools import __all__
        
        # Count portmanteau tools (should be first 8 in __all__)
        portmanteau_tools = [tool for tool in __all__ if tool.startswith('adn_')]
        
        assert len(portmanteau_tools) == 8, f"Expected 8 portmanteau tools, found {len(portmanteau_tools)}"
        
        expected_tools = ["adn_content", "adn_project", "adn_export", "adn_import", 
                         "adn_search", "adn_knowledge", "adn_navigation", "adn_editor"]
        
        for tool in expected_tools:
            assert tool in portmanteau_tools, f"Missing portmanteau tool: {tool}"
        
        print(f"[PASS] Correct number of portmanteau tools: {len(portmanteau_tools)}")
        return True
    except Exception as e:
        print(f"[FAIL] Tool count test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("Testing Advanced Memory Portmanteau Tools")
    print("=" * 50)
    
    tests = [
        test_tool_imports,
        test_tool_registration,
        test_tool_signatures,
        test_tool_count
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print("=" * 50)
    print(f"Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("[SUCCESS] All portmanteau tools working correctly!")
        print("Ready for Cursor IDE with 8 consolidated tools!")
        return True
    else:
        print("[FAILURE] Some tests failed")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
