"""Rebuild all packaged skill archives after metadata updates."""

from __future__ import annotations

import sys
from pathlib import Path

from loguru import logger

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from advanced_memory.services.skill_creator import package_skill  # noqa: E402


def collect_skill_dirs(skills_root: Path) -> list[Path]:
    """Collect all directories containing a SKILL.md file."""
    skill_dirs: set[Path] = set()
    for skill_file in skills_root.rglob("SKILL.md"):
        skill_dirs.add(skill_file.parent)
    return sorted(skill_dirs)


def clean_output_dir(output_dir: Path) -> None:
    """Remove existing archives and manifests prior to regeneration."""
    for pattern in ("*.zip", "*.manifest.json"):
        for artifact in output_dir.glob(pattern):
            artifact.unlink(missing_ok=True)


def rebuild_archives(skills_root: Path, output_dir: Path) -> None:
    """Package each skill into the output directory."""
    skill_dirs = collect_skill_dirs(skills_root)
    if not skill_dirs:
        logger.warning("No skills found under %s", skills_root)
        return

    logger.info("Packaging {} skill(s) into {}", len(skill_dirs), output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    clean_output_dir(output_dir)

    failures: list[tuple[Path, str]] = []

    for skill_dir in skill_dirs:
        try:
            archive = package_skill(skill_dir, output_dir)
            logger.info("Packaged {} → {}", skill_dir.name, archive.name)
        except Exception as exc:  # noqa: BLE001
            logger.error("Failed to package {}: {}", skill_dir.name, exc)
            failures.append((skill_dir, str(exc)))

    if failures:
        logger.error("Completed with {} failure(s).", len(failures))
        for skill_dir, message in failures:
            logger.error("  {}: {}", skill_dir.name, message)
        raise SystemExit(1)

    logger.success("All skill archives regenerated successfully.")


def main() -> None:
    repo_root = Path(__file__).resolve().parents[2]
    skills_root = repo_root / "skills"
    output_dir = repo_root / "skill-zips"

    rebuild_archives(skills_root, output_dir)


if __name__ == "__main__":
    main()


