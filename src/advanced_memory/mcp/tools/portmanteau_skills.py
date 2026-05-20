"""Portmanteau tool for skill system operations.

PORTMANTEAU PATTERN RATIONALE: Consolidates 6+ skill-related operations including
creation, reading, management, and advanced skill operations into a single tool.
Skill operations have clear boundaries and benefit from consolidation while maintaining
conceptual clarity for AI skill management.
"""

from typing import Annotated, Literal

from loguru import logger
from pydantic import BaseModel, Field

from advanced_memory.mcp.mcp_instance import mcp
from advanced_memory.mcp.tools.utils import build_error_response, build_success_response


class SkillCreate(BaseModel):
    operation: Literal["create"] = Field(..., description="Create a new skill")
    name: str = Field(..., description="Unique hyphen-case name for the skill")
    content: str = Field(..., description="Markdown content or description of the skill")
    tags: list[str] | None = Field(None, description="Optional categorization tags")


class SkillRead(BaseModel):
    operation: Literal["read"] = Field(..., description="Read skill content")
    name: str = Field(..., description="Name of the skill to retrieve")


class SkillList(BaseModel):
    operation: Literal["list"] = Field(..., description="List all registered skills")


class SkillSearch(BaseModel):
    operation: Literal["search"] = Field(..., description="Search across the skill library")
    query: str = Field(..., description="Search term or regex")


class SkillDelete(BaseModel):
    operation: Literal["delete"] = Field(..., description="Permanently remove a skill")
    name: str = Field(..., description="Name of the skill to delete")


class SkillAdvancedCreate(BaseModel):
    operation: Literal["advanced_create"] = Field(..., description="Create skill with research chain")
    topic: str = Field(..., description="Topic to research and distill into a skill")
    name: str | None = Field(None, description="Optional name override")


class SkillResearch(BaseModel):
    operation: Literal["research"] = Field(..., description="Run research chain on a topic")
    topic: str = Field(..., description="Topic to investigate")
    max_iterations: int = Field(3, description="Maximum research depth iterations")


SkillOperation = Annotated[
    SkillCreate | SkillRead | SkillList | SkillSearch | SkillDelete | SkillAdvancedCreate | SkillResearch,
    Field(discriminator="operation"),
]


@mcp.tool
async def adn_skills(args: SkillOperation) -> dict:
    """[RATIONALE]
    Registry Optimization: This tool consolidates all skill-related operations (CRUD, Research, Synthesis)
    into a single portmanteau to stay within the ~100-tool limit of agentic IDEs like Antigravity.
    By using a Discriminated Union, we maintain 100% parameter fidelity and static scannability.

    [SUPPORTED OPERATIONS]
    - create: Register a new skill manually
    - read: Retrieve full skill content and metadata
    - list: Inventory all active skills in the library
    - search: Semantic search across skill titles and descriptions
    - delete: Permanently remove a skill from the ecosystem
    - advanced_create: Autonomous research -> synthesis -> skill creation loop
    - research: Standalone knowledge distillation chain
    - create: Register a new skill with standardized folder structure
    - read: Retrieve full SKILL.md content and metadata
    - update: Modify existing skill content or metadata
    - delete: Permanently remove a skill and its resources
    - list: Inventory all available skills with status summaries
    - activate: Load a skill's Table of Contents into active context
    - deactivate: Remove skills from active context to reclaim space
    - active: List currently 'open' skills and their loaded sections
    - load_section: Inject a specific subsection (e.g. 'Decorators') on-demand
    - load_resource: Inject a bundled resource file (script/reference)
    - research: Automated knowledge distillation from external sources
    - suggest_tags: Metadata discovery for better skill organization

    [EXAMPLES]
    - adn_skills(operation="create", skill_name="python-expert", description="Expert Python rules")
    - adn_skills(operation="activate", identifier="python-expert", scope="session")
    - adn_skills(operation="load_section", identifier="python-expert", section="Decorators")
    """
    try:
        operation = args.operation
        logger.info(f"Skill operation: {operation}")

        if isinstance(args, SkillCreate):
            from advanced_memory.mcp.tools.adn_skills_creator import adn_skills_creator
            result = await adn_skills_creator(
                name=args.skill_name,
                description=args.description,
                category=args.category,
                difficulty=args.difficulty,
                project=args.project
            )
            return build_success_response("create", result)

        elif isinstance(args, SkillRead):
            from advanced_memory.mcp.tools.adn_skills_reader import adn_skills_reader
            result = await adn_skills_reader(args.identifier, project=args.project)
            return build_success_response("read", result)

        elif isinstance(args, SkillDelete):
            from advanced_memory.mcp.tools.adn_skills import adn_skills as _adn_skills
            result = await _adn_skills("delete", name=args.name, project=args.project)
            return build_success_response("delete", result)

        elif isinstance(args, SkillAdvancedCreate):
            from advanced_memory.mcp.tools.make_skill_advanced import make_skill_advanced
            result = await make_skill_advanced(
                args.name or args.topic,
                args.topic,
                max_iterations=getattr(args, "max_iterations", 3)
            )
            return build_success_response("advanced_create", result)

        elif isinstance(args, SkillSearch):
            from advanced_memory.mcp.tools.adn_skills_research import adn_skills_research
            result = await adn_skills_research(
                topic=str(args.query),
                sources=None,
                max_iterations=3,
                coverage_threshold=0.85,
                output_format="bundle",
                output_path=None,
            )
            if not result.get("success"):
                return build_error_response(
                    "SKILLS_RESEARCH_ERROR",
                    result.get("error_code", "UNKNOWN"),
                    result.get("error", "Research failed"),
                )
            return build_success_response("research", result)

        elif isinstance(args, SkillList):
            from advanced_memory.mcp.tools.adn_skills_operations_new import adn_skills_operations
            result = await adn_skills_operations("list")
            return build_success_response("operations", result)

        else:
            return build_error_response(
                "VALIDATION_ERROR",
                "VALIDATION_ERROR",
                f"Unknown skill operation: {operation}",
            )

    except Exception as e:
        logger.error(f"Skill operation failed: {e}")
        return build_error_response(
            "VALIDATION_ERROR", "VALIDATION_ERROR", f"Operation failed: {e!s}"
        )
