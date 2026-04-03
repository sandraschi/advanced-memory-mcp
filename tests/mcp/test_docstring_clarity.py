"""Test docstring clarity and parameter documentation for portmanteau tools.

This test ensures that all portmanteau tools have clear, unambiguous docstrings
that specify which operations use which parameters.
"""

import inspect
import re

import pytest

from advanced_memory.mcp.tools import (
    adn_audio,
    adn_content,
    adn_export,
    adn_import,
    adn_inbox,
    adn_knowledge,
    adn_llm,
    adn_navigation,
    adn_project,
    adn_search,
    adn_skills,
)


def extract_docstring_parameters(docstring: str) -> dict[str, list[str]]:
    """Extract parameter documentation from docstring."""
    if not docstring:
        return {}

    params = {}
    current_param = None
    current_lines = []

    # Find Args section
    args_match = re.search(r"Args:\s*\n", docstring)
    if not args_match:
        return {}

    args_section = docstring[args_match.end() :]
    lines = args_section.split("\n")

    for line in lines:
        # Check if this is a parameter definition (starts with parameter name)
        # After inspect.cleandoc(), Args entries are typically indented with 4 spaces
        param_match = re.match(r"^\s{4}(\w+):\s*(.*)$", line)
        if param_match:
            # Save previous parameter
            if current_param:
                params[current_param] = "\n".join(current_lines)

            # Start new parameter
            current_param = param_match.group(1)
            current_lines = [param_match.group(2).strip()]
        elif current_param and line.strip():
            # Continuation of current parameter
            current_lines.append(line.strip())

    # Save last parameter
    if current_param:
        params[current_param] = "\n".join(current_lines)

    return params


def check_parameter_clarity(param_doc: str, param_name: str) -> list[str]:
    """Check if parameter documentation is clear and unambiguous."""
    issues = []

    if not param_doc:
        issues.append(f"Parameter '{param_name}' has no documentation")
        return issues

    # Check for ambiguous phrases
    ambiguous_phrases = [
        "depends on",
        "varies",
        "see above",
        "see below",
        "as needed",
        "if applicable",
    ]

    param_lower = param_doc.lower()
    for phrase in ambiguous_phrases:
        if phrase in param_lower and "NOT USED" not in param_doc:
            issues.append(
                f"Parameter '{param_name}' uses ambiguous phrase '{phrase}' without clear operation-specific details"
            )

    # Check that it specifies which operations use it
    if "NOT USED" not in param_doc and "*" not in param_doc:
        # Should have operation-specific documentation
        if not re.search(r"\*\s+\w+\s+operation", param_doc):
            issues.append(f"Parameter '{param_name}' doesn't specify which operations use it")

    # Check for REQUIRED/Optional/NOT USED markers
    if "REQUIRED" not in param_doc and "Optional" not in param_doc and "NOT USED" not in param_doc:
        issues.append(
            f"Parameter '{param_name}' doesn't specify if it's REQUIRED, Optional, or NOT USED"
        )

    return issues


@pytest.mark.parametrize(
    "tool_name,tool",
    [
        ("adn_content", adn_content),
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
def test_portmanteau_tool_docstring_clarity(tool_name, tool):
    """Test that portmanteau tools have clear, unambiguous docstrings."""
    fn = tool.fn if hasattr(tool, "fn") else tool
    docstring = inspect.getdoc(fn)

    assert docstring, f"{tool_name} has no docstring"

    # Check for PORTMANTEAU PATTERN section (should be concise)
    if "PORTMANTEAU PATTERN" in docstring:
        pattern_section = re.search(
            r"PORTMANTEAU PATTERN[^\n]*\n(.*?)(?=\n[A-Z]|\Z)", docstring, re.DOTALL
        )
        if pattern_section:
            pattern_text = pattern_section.group(1)
            # Should be concise (not more than 3 lines)
            pattern_lines = [line.strip() for line in pattern_text.split("\n") if line.strip()]
            assert len(pattern_lines) <= 3, (
                f"{tool_name} PORTMANTEAU PATTERN section is too verbose ({len(pattern_lines)} lines)"
            )

    # Extract parameter documentation
    param_docs = extract_docstring_parameters(docstring)

    # Get actual function parameters
    sig = inspect.signature(fn)
    func_params = list(sig.parameters.keys())

    # Check each parameter
    all_issues = []
    for param_name in func_params:
        if param_name == "self":
            continue

        param_doc = param_docs.get(param_name, "")
        issues = check_parameter_clarity(param_doc, param_name)
        all_issues.extend(issues)

    # Report all issues
    if all_issues:
        error_msg = f"{tool_name} docstring clarity issues:\n" + "\n".join(
            f"  - {issue}" for issue in all_issues
        )
        pytest.fail(error_msg)


def test_portmanteau_pattern_sections_are_concise():
    """Test that all PORTMANTEAU PATTERN sections are concise."""
    tools = [
        ("adn_content", adn_content),
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
    ]

    issues = []
    for tool_name, tool in tools:
        fn = tool.fn if hasattr(tool, "fn") else tool
        docstring = inspect.getdoc(fn)

        if "PORTMANTEAU PATTERN" in docstring:
            # Check that it's concise (one line or very short)
            pattern_match = re.search(
                r"PORTMANTEAU PATTERN[^\n]*\n(.*?)(?=\n[A-Z]|\Z)", docstring, re.DOTALL
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
