"""Knowledge Manager portmanteau tool for Advanced Memory MCP server.

This tool consolidates knowledge operations and research orchestration.
It reduces the number of MCP tools while maintaining full functionality.
"""

from typing import Any

from loguru import logger

from advanced_memory.mcp.mcp_instance import mcp
from advanced_memory.mcp.models.portmanteau import KnowledgeOperation


@mcp.tool(name="adn_knowledge")
async def adn_knowledge(op: KnowledgeOperation) -> Any:
    """
    Advanced intelligence and analysis for the knowledge base.

    This tool leverages LLMs and semantic metrics to enhance, summarize,
    and visualize the maturity of the knowledge graph.

    ---------------------------------------------------------------------------
    [RATIONALE]
    Knowledge bases often suffer from 'runt' notes (thin, low-value content)
    or missing connections. By consolidating intelligence operations, we
    provide a unified interface for active maintenance, ensuring the corpus
    remains high-quality, discoverable, and visually mapped.

    ---------------------------------------------------------------------------
    [SUPPORTED OPERATIONS]
    - suggest_tags: Proposes semantically relevant tags based on content.
    - summarize: Generates a high-fidelity executive summary of a note.
    - enhance: Upgrades quality, structure, and context of existing notes.
    - qc: Quality Control (detects runts/thin notes or junk).
    - canvas: Generates Obsidian-compatible visual maps of note relations.
    - analyze: Performs deeper structural analysis of knowledge clusters.
    - bulk: Applies intelligence operations across multiple notes.

    ---------------------------------------------------------------------------
    [PARAMETERS]
    - operation (str): The intelligence task (summarize, enhance, qc, canvas, etc.).
    - identifier (str, optional): Target note title or permalink.
    - mode (str, optional): QC strategy ('find_runts' or 'find_junk').
    - folder (str, optional): Target directory for scanning or output.
    - max_length (int, optional): Character threshold for runt detection.
    - nodes/edges (list, optional): Graph data for 'canvas' generation.
    - title (str, optional): Filename for the generated .canvas file.
    - update_style/add_context/expand (bool, optional): Enhancement flags.
    - project (str, optional): Override the current active project context.

    ---------------------------------------------------------------------------
    [EXAMPLES]
    ```python
    # Enhance a note with style improvements and extra context
    adn_knowledge(operation="enhance", identifier="Quantum Crypto", update_style=True, add_context=True)

    # Detect 'runt' notes (notes shorter than 200 characters)
    adn_knowledge(operation="qc", mode="find_runts", max_length=200)
    ```
    """
    operation = op.operation
    logger.info(f"MCP tool call tool=adn_knowledge operation={operation}")

    from advanced_memory.mcp.tools.content_manager import _dispatch_content_operations

    # Route to appropriate operation
    if operation == "suggest_tags":
        return await _dispatch_content_operations(
            operation="suggest_tags",
            identifier=op.identifier,
            project=op.project,
            mcp_tool="adn_knowledge:suggest_tags",
        )
    elif operation == "summarize":
        return await _dispatch_content_operations(
            operation="summarize", identifier=op.identifier, project=op.project, mcp_tool="adn_knowledge:summarize"
        )
    elif operation == "enhance":
        return await _dispatch_content_operations(
            operation="enhance",
            identifier=op.identifier,
            update_style=op.update_style,
            add_context=op.add_context,
            expand_sections=op.expand,
            project=op.project,
            mcp_tool="adn_knowledge:enhance",
        )
    elif operation == "qc":
        return await _dispatch_content_operations(
            operation=op.mode,
            folder=op.folder,
            max_content_length=op.max_length,
            project=op.project,
            mcp_tool="adn_knowledge:qc",
        )
    elif operation == "canvas":
        from advanced_memory.mcp.tools.canvas import canvas

        return await (canvas.fn if hasattr(canvas, "fn") else canvas)(
            nodes=op.nodes, edges=op.edges, title=op.title, folder=op.folder, project=op.project
        )
    elif operation == "bulk":
        from advanced_memory.mcp.tools.knowledge_operations import adn_knowledge_bulk

        return await (adn_knowledge_bulk.fn if hasattr(adn_knowledge_bulk, "fn") else adn_knowledge_bulk)(
            operation=op.bulk_operation,
            filters=op.filters,
            action=op.action,
            dry_run=op.dry_run,
            limit=op.limit,
            project=op.project,
        )
    elif operation == "analyze":
        return await _adn_knowledge_analyze(
            operation=op.analysis_type, filters=op.filters, action=op.action, limit=op.limit, project=op.project
        )
    else:
        return f"Error: Unsupported operation {operation}"


async def _adn_knowledge_analyze(
    operation: str,
    filters: dict[str, Any] | None,
    action: dict[str, Any] | None,
    limit: int,
    project: str | None,
) -> str:
    """Handle LLM-powered content analysis operations."""
    from advanced_memory.mcp.project_session import get_active_project

    active_project = get_active_project(project)
    if not active_project:
        return "# Error\n\nNo active project found."

    try:
        from advanced_memory.services.llm_client import get_llm_client

        llm = get_llm_client()

        if operation == "analyze_quality":
            return await _analyze_content_quality(active_project, filters, action, limit, llm)

        elif operation == "suggest_relationships":
            return await _suggest_relationships(active_project, filters, action, limit, llm)

        elif operation == "find_knowledge_gaps" or operation == "find_gaps":
            return await _find_knowledge_gaps(active_project, filters, action, limit, llm)

        elif operation == "cluster_content":
            return await _cluster_content(active_project, filters, action, limit, llm)

        elif operation == "extract_insights":
            return await _extract_insights(active_project, filters, action, limit, llm)

        else:
            return f"# Error\n\nUnknown LLM analysis operation: {operation}"

    except Exception as e:
        logger.error(f"LLM content analysis error: {e}", exc_info=True)
        return f"# Error\n\nFailed to perform analysis: {e!s}\n\nMake sure an LLM provider is configured (use adn_llm to select one)."


async def _analyze_content_quality(
    active_project,
    filters: dict[str, Any] | None,
    action: dict[str, Any] | None,
    limit: int,
    llm,
) -> str:
    """Analyze content quality using LLM."""
    from advanced_memory.mcp.models.portmanteau import SearchQueryOp
    from advanced_memory.mcp.tools.adn_search import adn_search

    # Get notes to analyze
    query = filters.get("query", "*") if filters else "*"
    search_op = SearchQueryOp(operation="query", text=query, page_size=limit, project=active_project.name)

    search_result = await (adn_search.fn if hasattr(adn_search, "fn") else adn_search)(search_op)

    if "No results" in str(search_result) or str(search_result).startswith("# Error"):
        return f"# Quality Analysis\n\nNo notes found to analyze.\n\n{search_result}"

    # Use LLM to analyze quality
    system_prompt = """You are a content quality analyst. Analyze notes and provide quality assessments.

For each note, assess:
1. Readability (clarity, structure)
2. Completeness (coverage of topic)
3. Organization (logical flow, headings)
4. Freshness (relevance, currency)
5. Overall quality score (1-10)

Respond with JSON array:
[
  {
    "note_title": "...",
    "readability": "good|fair|poor",
    "completeness": "complete|partial|incomplete",
    "organization": "excellent|good|needs_work",
    "freshness": "current|somewhat_dated|outdated",
    "quality_score": 8,
    "suggestions": ["suggestion1", "suggestion2"]
  }
]"""

    prompt = f"""Analyze the quality of these notes:

{str(search_result)[:3000]}

Provide quality assessments for each note."""

    try:
        assessments = await llm.generate_json(prompt, system_prompt, max_tokens=2000, temperature=0.3)

        if not isinstance(assessments, list):
            assessments = [assessments] if isinstance(assessments, dict) else []

        result = "# Content Quality Analysis\n\n"
        for assessment in assessments[:limit]:
            result += f"**{assessment.get('note_title', 'Unknown')}**\n"
            result += f"- Quality Score: {assessment.get('quality_score', 'N/A')}/10\n"
            result += f"- Readability: {assessment.get('readability', 'N/A')}\n"
            result += f"- Completeness: {assessment.get('completeness', 'N/A')}\n"
            result += f"- Organization: {assessment.get('organization', 'N/A')}\n"
            result += f"- Freshness: {assessment.get('freshness', 'N/A')}\n"
            if assessment.get("suggestions"):
                result += f"- Suggestions: {', '.join(assessment['suggestions'])}\n"
            result += "\n"

        return result

    except Exception as e:
        return f"# Error\n\nFailed to analyze quality: {e!s}"


async def _suggest_relationships(
    active_project,
    filters: dict[str, Any] | None,
    action: dict[str, Any] | None,
    limit: int,
    llm,
) -> str:
    """Suggest relationships between notes using LLM."""
    from advanced_memory.mcp.models.portmanteau import NotesReadOp, SearchQueryOp
    from advanced_memory.mcp.tools.adn_notes import adn_notes
    from advanced_memory.mcp.tools.adn_search import adn_search

    note_id = filters.get("note_id") if filters else None
    if not note_id:
        return "# Error\n\nsuggest_relationships requires note_id in filters\n\nExample: adn_knowledge({'operation': 'analyze', 'analysis_type': 'suggest_relationships', 'filters': {'note_id': 'My Note'}})"

    # Read the note
    read_op = NotesReadOp(operation="read", identifier=note_id, project=active_project.name)
    note_content = await (adn_notes.fn if hasattr(adn_notes, "fn") else adn_notes)(read_op)

    if not note_content or str(note_content).startswith("# Error"):
        return f"# Error\n\nCould not read note: {note_id}"

    # Get related notes
    search_op = SearchQueryOp(operation="query", text=note_id, page_size=20, project=active_project.name)
    search_result = await (adn_search.fn if hasattr(adn_search, "fn") else adn_search)(search_op)

    # Use LLM to suggest relationships
    system_prompt = """You are a knowledge graph assistant. Analyze notes and suggest relationships.

Suggest how notes relate to each other:
- "relates_to": General relationship
- "depends_on": Dependency relationship
- "implements": Implementation relationship
- "extends": Extension relationship
- "references": Reference relationship

Respond with JSON array:
[
  {
    "source_note": "...",
    "target_note": "...",
    "relationship_type": "relates_to",
    "reason": "explanation"
  }
]"""

    prompt = f"""Analyze this note and suggest relationships with other notes:

**Main Note:**
{str(note_content)[:1500]}

**Related Notes:**
{str(search_result)[:2000]}

Suggest relationships between the main note and related notes."""

    try:
        relationships = await llm.generate_json(prompt, system_prompt, max_tokens=1500, temperature=0.5)

        if not isinstance(relationships, list):
            relationships = [relationships] if isinstance(relationships, dict) else []

        result = f"# Relationship Suggestions\n\n**Note:** {note_id}\n\n"
        for rel in relationships[:limit]:
            result += f"**{rel.get('source_note', 'Unknown')}** → {rel.get('relationship_type', 'relates_to')} → **{rel.get('target_note', 'Unknown')}**\n"
            result += f"  Reason: {rel.get('reason', 'N/A')}\n\n"

        return result

    except Exception as e:
        return f"# Error\n\nFailed to suggest relationships: {e!s}"


async def _find_knowledge_gaps(
    active_project,
    filters: dict[str, Any] | None,
    action: dict[str, Any] | None,
    limit: int,
    llm,
) -> str:
    """Find knowledge gaps using LLM."""
    from advanced_memory.mcp.models.portmanteau import SearchQueryOp
    from advanced_memory.mcp.tools.adn_search import adn_search

    topics = filters.get("topics", []) if filters else []
    if not topics:
        return "# Error\n\nfind_gaps requires topics in filters\n\nExample: adn_knowledge({'operation': 'analyze', 'analysis_type': 'find_gaps', 'filters': {'topics': ['machine-learning', 'ai']}})"

    # Search for notes on these topics
    query = " OR ".join(topics)
    search_op = SearchQueryOp(operation="query", text=query, page_size=50, project=active_project.name)
    search_result = await (adn_search.fn if hasattr(adn_search, "fn") else adn_search)(search_op)

    # Use LLM to identify gaps
    system_prompt = """You are a knowledge gap analyst. Analyze existing content and identify knowledge gaps.

Identify:
1. Missing subtopics
2. Incomplete coverage areas
3. Related topics not covered
4. Areas needing more depth

Respond with JSON:
{
  "gaps": [
    {
      "topic": "...",
      "gap_type": "missing_subtopic|incomplete_coverage|missing_related|needs_depth",
      "description": "...",
      "priority": "high|medium|low"
    }
  ]
}"""

    prompt = f"""Analyze knowledge coverage for topics: {", ".join(topics)}

**Existing Content:**
{str(search_result)[:3000]}

Identify knowledge gaps - what's missing or incomplete?"""

    try:
        gap_analysis = await llm.generate_json(prompt, system_prompt, max_tokens=1500, temperature=0.5)

        gaps = gap_analysis.get("gaps", []) if isinstance(gap_analysis, dict) else []

        result = f"# Knowledge Gap Analysis\n\n**Topics Analyzed:** {', '.join(topics)}\n\n"
        for gap in gaps[:limit]:
            priority_emoji = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(gap.get("priority", "medium"), "🟡")
            result += f"{priority_emoji} **{gap.get('topic', 'Unknown')}**\n"
            result += f"  Type: {gap.get('gap_type', 'N/A')}\n"
            result += f"  Description: {gap.get('description', 'N/A')}\n"
            result += f"  Priority: {gap.get('priority', 'medium')}\n\n"

        return result

    except Exception as e:
        return f"# Error\n\nFailed to find gaps: {e!s}"


async def _cluster_content(
    active_project,
    filters: dict[str, Any] | None,
    action: dict[str, Any] | None,
    limit: int,
    llm,
) -> str:
    """Cluster content semantically using LLM."""
    from advanced_memory.mcp.models.portmanteau import SearchQueryOp
    from advanced_memory.mcp.tools.adn_search import adn_search

    query = filters.get("query", "*") if filters else "*"
    num_clusters = action.get("num_clusters", 5) if action else 5

    # Get notes to cluster
    search_op = SearchQueryOp(operation="query", text=query, page_size=limit, project=active_project.name)
    search_result = await (adn_search.fn if hasattr(adn_search, "fn") else adn_search)(search_op)

    if "No results" in str(search_result) or str(search_result).startswith("# Error"):
        return f"# Content Clustering\n\nNo notes found to cluster.\n\n{search_result}"

    # Use LLM to cluster
    system_prompt = """You are a content clustering assistant. Group related notes into semantic clusters.

Analyze notes and group them by:
- Similar topics/themes
- Related concepts
- Common subject matter

Respond with JSON:
{
  "clusters": [
    {
      "cluster_name": "...",
      "theme": "...",
      "notes": ["note1", "note2"],
      "description": "..."
    }
  ]
}"""

    prompt = f"""Cluster these notes into {num_clusters} semantic groups:

{str(search_result)[:4000]}

Group related notes together."""

    try:
        clusters_data = await llm.generate_json(prompt, system_prompt, max_tokens=2000, temperature=0.4)

        clusters = clusters_data.get("clusters", []) if isinstance(clusters_data, dict) else []

        result = "# Content Clustering\n\n"
        for i, cluster in enumerate(clusters, 1):
            result += f"## Cluster {i}: {cluster.get('cluster_name', 'Unnamed')}\n\n"
            result += f"**Theme:** {cluster.get('theme', 'N/A')}\n\n"
            result += f"**Description:** {cluster.get('description', 'N/A')}\n\n"
            result += f"**Notes ({len(cluster.get('notes', []))}):**\n"
            for note in cluster.get("notes", [])[:10]:
                result += f"- {note}\n"
            result += "\n"

        return result

    except Exception as e:
        return f"# Error\n\nFailed to cluster content: {e!s}"


async def _extract_insights(
    active_project,
    filters: dict[str, Any] | None,
    action: dict[str, Any] | None,
    limit: int,
    llm,
) -> str:
    """Extract key insights from notes using LLM."""
    from advanced_memory.mcp.models.portmanteau import SearchQueryOp
    from advanced_memory.mcp.tools.adn_search import adn_search

    query = filters.get("query", "*") if filters else "*"

    # Get notes to analyze
    search_op = SearchQueryOp(operation="query", text=query, page_size=limit, project=active_project.name)
    search_result = await (adn_search.fn if hasattr(adn_search, "fn") else adn_search)(search_op)

    if "No results" in str(search_result) or str(search_result).startswith("# Error"):
        return f"# Insights Extraction\n\nNo notes found to analyze.\n\n{search_result}"

    # Use LLM to extract insights
    system_prompt = """You are an insights extraction assistant. Analyze notes and extract key insights.

Extract:
1. Key findings
2. Important patterns
3. Notable connections
4. Actionable insights

Respond with JSON:
{
  "insights": [
    {
      "insight": "...",
      "category": "finding|pattern|connection|actionable",
      "supporting_notes": ["note1", "note2"],
      "importance": "high|medium|low"
    }
  ]
}"""

    prompt = f"""Extract key insights from these notes:

{str(search_result)[:4000]}

Identify the most important insights, patterns, and connections."""

    try:
        insights_data = await llm.generate_json(prompt, system_prompt, max_tokens=2000, temperature=0.5)

        insights = insights_data.get("insights", []) if isinstance(insights_data, dict) else []

        result = "# Extracted Insights\n\n"
        for insight in insights[:limit]:
            importance_emoji = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(
                insight.get("importance", "medium"), "🟡"
            )
            result += f"{importance_emoji} **{insight.get('category', 'insight').title()}**\n\n"
            result += f"{insight.get('insight', 'N/A')}\n\n"
            if insight.get("supporting_notes"):
                result += f"*Supported by: {', '.join(insight['supporting_notes'][:3])}*\n\n"

        return result

    except Exception as e:
        return f"# Error\n\nFailed to extract insights: {e!s}"
