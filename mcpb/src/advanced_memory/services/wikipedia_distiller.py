"""Wikipedia-based skill distiller for Advanced Memory.

This module provides functionality to extract and distill knowledge from Wikipedia
articles into high-quality Claude Skills.
"""

from typing import Any

from loguru import logger

try:
    import wikipediaapi
except ImportError:
    wikipediaapi = None


class WikipediaDistiller:
    """Distill Claude Skills from Wikipedia articles."""

    def __init__(self, language: str = "en"):
        """Initialize Wikipedia distiller.

        Args:
            language: Wikipedia language code (default: "en")
        """
        if wikipediaapi is None:
            raise ImportError(
                "wikipedia-api package required. Install with: pip install wikipedia-api"
            )

        self.language = language
        self.wiki = wikipediaapi.Wikipedia(
            language=language,
            user_agent="AdvancedMemory/1.0 (Knowledge Management System)",
        )
        logger.debug(f"WikipediaDistiller initialized for language: {language}")

    def get_article(self, title: str) -> dict[str, Any] | None:
        """Get Wikipedia article content.

        Args:
            title: Wikipedia article title

        Returns:
            Dictionary with article information:
            - title: Article title
            - summary: First paragraph summary
            - sections: Dictionary of section titles and content
            - categories: List of categories
            - links: List of linked articles
            - references: List of references
            - exists: Whether article exists

        Raises:
            ValueError: If article cannot be accessed
        """
        try:
            logger.info(f"Fetching Wikipedia article: {title}")
            page = self.wiki.page(title)

            if not page.exists():
                logger.warning(f"Wikipedia article not found: {title}")
                return {
                    "title": title,
                    "exists": False,
                    "summary": "",
                    "sections": {},
                    "categories": [],
                    "links": [],
                    "references": [],
                }

            # Extract sections
            sections = {}
            for section in page.sections:
                sections[section.title] = section.text

            # Extract links
            links = list(page.links.keys())

            # Extract categories
            categories = list(page.categories.keys())

            result = {
                "title": page.title,
                "summary": page.summary,
                "sections": sections,
                "categories": categories,
                "links": links,
                "references": [],  # References not directly available in wikipediaapi
                "exists": True,
                "full_text": page.text,
            }

            logger.info(f"Successfully fetched article: {title} ({len(sections)} sections)")
            return result
        except Exception as e:
            logger.error(f"Error fetching Wikipedia article: {e}")
            raise ValueError(f"Failed to fetch Wikipedia article '{title}': {str(e)}") from e

    def search_articles(self, query: str, limit: int = 10) -> list[dict[str, Any]]:
        """Search Wikipedia for articles.

        Args:
            query: Search query
            limit: Maximum number of results (default: 10)

        Returns:
            List of article search results with title and snippet
        """
        try:
            logger.info(f"Searching Wikipedia: {query}")
            # Note: wikipediaapi doesn't have direct search, would need to use Wikipedia API
            # For now, return empty list - can be enhanced with requests to Wikipedia API
            logger.warning("Wikipedia search not fully implemented - requires Wikipedia API")
            return []
        except Exception as e:
            logger.error(f"Error searching Wikipedia: {e}")
            return []

    def distill_to_skill(
        self,
        title: str,
        depth: int = 0,
        include_related: bool = False,
        quality: str = "comprehensive",
    ) -> dict[str, Any]:
        """Distill Wikipedia article into skill format.

        Args:
            title: Wikipedia article title
            depth: Depth of related articles to include (default: 0)
            include_related: Whether to include related articles (default: False)
            quality: Quality level - "basic", "comprehensive", or "expert" (default: "comprehensive")

        Returns:
            Dictionary with skill information:
            - name: Skill name (slugified)
            - description: Skill description
            - content: Skill content (markdown)
            - sections: Organized sections
            - related_topics: List of related topics
        """
        try:
            article = self.get_article(title)
            if not article or not article.get("exists"):
                raise ValueError(f"Wikipedia article not found: {title}")

            # Extract key information
            skill_name = self._slugify(article["title"])
            sections = article.get("sections", {})
            links = article.get("links", [])[:10] if include_related else []

            # Build skill content based on quality level
            if quality == "basic":
                content = self._create_basic_skill(article)
            elif quality == "comprehensive":
                content = self._create_comprehensive_skill(article)
            elif quality == "expert":
                content = self._create_expert_skill(article, depth, links)
            else:
                content = self._create_comprehensive_skill(article)

            description = (
                f"Guide for {article['title']}. Use when working with {article['title'].lower()} "
                f"or related topics. Based on Wikipedia article."
            )

            return {
                "name": skill_name,
                "description": description,
                "content": content,
                "sections": list(sections.keys()),
                "related_topics": links,
                "source": f"Wikipedia: {title}",
                "quality": quality,
            }
        except Exception as e:
            logger.error(f"Error distilling Wikipedia article: {e}")
            raise ValueError(f"Failed to distill article '{title}': {str(e)}") from e

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

    def _create_basic_skill(self, article: dict[str, Any]) -> str:
        """Create basic skill content from article.

        Args:
            article: Article dictionary

        Returns:
            Markdown content for basic skill
        """
        sections_text = "\n\n".join(
            f"## {title}\n\n{content[:500]}..."
            for title, content in list(article.get("sections", {}).items())[:3]
        )

        return f"""# {article["title"]}

## Overview

{article.get("summary", "")}

{sections_text}

## Source

Based on Wikipedia article: {article["title"]}
"""

    def _create_comprehensive_skill(self, article: dict[str, Any]) -> str:
        """Create comprehensive skill content from article.

        Args:
            article: Article dictionary

        Returns:
            Markdown content for comprehensive skill
        """
        sections_text = "\n\n".join(
            f"## {title}\n\n{content}" for title, content in article.get("sections", {}).items()
        )

        categories_text = ""
        if article.get("categories"):
            categories_text = (
                f"\n\n## Related Categories\n\n{', '.join(article['categories'][:10])}"
            )

        return f"""# {article["title"]}

## Overview

{article.get("summary", "")}

{sections_text}

{categories_text}

## Source

Based on Wikipedia article: {article["title"]}
"""

    def _create_expert_skill(
        self, article: dict[str, Any], depth: int, related_links: list[str]
    ) -> str:
        """Create expert-level skill content with related articles.

        Args:
            article: Article dictionary
            depth: Depth of related articles
            related_links: List of related article titles

        Returns:
            Markdown content for expert skill
        """
        sections_text = "\n\n".join(
            f"## {title}\n\n{content}" for title, content in article.get("sections", {}).items()
        )

        related_text = ""
        if related_links:
            related_text = "\n\n## Related Topics\n\n"
            related_text += "\n".join(f"- {link}" for link in related_links[:20])

        categories_text = ""
        if article.get("categories"):
            categories_text = f"\n\n## Categories\n\n{', '.join(article['categories'])}"

        return f"""# {article["title"]}

## Overview

{article.get("summary", "")}

{sections_text}

{categories_text}

{related_text}

## Source

Based on Wikipedia article: {article["title"]} and related topics.
"""
