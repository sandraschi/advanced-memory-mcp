"""Knowledge Manager portmanteau tool for Advanced Memory MCP server.

This tool consolidates knowledge operations and research orchestration.
It reduces the number of MCP tools while maintaining full functionality.
"""

from typing import Optional, List, Dict, Any

from loguru import logger

from advanced_memory.mcp.server import mcp


@mcp.tool(
    description="""Comprehensive knowledge management tool for Advanced Memory knowledge base.

This portmanteau tool consolidates all knowledge operations into a single interface,
reducing MCP tool count while maintaining full functionality for Cursor IDE compatibility.

SUPPORTED OPERATIONS:
- **bulk_update**: Batch update multiple notes (tags, content, metadata)
- **bulk_move**: Move multiple notes between folders
- **bulk_delete**: Delete multiple notes with confirmation
- **tag_analytics**: Analyze tag usage and statistics
- **consolidate_tags**: Merge similar tags (including semantic similarity)
- **tag_maintenance**: Clean up tags (remove duplicates, standardize case)
- **validate_content**: Check note quality and fix issues
- **project_stats**: Analyze project content and activity
- **find_duplicates**: Identify duplicate or similar content
- **research_plan**: Create detailed research roadmap with questions and methodology
- **research_methodology**: Get proven research approaches for different topics
- **research_questions**: Generate focused research questions and sub-questions
- **note_blueprint**: Design optimal note structure for research findings
- **research_workflow**: Step-by-step research execution guide

KNOWLEDGE FEATURES:
- Bulk content operations for efficiency
- Advanced tag analytics and consolidation
- Content validation and quality checking
- Duplicate detection and management
- AI-guided research planning and methodology
- Structured note blueprint generation
- Project statistics and activity analysis

PARAMETERS:
- operation (str, REQUIRED): Knowledge operation type (bulk_update, tag_analytics, research_plan, etc.)
- filters (Dict, optional): Filtering criteria for bulk operations
- action (Dict, optional): Action parameters for bulk operations
- topic (str, optional): Research topic for research operations
- topic_type (str, optional): Type of topic (technical, academic, business, etc.)
- research_type (str, optional): Type of research (exploratory, analysis, comparative, etc.)
- step (int, optional): Research workflow step number
- parameters (Dict, optional): Additional parameters for research operations
- dry_run (bool, default=True): Preview changes without applying them
- limit (int, default=100): Maximum items to process
- project (str, optional): Target project for operations

USAGE EXAMPLES:
Tag analytics: adn_knowledge("tag_analytics", action={"analyze_usage": True})
Bulk tag update: adn_knowledge("bulk_update", filters={"tags": ["draft"]}, action={"add_tags": ["reviewed"]})
Research plan: adn_knowledge("research_plan", topic="quantum computing", topic_type="technical")
Tag consolidation: adn_knowledge("consolidate_tags", action={"semantic_groups": [["mcp", "mcp-server"]]})
Content validation: adn_knowledge("validate_content", action={"checks": ["broken_links", "formatting"]})
Project stats: adn_knowledge("project_stats", project="work")

RETURNS:
Operation-specific results with processing details, statistics, and recommendations.

NOTE: This tool provides all knowledge management functionality in a single interface for better MCP client compatibility.""",
)
async def adn_knowledge(
    operation: str,
    filters: Optional[Dict[str, Any]] = None,
    action: Optional[Dict[str, Any]] = None,
    topic: Optional[str] = None,
    topic_type: Optional[str] = None,
    research_type: Optional[str] = None,
    step: Optional[int] = None,
    parameters: Optional[Dict[str, Any]] = None,
    dry_run: bool = True,
    limit: int = 100,
    project: Optional[str] = None,
) -> str:
    """Comprehensive knowledge management for Advanced Memory knowledge base.

    This portmanteau tool consolidates all knowledge operations:
    - Bulk operations: Update, move, delete multiple notes
    - Tag management: Analytics, consolidation, maintenance
    - Content validation: Quality checking and issue detection
    - Research orchestration: Planning, methodology, workflows
    - Project analysis: Statistics and activity tracking

    Args:
        operation: The knowledge operation to perform
        filters: Filtering criteria for bulk operations
        action: Action parameters for bulk operations
        topic: Research topic for research operations
        topic_type: Type of topic (technical, academic, business, etc.)
        research_type: Type of research (exploratory, analysis, comparative, etc.)
        step: Research workflow step number
        parameters: Additional parameters for research operations
        dry_run: Preview changes without applying them
        limit: Maximum items to process
        project: Optional project name

    Returns:
        Operation-specific result with processing details and statistics

    Examples:
        # Analyze tag usage
        adn_knowledge("tag_analytics", action={"analyze_usage": True})

        # Bulk update notes
        adn_knowledge("bulk_update", filters={"tags": ["draft"]}, action={"add_tags": ["reviewed"]})

        # Create research plan
        adn_knowledge("research_plan", topic="quantum computing", topic_type="technical")

        # Consolidate similar tags
        adn_knowledge("consolidate_tags", action={"semantic_groups": [["mcp", "mcp-server"]]})

        # Validate content quality
        adn_knowledge("validate_content", action={"checks": ["broken_links", "formatting"]})
    """
    logger.info(f"MCP tool call tool=adn_knowledge operation={operation}")

    # Route to appropriate operation
    if operation in ["bulk_update", "bulk_move", "bulk_delete", "tag_analytics", "consolidate_tags", "tag_maintenance", "validate_content", "project_stats", "find_duplicates"]:
        return await _knowledge_operations(operation, filters, action, dry_run, limit, project)
    elif operation in ["research_plan", "research_methodology", "research_questions", "note_blueprint", "research_workflow"]:
        return await _research_orchestrator(operation, topic, topic_type, research_type, step, parameters)
    else:
        return f"# Error\n\nInvalid operation '{operation}'. Supported operations: bulk_update, tag_analytics, research_plan, research_methodology, research_questions, note_blueprint, research_workflow, consolidate_tags, validate_content, project_stats, find_duplicates"


async def _knowledge_operations(operation: str, filters: Optional[Dict[str, Any]], action: Optional[Dict[str, Any]], dry_run: bool, limit: int, project: Optional[str]) -> str:
    """Handle knowledge operations."""
    from advanced_memory.mcp.tools.knowledge_operations import knowledge_operations
    return await knowledge_operations(operation, filters, action, dry_run, limit, project)


async def _research_orchestrator(operation: str, topic: Optional[str], topic_type: Optional[str], research_type: Optional[str], step: Optional[int], parameters: Optional[Dict[str, Any]]) -> str:
    """Handle research orchestrator operations."""
    from advanced_memory.mcp.tools.research_orchestrator import research_orchestrator
    return await research_orchestrator(operation, topic, topic_type, research_type, step, parameters)
