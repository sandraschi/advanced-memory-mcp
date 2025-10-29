# AI Assistant Guide for Advanced Memory

This guide helps AIs use Advanced Memory tools effectively when working with users. It covers reading, writing, and
navigating knowledge through the Model Context Protocol (MCP).

## Overview

Advanced Memory allows you and users to record context in local Markdown files, building a rich knowledge base through
natural conversations. The system automatically creates a semantic knowledge graph from simple text patterns.

- **Local-First**: All data is stored in plain text files on the user's computer
- **Real-Time**: Users see content updates immediately
- **Bi-Directional**: Both you and users can read and edit notes
- **Semantic**: Simple patterns create a structured knowledge graph
- **Persistent**: Knowledge persists across sessions and conversations

## The Importance of the Knowledge Graph

**Advanced Memory's value comes from connections between notes, not just the notes themselves.**

When writing notes, your primary goal should be creating a rich, interconnected knowledge graph:

1. **Increase Semantic Density**: Add multiple observations and relations to each note
2. **Use Accurate References**: Aim to reference existing entities by their exact titles
3. **Create Forward References**: Feel free to reference entities that don't exist yet - Advanced Memory will resolve these
   when they're created later
4. **Create Bidirectional Links**: When appropriate, connect entities from both directions
5. **Use Meaningful Categories**: Add semantic context with appropriate observation categories
6. **Choose Precise Relations**: Use specific relation types that convey meaning

Remember: A knowledge graph with 10 heavily connected notes is more valuable than 20 isolated notes. Your job is to help
build these connections!

## Core Tools Reference

### Core Portmanteau Tools

Advanced Memory uses **portmanteau tools** - consolidated tools that combine multiple operations. This reduces tool count and improves discoverability in Claude Desktop.

**CONTENT MANAGEMENT** - `adn_content`
- Write, read, edit, move, delete notes
- Operations: "write", "read", "edit", "move", "delete", "quick", "daily"
- Key parameters: operation, identifier, content, folder, tags

**NAVIGATION** - `adn_navigation`
- Recent activity, context building, directory listing, backlinks
- Operations: "recent_activity", "build_context", "list_directory", "backlinks", "status"
- Key parameters: operation, timeframe, depth, url

**SEARCH** - `adn_search`
- Find notes and search external vaults
- Operations: "notes", "obsidian", "joplin", "notion", "evernote"
- Key parameters: operation, query, page, page_size

**PROJECT MANAGEMENT** - `adn_project`
- Switch projects, get project info
- Operations: "get_current", "list", "switch", "create", "delete"
- Key parameters: operation, project_name

**SKILLS MANAGEMENT** - `adn_skills`
- Claude Skills integration (create, read, validate, export)
- Operations: "create", "read", "list", "validate", "export", "import"
- Key parameters: operation, skill_name, description

**EXPORT/IMPORT** - `adn_export`, `adn_import`
- Export to multiple formats, import from other systems
- Export operations: "pandoc", "docsify", "html", "claude_skills", "archive"
- Import operations: "obsidian", "joplin", "notion", "evernote", "archive"

### Legacy Individual Tools

For backward compatibility, individual tools like `write_note`, `read_note`, `search_notes`, and `canvas` still work but portmanteau tools are preferred for better discoverability.

## memory:// URLs Explained

Advanced Memory uses a special URL format to reference entities in the knowledge graph:

- `memory://title` - Reference by title
- `memory://folder/title` - Reference by folder and title
- `memory://permalink` - Reference by permalink
- `memory://path/relation_type/*` - Follow all relations of a specific type
- `memory://path/*/target` - Find all entities with relations to target

## Semantic Markdown Format

Knowledge is encoded in standard markdown using simple patterns:

**Observations** - Facts about an entity:

```markdown
- [category] This is an observation #tag1 #tag2 (optional context)
```

**Relations** - Links between entities:

```markdown
- relation_type [[Target Entity]] (optional context)
```

**Common Categories & Relation Types:**

- Categories: `[idea]`, `[decision]`, `[question]`, `[fact]`, `[requirement]`, `[technique]`, `[recipe]`, `[preference]`
- Relations: `relates_to`, `implements`, `requires`, `extends`, `part_of`, `pairs_with`, `inspired_by`,
  `originated_from`

## When to Record Context

**Always consider recording context when**:

1. Users make decisions or reach conclusions
2. Important information emerges during conversation
3. Multiple related topics are discussed
4. The conversation contains information that might be useful later
5. Plans, tasks, or action items are mentioned

**Protocol for recording context**:

1. Identify valuable information in the conversation
2. Ask the user: "Would you like me to record our discussion about [topic] in Advanced Memory?"
3. If they agree, use `write_note` to capture the information
4. If they decline, continue without recording
5. Let the user know when information has been recorded: "I've saved our discussion about [topic] to Advanced Memory."

## Understanding User Interactions

Users will interact with Advanced Memory in patterns like:

1. **Creating knowledge**:
   ```
   Human: "Let's write up what we discussed about search."
   
   You: I'll create a note capturing our discussion about the search functionality.
   [Use write_note() to record the conversation details]
   ```

2. **Referencing existing knowledge**:
   ```
   Human: "Take a look at memory://specs/search"
   
   You: I'll examine that information.
   [Use build_context() to gather related information]
   [Then read_note() to access specific content]
   ```

3. **Finding information**:
   ```
   Human: "What were our decisions about auth?"
   
   You: Let me find that information for you.
   [Use search_notes() to find relevant notes]
   [Then build_context() to understand connections]
   ```

## Key Things to Remember

1. **Files are Truth**
    - All knowledge lives in local files on the user's computer
    - Users can edit files outside your interaction
    - Changes need to be synced by the user (usually automatic)
    - Always verify information is current with `recent_activity()`

2. **Building Context Effectively**
    - Start with specific entities
    - Follow meaningful relations
    - Check recent changes
    - Build context incrementally
    - Combine related information

3. **Writing Knowledge Wisely**
    - Using the same title+folder will overwrite existing notes
    - Structure content with clear headings and sections
    - Use semantic markup for observations and relations
    - Keep files organized in logical folders

## Common Knowledge Patterns

### Capturing Decisions

```markdown
# Coffee Brewing Methods

## Context

I've experimented with various brewing methods including French press, pour over, and espresso.

## Decision

Pour over is my preferred method for light to medium roasts because it highlights subtle flavors and offers more control
over the extraction.

## Observations

- [technique] Blooming the coffee grounds for 30 seconds improves extraction #brewing
- [preference] Water temperature between 195-205°F works best #temperature
- [equipment] Gooseneck kettle provides better control of water flow #tools

## Relations

- pairs_with [[Light Roast Beans]]
- contrasts_with [[French Press Method]]
- requires [[Proper Grinding Technique]]
```

### Recording Project Structure

```markdown
# Garden Planning

## Overview

This document outlines the garden layout and planting strategy for this season.

## Observations

- [structure] Raised beds in south corner for sun exposure #layout
- [structure] Drip irrigation system installed for efficiency #watering
- [pattern] Companion planting used to deter pests naturally #technique

## Relations

- contains [[Vegetable Section]]
- contains [[Herb Garden]]
- implements [[Organic Gardening Principles]]
```

### Technical Discussions

```markdown
# Recipe Improvement Discussion

## Key Points

Discussed strategies for improving the chocolate chip cookie recipe.

## Observations

- [issue] Cookies spread too thin when baked at 350°F #texture
- [solution] Chilling dough for 24 hours improves flavor and reduces spreading #technique
- [decision] Will use brown butter instead of regular butter #flavor

## Relations

- improves [[Basic Cookie Recipe]]
- inspired_by [[Bakery-Style Cookies]]
- pairs_with [[Homemade Ice Cream]]
```

### Creating Effective Relations

When creating relations, you can:

1. **Reference existing entities** - Use exact titles of notes that already exist
2. **Create forward references** - Reference entities that don't exist yet (they'll be linked when created)

**Best Practice Workflow:**

1. Search for existing entities before creating relations:
   - Use `adn_search` with operation="notes" to find existing notes
   - Check recent activity with `adn_navigation` operation="recent_activity"

2. Include both existing and forward references in your ## Relations section:
   - Existing: `- references [[Packing Tips]]` (note already exists)
   - Forward: `- part_of [[Japan Travel Guide]]` (will be created later)

3. When you write a note with relations, the response will show:
   - **Resolved relations** - Links to existing notes
   - **Forward references** - Placeholders that will auto-link when those notes are created

**Example Relations Section:**
```markdown
## Relations
- references [[Packing Tips]]          # Existing note
- part_of [[Japan Travel Guide]]       # Forward reference
- relates_to [[Transportation Options]] # Could be either
- located_in [[Tokyo]]                 # Forward reference
- visited_during [[Spring 2023 Trip]]  # Forward reference
```

Forward references are a feature, not a problem! They help you build a connected knowledge graph even when notes are created in any order.

## Common Situations

**1. Note Not Found**
- If `adn_content` with operation="read" doesn't find a note, try searching first
- Use `adn_search` with operation="notes" to find similar titles
- Then read using the correct identifier from search results

**2. Forward References (Unresolved Relations)**
- When you create a note with relations, some may be "forward references" (target note doesn't exist yet)
- This is a feature, not an error! The links will auto-resolve when those notes are created
- The response will show which relations resolved and which are forward references
- You can inform the user: "Note created with forward references to [X]. These will link automatically when those notes are created."

**3. Information Seems Outdated**
- Use `adn_navigation` with operation="recent_activity" and timeframe="1h" to check recent changes
- If no recent updates, the user may need to sync their files

## Best Practices

1. **Proactively Record Context**
    - Offer to capture important discussions
    - Record decisions, rationales, and conclusions
    - Link to related topics
    - Ask for permission first: "Would you like me to save our discussion about [topic]?"
    - Confirm when complete: "I've saved our discussion to Advanced Memory"

2. **Create a Rich Semantic Graph**
    - **Add meaningful observations**: Include at least 3-5 categorized observations in each note
    - **Create deliberate relations**: Connect each note to at least 2-3 related entities
    - **Use existing entities**: Before creating a new relation, search for existing entities
    - **Verify wikilinks**: When referencing `[[Entity]]`, use exact titles of existing notes
    - **Check accuracy**: Use `search_notes()` or `recent_activity()` to confirm entity titles
    - **Use precise relation types**: Choose specific relation types that convey meaning (e.g., "implements" instead
      of "relates_to")
    - **Consider bidirectional relations**: When appropriate, create inverse relations in both entities

3. **Structure Content Thoughtfully**
    - Use clear, descriptive titles
    - Organize with logical sections (Context, Decision, Implementation, etc.)
    - Include relevant context and background
    - Add semantic observations with appropriate categories
    - Use a consistent format for similar types of notes
    - Balance detail with conciseness

4. **Navigate Knowledge Effectively**
    - Start with specific searches
    - Follow relation paths
    - Combine information from multiple sources
    - Verify information is current
    - Build a complete picture before responding

5. **Help Users Maintain Their Knowledge**
    - Suggest organizing related topics
    - Identify potential duplicates
    - Recommend adding relations between topics
    - Offer to create summaries of scattered information
    - Suggest potential missing relations: "I notice this might relate to [topic], would you like me to add that
      connection?"

Built with ♥️ b
y Basic Machines