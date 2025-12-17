# Multi-Project Usage Examples

**Status**: ✅ Ready to Use

This guide shows practical examples of using multiple projects in Advanced Memory to organize your knowledge and avoid ambiguity.

## Why Multiple Projects?

Projects help you:
- **Separate contexts**: Personal vs work vs research
- **Avoid ambiguity**: "Steve" (your brother) vs "Steve Jobs" (public figure)
- **Organize by purpose**: Daily notes vs long-term research
- **Privacy**: Keep personal notes separate from work notes
- **Focus**: Search only in relevant context

## Common Project Setups

### Setup 1: Personal + Work Separation

**Projects:**
- `private` - Personal notes, family, friends, daily life
- `work` - Work projects, professional notes, business contacts

**Example:**
```
User: "Tomorrow I meet Steve"
AI: Detects "private" project (personal context)
    → Creates note in private project
    → Searches find "Steve" (your brother) not "Steve Jobs"
```

### Setup 2: Research + Personal + Work

**Projects:**
- `research` - Academic papers, research notes, deep dives
- `private` - Personal life, family, friends
- `work` - Professional work, clients, projects

**Example:**
```
User: "Find notes about machine learning"
AI: Detects "research" project (technical topic)
    → Searches in research project
    → Finds academic/research notes, not work implementation notes
```

### Setup 3: Daily + Archive + Projects

**Projects:**
- `daily` - Daily journal, quick notes, reminders
- `archive` - Old notes, completed projects, historical
- `work` - Active work projects

**Example:**
```
User: "What did I do last week?"
AI: Detects "daily" project (time-based query)
    → Searches daily project for recent entries
```

## Real-World Usage Examples

### Example 1: Personal Note with Name Disambiguation

**Scenario**: You want to note that you're meeting your brother Steve tomorrow.

**Without Projects:**
```
User: "Create a note: Tomorrow I meet Steve"
AI: Creates note, but "Steve" could match:
    - Your brother Steve
    - Steve Jobs (if you have notes about Apple)
    - Steve from work
    → Ambiguous results
```

**With Projects:**
```
User: "Create a note in my private project: Tomorrow I meet Steve"
AI: 
    1. Detects "private" project from query
    2. Switches to private project
    3. Creates note about meeting Steve
    4. When searching "Steve", finds your brother (not Steve Jobs)
```

**Or with AI detection:**
```
User: "Tomorrow I meet Steve"
AI:
    1. Analyzes context: "meet" + personal name → personal context
    2. Detects "private" project (confidence: 70%)
    3. Auto-switches to private project
    4. Creates note
    5. "I've switched to your private project and created the note about meeting Steve"
```

### Example 2: Work vs Personal Research

**Scenario**: You want to find information about Docker.

**Without Projects:**
```
User: "Find notes about Docker"
AI: Searches all notes
    → Finds:
    - Personal Docker setup notes
    - Work Docker deployment docs
    - Research about containerization
    → Mixed results, hard to find what you need
```

**With Projects:**
```
User: "Find Docker notes in my work project"
AI:
    1. Detects "work" project
    2. Switches to work project
    3. Searches only work notes
    4. Finds work-specific Docker deployment documentation
```

**Or with AI detection:**
```
User: "Show me work notes about Docker"
AI:
    1. Detects "work" from query (confidence: 80%)
    2. Auto-switches to work project
    3. Searches for Docker
    4. Returns only work-related Docker notes
```

### Example 3: Daily Journal vs Long-term Notes

**Scenario**: You want to add a quick thought vs create a detailed research note.

**Daily Note (Quick Capture):**
```
User: "Quick note: Had great coffee today"
AI:
    1. Detects "quick note" → daily project
    2. Creates note in daily project
    3. Simple, searchable later
```

**Research Note (Deep Dive):**
```
User: "Create a research note about coffee brewing methods"
AI:
    1. Detects "research" from query (confidence: 75%)
    2. Switches to research project
    3. Creates detailed research note
    4. Can link to other research notes
```

### Example 4: Family vs Work Contacts

**Scenario**: You want to find information about "John".

**Without Projects:**
```
User: "Find notes about John"
AI: Searches all notes
    → Finds:
    - John (your friend)
    - John (work colleague)
    - John (historical figure you researched)
    → Which John? Unclear
```

**With Projects:**
```
User: "Find notes about John in my private project"
AI:
    1. Detects "private" project
    2. Searches private project only
    3. Finds John (your friend), not work John
```

**Or with context:**
```
User: "What did I note about John last week?"
AI:
    1. "last week" + personal query → private project
    2. Detects private project (confidence: 65%)
    3. Searches private project for recent John notes
    4. Finds personal notes about your friend John
```

### Example 5: Project-Specific Searches

**Scenario**: You want to search for "API" but only in work context.

**Work API Notes:**
```
User: "Show me API documentation in work project"
AI:
    1. Detects "work" project (confidence: 85%)
    2. Switches to work project
    3. Searches for "API"
    4. Returns work API documentation, not personal API learning notes
```

**Research API Notes:**
```
User: "Find API research notes"
AI:
    1. Detects "research" from query (confidence: 70%)
    2. Switches to research project
    3. Searches for "API"
    4. Returns research/academic notes about APIs
```

## Creating Your First Multi-Project Setup

### Step 1: Create Projects

```python
# Create private project for personal notes
adn_project("create", 
    project_name="private",
    project_path="~/Documents/advanced-memory/private")

# Create work project
adn_project("create",
    project_name="work", 
    project_path="~/Documents/advanced-memory/work")

# Optional: Create research project
adn_project("create",
    project_name="research",
    project_path="~/Documents/advanced-memory/research")
```

### Step 2: Set Default Project

```python
# Set private as default (for personal use)
adn_project("set_default", project_name="private")
```

### Step 3: Start Using Projects

**Natural language works:**
```
User: "Create a note: Meeting with Steve tomorrow"
AI: Detects private project → Creates note there

User: "Find work notes about the API redesign"
AI: Detects work project → Searches there

User: "What research do I have on machine learning?"
AI: Detects research project → Searches there
```

## AI Detection Examples

### High Confidence Auto-Switch (≥60%)

```
User: "Show me notes from my work project"
AI: 
    - Detects "work" project (confidence: 80%)
    - Auto-switches to work project
    - "I've switched to your work project. Here are your notes..."

User: "Create a private note about vacation plans"
AI:
    - Detects "private" project (confidence: 75%)
    - Auto-switches to private project
    - Creates vacation note
```

### Medium Confidence Suggestion (40-60%)

```
User: "Find notes about Steve"
AI:
    - Detects "private" project (confidence: 45%)
    - Suggests switching but doesn't auto-switch
    - "I found notes about Steve. You might want to switch to your private project for better results. Should I switch?"

User: "What's in the research folder?"
AI:
    - Detects "research" project (confidence: 50%)
    - Suggests switching
    - "Based on 'research folder', you might want to switch to your research project."
```

### Low Confidence (Stay on Current)

```
User: "Show me notes"
AI:
    - No clear project detected (confidence: 20%)
    - Stays on current project
    - "I'll search in your current project (private). Specify a project name for better results."
```

## Project Organization Tips

### 1. Use Descriptive Project Names

**Good:**
- `private` - Clear, personal context
- `work` - Clear, professional context
- `research` - Clear, academic/research context

**Avoid:**
- `project1`, `project2` - Not descriptive
- `stuff` - Too vague
- Very long names - Hard to type

### 2. Keep Projects Focused

**Each project should have a clear purpose:**
- `private`: Personal life, family, friends, daily notes
- `work`: Professional work, clients, business
- `research`: Deep dives, academic papers, learning
- `archive`: Old notes, completed projects

### 3. Use Folders Within Projects

Projects can still have folders for organization:
```
private/
  ├── family/
  ├── friends/
  └── daily/

work/
  ├── clients/
  ├── projects/
  └── meetings/
```

### 4. Switch Projects Naturally

**Explicit:**
```
"Show me work notes"
"Create a private note"
"Search in research project"
```

**Context-based (AI detects):**
```
"Tomorrow I meet Steve" → private project
"Find API docs" → work project (if work context)
"Research on quantum computing" → research project
```

## Advanced: Cross-Project Operations

### Search Across Projects

```python
# Search all projects
adn_search("notes", query="Docker", projects="ALL")

# Search specific projects
adn_search("notes", query="API", projects="work,research")
```

### Export Multiple Projects

```python
# Export all projects
adn_export("pdf", project="ALL")

# Export specific projects
adn_export("html", project="work,private")
```

## Troubleshooting

### AI Not Detecting Project

**Problem**: AI doesn't switch projects automatically.

**Solution**: Be more explicit:
```
❌ "Find notes about Steve"
✅ "Find notes about Steve in my private project"
```

### Wrong Project Detected

**Problem**: AI switches to wrong project.

**Solution**: 
1. Manually switch: `adn_project("switch", project_name="correct-project")`
2. Use explicit project parameter in tool calls
3. Provide more context in your query

### Too Many Projects

**Problem**: You have too many projects and it's confusing.

**Solution**: 
- Consolidate similar projects
- Use folders within projects instead
- Archive old projects

## Best Practices Summary

1. **Start Simple**: Begin with 2-3 projects (private, work, research)
2. **Be Explicit**: Mention project names when needed
3. **Trust AI Detection**: Let AI auto-switch when confident
4. **Use Folders**: Organize within projects with folders
5. **Review Regularly**: Archive or consolidate projects as needed

## Next Steps

1. **Create your projects**: Start with `private` and `work`
2. **Set default**: Choose your most-used project as default
3. **Start using**: Create notes and let AI detect projects
4. **Refine**: Adjust project names/purposes as you learn

For more details, see:
- [AI-Managed Project Switching](../features/AI_MANAGED_PROJECT_SWITCHING.md)
- [Project Management Guide](./project-management.md)

