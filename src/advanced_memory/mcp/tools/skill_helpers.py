"""Helper utilities for Claude Skills creation and validation.

This module provides shared utilities for skill frontmatter generation,
validation, and repair suggestions. Used by both adn_content and adn_skills tools.

Claude Skills Format (Anthropic spec):
- name: (required) skill-name-in-hyphen-case
- description: (required) When Claude should use this skill
- license: (optional) License name or file
- allowed-tools: (optional) Pre-approved tools list
- metadata: (optional) Custom key-value pairs
"""

import re
from dataclasses import dataclass

import yaml
from loguru import logger


@dataclass
class SkillFrontmatter:
    """Claude Skills frontmatter structure."""

    name: str  # Required: hyphen-case
    description: str  # Required: when to use skill
    license: str | None = None
    allowed_tools: list[str] | None = None
    metadata: dict | None = None


def generate_skill_frontmatter(
    name: str | None = None,
    description: str | None = None,
    category: str | None = None,
    difficulty: str | None = None,
    license_type: str = "CC-BY-4.0",
    metadata: dict | None = None,
) -> str:
    """Generate Claude Skills YAML frontmatter.

    Args:
        name: Skill name in hyphen-case (auto-generated from title if not provided)
        description: When Claude should use this skill (required)
        category: Skill category (developer, researcher, writer, etc.)
        difficulty: Difficulty level (beginner, intermediate, advanced, expert)
        license_type: License (default: CC-BY-4.0)
        metadata: Additional metadata dict

    Returns:
        YAML frontmatter string ready to prepend to content

    Example:
        frontmatter = generate_skill_frontmatter(
            name="python-expert",
            description="Expert Python guidance...",
            category="developer",
            difficulty="advanced"
        )
    """
    if not description:
        raise ValueError(
            "description is required for skill frontmatter. "
            "Provide a clear description of when Claude should use this skill. "
            "Example: 'Expert Python guidance for advanced patterns and best practices'"
        )

    # Build frontmatter dict
    frontmatter = {"name": name, "description": description, "type": "skill"}

    if license_type:
        frontmatter["license"] = license_type

    # Build metadata section
    if category or difficulty or metadata:
        skill_metadata = metadata.copy() if metadata else {}
        if category:
            skill_metadata["category"] = category
        if difficulty:
            skill_metadata["difficulty"] = difficulty
        frontmatter["metadata"] = skill_metadata

    # Convert to YAML
    yaml_str = yaml.dump(frontmatter, default_flow_style=False, allow_unicode=True, sort_keys=False)

    # Return with --- markers
    return f"---\n{yaml_str}---\n"


def validate_skill_name(name: str) -> tuple[bool, list[str]]:
    """Validate skill name against Anthropic spec.

    Args:
        name: Skill name to validate

    Returns:
        Tuple of (is_valid, list_of_errors)

    Example:
        is_valid, errors = validate_skill_name("python-expert")
        if not is_valid:
            print("\\n".join(errors))
    """
    errors = []

    # Must be hyphen-case (lowercase alphanumeric + hyphen)
    if not re.match(r"^[a-z0-9-]+$", name):
        errors.append(
            f"Name must be hyphen-case (lowercase letters, digits, hyphens only). Got: {name}"
        )

    # Must not start/end with hyphen
    if name.startswith("-") or name.endswith("-"):
        errors.append(f"Name cannot start or end with hyphen. Got: {name}")

    # Must not have consecutive hyphens
    if "--" in name:
        errors.append(f"Name cannot have consecutive hyphens. Got: {name}")

    # Should not be too long
    if len(name) > 100:
        errors.append(f"Name too long ({len(name)} chars). Keep under 100 characters.")

    return (len(errors) == 0, errors)


def parse_skill_frontmatter(content: str) -> tuple[dict | None, str, list[str]]:
    """Parse YAML frontmatter from skill content.

    Args:
        content: Full skill content including frontmatter

    Returns:
        Tuple of (frontmatter_dict, body_content, errors)
        If no frontmatter found, frontmatter_dict is None

    Example:
        fm, body, errors = parse_skill_frontmatter(skill_content)
        if fm:
            print(f"Skill name: {fm['name']}")
    """
    errors = []

    # Match YAML frontmatter
    match = re.match(r"^---\n(.*?)\n---\n(.*)$", content, re.DOTALL)
    if not match:
        errors.append("No YAML frontmatter found. Skills must start with ---")
        return (None, content, errors)

    try:
        frontmatter = yaml.safe_load(match.group(1))
        body = match.group(2)
    except Exception as e:
        errors.append(f"Invalid YAML frontmatter: {str(e)}")
        return (None, content, errors)

    return (frontmatter, body, errors)


def validate_skill_frontmatter(frontmatter: dict) -> tuple[list[str], list[str]]:
    """Validate skill frontmatter against Anthropic spec.

    Args:
        frontmatter: Frontmatter dict to validate

    Returns:
        Tuple of (errors, warnings)

    Example:
        errors, warnings = validate_skill_frontmatter(fm)
        if errors:
            print("ERRORS:", errors)
    """
    errors = []
    warnings = []

    # Check required fields
    if "name" not in frontmatter:
        errors.append("Missing required field: name")
    else:
        name = frontmatter["name"]
        is_valid, name_errors = validate_skill_name(name)
        if not is_valid:
            errors.extend(name_errors)

    if "description" not in frontmatter:
        errors.append("Missing required field: description")
    else:
        desc = frontmatter["description"]
        if "<" in desc or ">" in desc:
            errors.append("Description cannot contain angle brackets (< or >)")
        if len(desc.strip()) < 20:
            warnings.append(
                "Description is quite short (< 20 chars). Consider expanding for better discoverability."
            )

    # Check optional fields format
    if "metadata" in frontmatter and not isinstance(frontmatter["metadata"], dict):
        warnings.append("metadata should be a dictionary")

    if "allowed-tools" in frontmatter and not isinstance(frontmatter["allowed-tools"], list):
        warnings.append("allowed-tools should be a list")

    return (errors, warnings)


def generate_repair_suggestions(errors: list[str], frontmatter: dict | None, content: str) -> str:
    """Generate actionable repair suggestions for invalid skills.

    Args:
        errors: List of validation errors
        frontmatter: Current frontmatter dict (if parseable)
        content: Full skill content

    Returns:
        Markdown-formatted repair suggestions

    Example:
        suggestions = generate_repair_suggestions(errors, fm, content)
        print(suggestions)
    """
    suggestions = ["# Repair Suggestions\n"]

    # No frontmatter at all
    if frontmatter is None:
        suggestions.append("## Add YAML Frontmatter\n")
        suggestions.append(
            "Your skill is missing YAML frontmatter. Add this at the top of the file:\n"
        )
        suggestions.append("```yaml")
        suggestions.append("---")
        suggestions.append("name: your-skill-name  # hyphen-case, lowercase")
        suggestions.append("description: When Claude should use this skill")
        suggestions.append("license: CC-BY-4.0")
        suggestions.append("metadata:")
        suggestions.append("  category: developer  # or researcher, writer, etc.")
        suggestions.append("  difficulty: intermediate  # beginner, intermediate, advanced, expert")
        suggestions.append("---")
        suggestions.append("```\n")
        suggestions.append("**Then add your content below the frontmatter.**\n")
        return "\n".join(suggestions)

    # Missing required fields
    if "name" not in frontmatter:
        suggestions.append("## Add Required Field: name\n")
        suggestions.append("Add this to your frontmatter:\n")
        suggestions.append("```yaml")
        suggestions.append("name: your-skill-name  # Use hyphen-case, lowercase")
        suggestions.append("```\n")

    if "description" not in frontmatter:
        suggestions.append("## Add Required Field: description\n")
        suggestions.append("Add this to your frontmatter:\n")
        suggestions.append("```yaml")
        suggestions.append(
            "description: Expert guidance for [topic]. Use when user asks about [specific use cases]."
        )
        suggestions.append("```\n")
        suggestions.append(
            "**Make the description detailed** so Claude knows when to use the skill.\n"
        )

    # Invalid name format
    if "name" in frontmatter:
        name = frontmatter["name"]
        is_valid, name_errors = validate_skill_name(name)
        if not is_valid:
            suggestions.append("## Fix Skill Name\n")
            suggestions.append(f"Current name: `{name}`\n")
            suggestions.append("Problems:")
            for error in name_errors:
                suggestions.append(f"- {error}")
            suggestions.append("\n**Suggested fix:**")
            # Generate corrected name
            corrected = name.lower()
            corrected = re.sub(r"[^a-z0-9-]", "", corrected)
            corrected = re.sub(r"-+", "-", corrected)
            corrected = corrected.strip("-")
            suggestions.append(f"```yaml\nname: {corrected}\n```\n")

    # Short description
    if "description" in frontmatter:
        desc = frontmatter["description"]
        if len(desc.strip()) < 20:
            suggestions.append("## Improve Description\n")
            suggestions.append(f'Current description ({len(desc)} chars): "{desc}"\n')
            suggestions.append("**Why longer is better:**")
            suggestions.append("- Claude uses description to decide when to load the skill")
            suggestions.append("- More keywords = better discoverability")
            suggestions.append("- Include specific use cases\n")
            suggestions.append("**Example good description:**")
            suggestions.append("```yaml")
            suggestions.append(
                "description: Expert Python guidance for advanced patterns, best practices, and architectural decisions. Use when writing Python code, debugging issues, or discussing Python-specific design patterns."
            )
            suggestions.append("```\n")

    # Add example of complete valid frontmatter
    if len(errors) > 0:
        suggestions.append("## Complete Example\n")
        suggestions.append("Here's a complete, valid frontmatter example:\n")
        suggestions.append("```yaml")
        suggestions.append("---")
        suggestions.append("name: autohotkey-v2-expert")
        suggestions.append(
            "description: Expert guidance for AutoHotkey v2 scripting, automation, and best practices. Use when working with AHK v2, creating hotkeys, or automating Windows tasks."
        )
        suggestions.append("license: CC-BY-4.0")
        suggestions.append("metadata:")
        suggestions.append("  category: developer")
        suggestions.append("  difficulty: advanced")
        suggestions.append("  created: 2025-10-27")
        suggestions.append("---")
        suggestions.append("```\n")

    return "\n".join(suggestions)


def detect_skill_path(folder: str) -> bool:
    """Detect if folder path is for skills.

    Args:
        folder: Folder path to check

    Returns:
        True if this looks like a skills folder

    Example:
        if detect_skill_path("skills/developer"):
            # Auto-generate skill frontmatter
    """
    folder_lower = folder.lower()
    return folder_lower.startswith("skills/") or folder_lower == "skills"


def title_to_skill_name(title: str) -> str:
    """Convert title to valid skill name (hyphen-case).

    Args:
        title: Note title (e.g., "Python Expert" or "AutoHotkey v2 Guide")

    Returns:
        Skill name in hyphen-case (e.g., "python-expert", "autohotkey-v2-guide")

    Example:
        name = title_to_skill_name("Python Best Practices")
        # Returns: "python-best-practices"
    """
    # Convert to lowercase
    name = title.lower()
    # Replace spaces with hyphens
    name = re.sub(r"\s+", "-", name)
    # Remove non-alphanumeric except hyphens
    name = re.sub(r"[^a-z0-9-]", "", name)
    # Remove consecutive hyphens
    name = re.sub(r"-+", "-", name)
    # Strip leading/trailing hyphens
    return name.strip("-")


logger.debug("Loaded skill_helpers module")
