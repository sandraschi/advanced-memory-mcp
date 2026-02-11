"""Reference scaffolding for skills from research bundles."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from loguru import logger

if TYPE_CHECKING:
    from advanced_memory.services.skill_research_chain import ResearchBundle


def scaffold_references_from_research(
    skill_path: Path | str,
    research_bundle: ResearchBundle,
    *,
    include_sources_md: bool = True,
) -> Path:
    """Create references/ directory and populate REFERENCE.md (and optionally SOURCES.md).

    Args:
        skill_path: Path to skill directory (e.g. skills/my-skill)
        research_bundle: Output from run_chain()
        include_sources_md: If True, also write references/SOURCES.md (bib-style)

    Returns:
        Path to references/ directory
    """
    from advanced_memory.services.skill_research_chain import ResearchBundle as RB

    if not isinstance(research_bundle, RB):
        raise TypeError("research_bundle must be ResearchBundle")

    path = Path(skill_path).expanduser().resolve()
    ref_dir = path / "references"
    ref_dir.mkdir(parents=True, exist_ok=True)

    synthesis = research_bundle.synthesis or "Research synthesis not available."
    citations = research_bundle.citations or []
    gaps = research_bundle.gaps_remaining or []
    topic = research_bundle.topic or "Unknown topic"
    sources_used = research_bundle.sources_used or []

    # REFERENCE.md
    ref_content_parts = [
        f"# Reference: {topic}",
        "",
        "## Synthesis",
        "",
        synthesis,
        "",
    ]

    if gaps:
        ref_content_parts.extend(
            [
                "## Gaps / Areas for Further Research",
                "",
            ]
        )
        for g in gaps:
            ref_content_parts.append(f"- {g}")
        ref_content_parts.extend(["", ""])

    if citations:
        ref_content_parts.extend(
            [
                "## Citations",
                "",
            ]
        )
        for i, cite in enumerate(citations[:50], 1):
            ref_content_parts.append(f"{i}. {cite}")
        ref_content_parts.extend(["", ""])

    ref_content_parts.extend(
        [
            "---",
            f"Sources: {', '.join(sources_used) or 'none'}",
            "",
        ]
    )

    (ref_dir / "REFERENCE.md").write_text("\n".join(ref_content_parts), encoding="utf-8")
    logger.debug("Wrote references/REFERENCE.md at %s", ref_dir)

    if include_sources_md:
        sources_lines = [
            "# Sources",
            "",
            "References used during research.",
            "",
        ]
        for i, cite in enumerate(citations[:30], 1):
            label = f"source_{i}"
            sources_lines.append(f"[{label}] {cite}")
            sources_lines.append("")
        (ref_dir / "SOURCES.md").write_text("\n".join(sources_lines), encoding="utf-8")
        logger.debug("Wrote references/SOURCES.md at %s", ref_dir)

    return ref_dir
