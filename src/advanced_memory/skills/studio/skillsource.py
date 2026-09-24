"""Resolve SKILL.md files on disk: frontmatter description + header TOC.

Decoupled from the engine on purpose (extraction seam): the studio reads files,
never engine internals.
"""

from __future__ import annotations

import os
import re
from pathlib import Path


def catalog_roots() -> list[Path]:
    """Candidate skill roots, first hit wins per identifier."""
    roots: list[Path] = []
    home = Path.home()
    candidates = [
        home / ".claude" / "skills",
        Path(os.getenv("ADVANCED_MEMORY_SKILLS_DIR", "")),
        Path(__file__).resolve().parents[3] / "skills",
    ]
    for c in candidates:
        try:
            if str(c) and c.is_dir() and c not in roots:
                roots.append(c)
        except OSError:
            continue
    return roots


def find_skill_file(identifier: str) -> Path | None:
    """Locate a SKILL.md by skill name, nested path, or absolute path."""
    ident = (identifier or "").strip()
    if not ident:
        return None
    p = Path(ident)
    if p.is_file() and p.name.lower() == "skill.md":
        return p
    if p.is_dir() and (p / "SKILL.md").is_file():
        return p / "SKILL.md"
    for root in catalog_roots():
        direct = root / ident / "SKILL.md"
        if direct.is_file():
            return direct
        try:
            for cand in root.rglob("SKILL.md"):
                if cand.parent.name.lower() == ident.lower():
                    return cand
        except OSError:
            continue
    return None


def parse_frontmatter(text: str) -> tuple[dict[str, str], str]:
    """Split YAML frontmatter (no PyYAML dependency). Returns (fields, body)."""
    fields: dict[str, str] = {}
    if not text.startswith("---"):
        return fields, text
    end = text.find("\n---", 3)
    if end == -1:
        return fields, text
    raw = text[3:end].strip()
    body = text[end + 4 :].lstrip("\n")
    current_key: str | None = None
    for line in raw.splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        m = re.match(r"^([A-Za-z0-9_-]+):\s*(.*)$", line)
        if m:
            current_key = m.group(1).strip().lower()
            fields[current_key] = m.group(2).strip().strip("'\"")
        elif current_key and (line.startswith(" ") or line.startswith("\t")):
            fields[current_key] += " " + line.strip().strip("'\"")
    return fields, body


def skill_headers(body: str) -> list[str]:
    """Top-level section headers (The Door TOC)."""
    return [h.strip() for h in re.findall(r"^##\s+(.+)$", body, flags=re.MULTILINE)]


def load_skill(identifier: str) -> dict[str, object]:
    """Load description + TOC for lab judging. Raises FileNotFoundError."""
    path = find_skill_file(identifier)
    if path is None:
        raise FileNotFoundError(f"Skill not found: {identifier}")
    text = path.read_text(encoding="utf-8", errors="replace")
    fields, body = parse_frontmatter(text)
    return {
        "identifier": identifier,
        "path": str(path),
        "name": fields.get("name", identifier),
        "description": fields.get("description", ""),
        "toc": skill_headers(body),
    }
