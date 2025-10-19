"""Converter between Advanced Memory zettelkasten and Claude Skills formats.

This module enables bidirectional conversion between:
- Advanced Memory zettelkasten notes (with frontmatter)
- Claude Skills (Anthropic's agent skills format, released Oct 15, 2025)

References:
- Claude Skills Spec: https://github.com/anthropics/anthropic-skills/blob/main/agent_skills_spec.md
"""

import re
from dataclasses import dataclass
from typing import Any

from loguru import logger


@dataclass
class SkillsFrontmatter:
    """Claude Skills frontmatter format.

    Required fields:
    - name: skill name in hyphen-case
    - description: when Claude should use this skill

    Optional fields:
    - license: license name or path to license file
    - allowed_tools: list of pre-approved tools (Claude Code only)
    - metadata: additional key-value pairs
    """

    name: str  # REQUIRED: hyphen-case
    description: str  # REQUIRED: when to use
    license: str | None = None
    allowed_tools: list[str] | None = None
    metadata: dict[str, Any] | None = None


class SkillsConverter:
    """Bidirectional converter between Advanced Memory and Claude Skills."""

    @staticmethod
    def slugify(text: str) -> str:
        """Convert text to hyphen-case slug for skill names.

        Args:
            text: Text to slugify (e.g., "Python Fundamentals")

        Returns:
            Hyphen-case slug (e.g., "python-fundamentals")
        """
        # Convert to lowercase
        text = text.lower()
        # Replace spaces and underscores with hyphens
        text = re.sub(r"[\s_]+", "-", text)
        # Remove non-alphanumeric except hyphens
        text = re.sub(r"[^a-z0-9-]", "", text)
        # Remove consecutive hyphens
        text = re.sub(r"-+", "-", text)
        # Strip leading/trailing hyphens
        return text.strip("-")

    @staticmethod
    def zettel_to_skill(
        zettel_frontmatter: dict,
        zettel_content: str | None = None,
        category: str | None = None,
    ) -> SkillsFrontmatter:
        """Convert Advanced Memory zettel frontmatter to Claude Skills format.

        Args:
            zettel_frontmatter: Advanced Memory frontmatter dict
            zettel_content: Optional content to extract description from
            category: Optional category for metadata

        Returns:
            SkillsFrontmatter with required and optional fields
        """
        # REQUIRED: Generate name from title (slugify)
        title = zettel_frontmatter.get("title", "untitled")
        name = SkillsConverter.slugify(title)

        # REQUIRED: Generate or extract description
        description = zettel_frontmatter.get("description")

        if not description and zettel_content:
            # Extract first paragraph as description
            description = SkillsConverter._extract_first_paragraph(zettel_content)

        if not description:
            # Generate from title
            description = (
                f"Guide for {title}. Use when working with {title.lower()} or related topics."
            )

        # OPTIONAL: License (default MIT for open source)
        license_text = zettel_frontmatter.get("license", "MIT")

        # OPTIONAL: Allowed tools (extract from content or metadata)
        allowed_tools = zettel_frontmatter.get("allowed_tools")

        # OPTIONAL: Metadata (preserve Advanced Memory fields)
        metadata = {
            "advanced_memory": {
                "type": zettel_frontmatter.get("type", "note"),
                "permalink": zettel_frontmatter.get("permalink", name),
                "tags": zettel_frontmatter.get("tags", []),
                "created": str(zettel_frontmatter.get("created", "")),
                "modified": str(zettel_frontmatter.get("modified", "")),
            }
        }

        # Add category if provided
        if category:
            metadata["category"] = category

        # Preserve any existing skills metadata
        if "skills_metadata" in zettel_frontmatter:
            metadata.update(zettel_frontmatter["skills_metadata"])

        logger.debug(f"Converted zettel '{title}' to skill '{name}'")

        return SkillsFrontmatter(
            name=name,
            description=description,
            license=license_text,
            allowed_tools=allowed_tools,
            metadata=metadata,
        )

    @staticmethod
    def skill_to_zettel(skills_frontmatter: SkillsFrontmatter) -> dict:
        """Convert Claude Skills frontmatter to Advanced Memory zettel format.

        Args:
            skills_frontmatter: Claude Skills frontmatter

        Returns:
            Dict with Advanced Memory frontmatter fields
        """
        # Extract Advanced Memory metadata if preserved
        am_metadata = {}
        if skills_frontmatter.metadata:
            am_metadata = skills_frontmatter.metadata.get("advanced_memory", {})

        # Convert name to title (Title Case from hyphen-case)
        title = am_metadata.get("title") or skills_frontmatter.name.replace("-", " ").title()

        # Build Advanced Memory frontmatter
        zettel_fm = {
            "title": title,
            "type": am_metadata.get("type", "skill"),
            "permalink": am_metadata.get("permalink", skills_frontmatter.name),
            "tags": am_metadata.get("tags", []),
            "description": skills_frontmatter.description,
        }

        # Add tags for Claude Skills
        if "claude-skill" not in zettel_fm["tags"]:
            zettel_fm["tags"].append("claude-skill")

        # Preserve Skills-specific fields in metadata
        zettel_fm["skills_name"] = skills_frontmatter.name
        if skills_frontmatter.license:
            zettel_fm["skills_license"] = skills_frontmatter.license
        if skills_frontmatter.allowed_tools:
            zettel_fm["skills_allowed_tools"] = skills_frontmatter.allowed_tools
        if skills_frontmatter.metadata:
            zettel_fm["skills_metadata"] = skills_frontmatter.metadata

        # Preserve created/modified if available
        if am_metadata.get("created"):
            zettel_fm["created"] = am_metadata["created"]
        if am_metadata.get("modified"):
            zettel_fm["modified"] = am_metadata["modified"]

        logger.debug(f"Converted skill '{skills_frontmatter.name}' to zettel '{title}'")

        return zettel_fm

    @staticmethod
    def _extract_first_paragraph(content: str) -> str:
        """Extract first meaningful paragraph from content.

        Args:
            content: Markdown content

        Returns:
            First paragraph (up to 200 chars)
        """
        # Remove frontmatter if present
        content = re.sub(r"^---\n.*?\n---\n", "", content, flags=re.DOTALL)

        # Remove leading headings
        lines = content.strip().split("\n")
        for i, line in enumerate(lines):
            if line.strip() and not line.strip().startswith("#"):
                # Found first non-heading line
                paragraph = line.strip()
                # Continue until empty line or heading
                for j in range(i + 1, len(lines)):
                    if not lines[j].strip() or lines[j].strip().startswith("#"):
                        break
                    paragraph += " " + lines[j].strip()

                # Truncate to reasonable length
                if len(paragraph) > 200:
                    paragraph = paragraph[:197] + "..."

                return paragraph

        return "No description available."

    @staticmethod
    def validate_skill_name(name: str) -> tuple[bool, str]:
        """Validate skill name against Claude Skills spec.

        Args:
            name: Skill name to validate

        Returns:
            Tuple of (is_valid, error_message)
        """
        # Must be hyphen-case (lowercase alphanumeric + hyphen)
        if not re.match(r"^[a-z0-9]+(-[a-z0-9]+)*$", name):
            return (
                False,
                f"Invalid name '{name}': must be hyphen-case (lowercase alphanumeric + hyphen)",
            )

        # Must not start or end with hyphen
        if name.startswith("-") or name.endswith("-"):
            return False, f"Invalid name '{name}': cannot start or end with hyphen"

        # Should not be too long (practical limit)
        if len(name) > 100:
            return False, f"Invalid name '{name}': too long (max 100 chars)"

        return True, ""

    @staticmethod
    def format_skill_markdown(skills_fm: SkillsFrontmatter, content: str) -> str:
        """Format complete SKILL.md content with frontmatter.

        Args:
            skills_fm: Skills frontmatter
            content: Markdown content

        Returns:
            Complete SKILL.md content
        """
        # Build frontmatter
        fm_lines = ["---"]
        fm_lines.append(f"name: {skills_fm.name}")
        fm_lines.append(f"description: {skills_fm.description}")

        if skills_fm.license:
            fm_lines.append(f"license: {skills_fm.license}")

        if skills_fm.allowed_tools:
            fm_lines.append("allowed-tools:")
            for tool in skills_fm.allowed_tools:
                fm_lines.append(f"  - {tool}")

        if skills_fm.metadata:
            fm_lines.append("metadata:")
            for key, value in skills_fm.metadata.items():
                # Handle nested dicts
                if isinstance(value, dict):
                    fm_lines.append(f"  {key}:")
                    for subkey, subvalue in value.items():
                        fm_lines.append(f"    {subkey}: {subvalue}")
                else:
                    fm_lines.append(f"  {key}: {value}")

        fm_lines.append("---")
        fm_lines.append("")  # Blank line after frontmatter

        # Combine frontmatter + content
        return "\n".join(fm_lines) + content

    @staticmethod
    def parse_skill_frontmatter(skill_content: str) -> tuple[SkillsFrontmatter, str]:
        """Parse SKILL.md content into frontmatter and body.

        Args:
            skill_content: Complete SKILL.md content

        Returns:
            Tuple of (SkillsFrontmatter, content_without_frontmatter)

        Raises:
            ValueError: If frontmatter is invalid or missing required fields
        """
        # Use python-frontmatter library
        import frontmatter

        try:
            post = frontmatter.loads(skill_content)
            fm = post.metadata
            content = post.content

            # Validate required fields
            if "name" not in fm:
                raise ValueError("Missing required field 'name' in Skills frontmatter")
            if "description" not in fm:
                raise ValueError("Missing required field 'description' in Skills frontmatter")

            # Validate name format
            is_valid, error_msg = SkillsConverter.validate_skill_name(fm["name"])
            if not is_valid:
                raise ValueError(error_msg)

            # Build SkillsFrontmatter
            skills_fm = SkillsFrontmatter(
                name=fm["name"],
                description=fm["description"],
                license=fm.get("license"),
                allowed_tools=fm.get("allowed-tools") or fm.get("allowed_tools"),
                metadata=fm.get("metadata"),
            )

            return skills_fm, content

        except Exception as e:
            logger.error(f"Failed to parse Skills frontmatter: {e}")
            raise ValueError(f"Invalid SKILL.md format: {e}") from e
