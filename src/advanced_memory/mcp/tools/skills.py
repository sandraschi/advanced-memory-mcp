"""Skills namespaced app for Advanced Memory MCP.

Decomposed from the legacy adn_skills portmanteau.
Implements 'THE DOOR' staged loading pattern for Claude Skills.
Follows FastMCP 3.2 GA Managed Namespace standards.
"""

from typing import Annotated, Any, Literal

from fastmcp import FastMCP
from pydantic import Field

# Initialize the namespaced app
skills_app = FastMCP("skills")


@skills_app.tool()
async def create(
    name: Annotated[str, Field(description="Unique hyphen-case identifier for the skill (e.g., 'python-expert')")],
    description: Annotated[str, Field(description="Clear explanation of when Claude should use this skill (no angle brackets)")],
    category: Annotated[str | None, Field(description="Optional category folder (e.g., 'developer', 'research')")] = "general",
    difficulty: Annotated[Literal["beginner", "intermediate", "advanced", "expert"] | None, Field(description="Target proficiency level")] = "intermediate",
    project: Annotated[str | None, Field(description="Project context override")] = None,
) -> Any:
    """Skill Scaffolding Engine

    Initializes a new Claude Skill with standardized folder structure (scripts, references, assets).
    """
    from advanced_memory.mcp.tools.adn_skills import _create_operation
    return await _create_operation(
        skill_name=name,
        description=description,
        category=category,
        difficulty=difficulty,
        metadata=None,
        project=project
    )


@skills_app.tool()
async def read(
    identifier: Annotated[str, Field(description="Skill name or permalink to retrieve")],
    project: Annotated[str | None, Field(description="Project context override")] = None,
) -> Any:
    """Skill Insight Tool

    Reads the full SKILL.md content and associated metadata for a specific skill.
    """
    from advanced_memory.mcp.tools.adn_skills import _read_operation
    return await _read_operation(identifier, project)


@skills_app.tool()
async def list_skills(
    category: Annotated[str | None, Field(description="Filter by skill category")] = None,
    page: Annotated[int, Field(description="Results page number", ge=1)] = 1,
    page_size: Annotated[int, Field(description="Items per page", ge=1, le=50)] = 20,
    project: Annotated[str | None, Field(description="Project context override")] = None,
) -> Any:
    """Skill Discovery Tool

    Lists all available skills in the knowledge base with status and metadata summaries.
    """
    from advanced_memory.mcp.tools.adn_skills import _list_operation
    filters = {"category": category} if category else None
    return await _list_operation(filters, page, page_size, project)


@skills_app.tool()
async def update(
    identifier: Annotated[str, Field(description="Skill name or permalink to update")],
    content: Annotated[str, Field(description="New markdown content for the SKILL.md file")],
    project: Annotated[str | None, Field(description="Project context override")] = None,
) -> Any:
    """Skill Modification Engine

    Updates the content or metadata of an existing skill.
    """
    from advanced_memory.mcp.tools.adn_skills import _update_operation
    return await _update_operation(identifier, None, content, None, None, project)


@skills_app.tool()
async def delete(
    identifier: Annotated[str, Field(description="Skill name or permalink to permanently remove")],
    project: Annotated[str | None, Field(description="Project context override")] = None,
) -> Any:
    """Skill Deletion Tool

    Permanently removes a skill and its associated resource folders from the knowledge base.
    """
    from advanced_memory.mcp.tools.adn_skills import _delete_operation
    return await _delete_operation(identifier, project)


# --- THE DOOR: Staged Loading (Activation) ---

@skills_app.tool()
async def activate(
    identifier: Annotated[str, Field(description="Skill name to load into active context")],
    scope: Annotated[Literal["message", "session", "persistent"], Field(description="Lifespan of the skill activation")] = "session",
    project: Annotated[str | None, Field(description="Project context override")] = None,
) -> Any:
    """The Door: Skill Activation

    Loads a skill's Table of Contents into the active context without flooding it with full content.
    """
    from advanced_memory.mcp.tools.adn_skills import _activate_operation
    return await _activate_operation(identifier, scope, project)


@skills_app.tool()
async def deactivate(
    identifier: Annotated[str | None, Field(description="Specific skill to unload")] = None,
    all: Annotated[bool, Field(description="If true, clear all active skills from context")] = False,
    project: Annotated[str | None, Field(description="Project context override")] = None,
) -> Any:
    """The Door: Skill Deactivation

    Removes specific or all skills from the active context to reclaim context space.
    """
    from advanced_memory.mcp.tools.adn_skills import _deactivate_operation
    return await _deactivate_operation(identifier, all, project)


@skills_app.tool()
async def active(
    verbose: Annotated[bool, Field(description="Include detailed metadata and activation times")] = False,
    project: Annotated[str | None, Field(description="Project context override")] = None,
) -> Any:
    """The Door: Active Inventory

    Lists all currently 'open' skills and their loaded sections.
    """
    from advanced_memory.mcp.tools.adn_skills import _active_operation
    return await _active_operation(verbose, project)


@skills_app.tool()
async def load_section(
    identifier: Annotated[str, Field(description="Skill name containing the section")],
    section: Annotated[str, Field(description="Section header title (e.g., 'Decorators')")],
    project: Annotated[str | None, Field(description="Project context override")] = None,
) -> Any:
    """The Door: Staged Section Loading

    Injects a specific subsection of a skill into the active context on-demand.
    """
    from advanced_memory.mcp.tools.adn_skills import _load_section_operation
    return await _load_section_operation(identifier, section, project)


@skills_app.tool()
async def load_resource(
    identifier: Annotated[str, Field(description="Skill name containing the resource")],
    resource: Annotated[str, Field(description="Relative path to asset (e.g., 'scripts/linter.py')")],
    project: Annotated[str | None, Field(description="Project context override")] = None,
) -> Any:
    """The Door: Resource Access

    Reads and injects a bundled resource file (script or reference) from the skill's folder.
    """
    from advanced_memory.mcp.tools.adn_skills import _load_resource_operation
    return await _load_resource_operation(identifier, resource, project)


# --- Research & Distillation ---

@skills_app.tool(task=True)
async def research(
    topic: Annotated[str, Field(description="Subject matter to investigate")],
    source: Annotated[Literal["wikipedia", "arxiv", "github", "textbook", "expert"], Field(description="Target intelligence source")] = "wikipedia",
    query: Annotated[str | None, Field(description="Specific search query (optional)")] = None,
    quality: Annotated[Literal["basic", "comprehensive", "expert"], Field(description="Depth of the resulting distillation")] = "comprehensive",
    category: Annotated[str | None, Field(description="Category folder for the generated skill")] = None,
    project: Annotated[str | None, Field(description="Project context override")] = None,
) -> Any:
    """Knowledge Distillation Engine

    Automated research that synthesizes SOTA information from external sources into a structured skill.
    """
    from advanced_memory.mcp.tools.adn_skills_operations_new import (
        _distill_from_arxiv_operation,
        _distill_from_expert_operation,
        _distill_from_textbook_operation,
        _distill_from_wikipedia_operation,
        _import_from_github_operation,
    )

    actual_query = query or topic

    if source == "wikipedia":
        return await _distill_from_wikipedia_operation(topic, depth=1, include_related=True, quality=quality, category=category, project=project)
    elif source == "arxiv":
        return await _distill_from_arxiv_operation(actual_query, max_papers=5, synthesis_level=quality, category=category, project=project)
    elif source == "github":
        return await _import_from_github_operation(repository=topic, source_path=None, branch="main", category=category, project=project)
    elif source == "textbook":
        return await _distill_from_textbook_operation(pdf_path=topic, chapters=None, level="intermediate", category=category, project=project)
    elif source == "expert":
        return await _distill_from_expert_operation(expert_name=topic, source_types=None, focus_area=actual_query, category=category, project=project)

    return f"Unsupported research source: {source}"
