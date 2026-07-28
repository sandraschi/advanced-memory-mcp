"""MCP tool documentation checks.

**Official / conventional docstring standards (Python):**
- **PEP 257** — docstring conventions (summary line, optional blank line, rest): https://peps.python.org/pep-0257/
- **Google Python Style Guide** — one common narrative style; **not** a Python stdlib spec: https://google.github.io/styleguide/pyguide.html#38-comments-and-docstrings
- **NumPy / Sphinx** — common in scientific code; still not a single “one true” standard.

**MCP / FastMCP (this repo):** Cursor and other clients show **per-parameter text from the JSON Schema**
(`inputSchema.properties.<name>.description`), which comes from **Pydantic `Field(description=...)`** on
`Annotated[...]` parameters—not from a long docstring bullet list. The function docstring is the
**tool description**; keep it **short** (PEP 257 summary + one short paragraph at most).

See also: https://gofastmcp.com/ (Tools).
"""

import inspect
import re
from typing import Annotated, get_args, get_origin

import pytest

from advanced_memory.mcp.tools.adn_audio import adn_audio
from advanced_memory.mcp.tools.adn_export import adn_export
from advanced_memory.mcp.tools.adn_import import adn_import
from advanced_memory.mcp.tools.adn_inbox import adn_inbox
from advanced_memory.mcp.tools.adn_llm import adn_llm
from advanced_memory.mcp.tools.adn_navigation import adn_navigation
from advanced_memory.mcp.tools.adn_search import adn_search
from advanced_memory.mcp.tools.content_manager import adn_content
from advanced_memory.mcp.tools.portmanteau_knowledge import adn_knowledge
from advanced_memory.mcp.tools.portmanteau_skills import adn_skills
from advanced_memory.mcp.tools.project_manager import adn_project

_FORBIDDEN_SECTION = re.compile(r"(?im)^\s*(Args|Arguments)\s*:\s*$")

_CONTENT_TOOLS = (("adn_content", adn_content),)


def _tool_fn(tool: object):
    return tool.fn if hasattr(tool, "fn") else tool


def _forbidden_args_section_lines(doc: str) -> list[str]:
    hits = []
    for line in doc.splitlines():
        if _FORBIDDEN_SECTION.match(line.strip()):
            hits.append(line.strip())
    return hits


def _pydantic_field_description(annotation: object) -> str | None:
    """Return Field(description=...) text from Annotated[..., Field(...)], if any."""
    if get_origin(annotation) is not Annotated:
        return None
    for meta in get_args(annotation)[1:]:
        desc = getattr(meta, "description", None)
        if isinstance(desc, str) and desc.strip():
            return desc.strip()
    return None


def _content_tool_params_have_field_descriptions(fn: object) -> list[str]:
    """Return parameter names missing a non-empty Field(description=...)."""
    sig = inspect.signature(fn)
    missing: list[str] = []
    for name, param in sig.parameters.items():
        if name in ("self", "ctx"):
            continue
        ann = param.annotation
        desc = _pydantic_field_description(ann)
        if not desc:
            missing.append(name)
    return missing


@pytest.mark.parametrize("tool_name,tool", _CONTENT_TOOLS)
def test_content_tools_use_field_descriptions_for_mcp_schema(tool_name: str, tool: object) -> None:
    """MCP clients read per-parameter descriptions from Field metadata, not docstring bullets."""
    fn = _tool_fn(tool)
    missing = _content_tool_params_have_field_descriptions(fn)
    assert not missing, (
        f"{tool_name}: add Field(description=...) on Annotated parameters: {missing}. "
        "That text is what Cursor shows next to each parameter."
    )


@pytest.mark.parametrize("tool_name,tool", _CONTENT_TOOLS)
def test_content_tool_docstrings_stay_short(tool_name: str, tool: object) -> None:
    """Long markdown docstrings often render poorly in UIs; keep the tool description compact."""
    fn = _tool_fn(tool)
    doc = inspect.getdoc(fn) or ""
    assert doc.strip(), f"{tool_name} needs a short docstring"
    assert len(doc) <= 1200, (
        f"{tool_name} docstring is {len(doc)} chars; keep under ~1200 (summary + one short paragraph)."
    )
    forbidden = _forbidden_args_section_lines(doc)
    assert not forbidden, f"{tool_name}: do not use Google-style {forbidden} headers; use Field() for params"


@pytest.mark.parametrize(
    "tool_name,tool",
    [
        ("adn_export", adn_export),
        ("adn_import", adn_import),
        ("adn_search", adn_search),
        ("adn_navigation", adn_navigation),
        ("adn_knowledge", adn_knowledge),
        ("adn_skills", adn_skills),
        ("adn_llm", adn_llm),
        ("adn_audio", adn_audio),
        ("adn_inbox", adn_inbox),
        ("adn_project", adn_project),
    ],
)
def test_portmanteau_tools_forbid_google_args_section(tool_name: str, tool: object) -> None:
    fn = _tool_fn(tool)
    doc = inspect.getdoc(fn) or ""
    assert doc.strip(), f"{tool_name} has no docstring"
    forbidden = _forbidden_args_section_lines(doc)
    assert not forbidden, (
        f"{tool_name}: remove {forbidden!r}. Use Field(description=...) on parameters where the UI shows 'no description'."
    )


def test_portmanteau_pattern_sections_are_concise() -> None:
    issues = []
    for tool_name, tool in _CONTENT_TOOLS:
        fn = _tool_fn(tool)
        doc = inspect.getdoc(fn) or ""

        if "PORTMANTEAU PATTERN" in doc:
            pattern_match = re.search(
                r"PORTMANTEAU PATTERN[^\n]*\n(.*?)(?=\n\s*\*\*|\n\s*-\s|`|\Z)",
                doc,
                re.DOTALL,
            )
            if pattern_match:
                pattern_text = pattern_match.group(1)
                pattern_lines = [line.strip() for line in pattern_text.split("\n") if line.strip()]
                if len(pattern_lines) > 3:
                    issues.append(
                        f"{tool_name}: PORTMANTEAU PATTERN section has {len(pattern_lines)} lines (should be ≤3)"
                    )

    if issues:
        pytest.fail("PORTMANTEAU PATTERN sections should be concise:\n" + "\n".join(issues))
