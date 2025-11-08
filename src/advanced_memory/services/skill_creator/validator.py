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
    "last_validated",
    "confidence",
    "requires_web_research",
    "status",
    "skill_version",
    "sources",
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

    metadata = data.get("metadata")
    if not isinstance(metadata, dict):
        issues.append(
            SkillValidationIssue(
                path=str(path),
                issue="Missing 'metadata' mapping in frontmatter.",
                fix="Add a metadata block with category, last_validated, confidence, requires_web_research, status, skill_version, sources.",
            )
        )
        metadata = {}

    missing_keys = REQUIRED_METADATA_KEYS - set(metadata.keys())
    for key in sorted(missing_keys):
        issues.append(
            SkillValidationIssue(
                path=str(path),
                issue=f"Metadata missing `{key}`.",
                fix=f"Add `{key}` to the metadata block.",
            )
        )

    sources = metadata.get("sources")
    if isinstance(sources, Iterable) and not isinstance(sources, str):
        sources_list = list(sources)
        if not sources_list:
            issues.append(
                SkillValidationIssue(
                    path=str(path),
                    issue="Metadata.sources list is empty.",
                    fix="Record at least one placeholder (e.g., 'UNVERIFIED: ...') or real source.",
                )
            )
    else:
        issues.append(
            SkillValidationIssue(
                path=str(path),
                issue="Metadata.sources must be a list of strings.",
                fix="Provide a YAML list under metadata.sources.",
            )
        )

    status_markers = [
        "⚠️ Requires web research",
        "✅ Research complete",
        "🔴 Low",
        "🟡 Medium",
        "🟢 High",
    ]
    if not any(marker in body for marker in status_markers):
        issues.append(
            SkillValidationIssue(
                path=str(path),
                issue="SKILL.md body missing research status banner.",
                fix="Include the standard status section indicating research pending and confidence level.",
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
                    fix="Include guidance such as `Use adn_skills(\"distill_from_wikipedia\", ...)`.",
                )
            )

    is_valid = len(issues) == 0
    return is_valid, issues

