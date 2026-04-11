"""arXiv-based skill distiller for Advanced Memory.

This module provides functionality to extract and distill knowledge from arXiv
research papers into high-quality Claude Skills.
"""

from typing import Any

from loguru import logger

try:
    import arxiv
except ImportError:
    arxiv = None


class ArXivDistiller:
    """Distill Claude Skills from arXiv research papers."""

    def __init__(self):
        """Initialize arXiv distiller."""
        if arxiv is None:
            raise ImportError("arxiv package required. Install with: pip install arxiv")
        logger.debug("ArXivDistiller initialized")

    def search_papers(self, query: str, max_results: int = 10) -> list[dict[str, Any]]:
        """Search arXiv for papers.

        Args:
            query: Search query (e.g., "transformer architecture" or "arxiv:1706.03762")
            max_results: Maximum number of results (default: 10)

        Returns:
            List of paper information dictionaries:
            - entry_id: ArXiv ID
            - title: Paper title
            - authors: List of authors
            - summary: Abstract
            - published: Publication date
            - categories: List of categories
            - pdf_url: URL to PDF
        """
        try:
            # Check if query is an arXiv ID
            if query.startswith("arxiv:") or query.startswith("arXiv:"):
                paper_id = query.replace("arxiv:", "").replace("arXiv:", "").strip()
                search = arxiv.Search(id_list=[paper_id], max_results=1)
            else:
                search = arxiv.Search(
                    query=query,
                    max_results=max_results,
                    sort_by=arxiv.SortCriterion.Relevance,
                )

            logger.info(f"Searching arXiv: {query} (max_results={max_results})")
            papers = []

            for result in search.results():
                papers.append(
                    {
                        "entry_id": result.entry_id,
                        "title": result.title,
                        "authors": [str(author) for author in result.authors],
                        "summary": result.summary,
                        "published": result.published,
                        "updated": result.updated,
                        "categories": result.categories,
                        "pdf_url": result.pdf_url,
                        "doi": result.doi,
                        "comment": result.comment,
                    }
                )

            logger.info(f"Found {len(papers)} papers")
            return papers
        except Exception as e:
            logger.error(f"Error searching arXiv: {e}")
            return []

    def get_paper(self, paper_id: str) -> dict[str, Any] | None:
        """Get specific paper by arXiv ID.

        Args:
            paper_id: ArXiv paper ID (e.g., "1706.03762")

        Returns:
            Paper information dictionary or None if not found
        """
        papers = self.search_papers(f"arxiv:{paper_id}", max_results=1)
        return papers[0] if papers else None

    def distill_to_skill(
        self,
        query: str,
        max_papers: int = 5,
        synthesis_level: str = "comprehensive",
    ) -> dict[str, Any]:
        """Distill arXiv papers into skill format.

        Args:
            query: Search query or paper ID
            max_papers: Maximum number of papers to synthesize (default: 5)
            synthesis_level: Synthesis level - "summary", "synthesis", or "comprehensive" (default: "comprehensive")

        Returns:
            Dictionary with skill information:
            - name: Skill name (derived from papers)
            - description: Skill description
            - content: Skill content (markdown)
            - papers: List of source papers
            - key_concepts: Extracted key concepts
        """
        try:
            papers = self.search_papers(query, max_results=max_papers)
            if not papers:
                raise ValueError(f"No papers found for query: {query}")

            # Extract key information
            main_paper = papers[0]
            skill_name = self._slugify(main_paper["title"])

            # Build skill content based on synthesis level
            if synthesis_level == "summary":
                content = self._create_summary_skill(papers)
            elif synthesis_level == "synthesis":
                content = self._create_synthesis_skill(papers)
            elif synthesis_level == "comprehensive":
                content = self._create_comprehensive_skill(papers)
            else:
                content = self._create_synthesis_skill(papers)

            description = (
                f"Research-based guide for {main_paper['title']}. "
                f"Use when working with this topic or related research areas. "
                f"Based on {len(papers)} arXiv paper(s)."
            )

            # Extract key concepts from titles and summaries
            key_concepts = self._extract_key_concepts(papers)

            return {
                "name": skill_name,
                "description": description,
                "content": content,
                "papers": papers,
                "key_concepts": key_concepts,
                "source": f"arXiv: {len(papers)} paper(s)",
                "synthesis_level": synthesis_level,
            }
        except Exception as e:
            logger.error(f"Error distilling arXiv papers: {e}")
            raise ValueError(f"Failed to distill papers for '{query}': {e!s}") from e

    def _slugify(self, text: str) -> str:
        """Convert text to hyphen-case slug.

        Args:
            text: Text to slugify

        Returns:
            Hyphen-case slug
        """
        import re

        text = text.lower()
        text = re.sub(r"[^\w\s-]", "", text)
        text = re.sub(r"[-\s]+", "-", text)
        # Limit length
        text = text[:50]
        return text.strip("-")

    def _extract_key_concepts(self, papers: list[dict[str, Any]]) -> list[str]:
        """Extract key concepts from papers.

        Args:
            papers: List of paper dictionaries

        Returns:
            List of key concept terms
        """
        # Simple extraction - could be enhanced with NLP
        concepts = set()
        for paper in papers:
            # Extract words from title (capitalized terms often indicate concepts)
            title_words = [w for w in paper["title"].split() if w[0].isupper()]
            concepts.update(title_words[:5])

        return sorted(concepts)[:10]

    def _create_summary_skill(self, papers: list[dict[str, Any]]) -> str:
        """Create summary-level skill content.

        Args:
            papers: List of paper dictionaries

        Returns:
            Markdown content for summary skill
        """
        main_paper = papers[0]
        content = f"""# {main_paper["title"]}

## Overview

{main_paper["summary"]}

## Key Points

{self._extract_key_points(main_paper["summary"])}

## Authors

{", ".join(main_paper["authors"])}

## Publication

Published: {main_paper["published"]}
Categories: {", ".join(main_paper["categories"])}

## Source

ArXiv: {main_paper["entry_id"]}
PDF: {main_paper["pdf_url"]}
"""
        return content

    def _create_synthesis_skill(self, papers: list[dict[str, Any]]) -> str:
        """Create synthesis-level skill content.

        Args:
            papers: List of paper dictionaries

        Returns:
            Markdown content for synthesis skill
        """
        main_paper = papers[0]
        content = f"""# {main_paper["title"]}

## Overview

{main_paper["summary"]}

## Key Insights

{self._extract_key_points(main_paper["summary"])}

## Related Research

"""
        for i, paper in enumerate(papers[1:6], 1):
            content += f"""
### {i}. {paper["title"]}

{paper["summary"][:300]}...

**Authors**: {", ".join(paper["authors"][:3])}
**ArXiv**: {paper["entry_id"]}
"""

        content += f"""
## Primary Source

**Title**: {main_paper["title"]}
**Authors**: {", ".join(main_paper["authors"])}
**Published**: {main_paper["published"]}
**Categories**: {", ".join(main_paper["categories"])}
**ArXiv**: {main_paper["entry_id"]}
**PDF**: {main_paper["pdf_url"]}
"""
        return content

    def _create_comprehensive_skill(self, papers: list[dict[str, Any]]) -> str:
        """Create comprehensive skill content.

        Args:
            papers: List of paper dictionaries

        Returns:
            Markdown content for comprehensive skill
        """
        main_paper = papers[0]
        content = f"""# {main_paper["title"]}

## Abstract

{main_paper["summary"]}

## Key Concepts

{self._extract_key_points(main_paper["summary"])}

## Methodology

Based on analysis of {len(papers)} research papers on this topic.

## Related Research Papers

"""
        for i, paper in enumerate(papers[:10], 1):
            content += f"""
### {i}. {paper["title"]}

**Authors**: {", ".join(paper["authors"])}
**Published**: {paper["published"]}
**Categories**: {", ".join(paper["categories"])}

{paper["summary"][:400]}...

**ArXiv ID**: {paper["entry_id"]}
**PDF**: {paper["pdf_url"]}
"""

        content += f"""
## Primary Source

**Paper**: {main_paper["title"]}
**Authors**: {", ".join(main_paper["authors"])}
**Published**: {main_paper["published"]}
**Updated**: {main_paper.get("updated", "N/A")}
**Categories**: {", ".join(main_paper["categories"])}
**ArXiv ID**: {main_paper["entry_id"]}
**DOI**: {main_paper.get("doi", "N/A")}
**PDF**: {main_paper["pdf_url"]}
"""
        return content

    def _extract_key_points(self, text: str, max_points: int = 5) -> str:
        """Extract key points from text.

        Args:
            text: Text to extract points from
            max_points: Maximum number of points

        Returns:
            Formatted key points as markdown list
        """
        # Simple extraction - split into sentences and take first few
        sentences = text.split(". ")
        key_points = sentences[:max_points]
        return "\n".join(f"- {point.strip()}." for point in key_points if point.strip())
