"""Guard against BUG-048-class drift: an operation implemented in
portmanteau_system.py's dispatch chain but never wired into adn_system.py,
the actual @mcp.tool entry point.

Found 2026-09-25: inter_server, sampling_status, and batch_process were
fully implemented in portmanteau_system.py with no route from adn_system.py
and no matching SystemOperation Pydantic variant - permanently unreachable
from any MCP client, discovered only by manually diffing the two files'
`elif operation ==` chains during an unrelated conversation about tool
surface gaps.

This test automates that diff via ast so the same drift can't silently
recur. It's scoped to this one wrapper/impl pair deliberately - most other
adn_* portmanteau tools in this codebase are single-file (the dispatch and
the implementation live together), so the specific "two files can drift
apart" failure mode this test guards against doesn't apply to them the same
way. If another wrapper/impl split like this one is introduced elsewhere,
add a matching test rather than trying to generalize this one - the two
files here use a specific, simple `elif operation == "..."` shape that a
generic AST walker would need care to match correctly against other
dispatch styles without false positives.
"""

import ast
from pathlib import Path

_TOOLS_DIR = Path(__file__).resolve().parents[2] / "src" / "advanced_memory" / "mcp" / "tools"
_WRAPPER_PATH = _TOOLS_DIR / "adn_system.py"
_IMPL_PATH = _TOOLS_DIR / "portmanteau_system.py"

# Operations that exist in the impl's dispatch chain by design but are not
# meant to be reachable from adn_system.py's wrapper - e.g. an internal-only
# helper operation another function calls directly. Empty today; keep this
# as the deliberate escape hatch instead of silently loosening the assert.
_INTENTIONALLY_UNROUTED: set[str] = set()


def _dispatched_operation_literals(source_path: Path) -> set[str]:
    """Extract every string literal compared against `operation ==` in an
    if/elif chain anywhere in the file (handles both `if operation ==` and
    `elif operation ==`, since ast.If nodes chain identically either way)."""
    tree = ast.parse(source_path.read_text(encoding="utf-8"))
    found: set[str] = set()

    for node in ast.walk(tree):
        if not isinstance(node, ast.Compare):
            continue
        left = node.left
        is_operation_name = isinstance(left, ast.Name) and left.id == "operation"
        is_operation_attr = isinstance(left, ast.Attribute) and left.attr == "operation"
        if not (is_operation_name or is_operation_attr):
            continue
        for op, comparator in zip(node.ops, node.comparators, strict=False):
            if isinstance(op, ast.Eq) and isinstance(comparator, ast.Constant) and isinstance(comparator.value, str):
                found.add(comparator.value)

    return found


def test_wrapper_routes_every_impl_operation() -> None:
    """Every operation portmanteau_system.py's dispatcher handles must have
    a corresponding branch in adn_system.py's wrapper (or be explicitly
    listed in _INTENTIONALLY_UNROUTED)."""
    wrapper_ops = _dispatched_operation_literals(_WRAPPER_PATH)
    impl_ops = _dispatched_operation_literals(_IMPL_PATH)

    # adn_system.py's own operations use its own vocabulary for two entries
    # that map to differently-named impl operations by design (documented in
    # adn_system.py's dispatch): "sync" -> "sync_status", "external_bridge"
    # -> "external_call". Translate before diffing so those known, correct
    # renames don't look like gaps.
    _KNOWN_RENAMES = {"sync": "sync_status", "external_bridge": "external_call"}
    wrapper_ops_translated = {_KNOWN_RENAMES.get(op, op) for op in wrapper_ops}

    unrouted = impl_ops - wrapper_ops_translated - _INTENTIONALLY_UNROUTED
    assert not unrouted, (
        f"portmanteau_system.py implements operation(s) {sorted(unrouted)} with no route from "
        "adn_system.py's @mcp.tool wrapper - they are unreachable from any MCP client. Either "
        "wire them into adn_system.py + add a SystemOperation Pydantic variant, or add them to "
        "_INTENTIONALLY_UNROUTED with a comment explaining why they should stay unreachable."
    )
