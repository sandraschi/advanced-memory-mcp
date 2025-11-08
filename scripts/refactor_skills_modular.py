# SPDX-License-Identifier: AGPL-3.0-or-later
"""Convert legacy single-file Claude skills into the modular architecture."""

from __future__ import annotations

from pathlib import Path

from advanced_memory.services.skill_creator import upgrade_skill

ROOT = Path("skills")


def main() -> None:
    converted = []
    skipped = []
    for skill_file in ROOT.rglob("SKILL.md"):
        try:
            if (skill_file.parent / "modules").exists():
                skipped.append(str(skill_file))
                continue
            upgrade_skill(skill_file.parent)
            converted.append(str(skill_file))
        except Exception as exc:  # noqa: BLE001
            skipped.append(str(skill_file))
            print(f"[WARN] Skipped {skill_file}: {exc}")

    print(f"Converted {len(converted)} skills. Skipped {len(skipped)} others.")


if __name__ == "__main__":
    main()

