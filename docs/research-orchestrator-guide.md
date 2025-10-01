# Research Orchestrator Guide 🧠

AI-guided research planning and workflow orchestration for comprehensive knowledge building.

## Overview

The `research_orchestrator` tool provides structured guidance to help Claude/Sonnet conduct thorough, systematic research and create well-linked knowledge bases. While the MCP server cannot directly control the AI client, this tool returns detailed research plans, methodologies, and step-by-step workflows that Claude can follow.

## Key Concept

**MCP Boundary**: The server provides *guidance and structure*, while Claude executes the research and creates notes. This creates a collaborative workflow where the tool provides the "conductor's score" and Claude performs the "symphony."

## Operations

### 1. Research Plan (`research_plan`)

Generate comprehensive research roadmap with questions, sources, and methodology.

```python
await research_orchestrator.fn(
    operation="research_plan",
    topic="quantum computing",
    parameters={
        "depth": "comprehensive",
        "time_frame": "current",
        "scope": "broad"
    }
)
```

**Returns:**
- Research questions to answer
- Search queries to execute
- Sources to investigate
- Note structure blueprint
- Step-by-step execution plan

### 2. Research Methodology (`research_methodology`)

Get proven research approaches tailored to topic types.

```python
await research_orchestrator.fn(
    operation="research_methodology",
    topic_type="technical"  # technical, business, academic, general
)
```

**Available Methodologies:**
- **Technical**: Specification → Implementation → Applications → Limitations
- **Business**: Market → Competition → Strategy → Implementation
- **Academic**: Literature Review → Methodology → Findings → Implications
- **General**: Overview → Deep Analysis → Applications → Future Directions

### 3. Research Questions (`research_questions`)

Generate focused research questions organized by category.

```python
await research_orchestrator.fn(
    operation="research_questions",
    topic="machine learning",
    parameters={"depth": "comprehensive"}
)
```

**Question Categories:**
- Definition & Fundamentals
- Historical Context
- Current State
- Applications & Use Cases
- Limitations & Challenges
- Future Outlook

### 4. Note Blueprint (`note_blueprint`)

Design optimal note structure for research findings.

```python
await research_orchestrator.fn(
    operation="note_blueprint",
    research_type="analysis",  # analysis, technical, comparative, tutorial
    topic="AI ethics"
)
```

**Blueprint Types:**
- **Analysis**: Executive Summary → Key Findings → Methodology → Implications
- **Technical**: Overview → Specifications → Implementation → Best Practices
- **Comparative**: Criteria → Options → Comparison → Recommendation
- **Tutorial**: Introduction → Steps → Examples → FAQ

### 5. Research Workflow (`research_workflow`)

Step-by-step research execution guide.

```python
await research_orchestrator.fn(
    operation="research_workflow",
    topic="blockchain technology",
    step=1  # Current step in workflow
)
```

## Complete Research Workflow

### Phase 1: Planning (Steps 1-2)

**Step 1: Create Research Plan**
```python
await research_orchestrator.fn("research_plan", topic="your-topic")
```
- Get comprehensive research roadmap
- Claude studies the plan and asks clarifying questions

**Step 2: Choose Methodology**
```python
await research_orchestrator.fn("research_methodology", topic_type="appropriate-type")
```
- Get research approach guidance
- Claude confirms methodology fits the topic

### Phase 2: Preparation (Steps 3-4)

**Step 3: Generate Questions**
```python
await research_orchestrator.fn("research_questions", topic="your-topic")
```
- Get focused research questions
- Claude organizes questions by priority

**Step 4: Design Note Structure**
```python
await research_orchestrator.fn("note_blueprint", research_type="analysis", topic="your-topic")
```
- Get note structure blueprint
- Claude creates initial note framework

### Phase 3: Execution (Steps 5-10)

**Step 5: Execute Research Workflow**
```python
await research_orchestrator.fn("research_workflow", topic="your-topic", step=1)
```
- Follow step-by-step research guidance
- Claude conducts web searches, reads sources, creates notes

**Continue through all 6 workflow steps:**
1. Topic Overview
2. Key Sources
3. Deep Analysis
4. Relationship Mapping
5. Synthesis
6. Validation

## Example: Complete Research Session

### 1. Initial Planning
```python
# Claude asks for research plan
await research_orchestrator.fn("research_plan", topic="quantum computing")

# Tool returns comprehensive plan with questions, sources, methodology
# Claude reviews and asks: "Should I start with the overview questions?"
```

### 2. Method Selection
```python
# Claude gets methodology guidance
await research_orchestrator.fn("research_methodology", topic_type="technical")

# Tool returns: Technical Deep Dive approach
# Claude: "This fits perfectly for quantum computing research"
```

### 3. Question Generation
```python
# Claude requests focused questions
await research_orchestrator.fn("research_questions", topic="quantum computing")

# Tool returns categorized questions
# Claude: "I'll start with definition questions, then move to current state"
```

### 4. Note Structure
```python
# Claude designs note structure
await research_orchestrator.fn("note_blueprint", research_type="technical", topic="quantum computing")

# Tool returns structured blueprint
# Claude creates main note with proper sections
```

### 5. Research Execution
```python
# Claude begins systematic research
await research_orchestrator.fn("research_workflow", topic="quantum computing", step=1)

# Tool guides: "Research and create overview of quantum computing"
# Claude executes web searches, reads papers, creates notes

# Progress through steps...
await research_orchestrator.fn("research_workflow", topic="quantum computing", step=2)
# "Identify and evaluate primary sources"

await research_orchestrator.fn("research_workflow", topic="quantum computing", step=3)
# "Conduct detailed analysis of core aspects"
```

## Research Quality Framework

### Source Evaluation
- **Primary Sources**: Original research, official documentation
- **Secondary Sources**: Analysis of primary sources
- **Tertiary Sources**: Summaries and overviews

### Credibility Assessment
- Author expertise and credentials
- Publication date and recency
- Peer review status
- Institutional affiliation

### Confidence Levels
- **High**: Multiple primary sources agree
- **Medium**: Good secondary sources, some primary
- **Low**: Limited sources, conflicting information

## Integration with Knowledge Base

### Note Linking Strategy
```
Main Topic Note
├── Definition & Overview
├── Technical Details
├── Applications & Use Cases
├── Current Challenges
└── Future Outlook

Linked Sub-notes:
├── Quantum Algorithms Research
├── Hardware Implementations
├── Industry Applications
└── Ethical Considerations
```

### Tagging Strategy
- `#research` - All research-related notes
- `#quantum-computing` - Topic-specific tag
- `#primary-source` - Direct from original research
- `#analysis` - Analytical content
- `#question_fundamentals` - By research question category

## Best Practices

### Research Process
1. **Start Broad**: Use overview searches first
2. **Go Deep**: Follow promising leads systematically
3. **Cross-Reference**: Verify information across sources
4. **Note Contradictions**: Document conflicting information
5. **Link Concepts**: Connect related ideas within knowledge base

### Quality Assurance
- **Source Diversity**: Use multiple perspectives
- **Recency Check**: Prefer recent sources for fast-moving topics
- **Expert Consensus**: Note where experts agree/disagree
- **Gap Identification**: Mark areas needing more research

### Knowledge Organization
- **Hierarchical Structure**: Main topic → Subtopics → Details
- **Cross-References**: Link related concepts
- **Metadata**: Include confidence levels, source quality
- **Regular Updates**: Review and update based on new information

## Advanced Features

### Custom Research Profiles
```python
# Create custom research approach
await research_orchestrator.fn(
    operation="custom_methodology",
    topic="blockchain",
    custom_phases=["Market Analysis", "Technical Review", "Regulatory Landscape", "Future Scenarios"]
)
```

### Research Templates
```python
# Get research template for specific domains
await research_orchestrator.fn(
    operation="research_template",
    domain="scientific_paper",
    topic="machine learning"
)
```

### Progress Tracking
```python
# Track research progress
await research_orchestrator.fn(
    operation="research_status",
    topic="quantum computing",
    completed_steps=[1, 2, 3],
    current_step=4
)
```

## Troubleshooting

### Common Issues

#### "Research plan too broad"
**Solution**: Specify narrower scope or use `depth="focused"`
```python
await research_orchestrator.fn("research_plan", topic="quantum computing", parameters={"scope": "narrow"})
```

#### "Too many questions generated"
**Solution**: Use `depth="basic"` instead of `comprehensive`
```python
await research_orchestrator.fn("research_questions", topic="quantum computing", parameters={"depth": "basic"})
```

#### "Methodology doesn't fit"
**Solution**: Try different `topic_type`
```python
await research_orchestrator.fn("research_methodology", topic_type="academic")
```

### Getting Unstuck

#### Research Block
- Return to research plan overview
- Focus on unanswered questions
- Look for new angles or sources

#### Organization Issues
- Review note blueprint
- Simplify structure if overwhelming
- Focus on one section at a time

#### Quality Concerns
- Cross-reference with additional sources
- Consult domain experts
- Document uncertainties clearly

## Integration Examples

### With Knowledge Operations
```python
# After research, organize and tag notes
await knowledge_operations.fn(
    operation="bulk_update",
    filters={"folder": "/research/quantum-computing"},
    action={"add_tags": ["research-complete", "quantum-computing"]}
)
```

### With Note Creation
```python
# Create research notes based on blueprint
# (Use write_note with the blueprint structure)
```

### With Search Integration
```python
# Find related existing knowledge
# (Use search_notes to find connections)
```

## Success Metrics

### Research Quality
- **Completeness**: All major questions answered
- **Source Quality**: Mix of primary and secondary sources
- **Recency**: Current information for fast-moving topics
- **Balance**: Multiple perspectives represented

### Knowledge Organization
- **Connectivity**: Well-linked notes and concepts
- **Accessibility**: Easy to find and navigate
- **Maintainability**: Clear structure for updates
- **Shareability**: Suitable for collaboration

---

**The Research Orchestrator provides the structure and guidance for systematic knowledge building, while Claude provides the intelligence and execution. Together, they create comprehensive, well-organized research knowledge bases.** 🔬📚

**Ready to start your first orchestrated research session?** 🚀
