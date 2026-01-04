# AI-Managed Project Switching

**Status**: ✅ Implemented (v1.0.0+)

AI-managed project switching allows Claude to automatically detect which project you're referring to based on conversation context, eliminating the need for explicit project switching commands.

## Overview

Instead of manually switching projects with `adn_project("switch", project_name="work")`, the AI analyzes your queries and automatically switches to the relevant project when it detects clear context.

## How It Works

### Detection Strategies

The AI uses multiple strategies to detect the relevant project:

1. **Explicit Project Name Mentions**
   - "Show me notes from my work project"
   - "Search in research project"
   - Confidence: **High** (0.8)

2. **Partial Name Matches**
   - "work notes", "personal files"
   - Confidence: **Medium** (0.3)

3. **Search Result Analysis**
   - When search results contain project metadata
   - Confidence: **Medium** (0.5)

4. **File Path Matching**
   - File paths that match project directory structures
   - Confidence: **High** (0.6)

5. **Folder Mentions**
   - "What's in the personal folder?"
   - Confidence: **Medium** (0.4)

6. **Current Project Inertia**
   - Small boost to current project to avoid unnecessary switches
   - Confidence: **Low** (+0.1)

### Automatic Switching Logic

The AI automatically switches projects when:
- **Confidence ≥ 0.6**: High confidence match → Auto-switch
- **Confidence ≥ 0.4 + No Current Project**: Medium confidence but no active project → Auto-switch
- **Confidence < 0.6**: Lower confidence → Suggest switch or ask for confirmation

## Usage Examples

### Natural Language Queries

```python
# User: "Show me notes from my work project"
# AI automatically:
# 1. Detects "work" project from query
# 2. Switches to work project (if confidence high)
# 3. Executes the search in work project

# User: "What's in the research folder?"
# AI automatically:
# 1. Detects "research" project from folder mention
# 2. Switches to research project
# 3. Lists research project contents
```

### Explicit Project References

```python
# User: "Search for API docs in my work-notes project"
# AI detects "work-notes" and switches automatically

# User: "Create a note in personal project about vacation"
# AI switches to personal project before creating note
```

### Context from Search Results

```python
# User: "Find information about Docker"
# AI:
# 1. Searches across projects (or current project)
# 2. Finds results in "dev-notes" project
# 3. Automatically switches to "dev-notes" for follow-up queries
```

## Implementation Details

### Project Detection Service

The `ProjectDetector` service (`src/advanced_memory/services/project_detector.py`) provides:

```python
from advanced_memory.services.project_detector import get_project_detector

detector = get_project_detector()

# Detect project from context
result = await detector.detect_project_from_context(
    user_query="Show me work notes",
    current_project="personal",
    search_results=[...],  # Optional
    file_paths=[...],      # Optional
)

# Result structure:
{
    "suggested_project": "work",
    "confidence": 0.8,
    "reason": "Project name 'work' mentioned in query",
    "should_switch": True
}
```

### MCP Tool Integration

The `adn_project` tool includes a `detect` operation:

```python
# AI can call this to detect project context
adn_project("detect")
```

### Integration Points

The AI can use project detection in several ways:

1. **Before Tool Calls**: Detect project before executing operations
2. **After Search Results**: Analyze results to detect project context
3. **From File Paths**: Extract project from file paths in queries
4. **From Conversation History**: Learn from previous project switches

## Configuration

### Confidence Thresholds

Default thresholds (configurable in `ProjectDetector`):

- **Auto-switch threshold**: 0.6 (60% confidence)
- **Suggest threshold**: 0.4 (40% confidence)
- **Inertia boost**: +0.1 (10% boost for current project)

### Disabling Auto-Switching

If you prefer manual control:

1. Set confidence threshold to 1.0 (100%)
2. Always use explicit `project` parameter in tool calls
3. Disable the `detect` operation in tool descriptions

## Best Practices

### For Users

1. **Be Specific**: Mention project names explicitly for best results
   - ✅ "Show me work project notes"
   - ❌ "Show me notes" (ambiguous)

2. **Use Folder Names**: Reference folders that match project names
   - ✅ "What's in the research folder?"
   - ❌ "What's in folder X?" (unclear)

3. **Provide Context**: Give hints about which project you mean
   - ✅ "Search for Docker in my dev notes"
   - ❌ "Search for Docker" (could be any project)

### For AI Assistants

1. **Check Context First**: Use `detect` operation before switching
2. **Confirm High-Confidence Switches**: Auto-switch when confidence ≥ 0.6
3. **Ask for Low-Confidence**: Request confirmation when confidence < 0.6
4. **Explain Switches**: Tell user when you switch projects
5. **Respect Explicit Parameters**: If user specifies `project` parameter, use it

## Future Enhancements

### Planned Features

1. **Cross-Project Search**
   - Search across all projects to find content location
   - Automatically switch to project with most relevant results

2. **Learning from Patterns**
   - Track user's project usage patterns
   - Learn which projects are used for which topics
   - Time-based project suggestions (work hours → work project)

3. **Entity-Based Detection**
   - Detect projects based on entity mentions
   - "Show me notes about John" → Find which project contains John entity

4. **Conversation History Analysis**
   - Analyze full conversation context
   - Detect project switches from conversation flow
   - Maintain project context across conversation turns

5. **Smart Suggestions**
   - Suggest project switches proactively
   - "I notice you're asking about work topics. Switch to work project?"

## Troubleshooting

### AI Not Switching Projects

**Problem**: AI doesn't automatically switch even when project is mentioned.

**Solutions**:
1. Be more explicit: "Switch to work project and show notes"
2. Check if project name matches exactly (case-insensitive)
3. Verify project exists: `adn_project("list")`

### Wrong Project Detected

**Problem**: AI switches to wrong project.

**Solutions**:
1. Use explicit project parameter: `adn_content(..., project="correct-project")`
2. Manually switch: `adn_project("switch", project_name="correct-project")`
3. Provide more context in your query

### Too Many Switches

**Problem**: AI switches projects too frequently.

**Solutions**:
1. Increase confidence threshold in `ProjectDetector`
2. Use explicit `project` parameter to lock to one project
3. Disable auto-switching for specific operations

## Examples

### Example 1: Natural Project Detection

```
User: "Show me my work notes about the API redesign"

AI Process:
1. Detects "work" in query → confidence 0.8
2. Current project is "personal" → should switch
3. Auto-switches to "work" project
4. Searches for "API redesign" in work project
5. Returns results

Response: "I've switched to your work project and found 3 notes about the API redesign..."
```

### Example 2: Folder-Based Detection

```
User: "What's in the research folder?"

AI Process:
1. Detects "research" folder mention → confidence 0.4
2. Matches "research" to "research-papers" project → confidence 0.6
3. Auto-switches to "research-papers" project
4. Lists folder contents

Response: "I've switched to your research-papers project. Here's what's in the research folder..."
```

### Example 3: Search Result Context

```
User: "Find information about Docker"

AI Process:
1. Searches current project (personal) → no results
2. Searches other projects → finds results in "dev-notes"
3. Detects project from search results → confidence 0.5
4. Switches to "dev-notes" project
5. Returns Docker-related notes

Response: "I found Docker information in your dev-notes project. I've switched to that project and here are the results..."
```

## Technical Reference

### ProjectDetector API

```python
class ProjectDetector:
    async def detect_project_from_context(
        self,
        user_query: str,
        current_project: str | None = None,
        search_results: list[dict[str, Any]] | None = None,
        file_paths: list[str] | None = None,
    ) -> dict[str, Any]:
        """Detect relevant project from context."""

    async def search_across_projects(
        self,
        query: str,
        max_results_per_project: int = 3
    ) -> dict[str, Any]:
        """Search across all projects to find content location."""
```

### Integration with Tools

Tools can use project detection by:

1. **Calling detector before operations**:
```python
detector = get_project_detector()
detection = await detector.detect_project_from_context(user_query)
if detection["should_switch"]:
    await adn_project("switch", project_name=detection["suggested_project"])
```

2. **Using detection results**:
```python
project = detection["suggested_project"] if detection["confidence"] >= 0.6 else current_project
await adn_content("read", identifier="note", project=project)
```

## Related Documentation

- [Project Management Guide](../user-guide/project-management.md)
- [MCP Tools Reference](../TOOLS_REFERENCE.md)
- [Architecture Deep Dive](../ARCHITECTURE_DEEP_DIVE.md)
