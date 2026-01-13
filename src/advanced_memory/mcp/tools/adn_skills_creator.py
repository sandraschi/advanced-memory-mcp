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

    PORTMANTEAU PATTERN RATIONALE:
    Consolidates 5 skill creation operations into one tool to centralize skill manufacturing workflow.

    SUPPORTED OPERATIONS:
    - scaffold: Initialize a new skill with modular structure and templates
    - validate: Enforce Anthropic & Advanced Memory compliance checks
    - package: Create distributable .zip archives for sharing
    - inspect: Read and parse skill metadata without modifying files
    - upgrade: Convert legacy single-file skills to the new modular layout

    OPERATIONS DETAIL:

    scaffold: Creation Engine
    - Parameters: skill_name (required), category (optional)
    - Effect: Creates skills/<category>/<skill_name>/ with SKILL.md and folders
    - Use when: Starting a new skill from scratch

    validate: Quality Assurance
    - Parameters: skill_path (required)
    - Effect: Runs static analysis on skill structure and YAML frontmatter
    - Use when: Checking work before packaging

    package: Distribution Engine
    - Parameters: skill_path (required), output_dir (optional)
    - Effect: Zips the skill directory into a standardized format
    - Use when: Sharing skills with other agents or users

    inspect: Metadata Reader
    - Parameters: skill_path (required)
    - Effect: Returns the parsed frontmatter as JSON
    - Use when: Agent needs to understand what a skill does

    upgrade: Migration Engine
    - Parameters: skill_path (required)
    - Effect: Refactors file structure to meet current standards
    - Use when: Updating old skills to the new SOTA format

    Prerequisites:
        - Provide hyphen-case skill names for new scaffolds (e.g., `brand-guidelines`)
        - Ensure `skills/` directory is writable when creating or upgrading skills
        - Validation and packaging require an existing skill folder with `SKILL.md`

    Args:
        operation (str): REQUIRED. The action to perform.
            Must be one of: "scaffold", "validate", "package", "inspect", "upgrade".
        skill_name (str | None): Name of the skill to scaffold (hyphen-case preferred).
            Required for 'scaffold'.
        skill_path (str | None): Path to an existing skill directory.
            Required for 'validate', 'package', 'inspect', and 'upgrade'.
        output_dir (str | None): Destination directory for new scaffolds or archives.
            Defaults to current working directory when omitted.
        category (str): Metadata category inserted during scaffold. Default: "general".
        confidence (str): Initial confidence level for metadata ("low", "medium", "high").
            Default: "low".
        overwrite (bool): When True, existing scaffold directory will be replaced.
            Default: False.

    Returns:
        dict[str, Any]: Operation result containing:
            - success (bool): Whether the operation succeeded
            - data (dict): Operation-specific payload (paths, issues, metadata)
            - metadata (dict): Context about the operation performed
            - error (str, optional): Error message if failed
            - error_code (str, optional): Machine-readable error code
            - suggestions (list[str]): Actionable fixes for errors

    Usage:
        Use this tool to generate modular Claude skills that follow Anthropic's gold-standard
        layout while automatically adding Advanced Memory's hallucination guardrails.

    Examples:
        # Scaffold a new skill
        await adn_skills_creator(
            operation="scaffold",
            skill_name="brand-guidelines",
            category="enterprise"
        )

        # Validate a skill
        await adn_skills_creator(
            operation="validate",
            skill_path="skills/enterprise/brand-guidelines"
        )

        # Package for distribution
        await adn_skills_creator(
            operation="package",
            skill_path="skills/enterprise/brand-guidelines",
            output_dir="dist"
        )

    Errors:
        - "skill_name is required": Missing name when scaffolding.
        - "skill_path is required": Missing path for validation/packaging.
        - "Unsupported operation": Operation parameter is invalid.
        - "SKILL.md not found": skill_path exists but lacks manifest.
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
