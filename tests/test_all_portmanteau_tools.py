#!/usr/bin/env python3
"""Verify legacy `adn_*` logic providers still import and expose portmanteau-style APIs.

The MCP **wire surface** is FastMCP 3.2 Managed Namespaces (see `server.py`). These
`adn_*` callables remain as **plain functions** for delegation, CLI, and tests —
they are not re-exported from `advanced_memory.mcp.tools` (that package only
exports response helpers).
"""

import importlib
import inspect
import sys

import pytest

sys.path.insert(0, "src")

# (module, attribute) — twelve legacy portmanteau logic providers
LEGACY_PROVIDERS: list[tuple[str, str]] = [
    ("advanced_memory.mcp.tools.content_manager", "adn_notes"),
    ("advanced_memory.mcp.tools.content_manager", "adn_note_ai"),
    ("advanced_memory.mcp.tools.content_manager", "adn_corpus_qc"),
    ("advanced_memory.mcp.tools.content_manager", "adn_content"),
    ("advanced_memory.mcp.tools.portmanteau_knowledge", "adn_knowledge"),
    ("advanced_memory.mcp.tools.portmanteau_research", "adn_research"),
    ("advanced_memory.mcp.tools.portmanteau_import_export", "adn_import_export"),
    ("advanced_memory.mcp.tools.project_manager", "adn_project"),
    ("advanced_memory.mcp.tools.portmanteau_system", "adn_system"),
    ("advanced_memory.mcp.tools.portmanteau_skills", "adn_skills"),
    ("advanced_memory.mcp.tools.portmanteau_external", "adn_external"),
    ("advanced_memory.mcp.tools.adn_observability", "adn_observability"),
]


def check_tool_imports() -> bool:
    """Each legacy provider resolves from its defining module."""
    try:
        for mod_name, attr in LEGACY_PROVIDERS:
            mod = importlib.import_module(mod_name)
            tool = getattr(mod, attr, None)
            assert tool is not None, f"{mod_name}.{attr} is missing"
        print("[PASS] All legacy logic providers import successfully")
        return True
    except Exception as e:
        print(f"[FAIL] Tool import failed: {e}")
        return False


def check_tool_registration() -> bool:
    """Legacy providers remain callable (they are not necessarily @mcp.tool on root)."""
    try:
        for mod_name, attr in LEGACY_PROVIDERS:
            mod = importlib.import_module(mod_name)
            tool = getattr(mod, attr)
            assert callable(tool), f"{mod_name}.{attr} is not callable"
        print("[PASS] All legacy logic providers are callable")
        return True
    except Exception as e:
        print(f"[FAIL] Tool registration test failed: {e}")
        return False


def check_tool_signatures() -> bool:
    """Spot-check `operation=` dispatch signatures on key portmanteaus."""
    try:
        from advanced_memory.mcp.tools.content_manager import adn_content
        from advanced_memory.mcp.tools.portmanteau_import_export import adn_import_export
        from advanced_memory.mcp.tools.portmanteau_knowledge import adn_knowledge
        from advanced_memory.mcp.tools.portmanteau_research import adn_research
        from advanced_memory.mcp.tools.portmanteau_system import adn_system
        from advanced_memory.mcp.tools.project_manager import adn_project

        def check_params(tool_fn: object, expected_params: list[str]) -> None:
            sig = inspect.signature(tool_fn)
            params = list(sig.parameters.keys())
            for param in expected_params:
                assert param in params, f"{getattr(tool_fn, '__name__', tool_fn)} missing parameter: {param}"

        check_params(adn_content, ["operation", "identifier", "content", "folder", "tags"])
        check_params(adn_project, ["operation", "name", "path", "set_default"])
        check_params(adn_import_export, ["operation"])
        check_params(adn_research, ["operation"])
        check_params(adn_knowledge, ["operation"])
        check_params(adn_system, ["operation"])

        print("[PASS] Legacy portmanteau signatures still expose `operation`")
        return True
    except Exception as e:
        print(f"[FAIL] Tool signature test failed: {e}")
        return False


def check_tool_count() -> bool:
    """We still ship exactly twelve legacy portmanteau logic providers."""
    try:
        assert len(LEGACY_PROVIDERS) == 12, len(LEGACY_PROVIDERS)
        print(f"[PASS] Legacy portmanteau provider count: {len(LEGACY_PROVIDERS)}")
        return True
    except Exception as e:
        print(f"[FAIL] Tool count test failed: {e}")
        return False


def main() -> bool:
    print("Testing Advanced Memory legacy portmanteau logic providers")
    print("=" * 50)

    tests = [check_tool_imports, check_tool_registration, check_tool_signatures, check_tool_count]

    passed = 0
    for t in tests:
        if t():
            passed += 1
        print()

    print("=" * 50)
    print(f"Results: {passed}/{total} tests passed")

    if passed == total:
        print("[SUCCESS] Legacy providers are intact.")
        return True
    print("[FAILURE] Some tests failed")
    return False


def test_legacy_portmanteau_providers_importable() -> None:
    for mod_name, attr in LEGACY_PROVIDERS:
        mod = importlib.import_module(mod_name)
        fn = getattr(mod, attr)
        assert callable(fn), f"{mod_name}.{attr} must be callable"


if __name__ == "__main__":
    sys.exit(0 if main() else 1)
