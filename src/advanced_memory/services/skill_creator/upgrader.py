"""Utilities for upgrading legacy single-file skills to modular layout."""

from __future__ import annotations

import re
from pathlib import Path

import yaml
from loguru import logger

from .scaffolder import slugify_skill_name, title_from_slug
from .templates import (
    render_core_guidance,
    render_known_gaps,
    render_research_checklist,
    render_skill_markdown,
    render_toc,
)


def _parse_skill(skill_file: Path) -> tuple[dict, str]:
    """Parse YAML frontmatter and body from an existing SKILL.md."""
    text = skill_file.read_text(encoding="utf-8")
    match = re.match(r"^---\n(.*?)\n---\n(.*)$", text, re.DOTALL)
    if not match:
        raise ValueError(f"File {skill_file} is missing YAML frontmatter.")
    frontmatter_text, body = match.groups()
    data = yaml.safe_load(frontmatter_text) or {}
    if not isinstance(data, dict):
        raise ValueError("Frontmatter must be a mapping.")
    return data, body.strip()


def upgrade_skill(skill_path: str | Path) -> Path:
    """Upgrade an existing skill to the modular structure."""

    skill_root = Path(skill_path).expanduser().resolve()
    skill_file = skill_root / "SKILL.md"
    if not skill_file.exists():
        raise FileNotFoundError(f"SKILL.md not found in {skill_root}")

    frontmatter, body = _parse_skill(skill_file)
    existing_name = frontmatter.get("name") or slugify_skill_name(skill_root.name)
    slug = slugify_skill_name(existing_name)
    title = title_from_slug(slug)
    meta_block = frontmatter.get("metadata")
    if isinstance(meta_block, dict):
        category = meta_block.get("category", "general")
        confidence = meta_block.get("confidence", "low")
        status_note = meta_block.get(
            "status", "Legacy content converted — complete research checklist before use"
        )
        last_validated = meta_block.get("last_validated")
        requires_research = meta_block.get("requires_web_research", True)
    else:
        category = "general"
        confidence = "low"
        status_note = "Legacy content converted — complete research checklist before use"
        last_validated = None
        requires_research = True

    if requires_research is False:
        status_line = "✅ Research complete"
    else:
        status_line = status_note if status_note.startswith(("⚠️", "✅")) else f"⚠️ {status_note}"

    logger.debug("Upgrading skill %s (slug=%s)", skill_root, slug)

    # Directories
    modules_dir = skill_root / "modules"
    modules_dir.mkdir(exist_ok=True)
    (skill_root / "scripts").mkdir(exist_ok=True)
    (skill_root / "references").mkdir(exist_ok=True)
    (skill_root / "assets").mkdir(exist_ok=True)

    # Rewrite SKILL.md with updated metadata (preserve existing description if present)
    description = frontmatter.get("description", "")
    skill_file.write_text(
        render_skill_markdown(
            name=slug,
            title=title,
            description=description,
            category=category,
            confidence=confidence,
            status=status_line,
            confidence_note=status_note,
            last_validated=last_validated,
        ),
        encoding="utf-8",
    )

    # Write supporting files
    (skill_root / "_toc.md").write_text(render_toc(), encoding="utf-8")
    (modules_dir / "core-guidance.md").write_text(
        render_core_guidance(body), encoding="utf-8"
    )
    (modules_dir / "known-gaps.md").write_text(render_known_gaps(), encoding="utf-8")
    (modules_dir / "research-checklist.md").write_text(
        render_research_checklist(), encoding="utf-8"
    )

    logger.info("Skill upgraded to modular architecture: %s", skill_root)
    return skill_root

