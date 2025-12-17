# SPDX-License-Identifier: AGPL-3.0-or-later
"""Normalize SKILL.md files to match Anthropic's minimal YAML frontmatter."""

from __future__ import annotations

import argparse
import re
import unicodedata
from datetime import date
from pathlib import Path
from typing import Any

import frontmatter

DEFAULT_LICENSE = "Proprietary"
DEFAULT_STATUS = "⚠️ Requires web research before use"
CONFIDENCE_LABELS = {
    "low": "🔴 Low",
    "medium": "🟡 Medium",
    "high": "🟢 High",
}

LEGACY_REPLACEMENTS = {
    "`metadata.sources`": "`the Source Log`",
    "metadata.sources": "the Source Log",
    "`metadata.confidence`": "`the status banner`",
    "metadata.confidence": "the status banner",
    "metadata.last_validated": "the status banner",
    "metadata.tags": "the Source Log",
}


def ensure_string_list(value: Any, fallback: list[str]) -> list[str]:
    """Coerce the provided value into a list of strings."""
    if value is None:
        return list(fallback)
    if isinstance(value, list):
        return [str(item) for item in value if isinstance(item, str | bytes)]
    if isinstance(value, (set | tuple)):
        return [str(item) for item in value]
    if isinstance(value, (str | bytes)):
        return [str(value)]
    return list(fallback)


def slugify_name(value: str | None, fallback: str) -> str:
    """Convert arbitrary text into a hyphen-case ASCII slug."""
    base = value if isinstance(value, str) and value.strip() else fallback
    normalized = unicodedata.normalize("NFKD", base)
    ascii_only = normalized.encode("ascii", "ignore").decode("ascii")
    ascii_only = ascii_only.lower()
    ascii_only = re.sub(r"[^a-z0-9]+", "-", ascii_only)
    return ascii_only.strip("-") or fallback


def _replace_line(text: str, pattern: str, replacement: str) -> str:
    """Replace the first line matching pattern; prepend if missing."""
    if re.search(pattern, text, flags=re.MULTILINE):
        return re.sub(pattern, replacement, text, count=1, flags=re.MULTILINE)
    return replacement + "\n" + text


def _sanitize_body(body: str) -> str:
    """Swap legacy references for the new status/banner language."""
    updated = body
    for old, new in LEGACY_REPLACEMENTS.items():
        updated = updated.replace(old, new)
    return updated


def normalize_skill(skill_path: Path, dry_run: bool = False) -> bool:
    """Normalize a single SKILL.md file. Returns True when modifications were made."""
    original_text = skill_path.read_text(encoding="utf-8")
    multiline_description = bool(
        re.search(r"^description:\s+[^\r\n]+\r?\n\s+\S", original_text, flags=re.MULTILINE)
    )

    post = frontmatter.loads(original_text)
    original_metadata = dict(post.metadata)

    metadata = dict(original_metadata)
    meta_block = metadata.pop("metadata", None)

    changed = multiline_description or (meta_block is not None)

    folder_slug = slugify_name(metadata.get("name"), skill_path.parent.name)
    if metadata.get("name") != folder_slug:
        metadata["name"] = folder_slug
        changed = True

    description_value = metadata.get("description")
    if isinstance(description_value, str):
        normalized_description = " ".join(description_value.split())
        if normalized_description != description_value:
            metadata["description"] = normalized_description
            changed = True
    elif description_value is None:
        metadata["description"] = ""
        changed = True

    allowed_tools = ensure_string_list(metadata.get("allowed-tools"), [])
    if allowed_tools:
        metadata["allowed-tools"] = allowed_tools
    elif "allowed-tools" in metadata:
        metadata.pop("allowed-tools")
        changed = True

    license_value = metadata.get("license")
    if not license_value or not isinstance(license_value, str):
        metadata["license"] = DEFAULT_LICENSE
        changed = True

    new_frontmatter: dict[str, Any] = {
        "name": metadata["name"],
        "description": metadata["description"],
    }
    if allowed_tools:
        new_frontmatter["allowed-tools"] = allowed_tools
    if metadata.get("license"):
        new_frontmatter["license"] = metadata["license"]

    status_note = ""
    last_validated = None
    confidence_value = "low"
    requires_research = True
    if isinstance(meta_block, dict):
        status_note = str(meta_block.get("status", "")).strip()
        last_validated = meta_block.get("last_validated")
        confidence_value = str(meta_block.get("confidence", "low")).lower()
        requires_research = meta_block.get("requires_web_research", True)

    if requires_research is False:
        status_line = "✅ Research complete"
        confidence_note = status_note or "Fully validated"
    else:
        base_status = status_note or DEFAULT_STATUS
        if not base_status.startswith(("⚠️", "✅")):
            base_status = f"⚠️ {base_status}"
        status_line = base_status
        confidence_note = status_note or "Legacy content pending validation"

    confidence_label = CONFIDENCE_LABELS.get(confidence_value, CONFIDENCE_LABELS["medium"])
    confidence_line = (
        f"{confidence_label} — {confidence_note}" if confidence_note else confidence_label
    )
    last_validated_line = last_validated or date.today().isoformat()

    body = post.content or ""
    body = _sanitize_body(body)
    body = _replace_line(
        body,
        r"^> \*\*Status\*\*:.*$",
        f"> **Status**: {status_line}  ",
    )
    body = _replace_line(
        body,
        r"^> \*\*Last validated\*\*:.*$",
        f"> **Last validated**: {last_validated_line}  ",
    )
    body = _replace_line(
        body,
        r"^> \*\*Confidence\*\*:.*$",
        f"> **Confidence**: {confidence_line}",
    )

    if body != post.content:
        post.content = body
        changed = True

    if new_frontmatter != original_metadata:
        changed = True
    post.metadata = new_frontmatter

    if changed and not dry_run:
        skill_path.write_text(
            frontmatter.dumps(post, sort_keys=False, width=4096), encoding="utf-8"
        )

    return changed


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Normalize SKILL.md frontmatter across all skills."
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=Path("skills"),
        help="Root directory containing skill folders (default: skills/).",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Detect fixes without modifying files.",
    )
    args = parser.parse_args()

    root: Path = args.root.expanduser().resolve()
    if not root.exists():
        raise SystemExit(f"Root directory not found: {root}")

    updated = 0
    scanned = 0

    for skill_md in sorted(root.rglob("SKILL.md")):
        scanned += 1
        if normalize_skill(skill_md, dry_run=args.dry_run):
            updated += 1

    action = "would update" if args.dry_run else "updated"
    print(f"[normalize_skill_frontmatter] Scanned {scanned} SKILL.md files — {action} {updated}.")


if __name__ == "__main__":
    main()
