"""Template loader service for zettelkasten templates.

Loads templates from markdown files in zettelkasten/templates/ directory
instead of Python dictionaries in source code.
"""

import re
from pathlib import Path
from typing import Any

from loguru import logger


class TemplateLoader:
    """Load zettelkasten templates from markdown files"""

    def __init__(self, templates_dir: Path | None = None):
        """Initialize template loader

        Args:
            templates_dir: Optional custom templates directory.
                          Defaults to zettelkasten/templates/ in repo root or package data.
        """
        self.templates_dir = templates_dir or self._get_default_dir()
        logger.info(f"Template loader initialized with directory: {self.templates_dir}")

    def _get_default_dir(self) -> Path:
        """Get templates directory (repo root or package data)"""
        # Option 1: Repository root (development)
        repo_root = Path.cwd() / "zettelkasten" / "templates"
        if repo_root.exists():
            return repo_root

        # Option 2: Package data (installed package)
        try:
            from importlib import resources  # Python 3.9+

            pkg_data = resources.files("advanced_memory") / "data" / "zettelkasten" / "templates"  # type: ignore
            if pkg_data.exists():  # type: ignore
                return Path(str(pkg_data))
        except (ImportError, AttributeError):
            pass

        # Option 3: Fallback to old location (backward compatibility)
        logger.warning("zettelkasten/templates/ not found, falling back to Python templates")
        return Path(__file__).parent.parent / "cli" / "zettelkasten_content"

    def load_category(self, category: str) -> dict[str, list[dict[str, Any]]]:
        """Load all templates for a category

        Args:
            category: Category name (e.g., "developer", "devops")

        Returns:
            Dict mapping topic names to lists of template dicts:
            {
                "topic-name": [
                    {"title": "...", "folder": "...", "content": "..."},
                    ...
                ]
            }
        """
        category_dir = self.templates_dir / category

        if not category_dir.exists():
            logger.error(f"Category directory not found: {category_dir}")
            return {}

        templates: dict[str, list[dict[str, Any]]] = {}

        # Iterate through topic directories
        for topic_dir in sorted(category_dir.iterdir()):
            if not topic_dir.is_dir() or topic_dir.name.startswith("."):
                continue

            topic_templates = []

            # Load all markdown files in topic
            for template_file in sorted(topic_dir.glob("*.md")):
                try:
                    content = template_file.read_text(encoding="utf-8")

                    # Extract title from filename or first H1
                    title = self._extract_title(content, template_file.stem)

                    # Infer folder from category and topic
                    folder = f"{category}/{topic_dir.name}"

                    topic_templates.append({"title": title, "folder": folder, "content": content})
                except Exception as e:
                    logger.error(f"Error loading template {template_file}: {e}")

            if topic_templates:
                templates[topic_dir.name] = topic_templates

        logger.info(
            f"Loaded {sum(len(t) for t in templates.values())} templates for category '{category}'"
        )
        return templates

    def _extract_title(self, content: str, fallback: str) -> str:
        """Extract title from markdown content or use fallback

        Args:
            content: Markdown content
            fallback: Fallback title (filename stem)

        Returns:
            Extracted or fallback title
        """
        # Try to find first H1 heading
        match = re.search(r"^#\s+(.+?)$", content, re.MULTILINE)
        if match:
            return match.group(1).strip()

        # Use fallback (convert slug to title)
        return fallback.replace("-", " ").title()

    def list_available(self) -> dict[str, list[str]]:
        """List all available categories and topics

        Returns:
            Dict mapping category names to lists of topic names:
            {"developer": ["python-core", "git-version-control", ...], ...}
        """
        categories: dict[str, list[str]] = {}

        if not self.templates_dir.exists():
            logger.warning(f"Templates directory not found: {self.templates_dir}")
            return categories

        for category_dir in sorted(self.templates_dir.iterdir()):
            if not category_dir.is_dir() or category_dir.name.startswith("."):
                continue

            topics = [
                topic_dir.name
                for topic_dir in sorted(category_dir.iterdir())
                if topic_dir.is_dir() and not topic_dir.name.startswith(".")
            ]

            if topics:
                categories[category_dir.name] = topics

        return categories

    def get_template(self, category: str, topic: str, title: str) -> dict[str, Any] | None:
        """Get a specific template by category, topic, and title

        Args:
            category: Category name
            topic: Topic name
            title: Template title (or slug)

        Returns:
            Template dict with title, folder, content or None if not found
        """
        category_templates = self.load_category(category)

        if topic not in category_templates:
            logger.warning(f"Topic '{topic}' not found in category '{category}'")
            return None

        # Try exact title match first
        for template in category_templates[topic]:
            if template["title"] == title:
                return template

        # Try slug match
        title_slug = self._slugify(title)
        for template in category_templates[topic]:
            if self._slugify(template["title"]) == title_slug:
                return template

        logger.warning(f"Template '{title}' not found in {category}/{topic}")
        return None

    def _slugify(self, text: str) -> str:
        """Convert text to slug for comparison"""
        text = text.lower()
        text = re.sub(r"[^\w\s-]", "", text)
        text = re.sub(r"[-\s]+", "-", text)
        return text.strip("-")

    def load_all_categories(self) -> dict[str, dict[str, list[dict[str, Any]]]]:
        """Load all templates from all categories

        Returns:
            Dict mapping category names to their templates:
            {
                "developer": {"topic": [{"title": "...", "content": "..."}, ...]},
                "devops": {...},
                ...
            }
        """
        all_templates: dict[str, dict[str, list[dict[str, Any]]]] = {}

        available = self.list_available()

        for category in available.keys():
            all_templates[category] = self.load_category(category)

        logger.info(
            f"Loaded all templates: {len(all_templates)} categories, "
            f"{sum(len(topics) for topics in all_templates.values())} topics, "
            f"{sum(len(t) for cat in all_templates.values() for t in cat.values())} total templates"
        )

        return all_templates


# Global instance for easy import
_loader: TemplateLoader | None = None


def get_template_loader() -> TemplateLoader:
    """Get global template loader instance"""
    global _loader
    if _loader is None:
        _loader = TemplateLoader()
    return _loader


def get_content_templates() -> dict[str, dict[str, list[dict[str, Any]]]]:
    """Get all templates in the old CONTENT_TEMPLATES format for backward compatibility

    Returns:
        Dict mapping category names to their topic templates:
        {
            "developer": {"topic": [{"title": "...", "content": "..."}]},
            "devops": {...},
            ...
        }
    """
    loader = get_template_loader()
    return loader.load_all_categories()
