"""Main skill distiller service for Advanced Memory.

This module provides a unified interface for distilling high-quality Claude Skills
from various authoritative sources including Wikipedia, arXiv, textbooks, famous texts,
and SOTA thinkers.
"""

from typing import Any

from loguru import logger

from advanced_memory.services.arxiv_distiller import ArXivDistiller
from advanced_memory.services.expert_distiller import ExpertDistiller
from advanced_memory.services.text_distiller import TextDistiller
from advanced_memory.services.textbook_distiller import TextbookDistiller
from advanced_memory.services.wikipedia_distiller import WikipediaDistiller


class SkillDistiller:
    """Main interface for skill distillation from authoritative sources."""

    def __init__(self):
        """Initialize skill distiller with all sub-distillers."""
        self.wikipedia = WikipediaDistiller()
        self.arxiv = ArXivDistiller()
        self.textbook = TextbookDistiller()
        self.text = TextDistiller()
        self.expert = ExpertDistiller()
        logger.debug("SkillDistiller initialized with all sub-distillers")

    def distill_from_wikipedia(
        self,
        topic: str,
        depth: int = 0,
        include_related: bool = False,
        quality: str = "comprehensive",
    ) -> dict[str, Any]:
        """Distill skill from Wikipedia article.

        Args:
            topic: Wikipedia article title
            depth: Depth of related articles to include (default: 0)
            include_related: Whether to include related articles (default: False)
            quality: Quality level - "basic", "comprehensive", or "expert" (default: "comprehensive")

        Returns:
            Dictionary with skill information

        Raises:
            ValueError: If topic cannot be accessed or processed
        """
        try:
            logger.info(f"Distilling skill from Wikipedia: {topic}")
            result = self.wikipedia.distill_to_skill(
                title=topic, depth=depth, include_related=include_related, quality=quality
            )
            logger.info(f"Successfully distilled Wikipedia skill: {result['name']}")
            return result
        except Exception as e:
            logger.error(f"Error distilling from Wikipedia: {e}")
            raise ValueError(f"Failed to distill from Wikipedia '{topic}': {str(e)}") from e

    def distill_from_arxiv(
        self,
        query: str,
        max_papers: int = 5,
        synthesis_level: str = "comprehensive",
    ) -> dict[str, Any]:
        """Distill skill from arXiv research papers.

        Args:
            query: Search query or paper ID (e.g., "transformer architecture" or "arxiv:1706.03762")
            max_papers: Maximum number of papers to synthesize (default: 5)
            synthesis_level: Synthesis level - "summary", "synthesis", or "comprehensive" (default: "comprehensive")

        Returns:
            Dictionary with skill information

        Raises:
            ValueError: If query cannot be processed or no papers found
        """
        try:
            logger.info(f"Distilling skill from arXiv: {query}")
            result = self.arxiv.distill_to_skill(
                query=query, max_papers=max_papers, synthesis_level=synthesis_level
            )
            logger.info(f"Successfully distilled arXiv skill: {result['name']}")
            return result
        except Exception as e:
            logger.error(f"Error distilling from arXiv: {e}")
            raise ValueError(f"Failed to distill from arXiv '{query}': {str(e)}") from e

    def distill_from_textbook(
        self,
        pdf_path: str,
        chapters: list[int] | None = None,
        level: str = "intermediate",
    ) -> dict[str, Any]:
        """Distill skill from textbook PDF.

        Args:
            pdf_path: Path to textbook PDF file
            chapters: Specific chapter numbers to process (optional)
            level: Skill level - "beginner", "intermediate", or "advanced" (default: "intermediate")

        Returns:
            Dictionary with skill information

        Raises:
            ValueError: If PDF cannot be accessed or processed
        """
        try:
            logger.info(f"Distilling skill from textbook: {pdf_path}")
            result = self.textbook.distill_to_skill(
                pdf_path=pdf_path, chapters=chapters, level=level
            )
            logger.info(f"Successfully distilled textbook skill: {result['name']}")
            return result
        except Exception as e:
            logger.error(f"Error distilling from textbook: {e}")
            raise ValueError(f"Failed to distill from textbook '{pdf_path}': {str(e)}") from e

    def distill_from_text(
        self,
        text_path: str,
        focus: str = "principles",
        context_level: str = "basic",
    ) -> dict[str, Any]:
        """Distill skill from famous text or document.

        Args:
            text_path: Path to text file or PDF
            focus: What to distill - "principles", "examples", "methodology", or "all" (default: "principles")
            context_level: Historical context level - "basic", "comprehensive", or "detailed" (default: "basic")

        Returns:
            Dictionary with skill information

        Raises:
            ValueError: If text cannot be accessed or processed
        """
        try:
            logger.info(f"Distilling skill from text: {text_path}")
            result = self.text.distill_to_skill(
                text_path=text_path, focus=focus, context_level=context_level
            )
            logger.info(f"Successfully distilled text skill: {result['name']}")
            return result
        except Exception as e:
            logger.error(f"Error distilling from text: {e}")
            raise ValueError(f"Failed to distill from text '{text_path}': {str(e)}") from e

    def distill_from_expert(
        self,
        expert_name: str,
        source_types: list[str] | None = None,
        focus_area: str | None = None,
    ) -> dict[str, Any]:
        """Distill skill from expert/SOTA thinker's work.

        Args:
            expert_name: Name of expert/thinker
            source_types: List of sources to search - "arxiv", "papers", "lectures" (optional)
            focus_area: Specific domain/focus area (optional)

        Returns:
            Dictionary with skill information

        Raises:
            ValueError: If expert content cannot be found or processed
        """
        try:
            logger.info(f"Distilling skill from expert: {expert_name}")
            result = self.expert.distill_to_skill(
                expert_name=expert_name, source_types=source_types, focus_area=focus_area
            )
            logger.info(f"Successfully distilled expert skill: {result['name']}")
            return result
        except Exception as e:
            logger.error(f"Error distilling from expert: {e}")
            raise ValueError(f"Failed to distill from expert '{expert_name}': {str(e)}") from e
