"""Packaging utilities for modular skills."""

from __future__ import annotations

import hashlib
import json
import zipfile
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import yaml
from loguru import logger

from .validator import validate_skill


def _read_frontmatter(skill_root: Path) -> dict[str, Any]:
    skill_md = skill_root / "SKILL.md"
    if not skill_md.exists():
        raise FileNotFoundError(f"SKILL.md not found in {skill_root}")
    content = skill_md.read_text(encoding="utf-8")
    if not content.startswith("---"):
        raise ValueError("SKILL.md missing YAML frontmatter.")
    parts = content.split("---", 2)
    if len(parts) < 3:
        raise ValueError("Unable to parse SKILL.md frontmatter.")
    frontmatter = yaml.safe_load(parts[1]) or {}
    if not isinstance(frontmatter, dict):
        raise ValueError("Frontmatter must be a mapping.")
    return frontmatter


def package_skill(skill_path: str | Path, output_dir: str | Path | None = None) -> Path:
    """Validate and package a skill directory into a zip archive."""

    skill_root = Path(skill_path).expanduser().resolve()
    if not skill_root.exists():
        raise FileNotFoundError(f"Skill folder not found: {skill_root}")

    is_valid, issues = validate_skill(skill_root)
    if not is_valid:
        raise ValueError("Skill validation failed: " + "; ".join(f"{issue.path}: {issue.issue}" for issue in issues))

    metadata = _read_frontmatter(skill_root)

    target_dir = Path(output_dir).expanduser().resolve() if output_dir else skill_root.parent
    target_dir.mkdir(parents=True, exist_ok=True)

    zip_path = target_dir / f"{skill_root.name}.zip"
    logger.debug("Packaging skill %s into %s", skill_root, zip_path)

    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as archive:
        for file_path in skill_root.rglob("*"):
            if file_path.is_file():
                arcname = file_path.relative_to(skill_root.parent)
                archive.write(file_path, arcname)
    logger.info("Packaged skill to %s", zip_path)

    sha256 = hashlib.sha256(zip_path.read_bytes()).hexdigest()

    manifest = {
        "name": skill_root.name,
        "packaged_at": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
        "source_path": str(skill_root),
        "archive": str(zip_path),
        "sha256": sha256,
        "metadata": metadata,
    }
    (target_dir / f"{skill_root.name}.manifest.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    return zip_path
