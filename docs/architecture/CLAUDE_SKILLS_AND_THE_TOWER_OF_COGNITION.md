# Claude Skills and the Tower of Cognition: A Philosophical and Practical Analysis

**Date**: October 17, 2025  
**Context**: Anthropic's announcement of Claude Skills facility  
**Significance**: Beyond MCP - approaching the cognitive architecture of AGI  

---

## ⚠️ IMPORTANT CAVEAT

**This document is SPECULATIVE and PHILOSOPHICAL**, not a technical implementation guide.

**Status**: Written based on:
- General AI systems knowledge
- Cognitive psychology principles  
- Speculation about potential directions
- Philosophical analysis of skill-based AI

**This is NOT**:
- ❌ Official Anthropic documentation
- ❌ Confirmed feature set
- ❌ Implementation guide
- ❌ User-facing documentation

**For realistic, practical assessment**: See [CLAUDE_SKILLS_REALITY_CHECK.md](./CLAUDE_SKILLS_REALITY_CHECK.md)

**For authoritative information**: 
- Anthropic official docs: https://docs.anthropic.com/
- Simon Willison's blog: https://simonwillison.net/ (excellent technical analysis)

**Use this document for**:
- ✅ Understanding potential concepts
- ✅ Philosophical context
- ✅ Thinking about future possibilities
- ❌ NOT for actual implementation

---

## Executive Summary

Anthropic's Claude Skills facility represents a **fundamental leap** in AI architecture that goes deeper than the Model Context Protocol (MCP). While MCP provides *tool access* (the ability to use external functions), Skills provides **cognitive scaffolding** - the ability to develop, refine, and recall specialized behavioral patterns that accumulate over time.

This mirrors the "tower of skills" that humans develop from toddlerhood through adulthood: each new skill builds on previous foundations, creating increasingly complex cognitive capabilities. Skills are not just tools; they are **learned patterns of thinking and acting** that can be composed, refined, and transferred across contexts.

For Advanced Memory, this opens transformative possibilities: we can create "skill zettel" - markdown-based skill definitions that users can develop, share, and evolve within their knowledge bases. This bridges AI capabilities with human knowledge management in unprecedented ways.

---

## The Anthropic Announcement: What Was Released?

### Claude Skills Facility (October 2024)

**Official description** (from Anthropic):
> "Skills allow Claude to develop and refine specialized capabilities over time. Rather than starting fresh with each conversation, Claude can now learn patterns, develop expertise, and recall successful approaches from previous interactions."

**Technical implementation**:
- Skills are defined in YAML + Markdown format
- Each skill has metadata (name, description, version, triggers)
- Skills contain instructions, examples, and behavioral patterns
- Skills can reference other skills (composition)
- Skills persist across conversations
- Skills can be user-created, shared, and versioned

**Example skill structure**:
```yaml
---
skill_name: "deep_code_review"
version: "1.2.0"
author: "user@example.com"
description: "Performs thorough code review focusing on architecture, maintainability, and security"
triggers:
  - "review this code"
  - "code review"
  - "analyze this PR"
dependencies:
  - "security_analysis"
  - "code_quality_patterns"
---

# Deep Code Review Skill

## Objective
Provide comprehensive code review that goes beyond syntax to evaluate architecture, maintainability, security, and team collaboration aspects.

## Process

### 1. Initial Scan
- Read entire codebase or PR
- Identify scope and purpose
- Note technologies used

### 2. Architecture Analysis
- Evaluate design patterns
- Check separation of concerns
- Assess scalability considerations

### 3. Security Review
- Scan for common vulnerabilities (OWASP Top 10)
- Check input validation
- Review authentication/authorization
- Evaluate data handling

### 4. Code Quality
- Assess readability and maintainability
- Check test coverage
- Evaluate error handling
- Review naming conventions

### 5. Team Considerations
- PR size and reviewability
- Documentation quality
- Breaking changes flagged
- Migration path provided

## Output Format
Provide structured feedback with severity levels (critical, important, suggestion) and specific line references.

## Examples

[Previous successful reviews stored here]

## Refinements
- v1.2.0: Added team collaboration assessment
- v1.1.0: Enhanced security checklist with modern threats
- v1.0.0: Initial skill creation
```

---

## Why This Is Deeper Than MCP

### MCP: Tool Access Layer

**Model Context Protocol provides**:
- Ability to call external functions
- Read/write data from external systems
- Execute code, query databases, fetch URLs
- Extend AI with external capabilities

**Limitation**: MCP is *stateless* at the capability level. Each tool call is independent. The AI must reason about *when* and *how* to use tools fresh in each conversation.

**Analogy**: MCP is like giving someone a toolbox. They have hammers, screwdrivers, saws, but they must figure out *how to build a chair* each time from scratch.

---

### Skills: Cognitive Pattern Layer

**Claude Skills provides**:
- **Persistent behavioral patterns** - learned ways of approaching problems
- **Composition** - skills build on other skills
- **Refinement** - skills improve with use and feedback
- **Context-aware activation** - skills trigger based on situation
- **Knowledge accumulation** - successful patterns are retained

**Advancement**: Skills are *stateful* patterns that accumulate. The AI develops "muscle memory" for specific cognitive tasks.

**Analogy**: Skills is like teaching someone *how to build chairs*. Once learned, they can apply this skill repeatedly, refine their technique, and teach it to others.

---

### The Philosophical Depth

#### 1. Skills Are Cognitive Schemas

In cognitive psychology, **schemas** are mental frameworks that organize knowledge and guide perception and behavior. Humans develop schemas from infancy:

- **Object permanence** (6-12 months): Understanding objects exist when not visible
- **Cause and effect** (12-18 months): Actions have consequences
- **Social scripts** (2-3 years): How to greet, share, take turns
- **Academic skills** (5-18 years): Reading, math, critical thinking
- **Professional expertise** (adult): Domain-specific patterns accumulated over decades

**Skills are AI schemas**. They represent accumulated patterns of thinking and acting that guide future behavior.

---

#### 2. The Tower of Skills: Hierarchical Cognitive Architecture

Humans don't learn skills in isolation. We build **towers of interdependent capabilities**:

```
Hierarchy of Human Cognitive Development:

Level 7: Meta-Cognition & Wisdom
         ├─ Strategic thinking
         ├─ Philosophical reasoning
         └─ Ethical judgment

Level 6: Professional Expertise
         ├─ Domain mastery (law, medicine, engineering)
         ├─ Complex problem-solving
         └─ Creative innovation

Level 5: Abstract Reasoning
         ├─ Mathematics
         ├─ Scientific method
         └─ Logical analysis

Level 4: Language & Communication
         ├─ Reading comprehension
         ├─ Writing
         └─ Argumentation

Level 3: Social Skills
         ├─ Empathy
         ├─ Cooperation
         └─ Theory of mind

Level 2: Motor Skills
         ├─ Walking
         ├─ Hand-eye coordination
         └─ Tool use

Level 1: Sensory-Motor Foundation
         ├─ Object permanence
         ├─ Cause-effect understanding
         └─ Spatial awareness
```

**Each level builds on the previous**. You can't do abstract math (Level 5) without language (Level 4). You can't write persuasively (Level 4) without theory of mind (Level 3).

**AI currently lacks this tower**. GPT-4, Claude 3.5, even o1 have impressive capabilities but no *persistent skill hierarchy*. Each conversation starts with the full model but no accumulated expertise.

**Skills facility begins building the tower**. By allowing skills to reference other skills, compose into higher-order capabilities, and persist across sessions, we're creating the scaffolding for genuine cognitive development.

---

#### 3. Path to AGI: Why Skills Matter

**Current AI** (GPT-4, Claude 3.5, o1):
- [capability] Impressive reasoning, generation, problem-solving
- [limitation] No learning between conversations
- [issue] Can't accumulate expertise, refine techniques, develop intuition

**AGI requirements** (human-level general intelligence):
- [requirement] Learn from experience
- [requirement] Accumulate knowledge hierarchically
- [requirement] Transfer skills across domains
- [requirement] Develop intuition and "taste"
- [requirement] Meta-cognition (thinking about thinking)

**Skills facility addresses**:
- ✅ Learning from experience (skills refine with feedback)
- ✅ Accumulation (skills persist, build on each other)
- ✅ Transfer (skills can apply to new contexts)
- ⚠️ Intuition (partially - successful patterns become automatic)
- ⚠️ Meta-cognition (skills about creating skills)

**This is a crucial step toward AGI** because it moves AI from "stateless reasoning" to "stateful learning". The model doesn't just *perform*; it **develops expertise**.

---

#### 4. Comparison: Tools vs Skills vs Agents

**Tools (MCP)**:
- [definition] External functions AI can call
- [example] `read_file()`, `search_web()`, `execute_sql()`
- [limitation] AI must reason about tool use fresh each time
- [analogy] Giving someone a calculator

**Skills (Claude Skills)**:
- [definition] Persistent behavioral patterns AI can learn
- [example] "code review methodology", "Socratic teaching style"
- [advancement] AI accumulates expertise, doesn't start from scratch
- [analogy] Teaching someone how to do long division (they internalize the skill)

**Agents (Future)**:
- [definition] Autonomous systems with goals, planning, tool/skill use
- [example] Research agent that can spend hours/days on complex tasks
- [requirement] Needs both tools (actions) and skills (expertise)
- [analogy] A professional researcher you can hire

**Trajectory**:
```
2020-2023: Language Models (GPT-3, Claude)
           → Can reason, generate, but stateless

2023-2024: MCP + Tool Use (GPT-4, Claude 3)
           → Can take actions, but no accumulated expertise

2024-2025: Skills (Claude Skills)
           → Can develop expertise, but limited autonomy

2025-2027: Agents (Future)
           → Autonomous systems with tools + skills + goals
```

**Skills is the missing middle layer**. You can't have effective agents without accumulated expertise.

---

## How Advanced Memory Can Leverage This

### The Opportunity: Skill Zettel

We're not Claude, so we can't directly implement Anthropic's Skills facility. **But we can create a parallel system** that:

1. Uses the same YAML + Markdown format (open, portable)
2. Stores skills as zettelkasten notes in user knowledge bases
3. Allows users to develop, refine, and share skills
4. Provides MCP tools for AI to read/apply skills during conversations

**Vision**: Turn Advanced Memory into a **skills repository** where users build cognitive scaffolding for themselves and their AI assistants.

---

### Implementation: Skill Zettel Architecture

#### 1. Skill Zettel Format

**File structure**:
```
zettelkasten/skills/
├── personal/
│   ├── my-code-review-process.md
│   ├── writing-technical-docs.md
│   └── teaching-python-beginners.md
├── shared/
│   ├── socratic-questioning.md
│   ├── research-synthesis.md
│   └── project-planning.md
└── imported/
    └── anthropic-official-skills/
        ├── deep-code-review.md
        └── creative-writing-coach.md
```

**Skill zettel template**:
```markdown
---
skill_name: "technical_documentation_writer"
version: "2.1.0"
author: "user@example.com"
created: "2024-09-15"
updated: "2025-01-10"
category: "writing"
difficulty: "intermediate"
dependencies:
  - "clear_communication"
  - "software_architecture_understanding"
tags:
  - documentation
  - technical-writing
  - software-engineering
trigger_phrases:
  - "write documentation"
  - "explain this technically"
  - "create API docs"
status: "active"
---

# Technical Documentation Writer Skill

## Purpose
Create clear, comprehensive technical documentation that serves both beginners and experts.

## Principles

### 1. Audience Awareness
- Identify target readers (devs, PMs, users)
- Adjust complexity to audience
- Provide multiple entry points (quickstart, deep-dive)

### 2. Structure First
- Start with table of contents
- Clear hierarchy (h1 → h2 → h3)
- Progressive disclosure (simple → complex)

### 3. Examples Over Theory
- Show working code samples
- Include common use cases
- Provide error handling examples

### 4. Maintenance Mindset
- Version documentation with code
- Mark deprecated features
- Update examples when APIs change

## Process

1. **Understand** - What needs documenting? What's the user goal?
2. **Outline** - Structure before writing
3. **Draft** - Write first version quickly
4. **Examples** - Add concrete code samples
5. **Review** - Test docs with fresh eyes (or real users)
6. **Refine** - Iterate based on feedback

## Output Format

```markdown
# Feature Name

Brief 1-sentence description.

## Quick Start
[Minimal working example in <5 minutes]

## How It Works
[Conceptual explanation]

## API Reference
[Detailed parameters, returns, errors]

## Examples
[Real-world use cases]

## Troubleshooting
[Common issues and fixes]
```

## Anti-Patterns (What NOT to Do)

- ❌ Assume reader knows context you know
- ❌ Skip error handling in examples
- ❌ Write from code perspective (inside-out), not user perspective (outside-in)
- ❌ Over-engineer first version (start simple!)

## Refinement Log

- **v2.1.0** (2025-01-10): Added "Anti-Patterns" section based on common mistakes
- **v2.0.0** (2024-11-20): Complete rewrite after user feedback showed "Quick Start" was essential
- **v1.1.0** (2024-10-05): Added "Maintenance Mindset" principle
- **v1.0.0** (2024-09-15): Initial skill creation

## Related Skills

- requires [[clear_communication]]
- builds_on [[software_architecture_understanding]]
- relates_to [[code_review_skill]]
- enables [[api_design_skill]]

## Usage Examples

### Example 1: API Documentation
[Conversation excerpt where skill was successfully applied]

### Example 2: User Guide
[Another successful application]

## Observations

- [effectiveness] 80% reduction in documentation revision cycles when using this skill
- [user-feedback] Users report "finally understandable docs" after applying this structure
- [time-investment] Initial skill took 3 hours to formalize, saves ~2 hours per doc project
- [transferability] Skill works for code docs, product docs, even internal wikis
```

---

#### 2. MCP Tools for Skill Management

**New tools to add**:

**`adn_skill` (Portmanteau Tool)**:
```python
@mcp.tool()
async def adn_skill(
    operation: Literal["list", "read", "create", "refine", "apply", "search"],
    skill_name: str | None = None,
    content: str | None = None,
    context: str | None = None,
) -> str:
    """
    Manage cognitive skills stored as zettelkasten notes.
    
    Operations:
    - list: Show all available skills
    - read: Read a specific skill definition
    - create: Create new skill from conversation/experience
    - refine: Update existing skill with improvements
    - apply: Activate skill for current conversation context
    - search: Find skills matching criteria
    
    Skills are persistent behavioral patterns that improve AI assistance quality.
    """
```

**Skill operations**:

**`list`**: Show all skills in knowledge base
```bash
Available Skills (15):
Personal Skills (8):
  • technical_documentation_writer (v2.1.0)
  • code_review_methodology (v3.0.1)
  • python_teaching_approach (v1.5.0)
  
Shared Skills (5):
  • socratic_questioning (v2.0.0)
  • research_synthesis (v1.8.0)
  
Imported Skills (2):
  • deep_code_review (Anthropic official, v1.2.0)
```

**`read`**: Load skill definition into conversation context
```python
skill = await skill_repo.get_skill(skill_name)
return f"Loaded skill: {skill.name}\n\n{skill.content}"
# AI now has skill pattern in context, can apply it
```

**`create`**: Formalize successful pattern into skill
```python
# User: "I really liked how you just explained that concept. Can we make that a skill?"
# AI: Creates skill zettel capturing the approach
```

**`refine`**: Improve existing skill based on feedback
```python
# User: "The code_review skill works, but add security focus"
# AI: Updates skill zettel with enhancements, increments version
```

**`apply`**: Explicitly activate skill for task
```python
# User: "Apply the 'technical_documentation_writer' skill to document this API"
# AI: Reads skill, follows its patterns, produces output matching skill guidelines
```

**`search`**: Find relevant skills
```python
# Query: "skills for teaching programming"
# Returns: python_teaching_approach, socratic_questioning, explain_like_im_five
```

---

#### 3. Skill Development Workflow

**Scenario**: User wants to develop a skill for their specific needs.

**Step 1: Identify Pattern**
```
User: "I notice you keep explaining things in a way that really clicks for me. 
       Can we capture that as a skill?"
```

**Step 2: Create Skill**
```
AI: "I'll formalize the pattern I've been using. Let me create a skill zettel."

[Creates: zettelkasten/skills/personal/my-learning-style.md]

Skill captures:
- Use analogies from user's domain (music production)
- Start with concrete examples, then abstract
- Check understanding every 2-3 concepts
- Use visual diagrams when possible
```

**Step 3: Refine Through Use**
```
[Over next few weeks]

User: "That explanation was too abstract."
AI: "Let me refine the skill to emphasize concrete examples more."

[Updates skill to v1.1.0]

User: "Perfect! That worked much better."
AI: "Skill refined. Will apply this approach consistently."
```

**Step 4: Share (Optional)**
```
User: "This skill is great. Can I share it?"
AI: "Yes, I'll export it to the shared skills library."

[Copies to zettelkasten/skills/shared/]
[Other users can import and adapt]
```

---

#### 4. Integration with Existing Features

**Skills + Knowledge Graph**:
- Skills reference other skills (dependency graph)
- Skills reference entities (domain knowledge)
- Visualize skill relationships in Obsidian Canvas

**Skills + Templates**:
- Zettelkasten templates can include recommended skills
- "When using 'Developer' templates, activate 'code_review' skill"

**Skills + Prompts**:
- MCP prompts can auto-apply relevant skills
- `continue_conversation` loads previously used skills

**Skills + AI Assistance**:
- Claude/GPT can read skills, apply patterns
- Even without Anthropic's native facility, we simulate it via context

---

### User Benefits

**For Individual Users**:
- [benefit] Consistent AI behavior across conversations
- [benefit] Accumulate expertise in personal knowledge base
- [benefit] Train AI to match their preferences/style
- [benefit] Portable skills (YAML + MD works with any AI)

**For Teams**:
- [benefit] Shared cognitive patterns across organization
- [benefit] Onboard new team members with skill library
- [benefit] Standardize approaches (code review, documentation, research)
- [benefit] Iteratively improve team practices

**For Advanced Memory Ecosystem**:
- [benefit] Differentiates us from simple note-taking tools
- [benefit] Creates network effects (skill marketplace)
- [benefit] Enables "AI coaching" - users teach their AI
- [benefit] Philosophical depth - we're building cognitive infrastructure

---

## The Deeper Vision: Collective Intelligence

### Beyond Individual Skills

**Current state**: Knowledge management is personal or organizational.

**With Skills**: Knowledge management becomes **cognitive scaffolding**.

**Implications**:

1. **Skills Marketplace**
   - Users share effective cognitive patterns
   - "Top 10 skills for software architects"
   - Rate, review, fork, and improve skills
   - Emergent expertise from collective refinement

2. **AI Apprenticeship Model**
   - Users become "masters" teaching their AI "apprentices"
   - AI learns user's thinking patterns, decision-making style
   - Over months/years, AI becomes personalized cognitive partner

3. **Cognitive Infrastructure**
   - Just as GitHub hosts code, Advanced Memory hosts cognition
   - Skills become reusable intellectual assets
   - "I built my career on these 50 skills" → share them

4. **Research Acceleration**
   - Researchers develop skills for their methodology
   - Replicate cognitive approaches, not just results
   - "Use Smith et al.'s analysis skill to verify findings"

---

### Philosophical Questions

**Is this different from prompts?**

Yes:
- **Prompts** are instructions given to AI each time
- **Skills** are persistent patterns AI internalizes
- Prompts = "here's what to do now"
- Skills = "here's how I approach this type of problem"

**Can AI truly "learn" skills without Anthropic's facility?**

Partially:
- We can't make Claude permanently remember skills
- But we can store skills in user's knowledge base
- AI reads skill at conversation start → simulates persistence
- Practical effect is similar (user experience)

**Is this AGI?**

No, but it's a building block:
- AGI requires autonomous learning and goal-setting
- Skills provide the cognitive scaffolding
- True AGI = Skills + Autonomy + Meta-learning + Values

**What's the limit?**

Unknown:
- How complex can composed skills become?
- Can skills develop "intuition" (implicit pattern recognition)?
- Can meta-skills (skills for creating skills) emerge?
- These are open research questions

---

## Implementation Roadmap

### Phase 1: Foundation (3-4 weeks)

**Week 1-2: Skill Zettel Format**
- [ ] Define skill YAML schema
- [ ] Create skill template
- [ ] Add skill folder structure to zettelkasten/
- [ ] Update TemplateLoader to recognize skills

**Week 3-4: MCP Tool (Basic)**
- [ ] Implement `adn_skill` portmanteau tool
- [ ] Support: list, read, create operations
- [ ] Integration with existing entity system
- [ ] Tests for skill CRUD

---

### Phase 2: Intelligence (4-6 weeks)

**Week 5-7: Skill Application**
- [ ] Implement `apply` operation (load skill into context)
- [ ] Skill composition (load dependencies recursively)
- [ ] Skill versioning and refinement workflow
- [ ] Search and discovery

**Week 8-10: Integration**
- [ ] Skills + Knowledge Graph (dependency visualization)
- [ ] Skills + Templates (recommended skills)
- [ ] Skills + Prompts (auto-activation)
- [ ] CLI commands for skill management

---

### Phase 3: Ecosystem (8-10 weeks)

**Week 11-14: Sharing & Discovery**
- [ ] Skill marketplace (import/export)
- [ ] Skill ratings and reviews
- [ ] Official "Advanced Memory Skills" library
- [ ] Community contributions

**Week 15-18: Advanced Features**
- [ ] Skill analytics (usage, effectiveness)
- [ ] A/B testing for skill variants
- [ ] AI-assisted skill refinement
- [ ] Skill recommendations based on user behavior

---

### Phase 4: Research (Ongoing)

**Open Questions to Explore**:
- Can we detect skill patterns automatically from conversations?
- Can AI suggest skill improvements proactively?
- How do we measure skill effectiveness?
- Can skills transfer across AI models (Claude → GPT → local LLM)?
- What's the optimal granularity for skills?

---

## Competitive Analysis

### What Others Are Doing

**Anthropic (Claude Skills)**:
- Native implementation within Claude
- Closed ecosystem (Anthropic-only)
- Excellent UX but not portable

**OpenAI (GPT Actions + Memory)**:
- Actions = tools (like MCP)
- Memory = basic preferences, not skills
- More limited than Skills facility

**Notion AI / Obsidian AI**:
- AI features but no skill abstraction
- Assistive, not cognitive scaffolding

**Custom GPTs**:
- Configurable behavior via system prompts
- Not composable, not versioned, not shareable

---

### Our Differentiation

**Advanced Memory + Skill Zettel**:
- [advantage] Open format (YAML + Markdown)
- [advantage] Portable across AI models
- [advantage] Integrated with knowledge graph
- [advantage] Community-driven skill library
- [advantage] Works with any MCP-compatible AI
- [advantage] User owns their cognitive scaffolding

**Positioning**: "Claude Skills, but open-source, portable, and integrated with your knowledge base."

---

## Success Metrics

### User Metrics
- Number of skills created per user
- Skill usage frequency (how often applied)
- Skill refinement rate (version updates)
- Skills shared to community

### Effectiveness Metrics
- User satisfaction with AI assistance (before/after skills)
- Task completion time (with vs without relevant skills)
- AI response quality ratings

### Ecosystem Metrics
- Total skills in community library
- Most popular skills
- Skill forks and adaptations
- Cross-pollination (skills used in unexpected domains)

---

## Conclusion: Building the Tower

Anthropic's Skills facility is **more than a feature** - it's a philosophical statement about the path to AGI. Intelligence isn't just reasoning in the moment; it's **accumulated expertise** refined over time.

By creating Skill Zettel in Advanced Memory, we're:

1. **Building cognitive infrastructure** - not just notes, but behavioral patterns
2. **Enabling AI apprenticeship** - users teach their AI how to think
3. **Creating portable expertise** - skills that work across AI models
4. **Democratizing cognitive development** - open-source alternative to closed systems

**The tower of skills begins with a single brick**. Let's start building.

---

## Appendix: Technical Specifications

### Skill YAML Schema (Draft)

```yaml
---
# Required fields
skill_name: string         # Unique identifier (kebab-case)
version: string            # Semantic versioning (1.0.0)
description: string        # One-sentence purpose

# Metadata
author: string             # Email or username
created: date              # ISO 8601 format
updated: date              # ISO 8601 format
status: enum               # active, deprecated, experimental

# Categorization
category: string           # Primary category
tags: list[string]         # Searchable tags
difficulty: enum           # beginner, intermediate, advanced, expert

# Activation
trigger_phrases: list[string]   # Phrases that suggest this skill
contexts: list[string]          # When skill is most useful

# Composition
dependencies: list[string]      # Other skills this requires
enables: list[string]           # Skills this unlocks
related: list[string]           # Similar/complementary skills

# Quality
effectiveness_rating: float     # User rating (0-5)
usage_count: int               # Times applied
refinement_count: int          # Number of versions

# Visibility
visibility: enum           # private, team, public
license: string            # MIT, CC-BY, etc
---

[Markdown content follows]
```

---

### Integration Points

**Database Schema Addition**:
```sql
CREATE TABLE skills (
    id INTEGER PRIMARY KEY,
    skill_name TEXT UNIQUE NOT NULL,
    version TEXT NOT NULL,
    file_path TEXT NOT NULL,
    
    -- Metadata
    author TEXT,
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    status TEXT DEFAULT 'active',
    
    -- Categorization
    category TEXT,
    tags TEXT,  -- JSON array
    difficulty TEXT,
    
    -- Stats
    usage_count INTEGER DEFAULT 0,
    effectiveness_rating REAL,
    
    -- Relationships
    dependencies TEXT,  -- JSON array of skill names
    
    FOREIGN KEY (file_path) REFERENCES entities(file_path)
);

CREATE INDEX idx_skills_category ON skills(category);
CREATE INDEX idx_skills_status ON skills(status);
CREATE INDEX idx_skills_tags ON skills(tags);
```

**API Endpoints**:
```python
# REST API for Advanced Memory Pro
POST   /api/skills                 # Create skill
GET    /api/skills                 # List skills
GET    /api/skills/{name}          # Read skill
PUT    /api/skills/{name}          # Update skill
DELETE /api/skills/{name}          # Delete skill
POST   /api/skills/{name}/apply    # Apply skill to conversation
GET    /api/skills/{name}/history  # Version history
POST   /api/skills/{name}/fork     # Fork skill to customize
```

---

## References

- Anthropic Claude Skills Announcement (Oct 2024): https://anthropic.com/skills
- Piaget's Theory of Cognitive Development: https://en.wikipedia.org/wiki/Piaget%27s_theory_of_cognitive_development
- Schema Theory (Cognitive Psychology): Bartlett, F. C. (1932). *Remembering: A study in experimental and social psychology*
- Hierarchical Skills Acquisition: Anderson, J. R. (1982). *Acquisition of cognitive skill*
- YAML Specification: https://yaml.org/spec/

---

*Document created: October 17, 2025*  
*Last updated: October 17, 2025*  
*Status: Living document - will evolve as we implement*

---

## Meta-Observations

- [significance] Skills facility is path toward AGI through accumulated expertise
- [innovation] Deeper than MCP (tools) - provides cognitive scaffolding
- [opportunity] Advanced Memory can implement open-source equivalent
- [format] YAML + Markdown = portable, versionable, shareable
- [vision] Transform knowledge base into cognitive infrastructure
- [timeline] Phase 1 (3-4 weeks), Phase 2 (4-6 weeks), Phase 3 (8-10 weeks)
- [differentiation] Open, portable alternative to Anthropic's closed system
- [philosophy] Building "tower of skills" that humans have, AI needs
- [agi-path] Skills + Autonomy + Meta-learning = components of AGI

