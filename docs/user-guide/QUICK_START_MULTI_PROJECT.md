# Quick Start: Multi-Project Setup

**Get started with multiple projects in 5 minutes!**

## Why Use Multiple Projects?

Projects help you:
- **Avoid ambiguity**: "Steve" (your brother) vs "Steve Jobs" (public figure)
- **Separate contexts**: Personal notes vs work notes vs research
- **Better search**: Find exactly what you need without noise

## Quick Setup (3 Steps)

### Step 1: Create a Private Project

```python
adn_project("create",
    project_name="private",
    project_path="~/Documents/advanced-memory/private",
    set_default=True)  # Set as default if you use it most
```

### Step 2: Create a Work Project (Optional)

```python
adn_project("create",
    project_name="work",
    project_path="~/Documents/advanced-memory/work")
```

### Step 3: Start Using!

**That's it!** The AI will automatically detect which project to use:

```
You: "Tomorrow I meet Steve"
AI: Detects "private" project → Creates note there

You: "Find work notes about the API"
AI: Detects "work" project → Searches there
```

## Common Use Cases

### Personal Notes (Private Project)

**Use for:**
- Daily notes: "Tomorrow I meet Steve"
- Family & friends: "Marion's birthday next week"
- Personal reminders: "Call dentist tomorrow"
- Private thoughts: "Had great coffee today"

**Why it helps:**
- When you search "Steve", you find your brother, not "Steve Jobs"
- Personal notes stay separate from work/research

### Work Notes (Work Project)

**Use for:**
- Work projects: "API redesign meeting notes"
- Professional contacts: "Client John from Acme Corp"
- Business tasks: "Deadline for project X"
- Work research: "Docker deployment best practices"

**Why it helps:**
- Work notes don't mix with personal notes
- Professional context stays organized

### Research Notes (Research Project - Optional)

**Use for:**
- Deep dives: "Machine learning fundamentals"
- Academic papers: "Research on quantum computing"
- Learning notes: "Python async programming"
- Long-term knowledge: "History of containerization"

**Why it helps:**
- Research stays separate from daily notes
- Easy to find when you need deep knowledge

## How AI Detection Works

The AI automatically detects projects from your queries:

### High Confidence (Auto-Switches)

```
"Tomorrow I meet Steve" 
→ Detects: private project (personal context)
→ Confidence: 70%
→ Auto-switches ✓

"Show me work notes about Docker"
→ Detects: work project (explicit mention)
→ Confidence: 85%
→ Auto-switches ✓
```

### Medium Confidence (Suggests)

```
"Find notes about Steve"
→ Detects: private project (personal name)
→ Confidence: 45%
→ Suggests switching (doesn't auto-switch)

"Research on machine learning"
→ Detects: research project (research context)
→ Confidence: 55%
→ Suggests switching
```

### Low Confidence (Stays on Current)

```
"Show me notes"
→ No clear project detected
→ Confidence: 20%
→ Stays on current project
```

## Examples

### Example 1: Personal Note

```
You: "Create a note: Tomorrow I meet Steve"

AI Process:
1. Detects "meet" + personal name → private project
2. Confidence: 70%
3. Auto-switches to private project
4. Creates note about meeting Steve (your brother)

Result: Note created in private project. When you search "Steve" later, you find your brother, not Steve Jobs.
```

### Example 2: Work Note

```
You: "Find work notes about the API redesign"

AI Process:
1. Detects "work" explicitly mentioned
2. Confidence: 85%
3. Auto-switches to work project
4. Searches for "API redesign"

Result: Only work-related API notes, not personal API learning notes.
```

### Example 3: Ambiguous Query

```
You: "Find notes about Docker"

AI Process:
1. No clear project context
2. Confidence: 30%
3. Stays on current project (private)
4. Searches current project

Better Query: "Find Docker notes in my work project"
→ Explicit project → 100% confidence → Switches immediately
```

## Tips

1. **Be explicit when needed**: "work project", "private project"
2. **Trust AI detection**: It usually gets it right
3. **Start simple**: Begin with 2 projects (private + work)
4. **Add more later**: Create research/archive projects as needed

## Next Steps

- See [Multi-Project Examples](./MULTI_PROJECT_EXAMPLES.md) for detailed scenarios
- See [AI-Managed Project Switching](../features/AI_MANAGED_PROJECT_SWITCHING.md) for technical details
- See [Project Management Guide](./project-management.md) for all operations

