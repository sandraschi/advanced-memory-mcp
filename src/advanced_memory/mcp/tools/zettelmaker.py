"""Zettelmaker portmanteau tool for Advanced Memory MCP server.

This tool consolidates all zettelkasten generation and management operations.
It provides intelligent template generation, customization, expansion, suggestions,
connections, and knowledge gap analysis.
"""

from textwrap import dedent
from typing import Any, Literal

from fastmcp import Context
from loguru import logger

from advanced_memory.mcp.async_client import client
from advanced_memory.mcp.mcp_instance import mcp
from advanced_memory.mcp.project_session import add_project_metadata, session
from advanced_memory.mcp.tools import write_note as mcp_write_note
from advanced_memory.mcp.tools.utils import call_get
from advanced_memory.services.template_loader import get_content_templates

# Load all content templates from new zettelkasten/templates/ directory
# This supports both old Python-based templates and new markdown-based templates
CONTENT_TEMPLATES: dict[str, dict[str, Any]] = get_content_templates()


@mcp.tool
async def adn_zettelmaker(
    operation: Literal[
        "generate", "customize", "expand", "suggest", "connect", "analyze", "collect"
    ],
    category: str | None = None,
    topic: str | None = None,
    note_identifier: str | None = None,
    depth: int = 3,
    count: int = 5,
    ai_generate: bool = False,
    quality: Literal["quick", "standard", "comprehensive", "expert"] = "standard",
    ctx: Context | None = None,
) -> Any:
    """Intelligent Zettelkasten Portmanteau for Advanced Memory.

    This tool consolidates the entire zettelkasten scaffolding workflow into one interface.
    Instead of separate tools for generation, analysis, and expansion, this unifies
    the cognitive pipeline: Analyze -> Suggest -> Generate -> Expand -> Connect -> Collect.

    ---------------------------------------------------------------------------
    [PORTMANTEAU PATTERN RATIONALE]
    Consolidates zettelkasten scaffolding workflow into one tool to unify cognitive pipeline operations.

    The 10-category taxonomy provides a comprehensive structure for professional knowledge work,
    from development to creative arts.

    ---------------------------------------------------------------------------
    [SUPPORTED OPERATIONS]
    - generate: Create notes from templates (pre-built or AI-generated).
    - suggest: Get intelligent topic recommendations based on knowledge gaps.
    - expand: Extend existing notes with related concepts (horizontal growth).
    - analyze: Evaluate knowledge base composition and identify missing deeper layers.
    - connect: Auto-discover and instantiate relationships between existing notes.
    - customize: Configure template parameters (depth, tone, structure).
    - collect: Low-friction capture for 'off-the-cuff' atomic thoughts.

    ---------------------------------------------------------------------------
    [OPERATIONS DETAIL]

    generate: Creation Engine
    - Parameters: category (required), topic (required).
    - Optional: ai_generate=True (for custom topics), quality="expert".
    - Use when: Starting a new knowledge cluster.

    suggest: Discovery Engine
    - Parameters: category (optional), count (default: 5).
    - Returns: Prioritized list of next steps based on current graph state.
    - Use when: You don't know what to write next.

    collect: Capture Engine
    - Returns: ZettelCollector interactive UI for rapid note taking.
    - Use when: You have a sudden 'off-the-cuff' insight.

    analyze: Insight Engine
    - Parameters: category (optional), depth (default: 3).
    - Function: Scans for structural gaps and shallow areas.
    - Use when: Reviewing the maturity of your knowledge base.

    ---------------------------------------------------------------------------
    [PARAMETERS]
    - operation (str): The zettelkasten operation to perform (Required).
    - category (str): Template category (Required for 'generate').
    - topic (str): Specific topic name (Required for 'generate').
    - note_identifier (str): Target note title/permalink (Required for 'expand').
    - depth (int): Analysis or generation depth level (1-5).
    - count (int): Number of items to return (Default: 5).
    - ai_generate (bool): Enable LLM-based template generation (Default: False).
    - quality (str): Content quality model (quick, standard, comprehensive, expert).
    - ctx (Context): Internal context object (Auto-injected).

    ---------------------------------------------------------------------------
    [EXAMPLES]

    - Quick capture (interactive):
      adn_zettelmaker(operation="collect")

    - Standard generation (pre-built):
      adn_zettelmaker(operation="generate", category="developer", topic="python-core")

    - Custom AI generation:
      adn_zettelmaker(operation="generate", category="developer", topic="Rust Async", ai_generate=True, quality="expert")

    - Analyze gaps:
      adn_zettelmaker(operation="analyze", category="developer")

    - Get next steps:
      adn_zettelmaker(operation="suggest", count=3)
    """
    logger.info(
        f"MCP tool call tool=adn_zettelmaker operation={operation} category={category} topic={topic}"
    )

    from advanced_memory.mcp.prefabs import ZettelCollector

    # Route to appropriate operation
    if operation == "collect":
        return mcp.ToolResult(
            content=["Opening Zettel Collector for quick, off-the-cuff capture..."],
            app=ZettelCollector(),
        )

    result_text = ""
    app_to_return = None

    if operation == "generate":
        result_text = await _generate_operation(category, topic, ai_generate, quality, ctx)
    elif operation == "customize":
        result_text = await _customize_operation(category, topic, depth, ctx)
    elif operation == "expand":
        result_text = await _expand_operation(note_identifier, depth, ctx)
    elif operation == "suggest":
        result_text = await _suggest_operation(category, count, ctx)
    elif operation == "connect":
        result_text = await _connect_operation(count, ctx)
    elif operation == "analyze":
        result_text = await _analyze_operation(category, depth, ctx)
    else:
        result_text = dedent(
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
            - collect: Quick off-the-cuff capture

            Use: adn_zettelmaker("generate", category="developer", topic="python-core")
            """
        ).strip()

    return mcp.ToolResult(content=[result_text], app=app_to_return)


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

            result = await (mcp_write_note.fn if hasattr(mcp_write_note, "fn") else mcp_write_note)(
                title=template["title"],
                content=template["content"],
                folder=template["folder"],
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
                    result = await (
                        mcp_write_note.fn if hasattr(mcp_write_note, "fn") else mcp_write_note
                    )(
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

                result = await (
                    mcp_write_note.fn if hasattr(mcp_write_note, "fn") else mcp_write_note
                )(
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

            {e!s}

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

            **Error:** {e!s}

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
    """Handle suggest operation - get AI-suggested topics based on existing knowledge."""
    if ctx:  # pragma: no cover
        await ctx.info(
            f"Analyzing knowledge base for smart suggestions in {category or 'all categories'}"
        )

    # Use knowledge analyzer for smart suggestions
    try:
        from advanced_memory.services.knowledge_analyzer import KnowledgeAnalyzer

        analyzer = KnowledgeAnalyzer()
        analysis = await analyzer.analyze_knowledge_base(session.get_current_project())

        total_notes = analysis["total_notes"]
        detected_topics = analysis["topics"]
        skill_level = analysis["skill_level"]
        gaps = analysis["gaps"]

        # Build smart suggestions based on knowledge analysis
        suggestions = []

        # Priority 1: Fill knowledge gaps
        for gap in gaps[:2]:
            suggestions.append(
                {
                    "topic": gap["gap"],
                    "category": _map_gap_to_category(gap["gap"]),
                    "reason": f"🎯 Gap: {gap['reason']}",
                    "estimated_notes": 8,
                    "priority": "HIGH",
                }
            )

        # Priority 2: Expand detected topics
        for topic_info in detected_topics[:3]:
            topic_name = topic_info["topic"]
            suggestions.append(
                {
                    "topic": f"{topic_name}-advanced",
                    "category": _map_topic_to_category(topic_name),
                    "reason": f"📈 Deepen your {topic_name} knowledge",
                    "estimated_notes": 10,
                    "priority": "MEDIUM",
                }
            )

        # Priority 3: Complementary topics
        if not category or len(suggestions) < count:
            complementary = _get_complementary_topics(detected_topics)
            suggestions.extend(complementary[: count - len(suggestions)])

        # Limit to requested count
        suggestions = suggestions[:count]

        suggestions_text = "\n\n".join(
            f"**{i + 1}. {s['topic']}** ({s['category']})\n"
            f"   - Why: {s['reason']}\n"
            f"   - Will create: ~{s['estimated_notes']} interconnected notes\n"
            f"   - Generate: `adn_zettelmaker('generate', category='{s['category']}', topic='{s['topic']}')`"
            for i, s in enumerate(suggestions)
        )

        # Format detected topics
        topics_summary = (
            ", ".join(t["topic"] for t in detected_topics[:5]) if detected_topics else "None yet"
        )

        # Format knowledge gaps
        gaps_summary = (
            "\n".join(f"- {gap['gap']}: {gap['reason']}" for gap in gaps[:3])
            if gaps
            else "- No gaps detected"
        )

        result = dedent(
            f"""
            # 🧠 Smart Recommendations (Personalized for You!)

            **Current Notes:** {total_notes}
            **Detected Skill Level:** {skill_level.title()}
            **Main Topics:** {topics_summary}
            **Category Filter:** {category or "All categories"}

            ## Knowledge Gaps Identified
            {gaps_summary}

            ## Personalized Recommendations

            {suggestions_text}

            ## Your Knowledge Profile
            - **Skill Level**: {skill_level.title()}
            - **Active Topics**: {len(detected_topics)}
            - **Knowledge Gaps**: {len(gaps)}
            - **Learning Style**: {analysis.get("learning_style", "unknown").title()}

            ## Quick Actions

            Pick a topic and generate it:
            ```
            adn_zettelmaker("generate",
                category="developer",
                topic="python-core")
            ```

            ---
            *Recommendations powered by AI knowledge analysis! 🤖*
            """
        ).strip()

        return add_project_metadata(result, session.get_current_project())

    except Exception as e:
        logger.error(f"Error getting suggestions: {e}")
        return dedent(
            f"""
            # 💡 Topic Suggestions

            **Error getting current knowledge stats:** {e!s}

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

            **Error:** {e!s}

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


def _map_gap_to_category(gap: str) -> str:
    """Map knowledge gap to category."""
    gap_mapping = {
        "testing": "developer",
        "git": "developer",
        "ui-ux-design": "uiux-designer",
        "devops": "devops",
        "data-science": "data-scientist",
        "product": "product-manager",
        "business": "entrepreneur",
    }
    return gap_mapping.get(gap, "developer")


def _map_topic_to_category(topic: str) -> str:
    """Map detected topic to category."""
    topic_mapping = {
        "python": "developer",
        "javascript": "developer",
        "web": "developer",
        "git": "developer",
        "testing": "developer",
        "devops": "devops",
        "data-science": "data-scientist",
        "design": "uiux-designer",
        "product": "product-manager",
        "business": "entrepreneur",
    }
    return topic_mapping.get(topic, "developer")


def _get_complementary_topics(
    detected_topics: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Get complementary topics based on what user already has."""
    detected_names = {t["topic"] for t in detected_topics}
    complementary = []

    # If they have dev topics, suggest related professional skills
    if "python" in detected_names or "javascript" in detected_names:
        if "devops" not in detected_names:
            complementary.append(
                {
                    "topic": "containers",
                    "category": "devops",
                    "reason": "🔗 Complements development with deployment skills",
                    "estimated_notes": 6,
                    "priority": "MEDIUM",
                }
            )

        if "testing" not in detected_names:
            complementary.append(
                {
                    "topic": "testing",
                    "category": "developer",
                    "reason": "🔗 Essential for code quality",
                    "estimated_notes": 10,
                    "priority": "MEDIUM",
                }
            )

    # Always suggest productivity if not present
    if "knowledge-worker" not in [_map_topic_to_category(d["topic"]) for d in detected_topics]:
        complementary.append(
            {
                "topic": "productivity",
                "category": "knowledge-worker",
                "reason": "⚡ Boost your learning effectiveness",
                "estimated_notes": 14,
                "priority": "LOW",
            }
        )

    return complementary
