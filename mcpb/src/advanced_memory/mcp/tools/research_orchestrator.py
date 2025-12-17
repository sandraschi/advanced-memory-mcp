"""Research Orchestrator - Guides AI-powered research and note creation workflows."""

import json
from dataclasses import dataclass
from datetime import datetime
from typing import Any

from advanced_memory.mcp.mcp_instance import mcp


@dataclass
class ResearchPlan:
    """Structured research plan for AI-guided execution."""

    topic: str
    research_questions: list[str]
    search_queries: list[str]
    sources_to_check: list[str]
    note_structure: dict[str, Any]
    estimated_steps: int
    methodology: str


@dataclass
class ResearchStep:
    """Individual research step with instructions."""

    step_number: int
    action: str
    description: str
    expected_output: str
    tools_to_use: list[str]
    parameters: dict[str, Any]


@mcp.tool
async def research_orchestrator(
    operation: str,
    topic: str | None = None,
    topic_type: str | None = None,
    research_type: str | None = None,
    step: int | None = None,
    parameters: dict[str, Any] | None = None,
) -> str:
    """
    Research orchestrator tool for AI-guided knowledge building.

    Args:
        operation: Type of research operation
        topic: Research topic
        topic_type: Type of topic (technical, business, academic, etc.)
        research_type: Type of research (exploratory, deep_dive, comparative, etc.)
        step: Current step in workflow
        parameters: Additional parameters

    Returns:
        Structured research guidance and instructions
    """
    try:
        if operation == "research_plan":
            if not topic:
                return "# Error\n\nResearch plan requires: topic parameter"
            return await _create_research_plan(topic, parameters or {})
        elif operation == "research_methodology":
            return await _get_research_methodology(topic_type or "general", parameters or {})
        elif operation == "research_questions":
            if not topic:
                return "# Error\n\nResearch questions requires: topic parameter"
            return await _generate_research_questions(topic, parameters or {})
        elif operation == "note_blueprint":
            if not topic:
                return "# Error\n\nNote blueprint requires: topic parameter"
            return await _create_note_blueprint(research_type or "general", topic, parameters or {})
        elif operation == "research_workflow":
            if not topic:
                return "# Error\n\nResearch workflow requires: topic parameter"
            return await _execute_research_workflow(topic, step or 1, parameters or {})
        else:
            return _get_available_operations()

    except Exception as e:
        return f"[UNICODE] Research orchestration failed: {str(e)}"


async def _create_research_plan(topic: str, params: dict[str, Any]) -> str:
    """Create a comprehensive research plan for a topic."""
    if not topic:
        return "[UNICODE] Topic required for research planning"

    depth = params.get("depth", "comprehensive")
    time_frame = params.get("time_frame", "current")
    scope = params.get("scope", "broad")

    # Generate research plan based on topic
    plan = ResearchPlan(
        topic=topic,
        research_questions=_generate_topic_questions(topic, depth),
        search_queries=_generate_search_queries(topic, scope),
        sources_to_check=_get_relevant_sources(topic),
        note_structure=_design_note_structure(topic, depth),
        estimated_steps=len(_generate_topic_questions(topic, depth)) + 3,
        methodology=_select_methodology(topic, depth),
    )

    return f"""[UNICODE][UNICODE] **Research Plan: {topic}**

**Overview:**
[UNICODE] **Topic**: {topic}
[UNICODE] **Depth**: {depth}
[UNICODE] **Scope**: {scope}
[UNICODE] **Time Frame**: {time_frame}
[UNICODE] **Methodology**: {plan.methodology}
[UNICODE] **Estimated Steps**: {plan.estimated_steps}

**[SEARCH] Research Questions:**
{chr(10).join(f"[UNICODE] {q}" for q in plan.research_questions)}

**[UNICODE][UNICODE] Search Queries to Execute:**
{chr(10).join(f"[UNICODE] {q}" for q in plan.search_queries)}

**[BOOKS] Sources to Investigate:**
{chr(10).join(f"[UNICODE] {source}" for source in plan.sources_to_check)}

**[NOTE] Note Structure Blueprint:**
```json
{json.dumps(plan.note_structure, indent=2)}
```

**[TARGET] Next Steps for Claude:**
1. **Execute searches** using the search queries above
2. **Review sources** and extract key information
3. **Create main topic note** using the blueprint structure
4. **Create linked sub-notes** for each research question
5. **Establish relationships** between concepts and findings

**[UNICODE][UNICODE] Research Tips:**
[UNICODE] Start with broad searches, then narrow down
[UNICODE] Cross-reference information from multiple sources
[UNICODE] Note contradictions and areas needing clarification
[UNICODE] Link related concepts within your knowledge base

**Ready to begin research execution?** [LAUNCH]

Use: `research_orchestrator("research_workflow", topic="{topic}", step=1)`
"""


async def _get_research_methodology(topic_type: str, params: dict[str, Any]) -> str:
    """Provide research methodology guidance."""
    methodologies = {
        "technical": {
            "name": "Technical Deep Dive",
            "approach": "Specification [UNICODE] Implementation [UNICODE] Applications [UNICODE] Limitations",
            "tools": [
                "Official documentation",
                "GitHub repositories",
                "Technical papers",
                "API references",
            ],
            "validation": ["Code examples", "Performance benchmarks", "Security analysis"],
        },
        "business": {
            "name": "Business Analysis",
            "approach": "Market [UNICODE] Competition [UNICODE] Strategy [UNICODE] Implementation",
            "tools": [
                "Industry reports",
                "Financial data",
                "Competitor analysis",
                "Trend analysis",
            ],
            "validation": ["Case studies", "ROI analysis", "Risk assessment"],
        },
        "academic": {
            "name": "Academic Research",
            "approach": "Literature Review [UNICODE] Methodology [UNICODE] Findings [UNICODE] Implications",
            "tools": ["Academic databases", "Citation analysis", "Peer review", "Meta-analysis"],
            "validation": ["Statistical significance", "Peer review", "Reproducibility"],
        },
        "general": {
            "name": "Comprehensive Research",
            "approach": "Overview [UNICODE] Deep Analysis [UNICODE] Applications [UNICODE] Future Directions",
            "tools": ["Web search", "Expert interviews", "Data analysis", "Trend monitoring"],
            "validation": ["Multiple sources", "Fact-checking", "Expert consensus"],
        },
    }

    method = methodologies.get(topic_type, methodologies["general"])

    return f"""[LIST] **Research Methodology: {method["name"]}**

**[TARGET] Approach:**
{method["approach"]}

**[UNICODE][UNICODE][UNICODE] Recommended Tools & Sources:**
{chr(10).join(f"[UNICODE] {tool}" for tool in method["tools"])}

**[UNICODE] Validation Methods:**
{chr(10).join(f"[UNICODE] {validation}" for validation in method["validation"])}

**[CHART] Research Phases:**

**Phase 1: Foundation**
[UNICODE] Define research scope and objectives
[UNICODE] Gather preliminary information
[UNICODE] Identify key stakeholders and experts

**Phase 2: Investigation**
[UNICODE] Execute systematic information gathering
[UNICODE] Cross-reference multiple sources
[UNICODE] Identify patterns and contradictions

**Phase 3: Analysis**
[UNICODE] Synthesize findings
[UNICODE] Evaluate credibility and relevance
[UNICODE] Draw evidence-based conclusions

**Phase 4: Application**
[UNICODE] Identify practical implications
[UNICODE] Create actionable recommendations
[UNICODE] Plan implementation strategies

**[NOTE] Note-Taking Strategy:**
[UNICODE] Create main topic overview note
[UNICODE] Link to detailed sub-notes for each aspect
[UNICODE] Tag with research phase and confidence level
[UNICODE] Include source citations and credibility ratings

**Ready to start with this methodology?** [TARGET]
"""


async def _generate_research_questions(topic: str, params: dict[str, Any]) -> str:
    """Generate focused research questions."""
    if not topic:
        return "[UNICODE] Topic required for question generation"

    question_categories = {
        "definition": [
            "What is [topic] and how is it defined?",
            "What are the key components of [topic]?",
            "How does [topic] differ from related concepts?",
        ],
        "history": [
            "What is the historical development of [topic]?",
            "Who are the key figures in [topic]?",
            "How has [topic] evolved over time?",
        ],
        "current_state": [
            "What is the current state of [topic]?",
            "What are recent developments in [topic]?",
            "What are current challenges in [topic]?",
        ],
        "applications": [
            "Where is [topic] currently applied?",
            "What are successful use cases of [topic]?",
            "What are potential future applications?",
        ],
        "limitations": [
            "What are the limitations of [topic]?",
            "What challenges exist with [topic]?",
            "What criticisms exist regarding [topic]?",
        ],
        "future": [
            "What is the future outlook for [topic]?",
            "What emerging trends affect [topic]?",
            "What research directions are promising?",
        ],
    }

    all_questions = []
    for _category, questions in question_categories.items():
        all_questions.extend([q.replace("[topic]", topic) for q in questions])

    return f"""[UNICODE] **Research Questions for: {topic}**

**[LIST] Generated Questions:**

**Definition & Fundamentals:**
{chr(10).join(f"[UNICODE] {q}" for q in all_questions[:3])}

**Historical Context:**
{chr(10).join(f"[UNICODE] {q}" for q in all_questions[3:6])}

**Current State:**
{chr(10).join(f"[UNICODE] {q}" for q in all_questions[6:9])}

**Applications & Use Cases:**
{chr(10).join(f"[UNICODE] {q}" for q in all_questions[9:12])}

**Limitations & Challenges:**
{chr(10).join(f"[UNICODE] {q}" for q in all_questions[12:15])}

**Future Outlook:**
{chr(10).join(f"[UNICODE] {q}" for q in all_questions[15:18])}

**[TARGET] Research Strategy:**
1. **Start with definition questions** to build foundation
2. **Move to current state** for context
3. **Explore applications** for practical understanding
4. **Analyze limitations** for balanced perspective
5. **Consider future outlook** for strategic thinking

**[NOTE] Note Creation Approach:**
[UNICODE] Create one note per major question category
[UNICODE] Link questions to findings and sources
[UNICODE] Use tags like #research, #[topic], #question_[category]
[UNICODE] Include confidence levels and source quality ratings

**Ready to begin systematic research?** [SEARCH]
"""


async def _create_note_blueprint(research_type: str, topic: str, params: dict[str, Any]) -> str:
    """Design optimal note structure for research findings."""
    blueprints = {
        "analysis": {
            "title": f"{topic} Analysis",
            "sections": [
                "Executive Summary",
                "Key Findings",
                "Methodology",
                "Detailed Analysis",
                "Implications",
                "Recommendations",
                "Sources & References",
            ],
            "tags": ["analysis", "research", topic.lower().replace(" ", "-")],
            "relationships": ["links to data sources", "connects to related topics"],
        },
        "technical": {
            "title": f"{topic} Technical Deep Dive",
            "sections": [
                "Overview & Definition",
                "Technical Specifications",
                "Implementation Details",
                "Performance Characteristics",
                "Integration Options",
                "Troubleshooting",
                "Best Practices",
            ],
            "tags": ["technical", "deep-dive", topic.lower().replace(" ", "-")],
            "relationships": ["links to code examples", "connects to related technologies"],
        },
        "comparative": {
            "title": f"{topic} Comparison & Evaluation",
            "sections": [
                "Comparison Criteria",
                "Option 1 Analysis",
                "Option 2 Analysis",
                "Head-to-Head Comparison",
                "Recommendation",
                "Trade-offs & Considerations",
                "Implementation Guide",
            ],
            "tags": ["comparison", "evaluation", topic.lower().replace(" ", "-")],
            "relationships": ["links to evaluation criteria", "connects to alternatives"],
        },
        "tutorial": {
            "title": f"{topic} Guide & Tutorial",
            "sections": [
                "Introduction & Prerequisites",
                "Step-by-Step Instructions",
                "Common Issues & Solutions",
                "Advanced Techniques",
                "Examples & Use Cases",
                "Resources & Further Reading",
                "FAQ",
            ],
            "tags": ["tutorial", "guide", topic.lower().replace(" ", "-")],
            "relationships": ["links to prerequisite knowledge", "connects to advanced topics"],
        },
    }

    blueprint = blueprints.get(research_type, blueprints["analysis"])

    return f"""[LIST] **Note Blueprint: {blueprint["title"]}**

**[UNICODE][UNICODE][UNICODE] Structure:**
{chr(10).join(f"[UNICODE] **{section}**" for section in blueprint["sections"])}

**[UNICODE][UNICODE][UNICODE] Recommended Tags:**
{chr(10).join(f"[UNICODE] `{tag}`" for tag in blueprint["tags"])}

**[LINK] Relationship Suggestions:**
{chr(10).join(f"[UNICODE] {rel}" for rel in blueprint["relationships"])}

**[NOTE] Content Guidelines:**

**Headers & Formatting:**
[UNICODE] Use H2 (##) for main sections
[UNICODE] Use H3 (###) for subsections
[UNICODE] Use bullet points for lists
[UNICODE] Use **bold** for key terms
[UNICODE] Use `code` for technical terms

**Metadata to Include:**
[UNICODE] Research date: {datetime.now().strftime("%Y-%m-%d")}
[UNICODE] Confidence level: High/Medium/Low
[UNICODE] Source quality: Primary/Secondary/Tertiary
[UNICODE] Last updated: Auto-updated on changes

**Quality Checklist:**
- [ ] Clear, concise title
- [ ] Comprehensive overview section
- [ ] Well-structured content with headers
- [ ] Source citations for claims
- [ ] Links to related notes
- [ ] Appropriate tags applied
- [ ] Proofread for clarity

**[TARGET] Next Steps:**
1. Create the main note with this structure
2. Fill in each section with research findings
3. Add links to source materials
4. Create sub-notes for detailed sections
5. Review and refine based on new information

**Ready to create this note structure?** [NOTE]
"""


async def _execute_research_workflow(topic: str, current_step: int, params: dict[str, Any]) -> str:
    """Execute step-by-step research workflow."""
    if not topic:
        return "[UNICODE] Topic required for research workflow"

    workflow_steps = [
        ResearchStep(
            step_number=1,
            action="topic_overview",
            description="Research and create overview of the topic",
            expected_output="Main topic note with definition, scope, and key concepts",
            tools_to_use=["web_search", "write_note"],
            parameters={"focus": "definition and scope"},
        ),
        ResearchStep(
            step_number=2,
            action="key_sources",
            description="Identify and evaluate primary sources",
            expected_output="List of credible sources with quality ratings",
            tools_to_use=["web_search", "read_content"],
            parameters={"focus": "authoritative sources"},
        ),
        ResearchStep(
            step_number=3,
            action="deep_analysis",
            description="Conduct detailed analysis of core aspects",
            expected_output="Detailed sub-notes for each major aspect",
            tools_to_use=["web_search", "write_note", "read_note"],
            parameters={"focus": "technical details and implications"},
        ),
        ResearchStep(
            step_number=4,
            action="relationship_mapping",
            description="Map relationships between concepts and findings",
            expected_output="Network of linked notes showing connections",
            tools_to_use=["write_note", "edit_note"],
            parameters={"focus": "connections and dependencies"},
        ),
        ResearchStep(
            step_number=5,
            action="synthesis",
            description="Synthesize findings into comprehensive overview",
            expected_output="Updated main note with synthesis and conclusions",
            tools_to_use=["write_note", "edit_note"],
            parameters={"focus": "integration and conclusions"},
        ),
        ResearchStep(
            step_number=6,
            action="validation",
            description="Validate findings and identify gaps",
            expected_output="Quality assessment and gap analysis",
            tools_to_use=["read_note", "web_search"],
            parameters={"focus": "verification and completeness"},
        ),
    ]

    if current_step > len(workflow_steps):
        return f"""[UNICODE] **Research Workflow Complete for: {topic}**

**[SUCCESS] Congratulations!** You have completed a comprehensive research workflow.

**Summary of Work:**
[UNICODE] Created structured research notes
[UNICODE] Established knowledge connections
[UNICODE] Validated findings across sources
[UNICODE] Built comprehensive understanding

**Next Steps:**
[UNICODE] Review and refine your notes
[UNICODE] Share findings with others
[UNICODE] Plan follow-up research as needed
[UNICODE] Consider creating summary documents

**Research Quality Check:**
- [ ] All major questions answered
- [ ] Sources are credible and recent
- [ ] Notes are well-structured and linked
- [ ] Conclusions are evidence-based
- [ ] Gaps and uncertainties noted

**Want to research another topic?** [UNICODE][UNICODE]
Use: `research_orchestrator("research_plan", topic="new_topic")`
"""

    current_step_data = workflow_steps[current_step - 1]

    next_step = workflow_steps[current_step] if current_step < len(workflow_steps) else None

    return f"""[UNICODE][UNICODE] **Research Workflow: {topic}**
**Step {current_step_data.step_number} of {len(workflow_steps)}**

**[TARGET] Current Step: {current_step_data.action.replace("_", " ").title()}**

**[NOTE] Description:**
{current_step_data.description}

**[TARGET] Expected Output:**
{current_step_data.expected_output}

**[UNICODE][UNICODE][UNICODE] Tools to Use:**
{chr(10).join(f"[UNICODE] `{tool}`" for tool in current_step_data.tools_to_use)}

**[LIST] Detailed Instructions:**

**Focus Area:** {current_step_data.parameters.get("focus", "General research")}

**Specific Actions:**
{
        chr(10).join(
            f"[UNICODE] {action}" for action in _get_step_actions(current_step_data.action, topic)
        )
    }

**Quality Guidelines:**
[UNICODE] Ensure information is from credible sources
[UNICODE] Cross-reference multiple perspectives
[UNICODE] Note uncertainties and conflicting information
[UNICODE] Create clear, well-structured notes

{
        f'''
**[UNICODE][UNICODE] Next Step Preview:**
**Step {next_step.step_number}:** {next_step.action.replace("_", " ").title()}
{next_step.description}

Use: `research_orchestrator("research_workflow", topic="{topic}", step={next_step.step_number})`
'''
        if next_step
        else "**[SUCCESS] Final Step!**"
    }

**[CHART] Progress:** {
        "[UNICODE]" * current_step + "[UNICODE]" * (len(workflow_steps) - current_step)
    } ({current_step}/{len(workflow_steps)})

**Ready to execute this step?** [LAUNCH]
"""


def _get_available_operations() -> str:
    """Return list of available operations."""
    return """[UNICODE][UNICODE] **Research Orchestrator - Available Operations**

**Planning & Design:**
[UNICODE] `research_plan` - Create comprehensive research roadmap
[UNICODE] `research_methodology` - Get proven research approaches
[UNICODE] `research_questions` - Generate focused research questions
[UNICODE] `note_blueprint` - Design optimal note structure

**Execution & Workflow:**
[UNICODE] `research_workflow` - Step-by-step research execution guide

**Examples:**
```python
# Create research plan
await research_orchestrator.fn("research_plan", topic="quantum computing")

# Get methodology
await research_orchestrator.fn("research_methodology", topic_type="technical")

# Generate questions
await research_orchestrator.fn("research_questions", topic="machine learning")

# Design note structure
await research_orchestrator.fn("note_blueprint", research_type="analysis", topic="AI ethics")

# Execute workflow
await research_orchestrator.fn("research_workflow", topic="blockchain", step=1)
```

**Each operation returns structured guidance for Claude to execute comprehensive research and create well-linked knowledge notes.** [BOOKS][LINK]"""


def _generate_topic_questions(topic: str, depth: str) -> list[str]:
    """Generate research questions based on topic and depth."""
    base_questions = [
        f"What is {topic} and how does it work?",
        f"What are the key components of {topic}?",
        f"What are the main applications of {topic}?",
        f"What are the advantages and disadvantages of {topic}?",
        f"What is the future outlook for {topic}?",
    ]

    if depth == "comprehensive":
        base_questions.extend(
            [
                f"How has {topic} evolved over time?",
                f"What are current challenges in {topic}?",
                f"Who are the key players in {topic}?",
                f"What research is being done on {topic}?",
                f"How might {topic} impact society?",
            ]
        )

    return base_questions


def _generate_search_queries(topic: str, scope: str) -> list[str]:
    """Generate effective search queries."""
    queries = [
        f'"{topic}" overview',
        f'"{topic}" explained',
        f'"{topic}" applications',
        f'"{topic}" future',
    ]

    if scope == "broad":
        queries.extend(
            [
                f'"{topic}" recent developments',
                f'"{topic}" challenges',
                f'"{topic}" vs alternatives',
            ]
        )

    return queries


def _get_relevant_sources(topic: str) -> list[str]:
    """Get relevant sources for research."""
    return [
        f"Wikipedia: {topic}",
        f"Scholarly articles on {topic}",
        "Official documentation/websites",
        "Expert blogs and publications",
        "GitHub repositories (if technical)",
        "Industry reports and whitepapers",
    ]


def _design_note_structure(topic: str, depth: str) -> dict[str, Any]:
    """Design note structure based on topic and depth."""
    structure = {
        "title": f"{topic} Research",
        "sections": [
            "Overview & Definition",
            "Key Concepts",
            "Applications",
            "Advantages & Limitations",
            "Current State",
            "Future Outlook",
            "Sources & References",
        ],
        "tags": ["research", topic.lower().replace(" ", "-")],
        "metadata": {
            "research_date": datetime.now().strftime("%Y-%m-%d"),
            "confidence_level": "medium",
            "last_updated": datetime.now().strftime("%Y-%m-%d"),
        },
    }

    if depth == "comprehensive":
        structure["sections"].extend(
            ["Historical Development", "Technical Details", "Case Studies", "Expert Opinions"]
        )

    return structure


def _select_methodology(topic: str, depth: str) -> str:
    """Select appropriate research methodology."""
    if "technical" in topic.lower() or "software" in topic.lower():
        return "Technical Deep Dive: Documentation [UNICODE] Code [UNICODE] Applications [UNICODE] Limitations"
    elif "business" in topic.lower() or "market" in topic.lower():
        return "Business Analysis: Market [UNICODE] Competition [UNICODE] Strategy [UNICODE] Implementation"
    elif depth == "comprehensive":
        return "Comprehensive Research: Overview [UNICODE] Analysis [UNICODE] Synthesis [UNICODE] Validation"
    else:
        return (
            "Exploratory Research: Broad investigation [UNICODE] Key insights [UNICODE] Deep dives"
        )


def _get_step_actions(step_action: str, topic: str) -> list[str]:
    """Get detailed actions for a workflow step."""
    actions = {
        "topic_overview": [
            f"Search for '{topic}' definition and basic concepts",
            f"Identify key stakeholders and organizations in {topic}",
            f"Note current trends and buzzwords related to {topic}",
            "Create main topic overview note with basic structure",
        ],
        "key_sources": [
            f"Find authoritative sources on {topic} (official sites, experts, publications)",
            "Evaluate source credibility and recency",
            "Extract key quotes and data points",
            "Create source evaluation note with credibility ratings",
        ],
        "deep_analysis": [
            f"Research technical details and specifications of {topic}",
            "Analyze real-world applications and use cases",
            "Identify limitations and challenges",
            "Create detailed analysis notes for each major aspect",
        ],
        "relationship_mapping": [
            f"Identify how {topic} relates to other concepts",
            "Map dependencies and prerequisites",
            "Note complementary and competing technologies/concepts",
            "Update notes with cross-references and relationship links",
        ],
        "synthesis": [
            "Combine findings into coherent overview",
            "Identify key insights and conclusions",
            "Note areas of agreement and disagreement across sources",
            "Update main topic note with comprehensive synthesis",
        ],
        "validation": [
            "Cross-check facts across multiple sources",
            "Identify gaps in current understanding",
            "Assess confidence levels for different claims",
            "Create validation note with quality assessment",
        ],
    }

    return actions.get(
        step_action,
        ["Execute research for this step", "Document findings", "Create/update relevant notes"],
    )
