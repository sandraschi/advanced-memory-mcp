"""Portmanteau tool for skill system operations.

PORTMANTEAU PATTERN RATIONALE: Consolidates 6+ skill-related operations including
creation, reading, management, and advanced skill operations into a single tool.
Skill operations have clear boundaries and benefit from consolidation while maintaining
conceptual clarity for AI skill management.
"""

from typing import Annotated, Literal

from loguru import logger
from pydantic import Field

from advanced_memory.mcp.mcp_instance import mcp
from advanced_memory.mcp.tools.utils import build_error_response, build_success_response


@mcp.tool
async def adn_skills(
    operation: Annotated[
        Literal[
            "create",
            "read",
            "list",
            "update",
            "delete",
            "search",
            "advanced_create",
            "creator",
            "operations",
            "research",
        ],
        Field(description="Skill operation to perform"),
    ],
    name: Annotated[str | None, Field(description="Skill name")] = None,
    content: Annotated[
        str | None, Field(description="Skill content/description")
    ] = None,
    tags: Annotated[list[str] | None, Field(description="Skill tags")] = None,
    query: Annotated[str | None, Field(description="Search query")] = None,
    skill_type: Annotated[str | None, Field(description="Skill type/category")] = None,
    parameters: Annotated[
        dict | None, Field(description="Additional parameters")
    ] = None,
) -> dict:
    """Unified portmanteau for skill system operations.

    Operations: create, read, list, update, delete, search,
    advanced_create, creator, operations, research.

    For full documentation on parameters and usage examples, call:
    `help(topic="adn_skills")`
    """
    try:
        parameters = parameters or {}

        if operation == "create":
            if not name or not content:
                return build_error_response(
                    "VALIDATION_ERROR",
                    "MISSING_PARAMETER",
                    "Name and content required for skill creation",
                )

            from advanced_memory.mcp.tools.adn_skills import adn_skills as _adn_skills

            result = await _adn_skills(
                "create", name=name, content=content, tags=tags or []
            )
            return build_success_response("create", result)

        elif operation == "read":
            if not name:
                return build_error_response(
                    "VALIDATION_ERROR",
                    "MISSING_PARAMETER",
                    "Skill name required for reading",
                )

            from advanced_memory.mcp.tools.adn_skills_reader import adn_skills_reader

            result = await adn_skills_reader(name)
            return build_success_response("read", result)

        elif operation == "list":
            from advanced_memory.mcp.tools.adn_skills import adn_skills as _adn_skills

            result = await _adn_skills("list")
            return build_success_response("list", result)

        elif operation == "search":
            if not query:
                return build_error_response(
                    "VALIDATION_ERROR",
                    "MISSING_PARAMETER",
                    "Query required for skill search",
                )

            from advanced_memory.mcp.tools.adn_skills import adn_skills as _adn_skills

            result = await _adn_skills("search", query=query)
            return build_success_response("search", result)

        elif operation == "update":
            if not name:
                return build_error_response(
                    "VALIDATION_ERROR",
                    "MISSING_PARAMETER",
                    "Skill name required for update",
                )

            from advanced_memory.mcp.tools.adn_skills import adn_skills as _adn_skills

            update_params = {"name": name}
            if content:
                update_params["content"] = content
            if tags:
                update_params["tags"] = tags
            update_params.update(parameters)

            result = await _adn_skills("update", **update_params)
            return build_success_response("update", result)

        elif operation == "delete":
            if not name:
                return build_error_response(
                    "VALIDATION_ERROR",
                    "MISSING_PARAMETER",
                    "Skill name required for deletion",
                )

            from advanced_memory.mcp.tools.adn_skills import adn_skills as _adn_skills

            result = await _adn_skills("delete", name=name)
            return build_success_response("delete", result)

        elif operation == "advanced_create":
            if not name:
                return build_error_response(
                    "VALIDATION_ERROR",
                    "MISSING_PARAMETER",
                    "Skill name required for advanced creation",
                )

            from advanced_memory.mcp.tools.make_skill_advanced import (
                make_skill_advanced,
            )

            result = await make_skill_advanced(name, content or "", **parameters)
            return build_success_response("advanced_create", result)

        elif operation == "creator":
            if not content:
                return build_error_response(
                    "VALIDATION_ERROR",
                    "MISSING_PARAMETER",
                    "Content/description required for skill creator",
                )

            from advanced_memory.mcp.tools.adn_skills_creator import adn_skills_creator

            result = await adn_skills_creator(content, **parameters)
            return build_success_response("creator", result)

        elif operation == "operations":
            from advanced_memory.mcp.tools.adn_skills_operations_new import (
                adn_skills_operations,
            )

            result = await adn_skills_operations("list")
            return build_success_response("operations", result)

        elif operation == "research":
            topic = (
                query or parameters.get("topic") or (content[:200] if content else None)
            )
            if not topic:
                return build_error_response(
                    "VALIDATION_ERROR",
                    "MISSING_PARAMETER",
                    "query or parameters.topic required for skills research",
                )
            from advanced_memory.mcp.tools.adn_skills_research import (
                adn_skills_research,
            )

            result = await adn_skills_research(
                topic=str(topic),
                sources=parameters.get("sources"),
                max_iterations=parameters.get("max_iterations", 3),
                coverage_threshold=parameters.get("coverage_threshold", 0.85),
                output_format=parameters.get("output_format", "bundle"),
                output_path=parameters.get("output_path"),
            )
            if not result.get("success"):
                return build_error_response(
                    "SKILLS_RESEARCH_ERROR",
                    result.get("error_code", "UNKNOWN"),
                    result.get("error", "Research failed"),
                )
            return build_success_response("research", result)

        else:
            return build_error_response(
                "VALIDATION_ERROR",
                "VALIDATION_ERROR",
                f"Unknown skill operation: {operation}",
            )

    except Exception as e:
        logger.error(f"Skill operation '{operation}' failed: {e}")
        return build_error_response(
            "VALIDATION_ERROR", "VALIDATION_ERROR", f"Operation failed: {str(e)}"
        )
