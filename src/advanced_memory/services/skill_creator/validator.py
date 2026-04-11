"""Validation utilities for Advanced Memory modular skills."""

from __future__ import annotations

import re
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path

import yaml


@dataclass(slots=True)
class SkillValidationIssue:
    """Represents a single validation problem."""

    path: str
    issue: str
    fix: str


REQUIRED_METADATA_KEYS = {
    "category",
    "difficulty",
    "last_validated",
    "confidence",
    "requires_web_research",
    "status",
    "skill_version",
    "sources",
    "tags",
}

REQUIRED_MODULES = [
    "modules/core-guidance.md",
    "modules/known-gaps.md",
    "modules/research-checklist.md",
]


def _read_frontmatter(skill_md: Path) -> tuple[dict, str]:
    """Return frontmatter dict and body text."""
    content = skill_md.read_text(encoding="utf-8")
    if not content.startswith("---"):
        raise ValueError("SKILL.md is missing YAML frontmatter.")

    match = re.match(r"^---\n(.*?)\n---\n(.*)$", content, re.DOTALL)
    if not match:
        raise ValueError("Unable to parse YAML frontmatter.")

    frontmatter_text, body = match.groups()
    data = yaml.safe_load(frontmatter_text) or {}
    if not isinstance(data, dict):
        raise ValueError("Frontmatter must be a mapping.")
    return data, body


def _validate_frontmatter(path: Path, issues: list[SkillValidationIssue]) -> dict:
    """Validate and return frontmatter data."""
    data, body = _read_frontmatter(path)

    name = data.get("name")
    if not name or not isinstance(name, str):
        issues.append(
            SkillValidationIssue(
                path=str(path),
                issue="Missing 'name' field in frontmatter.",
                fix="Add `name: <hyphen-case>` to SKILL.md frontmatter.",
            )
        )
    elif not re.fullmatch(r"[a-z0-9-]+", name):
        issues.append(
            SkillValidationIssue(
                path=str(path),
                issue=f"Skill name '{name}' is not hyphen-case.",
                fix="Use lowercase letters, digits, and hyphens only (e.g., `brand-guidelines`).",
            )
        )

    description = data.get("description")
    if not description or not isinstance(description, str):
        issues.append(
            SkillValidationIssue(
                path=str(path),
                issue="Missing 'description' field in frontmatter.",
                fix="Add a short third-person description explaining what the skill does and when to use it.",
            )
        )
    elif "<" in description or ">" in description:
        issues.append(
            SkillValidationIssue(
                path=str(path),
                issue="Description contains angle brackets.",
                fix="Remove `<` and `>` characters to avoid markdown/HTML parsing issues.",
            )
        )

    allowed_tools = data.get("allowed-tools")
    if allowed_tools is not None and (
        not isinstance(allowed_tools, Iterable) or isinstance(allowed_tools, str | bytes)
    ):
        issues.append(
            SkillValidationIssue(
                path=str(path),
                issue="'allowed-tools' must be a YAML list.",
                fix="Provide a YAML list for allowed-tools (e.g., `allowed-tools: []` or `allowed-tools: ['adn_search']`).",
            )
        )
    elif allowed_tools:
        non_string_tools = [tool for tool in allowed_tools if not isinstance(tool, str)]
        if non_string_tools:
            issues.append(
                SkillValidationIssue(
                    path=str(path),
                    issue="'allowed-tools' entries must be strings.",
                    fix="Ensure every entry in allowed-tools is a string tool name.",
                )
            )

    license_value = data.get("license")
    if license_value is not None and not isinstance(license_value, str):
        issues.append(
            SkillValidationIssue(
                path=str(path),
                issue="'license' field must be a string.",
                fix="Provide a simple string identifier for the license (e.g., MIT, Apache-2.0, Proprietary).",
            )
        )

    if "metadata" in data:
        issues.append(
            SkillValidationIssue(
                path=str(path),
                issue="Legacy 'metadata' block detected in frontmatter.",
                fix="Remove the metadata mapping and migrate details into the markdown body (status banner, source log, etc.).",
            )
        )

    status_line_present = any(marker in body for marker in ("⚠️", "✅", "Research complete", "Requires web research"))
    if not status_line_present:
        issues.append(
            SkillValidationIssue(
                path=str(path),
                issue="SKILL.md body missing research status banner.",
                fix="Include a status line such as `> **Status**: ⚠️ Requires web research before use`.",
            )
        )

    confidence_marker_present = any(emoji in body for emoji in ("🔴", "🟡", "🟢"))
    if not confidence_marker_present:
        issues.append(
            SkillValidationIssue(
                path=str(path),
                issue="SKILL.md body missing confidence indicator.",
                fix="Add a confidence line (e.g., `> **Confidence**: 🔴 Low — pending validation`).",
            )
        )

    if "metadata." in body:
        issues.append(
            SkillValidationIssue(
                path=str(path),
                issue="Body references legacy `metadata.*` fields.",
                fix="Update guidance to reference the status banner or Source Log instead of metadata entries.",
            )
        )

    return data


def validate_skill(skill_path: str | Path) -> tuple[bool, list[SkillValidationIssue]]:
    """Validate that a skill matches Advanced Memory requirements."""

    path = Path(skill_path).expanduser().resolve()
    issues: list[SkillValidationIssue] = []

    if not path.exists():
        issues.append(
            SkillValidationIssue(
                path=str(path),
                issue="Skill directory does not exist.",
                fix="Create the skill or check the provided path.",
            )
        )
        return False, issues

    if not path.is_dir():
        issues.append(
            SkillValidationIssue(
                path=str(path),
                issue="Provided path is not a directory.",
                fix="Provide the directory for the skill root.",
            )
        )
        return False, issues

    skill_md = path / "SKILL.md"
    if not skill_md.exists():
        issues.append(
            SkillValidationIssue(
                path=str(skill_md),
                issue="SKILL.md is missing.",
                fix="Ensure the skill root contains SKILL.md with frontmatter.",
            )
        )
        return False, issues

    try:
        _validate_frontmatter(skill_md, issues)
    except ValueError as exc:
        issues.append(
            SkillValidationIssue(
                path=str(skill_md),
                issue=str(exc),
                fix="Ensure SKILL.md begins with YAML frontmatter enclosed by '---' and '---'.",
            )
        )
        return False, issues

    toc = path / "_toc.md"
    if not toc.exists():
        issues.append(
            SkillValidationIssue(
                path=str(toc),
                issue="_toc.md is missing.",
                fix="Generate `_toc.md` linking to core guidance, known gaps, and research checklist.",
            )
        )

    for rel in REQUIRED_MODULES:
        module_path = path / rel
        if not module_path.exists():
            issues.append(
                SkillValidationIssue(
                    path=str(module_path),
                    issue=f"Required module `{rel}` is missing.",
                    fix="Create the module file using the standard template.",
                )
            )

    known_gaps = path / "modules" / "known-gaps.md"
    if known_gaps.exists():
        text = known_gaps.read_text(encoding="utf-8")
        if "TODO" not in text and "❌" not in text:
            issues.append(
                SkillValidationIssue(
                    path=str(known_gaps),
                    issue="known-gaps.md lacks TODO entries.",
                    fix="List outstanding validation tasks so Claude knows what remains.",
                )
            )

    research_checklist = path / "modules" / "research-checklist.md"
    if research_checklist.exists():
        text = research_checklist.read_text(encoding="utf-8")
        if "distill_from_wikipedia" not in text:
            issues.append(
                SkillValidationIssue(
                    path=str(research_checklist),
                    issue="research-checklist.md missing reference to distillation helpers.",
                    fix='Include guidance such as `Use adn_skills("distill_from_wikipedia", ...)`.',
                )
            )

    is_valid = len(issues) == 0
    return is_valid, issues


def validate_skill_agentskills(skill_path: str | Path) -> tuple[bool, list[str], dict[str, bool]]:
    """Validate agentskills.io baseline (name, description, structure).

    Returns:
        (spec_compliant, warnings, agentskills_checks)
    """
    path = Path(skill_path).expanduser().resolve()
    warnings: list[str] = []
    checks: dict[str, bool] = {
        "name_present": False,
        "name_length_1_64": False,
        "name_hyphen_case": False,
        "name_matches_directory": False,
        "description_present": False,
        "description_length_1_1024": False,
    }

    if not path.exists() or not path.is_dir():
        return False, ["Skill path does not exist or is not a directory."], checks

    skill_md = path / "SKILL.md"
    if not skill_md.exists():
        return False, ["SKILL.md missing."], checks

    try:
        data, _ = _read_frontmatter(skill_md)
    except ValueError:
        return False, ["Invalid or missing YAML frontmatter."], checks

    name = data.get("name")
    if name and isinstance(name, str):
        checks["name_present"] = True
        checks["name_length_1_64"] = 1 <= len(name) <= 64
        checks["name_hyphen_case"] = bool(re.fullmatch(r"[a-z0-9-]+", name))
        checks["name_matches_directory"] = name == path.name
        if not checks["name_length_1_64"]:
            warnings.append(f"Name length {len(name)} outside 1-64 chars (agentskills.io)")
        if not checks["name_hyphen_case"]:
            warnings.append("Name must be lowercase, digits, hyphens only")
        if not checks["name_matches_directory"]:
            warnings.append(f"Name '{name}' does not match directory '{path.name}'")
    else:
        warnings.append("Missing 'name' in frontmatter")

    description = data.get("description")
    if description and isinstance(description, str):
        checks["description_present"] = True
        checks["description_length_1_1024"] = 1 <= len(description) <= 1024
        if not checks["description_length_1_1024"]:
            warnings.append(f"Description length {len(description)} outside 1-1024 chars (agentskills.io)")
    else:
        warnings.append("Missing or empty 'description' in frontmatter")

    spec_compliant = all(checks.values())
    return spec_compliant, warnings, checks
