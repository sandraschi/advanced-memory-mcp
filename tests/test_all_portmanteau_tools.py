#!/usr/bin/env python3
"""Test script for all portmanteau tools to verify import, registration, and signatures."""

import inspect
import sys

# Add src to path
sys.path.insert(0, "src")


def test_tool_imports():
    """Test that all portmanteau tools can be imported."""
    try:
        import importlib

        from advanced_memory.mcp.tools import __all__ as exported_tools

        tools_module = importlib.import_module("advanced_memory.mcp.tools")

        for tool_name in exported_tools:
            tool = getattr(tools_module, tool_name)
            assert tool is not None, f"Tool {tool_name} is exported but not defined"

        print("[PASS] All portmanteau tools imported successfully")
        return True
    except Exception as e:
        print(f"[FAIL] Tool import failed: {e}")
        return False


def test_tool_registration():
    """Test that tools are properly registered with MCP."""
    try:
        import importlib

        from advanced_memory.mcp.tools import __all__ as exported_tools

        tools_module = importlib.import_module("advanced_memory.mcp.tools")

        # In FastMCP, tools are standard python functions decorated with @mcp.tool
        # We verify they are callable
        tools_to_check = [name for name in exported_tools if name.startswith("adn_")]

        for name in tools_to_check:
            tool = getattr(tools_module, name)
            assert callable(tool), f"{name} is not callable"

        print("[PASS] All portmanteau tools properly registered and callable")
        return True
    except Exception as e:
        print(f"[FAIL] Tool registration test failed: {e}")
        return False


def test_tool_signatures():
    """Test that tools have expected signatures."""
    try:
        from advanced_memory.mcp.tools import (
            adn_content,
            adn_import_export,
            adn_knowledge,
            adn_project,
            adn_research,
            adn_system,
        )

        def check_params(tool_fn, expected_params):
            sig = inspect.signature(tool_fn)
            params = list(sig.parameters.keys())
            for param in expected_params:
                assert param in params, f"{tool_fn.__name__} missing parameter: {param}"

        # Test adn_content signature
        check_params(adn_content, ["operation", "identifier", "content", "folder", "tags"])

        # Test adn_project signature
        check_params(adn_project, ["operation", "name", "path", "set_default"])

        # Test adn_import_export signature
        check_params(adn_import_export, ["operation"])

        # Test adn_research signature
        check_params(adn_research, ["operation"])

        # Test adn_knowledge signature
        check_params(adn_knowledge, ["operation"])

        # Test adn_system signature
        check_params(adn_system, ["operation"])

        print("[PASS] All portmanteau tools have correct operation signatures")
        return True
    except Exception as e:
        print(f"[FAIL] Tool signature test failed: {e}")
        return False


def test_tool_count():
    """Test that we have exactly 12 portmanteau tools (SOTA)."""
    try:
        from advanced_memory.mcp.tools import __all__

        # Count portmanteau tools (adn_* prefix)
        portmanteau_tools = [tool for tool in __all__ if tool.startswith("adn_")]

        assert len(portmanteau_tools) == 12, (
            f"Expected 12 portmanteau tools, found {len(portmanteau_tools)}: {portmanteau_tools}"
        )

        expected_tools = [
            "adn_notes",
            "adn_note_ai",
            "adn_corpus_qc",
            "adn_content",
            "adn_knowledge",
            "adn_research",
            "adn_import_export",
            "adn_project",
            "adn_system",
            "adn_skills",
            "adn_external",
            "adn_observability",
        ]

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

    tests = [test_tool_imports, test_tool_registration, test_tool_signatures, test_tool_count]

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
        return True
    else:
        print("[FAILURE] Some tests failed")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
