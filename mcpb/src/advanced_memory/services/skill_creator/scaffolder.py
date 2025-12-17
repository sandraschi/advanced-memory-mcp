"""Scaffolding utilities for creating modular Claude skills."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Literal

from loguru import logger

from .templates import (
    render_core_guidance,
    render_example_asset,
    render_example_reference,
    render_example_script,
    render_known_gaps,
    render_research_checklist,
    render_skill_markdown,
    render_toc,
)

ConfidenceLevel = Literal["low", "medium", "high"]


def slugify_skill_name(name: str) -> str:
    """Return a hyphen-case slug for a given skill name."""
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", name.strip().lower())
    slug = re.sub(r"-{2,}", "-", slug).strip("-")
    if not slug:
        raise ValueError("Skill name cannot be empty after slugification.")
    if not re.fullmatch(r"[a-z0-9-]+", slug):
        raise ValueError(
            f"Invalid skill name '{slug}'. Use lowercase letters, digits, and hyphens only."
        )
    return slug


def title_from_slug(slug: str) -> str:
    """Convert hyphen-case slug to Title Case."""
    return " ".join(part.capitalize() for part in slug.split("-"))


def scaffold_skill(
    skill_name: str,
    output_dir: str | Path,
    *,
    category: str = "general",
    confidence: ConfidenceLevel = "low",
    overwrite: bool = False,
) -> Path:
    """Create a new modular skill directory with Advanced Memory defaults."""

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
            raise FileExistsError(
                f"Skill directory already exists at {skill_dir}. Set overwrite=True to replace."
            )
    else:
        skill_dir.mkdir(parents=True, exist_ok=True)

    modules_dir = skill_dir / "modules"
    modules_dir.mkdir(exist_ok=True)
    (skill_dir / "scripts").mkdir(exist_ok=True)
    (skill_dir / "references").mkdir(exist_ok=True)
    (skill_dir / "assets").mkdir(exist_ok=True)

    # Write primary files
    (skill_dir / "SKILL.md").write_text(
        render_skill_markdown(
            name=slug,
            title=title,
            description="",
            category=category,
            confidence=confidence,
            status="Draft scaffold – complete research checklist before use",
            confidence_note="Legacy content pending validation",
        ),
        encoding="utf-8",
    )
    (skill_dir / "_toc.md").write_text(render_toc(), encoding="utf-8")
    (modules_dir / "core-guidance.md").write_text(render_core_guidance(), encoding="utf-8")
    (modules_dir / "known-gaps.md").write_text(render_known_gaps(), encoding="utf-8")
    (modules_dir / "research-checklist.md").write_text(
        render_research_checklist(), encoding="utf-8"
    )

    # Placeholders for resources
    (skill_dir / "scripts" / "example.py").write_text(render_example_script(slug), encoding="utf-8")
    (skill_dir / "references" / "example.md").write_text(
        render_example_reference(title), encoding="utf-8"
    )
    (skill_dir / "assets" / "example.txt").write_text(render_example_asset(), encoding="utf-8")

    logger.info("Skill scaffolded at %s", skill_dir)
    return skill_dir
