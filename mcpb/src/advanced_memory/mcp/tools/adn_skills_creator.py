"""Skill creation facility portmanteau tool."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Literal

import yaml
from loguru import logger

from advanced_memory.mcp.mcp_instance import mcp
from advanced_memory.services.skill_creator import (
    package_skill,
    scaffold_skill,
    upgrade_skill,
    validate_skill,
)
from advanced_memory.services.skill_creator.scaffolder import ConfidenceLevel


def _load_metadata(skill_path: Path) -> dict[str, Any]:
    skill_md = skill_path / "SKILL.md"
    if not skill_md.exists():
        raise FileNotFoundError(f"SKILL.md not found in {skill_path}")
    text = skill_md.read_text(encoding="utf-8")
    if not text.startswith("---"):
        raise ValueError("SKILL.md missing YAML frontmatter.")
    sections = text.split("---", 2)
    if len(sections) < 3:
        raise ValueError("Unable to parse SKILL.md frontmatter.")
    frontmatter = yaml.safe_load(sections[1]) or {}
    if not isinstance(frontmatter, dict):
        raise ValueError("Frontmatter must be a mapping.")
    return frontmatter


@mcp.tool()
async def adn_skills_creator(
    operation: Literal["scaffold", "validate", "package", "inspect", "upgrade"],
    skill_name: str | None = None,
    skill_path: str | None = None,
    output_dir: str | None = None,
    category: str = "general",
    confidence: ConfidenceLevel = "low",
    overwrite: bool = False,
) -> dict[str, Any]:
    """Create, validate, and package Claude skills using the gold-standard workflow.

    This portmanteau tool mirrors Anthropic's skill-creator methodology while enforcing
    Advanced Memory's modular requirements (modules, research checklist, metadata).
    It can scaffold new skills, validate existing ones, package them for distribution,
    inspect metadata, or upgrade legacy skills into the modular layout.

    Prerequisites:
        - Provide hyphen-case skill names for new scaffolds (e.g., `brand-guidelines`)
        - Ensure `skills/` directory is writable when creating or upgrading skills
        - Validation and packaging require an existing skill folder with `SKILL.md`

    Parameters:
        operation: REQUIRED. Which action to perform.
            - Valid values: scaffold | validate | package | inspect | upgrade
        skill_name: Optional. Name of the skill to scaffold (hyphen-case preferred).
            - Used only when operation == scaffold.
        skill_path: Optional. Path to an existing skill directory.
            - Required for validate, package, inspect, and upgrade operations.
        output_dir: Optional. Destination directory for new scaffolds or archives.
            - Defaults to current working directory when omitted.
        category: Optional. Metadata category inserted during scaffold (default: general).
        confidence: Optional. Initial confidence level for scaffold metadata (low/medium/high).
        overwrite: Optional. When True, existing scaffold directory will be replaced.

    Returns:
        Dictionary containing:
            - success: bool indicating whether the operation succeeded
            - data: operation-specific payload (paths, validation issues, metadata)
            - metadata: supplemental context (operation, inputs)
            - error: present when success is False, with actionable guidance

    Usage:
        Use this tool to generate modular Claude skills that follow Anthropic's gold-standard
        layout while automatically adding Advanced Memory's hallucination guardrails.
        Validation ensures required modules are present, metadata is complete, and research
        instructions reference distillation helpers.

        Common scenarios:
        - scaffold: start a brand-new skill with placeholder modules and resources
        - validate: check compliance before packaging or publishing
        - package: create a distributable zip archive with manifest
        - inspect: retrieve metadata (name, description, category, confidence)
        - upgrade: convert legacy single-file skills to the modular layout

    Examples:
        Basic usage:
            await adn_skills_creator(
                operation="scaffold",
                skill_name="brand-guidelines",
                output_dir="skills/company",
                category="enterprise"
            )

        With optional parameters:
            await adn_skills_creator(
                operation="package",
                skill_path="skills/company/brand-guidelines",
                output_dir="dist"
            )

        Error handling:
            await adn_skills_creator(
                operation="validate",
                skill_path="skills/company/missing-skill"
            )
            # Returns: {'success': False, 'error': 'Skill directory does not exist.', ...}

    Errors:
        Common errors and solutions:
        - Missing skill_path: Provide the directory when validating, packaging, inspecting, or upgrading.
        - Invalid skill name: Use hyphen-case (lowercase letters, digits, hyphen) for new scaffolds.
        - Validation failures: Review returned issues and address missing modules or metadata.

    See Also:
        - adn_skills: For importing, exporting, and distilling skills content.
        - scripts/refactor_skills_modular.py: CLI bulk upgrade helper built on this service.
    """

    try:
        if operation == "scaffold":
            if not skill_name:
                raise ValueError("skill_name is required when operation='scaffold'.")
            target_dir = Path(output_dir or "skills").expanduser()
            path = scaffold_skill(
                skill_name,
                target_dir,
                category=category,
                confidence=confidence,
                overwrite=overwrite,
            )
            return {
                "success": True,
                "data": {"skill_path": str(path)},
                "metadata": {"operation": operation},
            }

        if operation in {"validate", "package", "inspect", "upgrade"}:
            if not skill_path:
                raise ValueError("skill_path is required for validate/package/inspect/upgrade.")
            path = Path(skill_path).expanduser().resolve()

            if operation == "validate":
                ok, issues = validate_skill(path)
                return {
                    "success": ok,
                    "data": {
                        "issues": [
                            {"path": issue.path, "issue": issue.issue, "fix": issue.fix}
                            for issue in issues
                        ]
                    },
                    "metadata": {"operation": operation, "skill_path": str(path)},
                }

            if operation == "package":
                archive = package_skill(path, output_dir)
                return {
                    "success": True,
                    "data": {"archive": str(archive)},
                    "metadata": {"operation": operation, "skill_path": str(path)},
                }

            if operation == "inspect":
                meta = _load_metadata(path)
                return {
                    "success": True,
                    "data": {"frontmatter": meta},
                    "metadata": {"operation": operation, "skill_path": str(path)},
                }

            if operation == "upgrade":
                upgraded = upgrade_skill(path)
                return {
                    "success": True,
                    "data": {"skill_path": str(upgraded)},
                    "metadata": {"operation": operation},
                }

        raise ValueError(f"Unsupported operation '{operation}'.")

    except Exception as exc:  # noqa: BLE001
        logger.error("adn_skills_creator_error: %s", exc, exc_info=True)
        return {
            "success": False,
            "error": str(exc),
            "error_code": "SKILL_CREATOR_ERROR",
            "suggestions": [
                "Verify the operation name (scaffold, validate, package, inspect, upgrade).",
                "Ensure skill paths exist and include SKILL.md.",
                "Use hyphen-case skill names when scaffolding.",
            ],
        }
