"""Expert/SOTA thinker-based skill distiller for Advanced Memory.

This module provides functionality to extract and distill knowledge from leading
experts and thought leaders' publications, lectures, and works into high-quality Claude Skills.
"""

from typing import Any

from loguru import logger


class ExpertDistiller:
    """Distill Claude Skills from expert/SOTA thinker publications."""

    def __init__(self):
        """Initialize expert distiller."""
        logger.debug("ExpertDistiller initialized")

    def search_expert_content(
        self,
        expert_name: str,
        source_types: list[str] | None = None,
        max_results: int = 10,
    ) -> list[dict[str, Any]]:
        """Search for expert's content across multiple sources.

        Args:
            expert_name: Name of expert/thinker
            source_types: List of sources to search - "arxiv", "papers", "lectures", "publishers" (optional)
            max_results: Maximum number of results per source (default: 10)

        Returns:
            List of content items with:
            - title: Content title
            - author: Author name
            - source_type: Type of source
            - url: URL if available
            - summary: Summary/abstract if available
            - date: Publication date if available
        """
        try:
            if source_types is None:
                source_types = ["arxiv", "papers"]

            results = []

            # Search arXiv
            if "arxiv" in source_types:
                arxiv_results = self._search_arxiv(expert_name, max_results)
                results.extend(arxiv_results)

            # Search other sources (placeholder for future implementation)
            if "papers" in source_types:
                # Could search Google Scholar, Semantic Scholar, etc.
                logger.info("Paper search not yet implemented - searching arXiv only")

            if "lectures" in source_types:
                # Could search YouTube, course platforms, etc.
                logger.info("Lecture search not yet implemented")

            logger.info(f"Found {len(results)} items for expert: {expert_name}")
            return results
        except Exception as e:
            logger.error(f"Error searching expert content: {e}")
            return []

    def distill_to_skill(
        self,
        expert_name: str,
        source_types: list[str] | None = None,
        focus_area: str | None = None,
    ) -> dict[str, Any]:
        """Distill expert's work into skill format.

        Args:
            expert_name: Name of expert/thinker
            source_types: List of sources to search (optional)
            focus_area: Specific domain/focus area (optional)

        Returns:
            Dictionary with skill information:
            - name: Skill name (from expert + focus area)
            - description: Skill description
            - content: Skill content (markdown)
            - publications: List of source publications
            - key_insights: Extracted key insights
            - methodology: Extracted methodology
        """
        try:
            logger.info(f"Distilling skill from expert: {expert_name} (focus: {focus_area})")

            # Search for content
            content_items = self.search_expert_content(expert_name, source_types)

            if not content_items:
                raise ValueError(f"No content found for expert: {expert_name}")

            # Extract key information
            skill_name = self._slugify(f"{expert_name}-{focus_area or 'principles'}")

            # Build skill content
            content = self._build_expert_skill_content(expert_name, content_items, focus_area)

            description = (
                f"Expert guidance based on {expert_name}'s work. "
                f"Use when working with methodologies and principles from this expert. "
                f"{f'Focus area: {focus_area}.' if focus_area else ''}"
            )

            return {
                "name": skill_name,
                "description": description,
                "content": content,
                "publications": content_items,
                "key_insights": self._extract_key_insights(content_items),
                "methodology": self._extract_methodology(content_items),
                "source": f"Expert: {expert_name}",
                "focus_area": focus_area,
            }
        except Exception as e:
            logger.error(f"Error distilling expert content: {e}")
            raise ValueError(f"Failed to distill expert '{expert_name}': {str(e)}") from e

    def _search_arxiv(self, expert_name: str, max_results: int) -> list[dict[str, Any]]:
        """Search arXiv for expert's papers.

        Args:
            expert_name: Expert name
            max_results: Maximum results

        Returns:
            List of paper dictionaries
        """
        try:
            import arxiv

            # Search by author name
            search = arxiv.Search(
                query=f'au:"{expert_name}"',
                max_results=max_results,
                sort_by=arxiv.SortCriterion.SubmittedDate,
            )

            results = []
            for result in search.results():
                results.append(
                    {
                        "title": result.title,
                        "author": str(result.authors[0]) if result.authors else expert_name,
                        "source_type": "arxiv",
                        "url": result.pdf_url,
                        "summary": result.summary,
                        "date": result.published,
                        "entry_id": result.entry_id,
                    }
                )

            return results
        except ImportError:
            logger.warning("arxiv package not available - install with: pip install arxiv")
            return []
        except Exception as e:
            logger.error(f"Error searching arXiv: {e}")
            return []

    def _build_expert_skill_content(
        self, expert_name: str, content_items: list[dict[str, Any]], focus_area: str | None
    ) -> str:
        """Build skill content from expert's work.

        Args:
            expert_name: Expert name
            content_items: List of content items
            focus_area: Focus area

        Returns:
            Markdown content
        """
        content_parts = [
            f"# {expert_name}'s Methodology and Principles",
            "",
        ]

        if focus_area:
            content_parts.append(f"## Focus Area: {focus_area}")
            content_parts.append("")

        content_parts.append("## Overview")
        content_parts.append("")
        content_parts.append(
            f"This skill is based on the work of {expert_name}, a leading expert in this field."
        )
        content_parts.append("")

        # Add publications
        content_parts.append("## Key Publications")
        content_parts.append("")
        for i, item in enumerate(content_items[:10], 1):
            content_parts.append(f"### {i}. {item['title']}")
            if item.get("summary"):
                content_parts.append(f"\n{item['summary'][:300]}...")
            content_parts.append(f"\n**Source**: {item.get('source_type', 'unknown')}")
            if item.get("url"):
                content_parts.append(f"**URL**: {item['url']}")
            content_parts.append("")

        # Add methodology section
        methodology = self._extract_methodology(content_items)
        if methodology:
            content_parts.append("## Methodology")
            content_parts.append("")
            content_parts.append(methodology)
            content_parts.append("")

        # Add key insights
        insights = self._extract_key_insights(content_items)
        if insights:
            content_parts.append("## Key Insights")
            content_parts.append("")
            for insight in insights[:10]:
                content_parts.append(f"- {insight}")
            content_parts.append("")

        return "\n".join(content_parts)

    def _extract_methodology(self, content_items: list[dict[str, Any]]) -> str:
        """Extract methodology from content items.

        Args:
            content_items: List of content dictionaries

        Returns:
            Methodology description
        """
        # Simple extraction - would be enhanced with NLP/LLM
        if not content_items:
            return ""

        # Look for methodology-related content in summaries
        methodology_keywords = ["method", "approach", "technique", "framework", "model"]
        methodology_texts = []

        for item in content_items:
            summary = item.get("summary", "").lower()
            if any(keyword in summary for keyword in methodology_keywords):
                methodology_texts.append(item.get("summary", "")[:500])

        if methodology_texts:
            return "\n\n".join(methodology_texts[:3])
        return "Methodology extraction would analyze papers for common approaches and techniques."

    def _extract_key_insights(self, content_items: list[dict[str, Any]]) -> list[str]:
        """Extract key insights from content items.

        Args:
            content_items: List of content dictionaries

        Returns:
            List of insight strings
        """
        # Simple extraction - would be enhanced with NLP/LLM
        insights = []

        for item in content_items[:5]:
            title = item.get("title", "")
            summary = item.get("summary", "")

            # Extract first sentence from summary as key insight
            if summary:
                first_sentence = summary.split(". ")[0]
                if len(first_sentence) > 50:
                    insights.append(f"{title}: {first_sentence}")

        return insights[:10]

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
        return text.strip("-")
