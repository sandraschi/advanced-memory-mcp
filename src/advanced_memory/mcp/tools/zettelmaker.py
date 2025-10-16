"""Zettelmaker portmanteau tool for Advanced Memory MCP server.

This tool consolidates all zettelkasten generation and management operations.
It provides intelligent template generation, customization, expansion, suggestions,
connections, and knowledge gap analysis.
"""

from textwrap import dedent
from typing import Any

from fastmcp import Context
from loguru import logger

from advanced_memory.cli.zettelkasten_content import (
    DEVELOPER_TEMPLATES,
    KNOWLEDGE_WORKER_TEMPLATES,
    RESEARCHER_TEMPLATES,
    WRITER_TEMPLATES,
)
from advanced_memory.mcp.async_client import client
from advanced_memory.mcp.mcp_instance import mcp
from advanced_memory.mcp.project_session import add_project_metadata, session
from advanced_memory.mcp.tools import write_note as mcp_write_note
from advanced_memory.mcp.tools.utils import call_get

# Aggregate all content templates
CONTENT_TEMPLATES: dict[str, dict[str, Any]] = {
    "developer": DEVELOPER_TEMPLATES,
    "researcher": RESEARCHER_TEMPLATES,
    "writer": WRITER_TEMPLATES,
    "knowledge-worker": KNOWLEDGE_WORKER_TEMPLATES,
}


@mcp.tool
async def adn_zettelmaker(
    operation: str,
    category: str | None = None,
    topic: str | None = None,
    note_identifier: str | None = None,
    depth: int = 3,
    count: int = 5,
    ai_generate: bool = False,
    quality: str = "standard",
    ctx: Context | None = None,
) -> str:
    """Intelligent zettelkasten generation and management for knowledge scaffolding.

    This portmanteau tool consolidates all zettelkasten operations into a single interface,
    providing AI-powered template generation, customization, expansion, and analysis.

    SUPPORTED OPERATIONS:
    - generate: Generate notes from templates (category + topic required)
    - customize: Customize template generation parameters
    - expand: Extend existing notes with new related topics
    - suggest: Get AI-suggested topics based on existing knowledge
    - connect: Auto-create relationships between related notes
    - analyze: Analyze knowledge gaps and recommend templates

    CATEGORIES:
    - developer: Python, Git, Testing, Architecture, etc.
    - researcher: Research methods, critical thinking, writing
    - writer: Craft, storytelling, publishing
    - knowledge-worker: Productivity, PKM, communication

    TOPICS (examples by category):
    - developer: python-core, git, testing, architecture
    - researcher: research-methods, critical-thinking, academic-writing
    - writer: storytelling, editing, publishing
    - knowledge-worker: productivity, note-taking, communication

    Args:
        operation: The operation to perform (generate, customize, expand, suggest, connect, analyze)
        category: Template category (developer, researcher, writer, knowledge-worker)
        topic: Specific topic within category (python-core, git, etc.) or any custom topic with ai_generate=True
        note_identifier: Title/permalink of existing note (for expand operation)
        depth: Depth of analysis or generation (1-5, default: 3)
        count: Number of suggestions/connections to return (default: 5)
        ai_generate: Use AI to generate templates for any topic (requires API key, default: False)
        quality: Quality level for AI generation (quick, standard, comprehensive, expert, default: standard)
        ctx: Optional MCP context for progress reporting

    Returns:
        Operation-specific result with generated notes, suggestions, or analysis

    Examples:
        # Generate Python templates (pre-built)
        adn_zettelmaker("generate", category="developer", topic="python-core")

        # Generate AI-powered templates for any topic
        adn_zettelmaker("generate", category="developer", topic="Rust Programming",
                        ai_generate=True, quality="comprehensive")

        # Get suggestions for next topics
        adn_zettelmaker("suggest", category="developer", count=5)

        # Analyze knowledge gaps
        adn_zettelmaker("analyze", category="developer", depth=3)

        # Expand existing note
        adn_zettelmaker("expand", note_identifier="Python Fundamentals", depth=2)
    """
    logger.info(
        f"MCP tool call tool=adn_zettelmaker operation={operation} category={category} topic={topic}"
    )

    # Route to appropriate operation
    if operation == "generate":
        return await _generate_operation(category, topic, ai_generate, quality, ctx)
    elif operation == "customize":
        return await _customize_operation(category, topic, depth, ctx)
    elif operation == "expand":
        return await _expand_operation(note_identifier, depth, ctx)
    elif operation == "suggest":
        return await _suggest_operation(category, count, ctx)
    elif operation == "connect":
        return await _connect_operation(count, ctx)
    elif operation == "analyze":
        return await _analyze_operation(category, depth, ctx)
    else:
        return dedent(
            f"""
            # Error

            Invalid operation '{operation}'.

            Supported operations:
            - generate: Generate notes from templates
            - customize: Customize template generation
            - expand: Extend existing notes
            - suggest: Get topic suggestions
            - connect: Auto-create relationships
            - analyze: Analyze knowledge gaps

            Use: adn_zettelmaker("generate", category="developer", topic="python-core")
            """
        ).strip()


async def _generate_operation(
    category: str | None,
    topic: str | None,
    ai_generate: bool,
    quality: str,
    ctx: Context | None,
) -> str:
    """Handle generate operation - create notes from templates.

    Supports both pre-built templates and AI-powered generation for any topic.
    """
    if not category:
        return dedent(
            """
            # Error

            Generate operation requires 'category' parameter.

            Available categories:
            - developer: Python, Git, Testing, Architecture
            - researcher: Research methods, critical thinking
            - writer: Storytelling, editing, publishing
            - knowledge-worker: Productivity, PKM, communication

            Example: adn_zettelmaker("generate", category="developer", topic="python-core")
            """
        ).strip()

    if category not in CONTENT_TEMPLATES:
        return dedent(
            f"""
            # Error

            Unknown category '{category}'.

            Available categories: {", ".join(CONTENT_TEMPLATES.keys())}
            """
        ).strip()

    # If no topic specified, show available topics
    if not topic:
        available_topics = list(CONTENT_TEMPLATES[category].keys())
        topics_list = "\n".join(f"- {topic}" for topic in available_topics)

        return dedent(
            f"""
            # Available Topics in '{category}' Category

            {topics_list}

            Usage: adn_zettelmaker("generate", category="{category}", topic="<topic>")

            **AI Generation Available:**
            Generate templates for ANY topic:
            ```
            adn_zettelmaker("generate",
                category="{category}",
                topic="Your Custom Topic",
                ai_generate=True,
                quality="comprehensive")
            ```
            """
        ).strip()

    # Check if using AI generation
    if ai_generate:
        return await _generate_with_ai(category, topic, quality, ctx)

    # Validate topic exists in pre-built templates
    if topic not in CONTENT_TEMPLATES[category]:
        available_topics = list(CONTENT_TEMPLATES[category].keys())
        return dedent(
            f"""
            # Error

            Unknown topic '{topic}' in category '{category}'.

            Available topics: {", ".join(available_topics)}

            **Or use AI generation for custom topics:**
            ```
            adn_zettelmaker("generate",
                category="{category}",
                topic="{topic}",
                ai_generate=True,
                quality="standard")
            ```
            """
        ).strip()

    if ctx:  # pragma: no cover
        await ctx.info(f"Generating pre-built templates for {category}/{topic}")

    # Get templates for the topic
    templates = CONTENT_TEMPLATES[category][topic]
    notes_created = []

    # Create notes from templates
    for template in templates:
        try:
            if ctx:  # pragma: no cover
                await ctx.info(f"Creating note: {template['title']}")

            result = await mcp_write_note.fn(
                title=template["title"], content=template["content"], folder=template["folder"]
            )

            notes_created.append(template["title"])

        except Exception as e:
            logger.error(f"Error creating note {template['title']}: {e}")

    result = dedent(
        f"""
        # ✅ Zettelkasten Generated Successfully

        **Category:** {category}
        **Topic:** {topic}
        **Notes Created:** {len(notes_created)}
        **Source:** Pre-built templates

        ## Created Notes:
        {chr(10).join(f"- {title}" for title in notes_created)}

        ## Next Steps

        1. Explore your new notes with search
        2. Connect ideas by adding [[WikiLinks]]
        3. Build on this foundation with your own notes
        4. Use `adn_zettelmaker("suggest", category="{category}")` for next topics

        ---
        *Happy knowledge building! 📚*
        """
    ).strip()

    return add_project_metadata(result, session.get_current_project())


async def _generate_with_ai(category: str, topic: str, quality: str, ctx: Context | None) -> str:
    """Generate templates using AI for any custom topic.

    Args:
        category: Template category
        topic: Custom topic name
        quality: Quality level (quick, standard, comprehensive, expert)
        ctx: MCP context
    """
    from advanced_memory.services.ai_integration import AIIntegration
    from advanced_memory.services.template_generator import TemplateGenerator

    if ctx:  # pragma: no cover
        await ctx.info(f"Generating AI-powered templates for {topic} ({quality} quality)")

    try:
        # Initialize services
        generator = TemplateGenerator()
        ai_service = AIIntegration()

        # Check cache first
        cached_templates = generator.get_cached_template(topic, category, quality)
        if cached_templates:
            if ctx:  # pragma: no cover
                await ctx.info(f"Found {len(cached_templates)} cached templates for {topic}")

            # Create notes from cached templates
            notes_created = []
            for template in cached_templates:
                try:
                    result = await mcp_write_note.fn(
                        title=template["title"],
                        content=template["content"],
                        folder=template["folder"],
                    )
                    notes_created.append(template["title"])
                except Exception as e:
                    logger.error(f"Error creating note {template.get('title')}: {e}")

            result = dedent(
                f"""
                # ✅ AI-Generated Zettelkasten (Cached)

                **Category:** {category}
                **Topic:** {topic}
                **Quality Level:** {quality}
                **Notes Created:** {len(notes_created)}
                **Source:** Cached AI templates

                ## Created Notes:
                {chr(10).join(f"- {title}" for title in notes_created)}

                ---
                *Templates were retrieved from cache for instant generation! 🚀*
                """
            ).strip()

            return add_project_metadata(result, session.get_current_project())

        # Generate new templates with AI
        if ctx:  # pragma: no cover
            await ctx.info("Generating new templates with AI...")

        prompt = generator.get_generation_prompt(topic, category, quality)
        templates = await ai_service.generate_templates(prompt)

        # Validate templates
        is_valid, error_msg = generator.validate_generated_template(templates)
        if not is_valid:
            return dedent(
                f"""
                # ❌ Template Generation Failed

                **Error:** {error_msg}

                The AI-generated templates did not pass quality validation.
                Please try again or use a different quality level.
                """
            ).strip()

        # Cache templates for future use
        generator.cache_template(topic, category, quality, templates)

        # Create notes from generated templates
        notes_created = []
        for template in templates:
            try:
                if ctx:  # pragma: no cover
                    await ctx.info(f"Creating AI-generated note: {template['title']}")

                result = await mcp_write_note.fn(
                    title=template["title"],
                    content=template["content"],
                    folder=template["folder"],
                )
                notes_created.append(template["title"])

            except Exception as e:
                logger.error(f"Error creating note {template.get('title')}: {e}")

        quality_config = TemplateGenerator.QUALITY_LEVELS.get(quality, {})

        result = dedent(
            f"""
            # ✅ AI-Generated Zettelkasten Created!

            **Category:** {category}
            **Topic:** {topic}
            **Quality Level:** {quality} ({quality_config.get("description", "")})
            **Notes Created:** {len(notes_created)}
            **Source:** AI-generated (Claude/OpenAI)

            ## Created Notes:
            {chr(10).join(f"- {title}" for title in notes_created)}

            ## Template Details
            - Expected notes: {quality_config.get("note_count", "N/A")}
            - Depth: {quality_config.get("depth", "N/A")}
            - Examples: {"✅" if quality_config.get("examples") else "❌"}
            - Exercises: {"✅" if quality_config.get("exercises") else "❌"}

            ## Next Steps

            1. Review the AI-generated notes
            2. Refine and add your own insights
            3. Connect to your existing knowledge
            4. Generate related topics with AI

            ---
            *Templates cached for instant reuse! 🚀*
            """
        ).strip()

        return add_project_metadata(result, session.get_current_project())

    except NotImplementedError as e:
        return dedent(
            f"""
            # 🤖 AI Generation Setup Required

            {str(e)}

            ## Setup Instructions

            1. **Get API Key:**
               - Anthropic: https://console.anthropic.com/
               - OpenAI: https://platform.openai.com/

            2. **Set Environment Variable:**
               ```bash
               # For Anthropic (recommended)
               export ANTHROPIC_API_KEY=your-key-here

               # Or for OpenAI
               export OPENAI_API_KEY=your-key-here
               ```

            3. **Install Library:**
               ```bash
               pip install anthropic  # or openai
               ```

            4. **Restart Claude Desktop** to load new environment variable

            5. **Try again:**
               ```
               adn_zettelmaker("generate",
                   category="{category}",
                   topic="{topic}",
                   ai_generate=True,
                   quality="{quality}")
               ```

            ## For Now

            Use pre-built templates without AI:
            ```
            adn_zettelmaker("generate", category="{category}", topic="python-core")
            ```
            """
        ).strip()

    except Exception as e:
        logger.error(f"Error in AI generation: {e}")
        return dedent(
            f"""
            # ❌ AI Generation Error

            **Error:** {str(e)}

            ## Troubleshooting

            1. Check API key is set correctly
            2. Verify internet connection
            3. Check API quota/limits
            4. Try again with different quality level

            ## Fallback

            Use pre-built templates instead:
            ```
            adn_zettelmaker("generate", category="{category}", topic="python-core")
            ```
            """
        ).strip()


async def _customize_operation(
    category: str | None, topic: str | None, depth: int, ctx: Context | None
) -> str:
    """Handle customize operation - customize template generation parameters."""
    if not category or not topic:
        return dedent(
            """
            # Customize Template Generation

            This operation allows you to customize template generation parameters.

            **Status:** Coming in Phase 2 (Dynamic Template Generation)

            For now, use the standard generate operation:
            ```
            adn_zettelmaker("generate", category="developer", topic="python-core")
            ```

            **Future Features:**
            - Custom depth levels
            - Focus area selection
            - Quality levels (Quick, Standard, Comprehensive, Expert)
            - Skip specific sections
            - Add custom sections
            """
        ).strip()

    result = dedent(
        f"""
        # 🔧 Template Customization (Preview)

        **Category:** {category}
        **Topic:** {topic}
        **Depth:** {depth}

        **Current Status:** Phase 1 - Basic generation only

        **Coming in Phase 2:**
        - AI-powered template generation for any topic
        - Quality levels: Quick, Standard, Comprehensive, Expert
        - Custom focus areas
        - Section selection
        - Template modification before generation

        **For now, use:**
        ```
        adn_zettelmaker("generate", category="{category}", topic="{topic}")
        ```
        """
    ).strip()

    return add_project_metadata(result, session.get_current_project())


async def _expand_operation(note_identifier: str | None, depth: int, ctx: Context | None) -> str:
    """Handle expand operation - extend existing notes with new topics."""
    if not note_identifier:
        return dedent(
            """
            # Expand Existing Notes

            This operation extends existing notes with related topics.

            **Status:** Coming in Phase 1 (next sprint)

            **Usage:**
            ```
            adn_zettelmaker("expand",
                note_identifier="Python Fundamentals",
                depth=2)
            ```

            **What it will do:**
            - Analyze the existing note content
            - Identify related topics
            - Generate linked notes for those topics
            - Add cross-references automatically

            **For now:**
            Use `adn_zettelmaker("suggest")` to find related topics manually.
            """
        ).strip()

    result = dedent(
        f"""
        # 🌱 Expand Note (Preview)

        **Note:** {note_identifier}
        **Depth:** {depth}

        **Current Status:** Implementation in progress

        **Will analyze:**
        - Existing note content
        - Related concepts mentioned
        - Knowledge gaps in the area

        **Will create:**
        - {depth} levels of related notes
        - Automatic cross-references
        - Connected knowledge graph

        **Alternative for now:**
        1. Use search to find the note
        2. Manually identify related topics
        3. Generate those topics with `adn_zettelmaker("generate")`
        """
    ).strip()

    return add_project_metadata(result, session.get_current_project())


async def _suggest_operation(category: str | None, count: int, ctx: Context | None) -> str:
    """Handle suggest operation - get AI-suggested topics."""
    if ctx:  # pragma: no cover
        await ctx.info(
            f"Analyzing knowledge base for suggestions in {category or 'all categories'}"
        )

    # Get current project stats via API
    try:
        response = await call_get(client, f"/{session.get_current_project()}/entities")
        entities_data = response.json()

        total_notes = len(entities_data.get("entities", []))

        # Build suggestions based on what user has
        suggestions = []

        # If they have developer notes, suggest related topics
        if category == "developer" or not category:
            suggestions.extend(
                [
                    {
                        "topic": "python-core",
                        "category": "developer",
                        "reason": "Essential Python programming fundamentals",
                        "estimated_notes": 15,
                    },
                    {
                        "topic": "git",
                        "category": "developer",
                        "reason": "Version control for all developers",
                        "estimated_notes": 12,
                    },
                    {
                        "topic": "testing",
                        "category": "developer",
                        "reason": "Software quality and testing practices",
                        "estimated_notes": 10,
                    },
                ]
            )

        if category == "researcher" or not category:
            suggestions.extend(
                [
                    {
                        "topic": "research-methods",
                        "category": "researcher",
                        "reason": "Systematic research approaches",
                        "estimated_notes": 12,
                    }
                ]
            )

        if category == "writer" or not category:
            suggestions.extend(
                [
                    {
                        "topic": "storytelling",
                        "category": "writer",
                        "reason": "Narrative craft and structure",
                        "estimated_notes": 10,
                    }
                ]
            )

        if category == "knowledge-worker" or not category:
            suggestions.extend(
                [
                    {
                        "topic": "productivity",
                        "category": "knowledge-worker",
                        "reason": "Effective work practices",
                        "estimated_notes": 14,
                    }
                ]
            )

        # Limit to requested count
        suggestions = suggestions[:count]

        suggestions_text = "\n\n".join(
            f"**{i + 1}. {s['topic']}** ({s['category']})\n"
            f"   - Why: {s['reason']}\n"
            f"   - Will create: ~{s['estimated_notes']} interconnected notes\n"
            f"   - Generate: `adn_zettelmaker('generate', category='{s['category']}', topic='{s['topic']}')`"
            for i, s in enumerate(suggestions)
        )

        result = dedent(
            f"""
            # 💡 Suggested Topics for Your Knowledge Base

            **Current Notes:** {total_notes}
            **Category Filter:** {category or "All categories"}

            ## Recommended Topics

            {suggestions_text}

            ## How to Use

            Pick a topic and generate it:
            ```
            adn_zettelmaker("generate",
                category="developer",
                topic="python-core")
            ```

            **Coming in Phase 4 (Smart Onboarding):**
            - Personalized suggestions based on your existing notes
            - Knowledge gap detection
            - Skill level adaptation
            - Custom learning paths
            """
        ).strip()

        return add_project_metadata(result, session.get_current_project())

    except Exception as e:
        logger.error(f"Error getting suggestions: {e}")
        return dedent(
            f"""
            # 💡 Topic Suggestions

            **Error getting current knowledge stats:** {str(e)}

            **Popular Topics:**
            1. **python-core** (developer) - Python fundamentals
            2. **git** (developer) - Version control
            3. **research-methods** (researcher) - Research approaches
            4. **productivity** (knowledge-worker) - Effective work

            Generate any topic:
            ```
            adn_zettelmaker("generate", category="developer", topic="python-core")
            ```
            """
        ).strip()


async def _connect_operation(count: int, ctx: Context | None) -> str:
    """Handle connect operation - auto-create relationships between notes."""
    if ctx:  # pragma: no cover
        await ctx.info("Analyzing notes for potential connections")

    result = dedent(
        f"""
        # 🔗 Auto-Connect Notes (Preview)

        **Requested Connections:** {count}

        **Current Status:** Coming in Phase 1 (next sprint)

        **What it will do:**
        - Analyze note content for related concepts
        - Identify semantic similarities
        - Suggest relationship types (builds_on, related_to, etc.)
        - Auto-add [[WikiLinks]] between notes
        - Create bridge notes for complex relationships

        **Algorithm:**
        1. Extract key concepts from all notes
        2. Calculate semantic similarity scores
        3. Identify relationship patterns
        4. Rank connection opportunities
        5. Generate top {count} suggestions

        **For now:**
        - Manually add [[WikiLinks]] in your notes
        - Use consistent naming for automatic linking
        - Add observations with [category] prefixes

        **Example:**
        ```markdown
        - related_to [[Python Fundamentals]]
        - builds_on [[Programming Basics]]
        ```
        """
    ).strip()

    return add_project_metadata(result, session.get_current_project())


async def _analyze_operation(category: str | None, depth: int, ctx: Context | None) -> str:
    """Handle analyze operation - analyze knowledge gaps and recommend templates."""
    if ctx:  # pragma: no cover
        await ctx.info(f"Analyzing knowledge base for gaps in {category or 'all areas'}")

    try:
        # Get current entities
        response = await call_get(client, f"/{session.get_current_project()}/entities")
        entities_data = response.json()

        total_notes = len(entities_data.get("entities", []))

        # Basic analysis
        coverage = {}
        for cat_name, cat_templates in CONTENT_TEMPLATES.items():
            coverage[cat_name] = {
                "available_topics": len(cat_templates),
                "estimated_notes": sum(len(templates) for templates in cat_templates.values()),
            }

        coverage_text = "\n".join(
            f"- **{cat}**: {info['available_topics']} topics, ~{info['estimated_notes']} notes available"
            for cat, info in coverage.items()
        )

        result = dedent(
            f"""
            # 📊 Knowledge Base Analysis

            **Current Notes:** {total_notes}
            **Analysis Depth:** {depth}
            **Category Focus:** {category or "All categories"}

            ## Available Template Coverage

            {coverage_text}

            ## Recommendations

            ### 🎯 Quick Wins
            - Start with 'developer' → 'python-core' (15 notes)
            - Add 'git' fundamentals (12 notes)
            - Build testing knowledge (10 notes)

            ### 📈 Growth Opportunities
            - Expand into multiple categories
            - Create cross-category connections
            - Build progressive learning paths

            ### 🔮 Coming in Phase 4 (Smart Onboarding)
            - Automatic skill level detection
            - Personalized gap analysis
            - Custom learning paths based on your existing notes
            - Intelligent recommendations matching your style

            ## Get Started

            Generate your first template:
            ```
            adn_zettelmaker("generate",
                category="developer",
                topic="python-core")
            ```
            """
        ).strip()

        return add_project_metadata(result, session.get_current_project())

    except Exception as e:
        logger.error(f"Error analyzing knowledge base: {e}")
        return dedent(
            f"""
            # 📊 Knowledge Base Analysis

            **Error:** {str(e)}

            **Manual Analysis:**
            - Check your current note count
            - Identify areas of focus
            - Look for knowledge gaps

            **Available Categories:**
            - developer: Python, Git, Testing, Architecture
            - researcher: Methods, Critical Thinking, Writing
            - writer: Storytelling, Editing, Publishing
            - knowledge-worker: Productivity, PKM, Communication

            Start building:
            ```
            adn_zettelmaker("suggest", count=5)
            ```
            """
        ).strip()
