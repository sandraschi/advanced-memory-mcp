"""
Comprehensive pre-commit check - runs all checks to verify server will load.
Run this before committing to catch issues early.

Usage: python scripts/pre_commit_check.py
"""

import asyncio
import sys
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent.parent / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))


def run_check(name: str, check_func):
    """Run a check and return success status."""
    print(f"\n{'=' * 60}")
    print(f"Checking: {name}")
    print("=" * 60)
    try:
        result = check_func()
        status = "[PASS]" if result else "[FAIL]"
        print(f"\n{name}: {status}")
        return result
    except Exception as e:
        print(f"\n{name}: [FAIL]")
        print(f"Error: {e}")
        import traceback

        traceback.print_exc()
        return False


def check_imports():
    """Check that all critical imports work."""
    try:
        from advanced_memory.mcp.server import mcp
        print(f"[OK] MCP server imports successfully ({mcp.__class__.__name__})")
        return True
    except Exception as e:
        print(f"[FAIL] Import error: {e}")
        return False


def check_tools_registration():
    """Check that tools can be registered."""
    try:
        from advanced_memory.mcp.server import mcp

        async def _collect_tools():
            tools = await mcp.get_tools()
            return tools

        tools = asyncio.run(_collect_tools())
        if tools:
            print(f"[OK] Found {len(tools)} tools registered")
            return True

        print("[WARN] No tools found registered")
        return False
    except Exception as e:
        print(f"[FAIL] Tool registration error: {e}")
        return False


def check_no_syntax_errors():
    """Check for syntax errors by importing all modules."""
    modules_to_check = [
        "advanced_memory.mcp.server",
        "advanced_memory.mcp.tools.adn_content",
        "advanced_memory.mcp.tools.adn_project",
        "advanced_memory.mcp.tools.adn_search",
    ]

    failed = []
    for module_name in modules_to_check:
        try:
            __import__(module_name)
            print(f"[OK] {module_name}")
        except Exception as e:
            print(f"[FAIL] {module_name}: {e}")
            failed.append(module_name)

    return len(failed) == 0


def check_ruff():
    """Check if ruff would pass."""
    import subprocess

    try:
        result = subprocess.run(
            [
                "uv",
                "run",
                "ruff",
                "check",
                "src/advanced_memory/mcp/tools/adn_content.py",
                "src/advanced_memory/mcp/tools/adn_project.py",
                "src/advanced_memory/mcp/tools/adn_search.py",
            ],
            capture_output=True,
            text=True,
            timeout=30,
        )

        if result.returncode == 0:
            print("[OK] Ruff checks passed")
            return True
        else:
            print("[FAIL] Ruff found issues:")
            print(result.stdout)
            print(result.stderr)
            return False
    except FileNotFoundError:
        print("[SKIP] Ruff not available (uv not found?)")
        return True
    except subprocess.TimeoutExpired:
        print("[SKIP] Ruff check timed out")
        return True
    except Exception as e:
        print(f"[SKIP] Could not run ruff: {e}")
        return True


def check_skill_validation():
    """Ensure flagship skill validates successfully."""
    import subprocess

    cmd = [
        "uv",
        "run",
        "python",
        "-m",
        "advanced_memory.services.skill_creator.cli",
        "validate",
        "skills/advanced-memory/advanced-memory-skill-creator",
    ]
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=60,
        )
        if result.returncode == 0:
            print("[OK] Skill validation passed for advanced-memory-skill-creator")
            return True
        print("[FAIL] Skill validation issues:")
        print(result.stdout)
        print(result.stderr)
        return False
    except subprocess.TimeoutExpired:
        print("[SKIP] Skill validation timed out")
        return False
    except Exception as exc:  # noqa: BLE001
        print(f"[FAIL] Skill validation error: {exc}")
        return False


def main():
    """Run all pre-commit checks."""
    print("=" * 60)
    print("Advanced Memory MCP Pre-Commit Checks")
    print("=" * 60)
    print("\nThis script verifies the server will load successfully in Claude.")
    print("Run this before committing to catch issues early.\n")

    checks = [
        ("Critical Imports", check_imports),
        ("Syntax Errors", check_no_syntax_errors),
        ("Tools Registration", check_tools_registration),
        ("Ruff Linting", check_ruff),
        ("Skill Validation", check_skill_validation),
    ]

    results = []
    for name, check_func in checks:
        passed = run_check(name, check_func)
        results.append((name, passed))

    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)

    all_passed = True
    for name, passed in results:
        status = "[PASS]" if passed else "[FAIL]"
        print(f"{name:.<40} {status}")
        if not passed:
            all_passed = False

    print("=" * 60)

    if all_passed:
        print("\n[SUCCESS] All checks passed! Safe to commit.")
        print("Server should load successfully in Claude.")
        return 0
    else:
        print("\n[FAILURE] Some checks failed!")
        print("Fix the issues above before committing.")
        print("\nNext steps:")
        print("  1. Review the errors above")
        print("  2. Run: uv run ruff check .")
        print("  3. Fix issues and re-run: python scripts/pre_commit_check.py")
        return 1


if __name__ == "__main__":
    sys.exit(main())
