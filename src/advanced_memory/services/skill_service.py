"""Skill service for Claude Skills management."""

import json
from datetime import datetime, timezone

from loguru import logger
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from advanced_memory.models import Skill
from advanced_memory.repository.repository import Repository


class SkillService:
    """Service for managing Claude Skills in Advanced Memory."""

    def __init__(self, session: AsyncSession, repository: Repository):
        """Initialize skill service.

        Args:
            session: Database session
            repository: Repository instance for database operations
        """
        self.session = session
        self.repository = repository
        logger.debug("SkillService initialized")

    async def create_skill(
        self,
        name: str,
        description: str,
        entity_id: int | None = None,
        version: str = "1.0.0",
        category: str | None = None,
        difficulty: str | None = None,
        license: str | None = None,
        allowed_tools: list[str] | None = None,
        custom_metadata: dict | None = None,
    ) -> Skill:
        """Create a new skill.

        Args:
            name: Skill name in hyphen-case
            description: When Claude should use this skill
            entity_id: Optional link to entity
            version: Skill version
            category: Skill category (developer, researcher, etc.)
            difficulty: Difficulty level
            license: License name or path
            allowed_tools: List of pre-approved tools
            custom_metadata: Additional metadata

        Returns:
            Created Skill instance
        """
        now = datetime.now(timezone.utc)

        skill_data = {
            "name": name,
            "description": description,
            "entity_id": entity_id,
            "version": version,
            "category": category,
            "difficulty": difficulty,
            "license": license,
            "allowed_tools": json.dumps(allowed_tools) if allowed_tools else None,
            "custom_metadata": json.dumps(custom_metadata) if custom_metadata else None,
            "usage_count": 0,
            "created_at": now,
            "updated_at": now,
        }

        skill = await self.repository.create(Skill, skill_data)
        logger.info(f"Created skill: {name}")
        return skill

    async def get_skill(self, name: str) -> Skill | None:
        """Get skill by name.

        Args:
            name: Skill name

        Returns:
            Skill instance or None if not found
        """
        stmt = select(Skill).where(Skill.name == name)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def update_skill(
        self,
        name: str,
        description: str | None = None,
        version: str | None = None,
        category: str | None = None,
        custom_metadata: dict | None = None,
    ) -> Skill | None:
        """Update an existing skill.

        Args:
            name: Skill name to update
            description: New description
            version: New version
            category: New category
            custom_metadata: Updated metadata

        Returns:
            Updated Skill instance or None if not found
        """
        skill = await self.get_skill(name)
        if not skill:
            logger.warning(f"Skill not found for update: {name}")
            return None

        update_data = {"updated_at": datetime.now(timezone.utc)}

        if description is not None:
            update_data["description"] = description
        if version is not None:
            update_data["version"] = version
        if category is not None:
            update_data["category"] = category
        if custom_metadata is not None:
            update_data["custom_metadata"] = json.dumps(custom_metadata)

        updated_skill = await self.repository.update(Skill, skill.id, update_data)
        logger.info(f"Updated skill: {name}")
        return updated_skill

    async def delete_skill(self, name: str) -> bool:
        """Delete a skill.

        Args:
            name: Skill name to delete

        Returns:
            True if deleted, False if not found
        """
        skill = await self.get_skill(name)
        if not skill:
            logger.warning(f"Skill not found for deletion: {name}")
            return False

        await self.repository.delete(Skill, skill.id)
        logger.info(f"Deleted skill: {name}")
        return True

    async def list_skills(
        self, category: str | None = None, limit: int = 100, offset: int = 0
    ) -> list[Skill]:
        """List all skills with optional filtering.

        Args:
            category: Filter by category
            limit: Maximum results
            offset: Pagination offset

        Returns:
            List of Skill instances
        """
        stmt = select(Skill)

        if category:
            stmt = stmt.where(Skill.category == category)

        stmt = stmt.limit(limit).offset(offset).order_by(Skill.created_at.desc())

        result = await self.session.execute(stmt)
        skills = result.scalars().all()
        logger.debug(f"Listed {len(skills)} skills")
        return list(skills)

    async def increment_usage(self, name: str) -> None:
        """Increment usage counter for a skill.

        Args:
            name: Skill name
        """
        skill = await self.get_skill(name)
        if skill:
            await self.repository.update(
                Skill,
                skill.id,
                {
                    "usage_count": skill.usage_count + 1,
                    "updated_at": datetime.now(timezone.utc),
                },
            )
            logger.debug(f"Incremented usage for skill: {name}")

    def validate_skill_name(self, name: str) -> tuple[bool, str]:
        """Validate skill name format (Anthropic spec).

        Args:
            name: Skill name to validate

        Returns:
            Tuple of (valid: bool, message: str)
        """
        import re

        # Check hyphen-case format
        if not re.match(r"^[a-z0-9-]+$", name):
            return (
                False,
                f"Name '{name}' must be hyphen-case (lowercase letters, digits, and hyphens only)",
            )

        # Check no leading/trailing/consecutive hyphens
        if name.startswith("-") or name.endswith("-") or "--" in name:
            return (
                False,
                f"Name '{name}' cannot start/end with hyphen or contain consecutive hyphens",
            )

        # Check length (reasonable limit)
        if len(name) > 50:
            return False, f"Name '{name}' is too long (max 50 characters)"

        return True, "Valid skill name"

    def validate_description(self, description: str) -> tuple[bool, str]:
        """Validate skill description (Anthropic spec).

        Args:
            description: Description to validate

        Returns:
            Tuple of (valid: bool, message: str)
        """
        # Check for angle brackets (not allowed)
        if "<" in description or ">" in description:
            return False, "Description cannot contain angle brackets (< or >)"

        # Check minimum length
        if len(description.strip()) < 20:
            return False, "Description is too short (minimum 20 characters)"

        return True, "Valid description"
