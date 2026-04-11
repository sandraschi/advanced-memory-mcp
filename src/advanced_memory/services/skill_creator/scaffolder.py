"""Scaffolding utilities for creating Anthropic-compliant Claude skills."""

from __future__ import annotations

import re
from pathlib import Path

from loguru import logger

from .templates import render_skill_markdown


def slugify_skill_name(name: str) -> str:
    """Return a hyphen-case slug for a given skill name."""
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", name.strip().lower())
    slug = re.sub(r"-{2,}", "-", slug).strip("-")
    if not slug:
        raise ValueError("Skill name cannot be empty after slugification.")
    if not re.fullmatch(r"[a-z0-9-]+", slug):
        raise ValueError(f"Invalid skill name '{slug}'. Use lowercase letters, digits, and hyphens only.")
    return slug


def title_from_slug(slug: str) -> str:
    """Convert hyphen-case slug to Title Case."""
    return " ".join(part.capitalize() for part in slug.split("-"))


def scaffold_skill(
    skill_name: str,
    output_dir: str | Path,
    *,
    overwrite: bool = False,
    license_: str | None = None,
    allowed_tools: list[str] | None = None,
    metadata: dict[str, str] | None = None,
) -> Path:
    """Create a new skill directory following Anthropic's official skills specification."""

    slug = slugify_skill_name(skill_name)
    title = title_from_slug(slug)
    base_dir = Path(output_dir).expanduser().resolve()
    skill_dir = base_dir / slug

    logger.debug(
        "Scaffolding skill: slug=%s title=%s output=%s overwrite=%s",
        slug,
        title,
        skill_dir,
        overwrite,
    )

    if skill_dir.exists():
        if not overwrite:
            raise FileExistsError(f"Skill directory already exists at {skill_dir}. Set overwrite=True to replace.")
    else:
        skill_dir.mkdir(parents=True, exist_ok=True)

    # Write the SKILL.md file following Anthropic spec
    (skill_dir / "SKILL.md").write_text(
        render_skill_markdown(
            name=slug,
            title=title,
            description="",
            license_=license_,
            allowed_tools=allowed_tools,
            metadata=metadata,
        ),
        encoding="utf-8",
    )

    logger.info("Scaffolded Anthropic-compliant skill at %s", skill_dir)
    return skill_dir
