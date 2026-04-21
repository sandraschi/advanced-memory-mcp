"""Knowledge namespaced app for Advanced Memory MCP.

Decomposed from the legacy adn_note_ai and adn_corpus_qc tools.
Follows FastMCP 3.2 GA Managed Namespace standards for AI augmentation.
"""

from typing import Annotated, Any, Literal

from fastmcp import FastMCP
from pydantic import Field

# Initialize the namespaced app
knowledge_app = FastMCP("knowledge")


@knowledge_app.tool(task=True)
async def summarize(
    identifier: Annotated[str, Field(description="Note title or permalink to summarize")],
    project: Annotated[str | None, Field(description="Project context override")] = None,
) -> Any:
    """Intelligence Synthesis Tool
    
    Generates a concise executive summary of a note's content using a high-fidelity LLM.
    """
    from advanced_memory.mcp.tools.content_manager import _dispatch_content_operations
    return await _dispatch_content_operations(
        operation="summarize",
        identifier=identifier,
        project=project,
        mcp_tool="knowledge:summarize"
    )


@knowledge_app.tool(task=True)
async def enhance(
    identifier: Annotated[str, Field(description="Note title or permalink to improve")],
    update_style: Annotated[bool, Field(description="If true, improves tone, structure, and readability")] = True,
    add_context: Annotated[bool, Field(description="If true, pulls in linked definitions and context")] = False,
    expand: Annotated[bool, Field(description="If true, expands thin sections into full paragraphs")] = False,
    project: Annotated[str | None, Field(description="Project context override")] = None,
) -> Any:
    """Intelligence Augmentation Engine
    
    Upgrades the quality of a note by fixing errors, improving style, and expanding context.
    """
    from advanced_memory.mcp.tools.content_manager import _dispatch_content_operations
    return await _dispatch_content_operations(
        operation="enhance",
        identifier=identifier,
        update_style=update_style,
        add_context=add_context,
        expand_sections=expand,
        project=project,
        mcp_tool="knowledge:enhance"
    )


@knowledge_app.tool()
async def suggest_tags(
    identifier: Annotated[str, Field(description="Note title or permalink to analyze")],
    project: Annotated[str | None, Field(description="Project context override")] = None,
) -> Any:
    """Metadata Discovery Tool
    
    Analyzes note content to propose semantically relevant tags for better organization.
    """
    from advanced_memory.mcp.tools.content_manager import _dispatch_content_operations
    return await _dispatch_content_operations(
        operation="suggest_tags",
        identifier=identifier,
        project=project,
        mcp_tool="knowledge:suggest_tags"
    )


@knowledge_app.tool()
async def qc(
    mode: Annotated[Literal["find_runts", "find_junk"], Field(description="QC strategy: 'find_runts' (too short) or 'find_junk' (low value)")],
    folder: Annotated[str | None, Field(description="Optional folder to scan")] = None,
    max_length: Annotated[int, Field(description="Character limit for runt detection")] = 500,
    project: Annotated[str | None, Field(description="Project context override")] = None,
) -> Any:
    """Corpus Quality Control Engine
    
    Identifies thin or low-value notes that require consolidation or refinement.
    """
    from advanced_memory.mcp.tools.content_manager import _dispatch_content_operations
    return await _dispatch_content_operations(
        operation=mode,
        folder=folder,
        max_content_length=max_length,
        project=project,
        mcp_tool="knowledge:qc"
    )
