"""Research chain service for skill creation.

Chains arxiv, github, rag, web research with LLM-guided gap analysis.
Pattern inspired by Dark App Factory specialist council.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal

from loguru import logger
from pydantic import BaseModel, Field

from advanced_memory.services.llm_client import get_llm_client

SOURCE_TYPES = Literal["arxiv", "github", "rag", "web"]


class ResearchGapAnalysis(BaseModel):
    """LLM output: synthesis and next-step decisions."""

    synthesis: str = Field(description="Summary of findings so far")
    gaps: list[str] = Field(default_factory=list, description="Missing concepts or unclear areas")
    next_sources: list[str] = Field(default_factory=list, description="Sources to query next")
    coverage_score: float = Field(ge=0.0, le=1.0, description="0-1 coverage estimate")
    should_continue: bool = Field(description="Whether to run more research")


@dataclass
class ResearchBundle:
    """Aggregated research output for skill creation."""

    topic: str
    snippets: list[dict[str, Any]] = field(default_factory=list)
    citations: list[str] = field(default_factory=list)
    synthesis: str = ""
    gaps_remaining: list[str] = field(default_factory=list)
    coverage_score: float = 0.0
    iteration_count: int = 0
    sources_used: list[str] = field(default_factory=list)


def _extract_snippets(result: dict[str, Any], source: str) -> list[dict[str, Any]]:
    """Extract normalized snippets from research tool result."""
    snippets: list[dict[str, Any]] = []
    if not isinstance(result, dict):
        return snippets

    # arxiv: returns {"papers": [...]}
    if source == "arxiv":
        entries = result.get("papers", result.get("entries", []))
        for e in entries[:10] if isinstance(entries, list) else []:
            if isinstance(e, dict):
                title = e.get("title", e.get("Title", ""))
                abstract = e.get("abstract", e.get("Abstract", ""))
                url = e.get("id", e.get("link", e.get("url", "")))
                snippets.append(
                    {
                        "source": "arxiv",
                        "content": f"{title}\n{abstract}"[:1500],
                        "url": str(url) if url else "",
                        "relevance": 0.8,
                    }
                )
            elif isinstance(e, str):
                snippets.append(
                    {"source": "arxiv", "content": e[:1500], "url": "", "relevance": 0.7}
                )

    # github
    elif source == "github":
        items = result.get("items", result.get("repositories", result.get("results", [])))
        for i in items[:10] if isinstance(items, list) else []:
            if isinstance(i, dict):
                name = i.get("full_name", i.get("name", ""))
                desc = i.get("description", i.get("description", ""))
                url = i.get("html_url", i.get("url", ""))
                snippets.append(
                    {
                        "source": "github",
                        "content": f"{name}\n{desc}"[:1500],
                        "url": str(url) if url else "",
                        "relevance": 0.75,
                    }
                )

    # rag: returns {"results": [...]} - each item may have content, text, or be a chunk object
    elif source == "rag":
        chunks = result.get("results", result.get("chunks", []))
        for c in chunks[:10] if isinstance(chunks, list) else []:
            if isinstance(c, dict):
                content = (c.get("content") or c.get("text") or str(c))[:1500]
                snippets.append({"source": "rag", "content": content, "url": "", "relevance": 0.8})
            elif isinstance(c, str):
                snippets.append({"source": "rag", "content": c[:1500], "url": "", "relevance": 0.7})

    # web: returns {"results": [...]} or similar
    elif source == "web":
        results = result.get(
            "results", result.get("organic_results", result.get("web_results", []))
        )
        for r in results[:10] if isinstance(results, list) else []:
            if isinstance(r, dict):
                title = r.get("title", r.get("name", ""))
                snippet = r.get("snippet", r.get("description", ""))
                url = r.get("url", r.get("link", ""))
                snippets.append(
                    {
                        "source": "web",
                        "content": f"{title}\n{snippet}"[:1500],
                        "url": str(url) if url else "",
                        "relevance": r.get("relevance_score", 0.7),
                    }
                )

    return snippets


async def _run_source(source: str, topic: str, limit: int) -> tuple[list[dict], list[str]]:
    """Run one research source and return (snippets, citations)."""
    snippets: list[dict] = []
    citations: list[str] = []

    try:
        if source == "arxiv":
            from advanced_memory.mcp.tools.adn_arxiv_research import adn_arxiv_research

            out = await adn_arxiv_research.fn(
                operation="search_papers",
                query=topic,
                max_results=limit,
            )
            snippets = _extract_snippets(out, "arxiv")
            for s in snippets:
                if s.get("url"):
                    citations.append(s["url"])

        elif source == "github":
            from advanced_memory.mcp.tools.adn_github_research import adn_github_research

            out = await adn_github_research.fn(
                operation="search_repositories",
                query=topic,
                max_results=limit,
            )
            snippets = _extract_snippets(out, "github")
            for s in snippets:
                if s.get("url"):
                    citations.append(s["url"])

        elif source == "rag":
            from advanced_memory.mcp.tools.adn_rag import adn_rag

            out = await adn_rag.fn(
                operation="query_knowledge",
                query=topic,
                max_results=limit,
            )
            snippets = _extract_snippets(out, "rag")

        elif source == "web":
            from advanced_memory.mcp.tools.adn_web_search import adn_web_search

            out = await adn_web_search.fn(query=topic, max_results=limit)
            snippets = _extract_snippets(out, "web")
            for s in snippets:
                if s.get("url"):
                    citations.append(s["url"])

    except Exception as exc:  # noqa: BLE001
        logger.warning("skill_research_chain: source %s failed: %s", source, exc)
    return snippets, citations


def _build_gap_prompt(topic: str, snippets_text: str, iteration: int) -> str:
    return f"""You are analyzing research findings for a skill about: {topic}

Findings so far (iteration {iteration}):
{snippets_text[:12000]}

Tasks:
1. Synthesize what we know in 2-4 sentences.
2. List gaps: missing concepts, unclear areas, needed depth (as bullet points).
3. Recommend next sources to query: arxiv, github, rag, web (pick 1-2 most useful).
4. Estimate coverage_score 0.0-1.0 (how well we cover the topic).
5. Set should_continue: true if coverage < 0.85 and we have iterations left, else false.

Respond with valid JSON only:
{{
  "synthesis": "string",
  "gaps": ["gap1", "gap2"],
  "next_sources": ["arxiv", "web"],
  "coverage_score": 0.7,
  "should_continue": true
}}"""


async def run_chain(
    topic: str,
    sources: list[str] | None = None,
    max_iterations: int = 3,
    coverage_threshold: float = 0.85,
    limit_per_source: int = 5,
) -> ResearchBundle:
    """Run research chain with LLM-guided gap analysis.

    Args:
        topic: Research topic (e.g. "FastMCP 2.14 agentic workflows")
        sources: Initial sources to query (default: ["web", "arxiv", "github", "rag"])
        max_iterations: Max research loops
        coverage_threshold: Stop when coverage >= this
        limit_per_source: Max results per source per run

    Returns:
        ResearchBundle with snippets, citations, synthesis, gaps, coverage_score
    """
    if not sources:
        sources = ["web", "arxiv", "github", "rag"]

    bundle = ResearchBundle(topic=topic)
    remaining = list(sources)
    used: set[str] = set()

    for iteration in range(max_iterations):
        if not remaining:
            break

        batch_snippets: list[dict] = []
        batch_citations: list[str] = []

        for src in remaining:
            if src not in ("arxiv", "github", "rag", "web"):
                continue
            snips, cites = await _run_source(src, topic, limit_per_source)
            batch_snippets.extend(snips)
            batch_citations.extend(cites)
            used.add(src)

        bundle.snippets.extend(batch_snippets)
        bundle.citations = list(dict.fromkeys(bundle.citations + batch_citations))
        bundle.iteration_count = iteration + 1
        bundle.sources_used = list(used)

        snippets_text = "\n\n".join(
            f"[{s.get('source', '?')}] {s.get('content', '')}" for s in batch_snippets
        )
        if not snippets_text.strip():
            logger.warning("skill_research_chain: no snippets in iteration %d", iteration + 1)
            break

        # LLM gap analysis
        try:
            llm = get_llm_client()
            prompt = _build_gap_prompt(topic, snippets_text, iteration + 1)
            raw = await llm.generate_json(
                prompt,
                system_prompt="Respond with valid JSON only. No markdown.",
                max_tokens=800,
                temperature=0.2,
            )
            raw_dict = raw[0] if isinstance(raw, list) and raw and isinstance(raw[0], dict) else raw
            if isinstance(raw_dict, dict):
                analysis = ResearchGapAnalysis(
                    synthesis=str(raw_dict.get("synthesis", "")),
                    gaps=list(raw_dict.get("gaps", []))
                    if isinstance(raw_dict.get("gaps"), list)
                    else [],
                    next_sources=list(raw_dict.get("next_sources", []))
                    if isinstance(raw_dict.get("next_sources"), list)
                    else [],
                    coverage_score=float(raw_dict.get("coverage_score", 0.5)),
                    should_continue=bool(raw_dict.get("should_continue", False)),
                )
            else:
                analysis = ResearchGapAnalysis(
                    synthesis="Research collected; LLM analysis skipped.",
                    gaps=[],
                    next_sources=[],
                    coverage_score=0.5,
                    should_continue=False,
                )
        except Exception as exc:  # noqa: BLE001
            logger.warning("skill_research_chain: gap analysis failed: %s", exc)
            analysis = ResearchGapAnalysis(
                synthesis="Research collected; LLM analysis skipped.",
                gaps=[],
                next_sources=[],
                coverage_score=0.6,
                should_continue=False,
            )

        bundle.synthesis = analysis.synthesis
        bundle.gaps_remaining = analysis.gaps
        bundle.coverage_score = analysis.coverage_score

        if analysis.coverage_score >= coverage_threshold:
            break
        if not analysis.should_continue:
            break

        remaining = [s for s in analysis.next_sources if s in ("arxiv", "github", "rag", "web")]
        if not remaining:
            break

    return bundle
