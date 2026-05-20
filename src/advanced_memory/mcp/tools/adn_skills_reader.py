"""Skill content reader tool for structured skill loading."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Literal

import yaml
from loguru import logger

from advanced_memory.mcp.mcp_instance import mcp


def _load_skill_content(skill_path: Path) -> dict[str, Any]:
    """Load and parse a complete skill file into structured format."""
    skill_md = skill_path / "SKILL.md"
    if not skill_md.exists():
        raise FileNotFoundError(f"SKILL.md not found in {skill_path}")

    text = skill_md.read_text(encoding="utf-8")

    # Parse frontmatter
    if not text.startswith("---"):
        raise ValueError("SKILL.md missing YAML frontmatter.")
    sections = text.split("---", 2)
    if len(sections) < 3:
        raise ValueError("Unable to parse SKILL.md frontmatter.")
    frontmatter = yaml.safe_load(sections[1]) or {}
    if not isinstance(frontmatter, dict):
        raise ValueError("Frontmatter must be a mapping.")

    # Get body content
    body = sections[2].strip()

    return {
        "metadata": frontmatter,
        "content": body,
        "structure": {
            "has_frontmatter": True,
            "body_length": len(body),
            "sections": body.count("# ") if body else 0,
        },
    }


# @mcp.tool
async def adn_skills_reader(
    skill_path: str,
    format: Literal["structured", "raw", "metadata_only"] = "structured",
) -> dict[str, Any]:
    """Load skill content in structured format for IDE integration.

    This tool provides clean, structured access to Claude skills for IDEs like Windsurf,
    Cursor, and Antigravity. Returns properly formatted data instead of raw strings.

    PORTMANTEAU PATTERN RATIONALE:
    Specialized tool for skill content loading with structured output, separate from
    the skills_creator tool which handles creation/validation operations.

    SUPPORTED FORMATS:
    - structured: Full skill data with parsed metadata and content sections
    - raw: Original file content (for backward compatibility)
    - metadata_only: Just the YAML frontmatter

    Args:
        skill_path: Path to the skill directory containing SKILL.md
        format: Output format - "structured" (default), "raw", or "metadata_only"

    Returns:
        dict[str, Any]: Structured skill data:
        - For structured: {"skill": {...}, "format": "structured", "path": "..."}
        - For raw: {"content": "string", "format": "raw", "path": "..."}
        - For metadata_only: {"metadata": {...}, "format": "metadata_only", "path": "..."}

    Examples:
        # Load skill in structured format (recommended)
        result = await adn_skills_reader("skills/technical/python-debugging", "structured")

        # Load just metadata
        metadata = await adn_skills_reader("skills/creative/writing", "metadata_only")

        # Load raw content (fallback)
        raw = await adn_skills_reader("skills/math/calculus", "raw")
    """

    try:
        path = Path(skill_path).expanduser().resolve()

        if not path.exists():
            raise FileNotFoundError(f"Skill path does not exist: {skill_path}")

        if not path.is_dir():
            raise ValueError(f"Skill path must be a directory: {skill_path}")

        if format == "raw":
            # Return raw content for backward compatibility
            skill_md = path / "SKILL.md"
            if not skill_md.exists():
                raise FileNotFoundError(f"SKILL.md not found in {skill_path}")

            content = skill_md.read_text(encoding="utf-8")
            return {
                "content": content,
                "format": "raw",
                "path": str(path),
                "warning": "Raw format returns string data - use 'structured' for proper IDE integration",
            }

        elif format == "metadata_only":
            # Return just the frontmatter
            skill_data = _load_skill_content(path)
            return {
                "metadata": skill_data["metadata"],
                "format": "metadata_only",
                "path": str(path),
            }

        else:  # structured (default)
            # Return fully structured data
            skill_data = _load_skill_content(path)
            return {
                "skill": {
                    "name": skill_data["metadata"].get("name", path.name),
                    "description": skill_data["metadata"].get("description", ""),
                    "metadata": skill_data["metadata"],
                    "content": skill_data["content"],
                    "structure": skill_data["structure"],
                },
                "format": "structured",
                "path": str(path),
                "compatibility": {
                    "cursor": True,
                    "windsurf": True,
                    "antigravity": True,
                    "claude_desktop": True,
                },
            }

    except Exception as exc:
        logger.error("adn_skills_reader_error: %s", exc, exc_info=True)
        return {
            "error": str(exc),
            "format": "error",
            "path": skill_path,
            "suggestions": [
                "Verify the skill path exists and contains SKILL.md",
                "Use 'structured' format for proper IDE integration",
                "Check that the SKILL.md file has valid YAML frontmatter",
            ],
        }
