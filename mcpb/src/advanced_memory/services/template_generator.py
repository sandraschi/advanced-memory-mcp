"""AI-powered template generation service for Zettelmaker.

This service generates zettelkasten templates dynamically using AI,
supporting multiple quality levels and topic areas.
"""

import hashlib
import json
from pathlib import Path
from textwrap import dedent
from typing import Any

from loguru import logger


class TemplateGenerator:
    """AI-powered template generator using Claude/LLM API."""

    QUALITY_LEVELS = {
        "quick": {
            "note_count": 3,
            "depth": "basic",
            "examples": False,
            "exercises": False,
            "description": "Quick overview with essential concepts only",
        },
        "standard": {
            "note_count": 8,
            "depth": "intermediate",
            "examples": True,
            "exercises": False,
            "description": "Good coverage with practical examples",
        },
        "comprehensive": {
            "note_count": 15,
            "depth": "advanced",
            "examples": True,
            "exercises": True,
            "description": "Deep dive with examples and exercises",
        },
        "expert": {
            "note_count": 25,
            "depth": "expert",
            "examples": True,
            "exercises": True,
            "description": "Expert-level depth with advanced topics",
        },
    }

    def __init__(self, cache_dir: str | None = None):
        """Initialize template generator.

        Args:
            cache_dir: Directory for template cache (default: ~/.advanced-memory/template-cache)
        """
        if cache_dir:
            self.cache_dir = Path(cache_dir)
        else:
            self.cache_dir = Path.home() / ".advanced-memory" / "template-cache"

        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def get_generation_prompt(self, topic: str, category: str, quality: str = "standard") -> str:
        """Get the AI prompt for template generation.

        Args:
            topic: Topic to generate templates for
            category: Category (developer, researcher, writer, knowledge-worker)
            quality: Quality level (quick, standard, comprehensive, expert)

        Returns:
            Formatted prompt for AI template generation
        """
        quality_config = self.QUALITY_LEVELS.get(quality, self.QUALITY_LEVELS["standard"])

        prompt = dedent(
            f"""
            You are an expert zettelkasten template creator specializing in creating deeply interconnected, high-quality knowledge notes.

            Generate a comprehensive zettelkasten template set for the following topic:

            **Topic:** {topic}
            **Category:** {category}
            **Quality Level:** {quality} ({quality_config["description"]})
            **Number of Notes:** {quality_config["note_count"]}
            **Depth:** {quality_config["depth"]}
            **Include Examples:** {quality_config["examples"]}
            **Include Exercises:** {quality_config["exercises"]}

            ## Requirements

            1. **Structure**: Create {quality_config["note_count"]} interconnected notes
            2. **Format**: Each note as markdown with frontmatter
            3. **Connections**: Use [[WikiLinks]] between related concepts
            4. **Observations**: Include categorized facts: `- [category] content`
            5. **Relations**: Add directional links: `- relation_type [[Target]]`
            6. **Examples**: {"Include practical code/examples" if quality_config["examples"] else "Skip examples"}
            7. **Exercises**: {"Include practice exercises" if quality_config["exercises"] else "Skip exercises"}

            ## Note Structure Template

            ```markdown
            # [Note Title]

            [Brief introduction to the concept]

            ## Core Concepts

            [Main content with detailed explanations]

            {"## Examples" if quality_config["examples"] else ""}
            {"```" if quality_config["examples"] else ""}
            {"[Practical code examples or demonstrations]" if quality_config["examples"] else ""}
            {"```" if quality_config["examples"] else ""}

            {"## Practice Exercises" if quality_config["exercises"] else ""}
            {"1. [Exercise 1]" if quality_config["exercises"] else ""}
            {"2. [Exercise 2]" if quality_config["exercises"] else ""}

            ## Observations
            - [definition] [Key definition]
            - [example] [Practical example]
            - [principle] [Core principle]

            ## Relations
            - builds_on [[Foundational Concept]]
            - related_to [[Related Topic]]
            - enables [[Advanced Topic]]

            ## Further Reading
            - [[Related Note 1]]
            - [[Related Note 2]]
            ```

            ## Topic Coverage for {topic}

            Create notes that cover:
            1. **Fundamentals** - Core concepts and definitions
            2. **Practical Application** - Real-world usage and examples
            3. **Advanced Topics** - Deeper concepts building on fundamentals
            4. **Best Practices** - Industry standards and recommendations
            5. **Common Pitfalls** - What to avoid and why

            ## Output Format

            Return a JSON array of note objects with this structure:
            ```json
            [
                {{
                    "title": "Note Title",
                    "folder": "{category}/{topic}",
                    "content": "# Full markdown content here..."
                }},
                ...
            ]
            ```

            Generate {quality_config["note_count"]} high-quality, interconnected zettelkasten notes now.
            """
        ).strip()

        return prompt

    def _get_cache_key(self, topic: str, category: str, quality: str) -> str:
        """Generate cache key for template."""
        cache_input = f"{topic}:{category}:{quality}"
        return hashlib.md5(cache_input.encode()).hexdigest()

    def _get_cache_path(self, cache_key: str) -> Path:
        """Get file path for cached template."""
        return self.cache_dir / f"{cache_key}.json"

    def get_cached_template(self, topic: str, category: str, quality: str = "standard") -> list[dict[str, Any]] | None:
        """Get cached template if available.

        Args:
            topic: Topic name
            category: Category name
            quality: Quality level

        Returns:
            Cached template list or None if not cached
        """
        cache_key = self._get_cache_key(topic, category, quality)
        cache_path = self._get_cache_path(cache_key)

        if cache_path.exists():
            try:
                with open(cache_path, encoding="utf-8") as f:
                    cached_data = json.load(f)
                    logger.info(f"Template cache hit: {topic}/{category}/{quality}")
                    return cached_data.get("templates", [])
            except Exception as e:
                logger.warning(f"Error reading cache: {e}")
                return None

        logger.info(f"Template cache miss: {topic}/{category}/{quality}")
        return None

    def cache_template(self, topic: str, category: str, quality: str, templates: list[dict[str, Any]]) -> None:
        """Cache generated template for future use.

        Args:
            topic: Topic name
            category: Category name
            quality: Quality level
            templates: Template list to cache
        """
        cache_key = self._get_cache_key(topic, category, quality)
        cache_path = self._get_cache_path(cache_key)

        try:
            cache_data = {
                "topic": topic,
                "category": category,
                "quality": quality,
                "templates": templates,
                "note_count": len(templates),
            }

            with open(cache_path, "w", encoding="utf-8") as f:
                json.dump(cache_data, f, indent=2, ensure_ascii=False)

            logger.info(f"Template cached: {topic}/{category}/{quality}")

        except Exception as e:
            logger.warning(f"Error writing cache: {e}")

    def validate_generated_template(self, templates: list[dict[str, Any]]) -> tuple[bool, str]:
        """Validate generated template quality.

        Args:
            templates: List of generated template dictionaries

        Returns:
            Tuple of (is_valid, error_message)
        """
        if not templates:
            return False, "No templates generated"

        if not isinstance(templates, list):
            return False, "Templates must be a list"

        for i, template in enumerate(templates):
            # Check required fields
            if "title" not in template:
                return False, f"Template {i} missing 'title' field"

            if "content" not in template:
                return False, f"Template {i} missing 'content' field"

            if "folder" not in template:
                return False, f"Template {i} missing 'folder' field"

            # Check content quality
            content = template["content"]

            if len(content) < 100:
                return False, f"Template {i} content too short (< 100 chars)"

            # Check for markdown headers
            if not content.strip().startswith("#"):
                return False, f"Template {i} missing markdown header"

            # Check for some interconnections
            if "[[" not in content or "]]" not in content:
                logger.warning(f"Template {i} has no WikiLinks - may lack interconnections")

        return True, "All templates valid"

    async def generate_with_claude(
        self, topic: str, category: str, quality: str = "standard", use_cache: bool = True
    ) -> list[dict[str, Any]]:
        """Generate templates using Claude API.

        Args:
            topic: Topic to generate templates for
            category: Category (developer, researcher, etc.)
            quality: Quality level (quick, standard, comprehensive, expert)
            use_cache: Whether to use cached templates if available

        Returns:
            List of generated template dictionaries

        Note:
            This is a placeholder implementation. In production, this would:
            1. Check cache first (if use_cache=True)
            2. Call Claude API with generation prompt
            3. Parse JSON response into template list
            4. Validate generated templates
            5. Cache for future use
            6. Return templates
        """
        # Check cache first
        if use_cache:
            cached = self.get_cached_template(topic, category, quality)
            if cached:
                return cached

        # In Phase 2, this would call the actual Claude API
        # For now, return a placeholder message
        logger.info(f"AI template generation requested: {topic}/{category}/{quality} (not yet implemented)")

        raise NotImplementedError(
            "AI template generation coming in Phase 2! "
            "For now, use pre-built templates with: "
            f"adn_zettelmaker('generate', category='{category}', topic='<existing-topic>')"
        )

    def list_available_topics(self, category: str | None = None) -> dict[str, list[str]]:
        """List all available pre-built topics.

        Args:
            category: Optional category filter

        Returns:
            Dictionary of category -> topic list
        """
        # Use new TemplateLoader to get available topics from markdown files
        from advanced_memory.services.template_loader import get_template_loader

        loader = get_template_loader()
        all_templates = loader.list_available()

        if category:
            return {category: all_templates.get(category, [])}

        return all_templates
