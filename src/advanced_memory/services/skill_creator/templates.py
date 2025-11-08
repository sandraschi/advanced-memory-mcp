"""Static templates used by the skill creator service."""

from __future__ import annotations

import datetime
from textwrap import dedent


def today_iso() -> str:
    """Return today's date in ISO format."""
    return datetime.date.today().isoformat()


def render_skill_markdown(
    name: str,
    title: str,
    description: str,
    category: str,
    confidence: str,
    status: str,
) -> str:
    """Render the SKILL.md body for a modular skill."""

    metadata_block = {
        "name": name,
        "description": description
        or "[TODO] Concise description of what this skill does and when Claude should load it.",
        "metadata": {
            "category": category,
            "last_validated": today_iso(),
            "confidence": confidence,
            "requires_web_research": True,
            "status": status,
            "skill_version": "0.2.0-modular",
            "sources": [
                "UNVERIFIED: Complete research checklist before relying on this skill."
            ],
        },
    }

    metadata_lines = ["---"]
    metadata_lines.append(f"name: {metadata_block['name']}")
    metadata_lines.append(f"description: {metadata_block['description']}")
    metadata_lines.append("metadata:")
    for key, value in metadata_block["metadata"].items():
        if isinstance(value, list):
            metadata_lines.append(f"  {key}:")
            for entry in value:
                metadata_lines.append(f"    - {entry}")
        else:
            metadata_lines.append(f"  {key}: {value}")
    metadata_lines.append("---")

    body = f"""# {title}
> **Status**: ⚠️ Requires web research before use
>
> **Last validated**: {today_iso()}
>
> **Confidence**: 🔴 Low — legacy content pending validation

## How to use this skill
1. Start with [modules/research-checklist.md](modules/research-checklist.md) and capture up-to-date sources.
2. Review [modules/known-gaps.md](modules/known-gaps.md) and resolve outstanding items.
3. Load topic-specific modules from [_toc.md](_toc.md) only after verification.
4. Update metadata when confidence improves.

## Module overview
- [Core guidance](modules/core-guidance.md) — legacy or placeholder instructions preserved for review.
- [Known gaps](modules/known-gaps.md) — validation tasks and open questions.
- [Research checklist](modules/research-checklist.md) — mandatory workflow for freshness.

## Research status
- Fresh web research pending (conversion captured on {today_iso()}).
- Document all new sources inside `metadata.sources` and the research checklist.
- Do not rely on this skill until confidence is upgraded to `medium` or `high`.
"""
    return "\n".join(metadata_lines) + "\n" + dedent(body).strip() + "\n"


def render_core_guidance(content: str | None = None) -> str:
    """Render the core-guidance module."""
    body = content or (
        "# Core Guidance\n\n"
        "Replace this section with validated, imperative instructions once research is complete."
    )
    return dedent(
        f"""# Core Guidance (Legacy Template)

**Confidence**: 🔴 LOW
**Last captured**: {today_iso()}

> This module preserves the original skill instructions prior to modular conversion.
> Treat every section as unverified until you complete the research checklist and add dated sources.

---

{body}
"""
    ).strip() + "\n"


def render_known_gaps() -> str:
    """Render the known-gaps module."""
    return dedent(
        """# Known Gaps & Validation Tasks

## Critical gaps
- ❌ Fresh web research has not been captured after the Oct 2024 training cutoff.
- ❌ Authoritative sources are missing from `metadata.sources`.
- ❌ Domain expert review pending.

## TODOs
1. Complete the research checklist and archive dated sources.
2. Update `modules/core-guidance.md` with verified guidance and confidence markers.
3. Adjust `metadata.confidence` once validation is complete.

## Notes
- Add additional items here as you uncover domain-specific gaps.
"""
    ).strip() + "\n"


def render_research_checklist() -> str:
    """Render the research-checklist module."""
    return dedent(
        f"""# Research Checklist

Follow these steps before trusting this skill:

1. Identify the freshness risk (APIs, frameworks, standards, or safety-critical topics).
2. Run targeted web searches (official docs, release notes, expert articles) dated {today_iso()[:4]} or newer.
3. Record each source with title, URL, and access date in this module and in `metadata.sources`.
4. Validate the legacy guidance inside [core-guidance.md](core-guidance.md) against the new sources.
5. Update `metadata.last_validated`, `metadata.confidence`, and cite the confirmed material.
6. Move confirmed instructions into dedicated topic modules and mark obsolete content for removal.
7. Document remaining unknowns in [known-gaps.md](known-gaps.md).

> Tip: Use `adn_skills("distill_from_wikipedia", ...)`, `adn_skills("distill_from_arxiv", ...)`, and trusted web research to bootstrap validation.
"""
    ).strip() + "\n"


def render_toc() -> str:
    """Render the module table of contents."""
    return dedent(
        """# Module Guide

| Module | Purpose |
| --- | --- |
| [modules/core-guidance.md](modules/core-guidance.md) | Legacy guidance captured prior to fresh research. Review and update after validation. |
| [modules/known-gaps.md](modules/known-gaps.md) | Track missing evidence, unresolved questions, and validation tasks. |
| [modules/research-checklist.md](modules/research-checklist.md) | Required web research workflow before using this skill. |
"""
    ).strip() + "\n"


def render_example_script(skill_name: str) -> str:
    """Render placeholder script content."""
    return dedent(
        f"""#!/usr/bin/env python3
\"\"\"
Example helper script for {skill_name}

Replace with actual implementation or delete if not needed.
\"\"\"


def main() -> None:
    print("This is an example script placeholder.")


if __name__ == "__main__":
    main()
"""
    ).strip() + "\n"


def render_example_reference(title: str) -> str:
    """Render placeholder reference content."""
    return dedent(
        f"""# Reference Documentation for {title}

Replace with domain-specific documentation or delete if not needed.
"""
    ).strip() + "\n"


def render_example_asset() -> str:
    """Render placeholder asset content."""
    return (
        "Example asset placeholder. Replace with templates, fonts, or other output resources.\n"
    )

