"""Zettelkasten namespaced app for Advanced Memory MCP.

Decomposed from the legacy zettelmaker portmanteau.
Follows FastMCP 3.2 GA Managed Namespace standards for complex cognitive pipelines.
"""

from typing import Annotated, Any, Literal

from fastmcp import FastMCP
from pydantic import Field

# Initialize the namespaced app
zettel_app = FastMCP("zettel")


@zettel_app.tool(task=True)
async def generate(
    topic: Annotated[str, Field(description="Specific topic or keyword for the new note")],
    category: Annotated[str, Field(description="Taxonomy category (e.g., developer, business, math, science)")],
    ai_generate: Annotated[bool, Field(description="If true, uses LLM to bridge gaps in local templates")] = False,
    quality: Annotated[Literal["quick", "standard", "comprehensive", "expert"], Field(description="Level of detail and rigor for the content")] = "standard",
    project: Annotated[str | None, Field(description="Project context override")] = None,
) -> Any:
    """Creation Engine
    
    Synthesizes atomic zettel notes using structured templates or intelligent AI generation.
    """
    from advanced_memory.mcp.tools.zettelmaker import adn_zettelmaker
    return await adn_zettelmaker(
        operation="generate",
        category=category,
        topic=topic,
        ai_generate=ai_generate,
        quality=quality,
        project=project
    )


@zettel_app.tool()
async def suggest(
    category: Annotated[str | None, Field(description="Focus recommendations on a specific domain")] = None,
    count: Annotated[int, Field(description="Number of intelligent topics to propose", ge=1, le=20)] = 5,
    project: Annotated[str | None, Field(description="Project context override")] = None,
) -> Any:
    """Discovery Engine
    
    Identifies structural gaps in the knowledge base and proposes high-value next topics.
    """
    from advanced_memory.mcp.tools.zettelmaker import adn_zettelmaker
    return await adn_zettelmaker(
        operation="suggest",
        category=category,
        count=count,
        project=project
    )


@zettel_app.tool(task=True)
async def expand(
    note_identifier: Annotated[str, Field(description="Title or permalink of the existing note to develop")],
    depth: Annotated[int, Field(description="Iteration depth for horizontal expansion (1-5)", ge=1, le=5)] = 1,
    project: Annotated[str | None, Field(description="Project context override")] = None,
) -> Any:
    """Horizontal Growth Engine
    
    Extends existing notes into broader clusters by identifying and generating related concepts.
    """
    from advanced_memory.mcp.tools.zettelmaker import adn_zettelmaker
    return await adn_zettelmaker(
        operation="expand",
        note_identifier=note_identifier,
        depth=depth,
        project=project
    )


@zettel_app.tool(task=True)
async def analyze(
    category: Annotated[str | None, Field(description="Scope analysis to a specific taxonomy folder")] = None,
    project: Annotated[str | None, Field(description="Project context override")] = None,
) -> Any:
    """Graph Analysis Tool
    
    Evaluates the maturity and connectivity of the current zettelkasten structure.
    """
    from advanced_memory.mcp.tools.zettelmaker import adn_zettelmaker
    return await adn_zettelmaker(
        operation="analyze",
        category=category,
        project=project
    )


@zettel_app.tool(task=True)
async def connect(
    note_identifier: Annotated[str | None, Field(description="Optional anchor note for relationship discovery")] = None,
    project: Annotated[str | None, Field(description="Project context override")] = None,
) -> Any:
    """Connection Engine
    
    Auto-discovers and instantiates semantic relations between existing atomic notes.
    """
    from advanced_memory.mcp.tools.zettelmaker import adn_zettelmaker
    return await adn_zettelmaker(
        operation="connect",
        note_identifier=note_identifier,
        project=project
    )


@zettel_app.tool()
async def collect() -> Any:
    """Rapid Capture Tool
    
    Launches an interactive session for low-friction, off-the-cuff atomic thought record.
    """
    from advanced_memory.mcp.tools.zettelmaker import adn_zettelmaker
    return await adn_zettelmaker(operation="collect")


@zettel_app.tool()
async def customize(
    category: Annotated[str, Field(description="Template category (e.g., 'developer', 'researcher')")],
    topic: Annotated[str, Field(description="Specific topic name within the category")],
    depth: Annotated[int, Field(description="Generation depth level (1-5)", ge=1, le=5)] = 3,
    project: Annotated[str | None, Field(description="Project context override")] = None,
) -> Any:
    """Pipeline Configuration Tool

    Adjusts the parameters of the zettelkasten scaffolding and generation engine
    for a given category/topic pair.
    """
    from advanced_memory.mcp.tools.zettelmaker import adn_zettelmaker
    return await adn_zettelmaker(
        operation="customize",
        category=category,
        topic=topic,
        depth=depth,
    )
