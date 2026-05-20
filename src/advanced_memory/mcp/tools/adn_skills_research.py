"""Skills research tool: chained research with LLM-guided gap analysis."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Literal

from loguru import logger

from advanced_memory.mcp.mcp_instance import mcp
from advanced_memory.services.skill_research_chain import ResearchBundle, run_chain


# @mcp.tool
async def adn_skills_research(
    topic: str,
    sources: list[str] | None = None,
    max_iterations: int = 3,
    coverage_threshold: float = 0.85,
    output_format: Literal["bundle", "skill_draft"] = "bundle",
    output_path: str | None = None,
) -> dict[str, Any]:
    """Run chained research (arxiv, github, rag, web) with LLM-guided gap analysis for skill creation.

    Chains multiple research sources, runs LLM gap analysis after each batch,
    and optionally loops until coverage threshold or max iterations.

    PORTMANTEAU PATTERN RATIONALE:
    Consolidates research chaining and gap analysis into one tool for
    research-first skill creation (Dark App Factory pattern).

    SUPPORTED SOURCES:
    - arxiv: Academic papers
    - github: Repositories and code
    - rag: Knowledge graph / ingested documents
    - web: Web search

    OUTPUT FORMATS:
    - bundle: Raw ResearchBundle (snippets, citations, synthesis, coverage_score)
    - skill_draft: Bundle plus pre-filled SKILL.md skeleton (placeholder for Phase 5)

    Args:
        topic: Research topic (e.g. "FastMCP 2.14 agentic workflows")
        sources: Initial sources to query (default: ["web", "arxiv", "github", "rag"])
        max_iterations: Max research loops (1-5)
        coverage_threshold: Stop when coverage >= this (0.0-1.0)
        output_format: "bundle" (default) or "skill_draft"
        output_path: If provided with skill_draft, scaffolds skill dir and references/ from research

    Returns:
        success, research_bundle (snippets, citations, synthesis, coverage_score),
        skill_draft (if output_format="skill_draft")
    """
    try:
        if not topic or not topic.strip():
            return {
                "success": False,
                "error": "topic is required",
                "error_code": "MISSING_TOPIC",
            }

        valid = ["arxiv", "github", "rag", "web"]
        if sources:
            sources = [s for s in sources if s in valid]
        if not sources:
            sources = ["web", "arxiv", "github", "rag"]

        max_iterations = max(1, min(5, max_iterations))
        coverage_threshold = max(0.0, min(1.0, coverage_threshold))

        bundle: ResearchBundle = await run_chain(
            topic=topic.strip(),
            sources=sources,
            max_iterations=max_iterations,
            coverage_threshold=coverage_threshold,
        )

        result: dict[str, Any] = {
            "success": True,
            "research_bundle": {
                "topic": bundle.topic,
                "snippets_count": len(bundle.snippets),
                "citations_count": len(bundle.citations),
                "synthesis": bundle.synthesis,
                "gaps_remaining": bundle.gaps_remaining,
                "coverage_score": bundle.coverage_score,
                "iteration_count": bundle.iteration_count,
                "sources_used": bundle.sources_used,
                "snippets": bundle.snippets[:20],
                "citations": bundle.citations[:30],
            },
        }

        if output_format == "skill_draft":
            result["skill_draft"] = {
                "synthesis_preview": bundle.synthesis[:500] if bundle.synthesis else "",
            }
            if output_path:
                try:
                    import re

                    from advanced_memory.services.skill_creator import (
                        scaffold_references_from_research,
                    )

                    out = Path(output_path).expanduser().resolve()
                    slug = re.sub(r"[^a-z0-9]+", "-", topic.strip().lower())[:64].strip("-")
                    if not slug:
                        slug = "skill"
                    skill_dir = out / slug if out.is_dir() else out.parent / slug
                    skill_dir.mkdir(parents=True, exist_ok=True)
                    scaffold_references_from_research(skill_dir, bundle, include_sources_md=True)
                    result["skill_draft"]["references_path"] = str(skill_dir / "references")
                    result["skill_draft"]["status"] = "references_scaffolded"
                except Exception as exc:
                    logger.warning("adn_skills_research: scaffold references failed: %s", exc)
                    result["skill_draft"]["status"] = "bundle_only"
                    result["skill_draft"]["scaffold_error"] = str(exc)
            else:
                result["skill_draft"]["status"] = "bundle_only"

        return result

    except Exception as exc:
        logger.error("adn_skills_research_error: %s", exc, exc_info=True)
        return {
            "success": False,
            "error": str(exc),
            "error_code": "SKILLS_RESEARCH_ERROR",
            "suggestions": [
                "Verify topic is non-empty",
                "Check sources are arxiv, github, rag, web",
                "Ensure LLM provider is configured for gap analysis",
            ],
        }
