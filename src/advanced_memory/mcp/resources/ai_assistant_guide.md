# AI Assistant Guide for Advanced Memory

_Last updated: 2025-11-09 — aligns with FastMCP 2.13 toolset, portmanteau alias handling, and skill-creator workflows._

This guide keeps Claude (and other MCP-aware assistants) aligned with the current Advanced Memory feature set. Follow it to read, write, and navigate knowledge safely while taking advantage of the portmanteau tooling and alias normalization that prevent common AI mis-calls.

---

## 1. Core Principles

- **Local-first knowledge graph**: Everything lives in Markdown inside the user’s repo. Files are the source of truth.
- **Semantic Markdown** creates the graph. Observations and relations power the retrieval experience.
- **Structured tagging**: Every new note must carry meaningful tags in its frontmatter (`tags: ["topic", "error-pattern", ...]`). Untagged notes drown in the archive.
- **Context freshness matters**: Use `adn_navigation` → `recent_activity` or `adn_content` → `read_latest` to confirm you are working with the newest material before acting.

Remember: 10 highly connected notes beat 20 isolated ones. Every action should either add useful connections or surface the right existing context quickly.

---

## 2. Portmanteau Tool Quick Reference

Advanced Memory exposes 15 consolidated tools by default. Each accepts an `operation` string that is normalized (spaces, hyphens, camelCase, and most typos map to the right entry). Friendly error messages tell you when an alias fails.

| Tool | Primary Use | Common Operations (canonical ➜ helpful aliases) |
| --- | --- | --- |
| `adn_content` | CRUD on notes | `write`, `read`, `read_latest`, `view`, `view_rendered`, `edit`, `edit_tags`, `move`, `delete`, `quick`, `daily` ➜ accepts `"create note"`, `"latest"`, `"modify tags"`, etc. |
| `adn_search` | Search notes & external vaults | `notes`, `obsidian`, `joplin`, `notion`, `evernote` ➜ `"text"`, `"title"`, `"searchnotes"` auto-map. `notes` sets sensible defaults (`entity_types=["entity","observation"]`). |
| `adn_navigation` | Recent activity, directories, backlinks | `recent_activity`, `list_directory`, `backlinks`, `build_context`, `status`, `sync_status` ➜ `"last activity"`, `"ListDirectory"`, etc. |
| `adn_project` | Project lifecycle | `list`, `get_current`, `switch`, `create`, `delete`, `status`, `sync` with case-agnostic aliases. |
| `adn_export` | Export flows | `pandoc`, `docsify`, `html`, `claude_skills`, `pdf_book`, `archive`, `notion`, `evernote`. |
| `adn_import` | Import flows | `obsidian`, `joplin`, `notion`, `evernote`, `archive`. |
| `adn_knowledge` | Bulk note ops, analytics | `tag_analytics`, `bulk_update`, `bulk_move`, `find_duplicates`, `validate_content`, etc. |
| `adn_skills` | Skill management | `create`, `list`, `read`, `update`, `delete`, `validate`, `export`, `import`, `package`, `import_from_github`, `distill_from_wikipedia/arxiv/textbook/text/expert`. |
| `adn_skills_creator` | Gold-standard skill scaffolding | `scaffold`, `validate`, `package`, `upgrade`, `inspect`. |
| `adn_zettelmaker` | Zettelkasten automation | `generate`, `customize`, `expand`, `suggest`, `connect`, `analyze`. |
| `adn_inbox` | File-drop inbox | `status`, `process`, `info`, `watch`. |
| `adn_audio` | Voice I/O | `dictate`, `speak`. |
| `canvas` | Visual graph | Create `.canvas` layouts for Obsidian. |
| `typora_control` | Typora automation | Interact with Typora (open files, apply templates) |
| `view_note_rendered` | Rendered HTML view | Use when users want a pretty read-only artifact. |

**Alias Safety Tips**
- Operation names ignore case and punctuation (`"ReadLatest"`, `"read latest"`, `"read-latest"` all land on `read_latest`).
- Unknown aliases trigger errors like `invalid operation parameter 'play the clarinet'` with suggestions. Act on the hints rather than guessing.
- Parameters such as `search_type`, `entity_types`, and `tag_operation` also allow underscore variants as a fallback (`"searchType"`, `"search_type"`, `"search type"` all work).

---

## 3. Example Workflows (Current API)

```python
# Create or append to a note (tags required – keep them meaningful)
await adn_content(
    operation="write",
    identifier="Search Architecture Plan",
    folder="specs/search",
    tags=["search", "architecture", "2025-release"],
    content="""# Search Architecture Plan
- [decision] Adopt hybrid BM25 + embedding rerank #retrieval
- [risk] Embedding index refresh takes >4h #ops
- influences [[Search Scalability OKR]]
""",
)

# Grab the latest activity intelligently (automatic fallback handles 'latest')
latest = await adn_content(operation="read_latest")

# Search across notes by content with relation filtering handled for you
results = await adn_search(operation="text", query="vector database rollout", page=1, page_size=5)

# Find what changed this week, including linked context
activity = await adn_navigation(operation="recent_activity", timeframe="7d", depth=2)

# Scaffold a Claude skill using the modular architecture
await adn_skills_creator(
    operation="scaffold",
    skill_name="vector-database-operations",
    category="developer",
    confidence="low",
)

# Package the skill (validates and emits a zip manifest)
await adn_skills_creator(operation="package", skill_path="skills/developer/vector-database-operations")

# Create an export for doc review
await adn_export(operation="pandoc", format_type="pdf", source_folder="docs/architecture")
```

---

## 4. Knowledge Graph Essentials

1. **Observations** (`- [category] fact #tag`) encode domain knowledge. Use categories like `[decision]`, `[issue]`, `[experiment]`, `[fact]`, `[recipe]`.
2. **Relations** (`- implements [[Entity]]`) connect entities. Prefer precise verbs (`implements`, `blocks`, `depends_on`, `pairs_with`) over generic `relates_to`.
3. **Forward references** are expected. If a relation targets a note that does not exist yet, Advanced Memory stores it for later resolution—mention this instead of treating it as an error.
4. **Always tag the note** in frontmatter. Use combinations that help future retrieval (`tags: ["search", "architecture", "mitigation"]`).

### memory:// URLs (still essential)
- `memory://title` – reference by title.
- `memory://folder/title` – reference with folder hint.
- `memory://permalink` – exact link.
- `memory://permalink/*/target` – follow relations.
- `memory://permalink/relation_type/*` – follow a specific relation type.

---

## 5. Keeping Context Fresh

- Use `adn_navigation(operation="recent_activity")` before editing to confirm the latest writes.
- `adn_content(operation="read_latest")` now uses direct GraphContext data and falls back elegantly if recent activity is empty.
- If `recent_activity` returns nothing but you expect changes, suggest running the repo sync (`scripts/restart_claude_and_check_mcp.ps1`) or a manual `basic-memory sync`.

---

## 6. Skills Workflow Highlights

- Skills use the **modular three-layer architecture** (Anthropic-aligned):
  1. `SKILL.md` (brief status banner + module overview)
  2. `_toc.md`
  3. `modules/` sub-files (core guidance, known gaps, research checklist, plus domain-specific modules)
- Use `adn_skills` for reading or validating existing skills.
- Use `adn_skills_creator` for new scaffolds, packaging with checksums, and upgrading legacy skills.
- `adn_skills` distillation operations (e.g., `distill_from_wikipedia`, `distill_from_arxiv`) bring in authoritative content—perfect for the “science track” skills or refreshing stale ones.

---

## 7. Error Handling Patterns

- Portmanteau tools never throw raw exceptions. You will always receive structured payloads with `success`, `error_code`, and `suggestions`.
- If an alias fails, read the error message (e.g., `invalid operation parameter 'listdirectory' — try one of ['list_directory', 'recent_activity', ...]`).
- Missing note? Use `adn_search(operation="text", query="...")` or the alias fallback rather than repeating the same call.
- Tagging operations in `adn_content` automatically normalize existing tag metadata (string or list). If tagging still fails, suggest running `adn_content(operation="read", identifier=...)` to inspect the current metadata first.

---

## 8. Best Practices & Reminders

- **Ask before writing**: “Should I capture our decision on vector search now?” Respect “no”.
- **Confirm after writing**: “Recorded our vector search rollout plan with tags `['search','architecture','2025-release']`.”
- **Keep titles stable**: Re-using `(folder, title)` overwrites the note; only do this intentionally.
- **Use aliases deliberately**: They exist to keep Claude friendly, but don’t rely on fuzzy matches when the canonical term is known.
- **Surface gaps**: When reading a skill, highlight items listed under `known-gaps.md` so the user knows what remains.
- **Cross-check scientific content**: For high-risk topics (APIs, fast-moving tech, regulations) run a web search before trusting existing guidance—then update the skill modules and note the source in the `Source Log`.

---

## 9. Quick Reference Snippets

```markdown
- [decision] Adopt Claude alias normalization in `adn_content` #tooling
- relates_to [[Portmanteau Normalization Plan 2025-11-09]]
- tagged_with [[Tag Discipline Policy]]
```

```python
# Friendly alias call (works)
await adn_content(
    operation="create note", identifier="Release Checklist", tags=["release", "checklist"], content="..."
)  # maps to write

# Bad alias (typo) – handle the structured error
try:
    await adn_navigation(operation="listdirectories")
except ToolError as exc:
    # suggestions include "list_directory"
    ...
```

Stay disciplined, surface context, and let the knowledge graph work for you. When in doubt, `adn_navigation` + `recent_activity` or `adn_search` with `operation="text"` will steer you back to solid ground.

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

1. Reference existing entities by their exact title
2. Create forward references to entities that don't exist yet

```python
# Example workflow for creating notes with effective relations
async def create_note_with_effective_relations():
    # Search for existing entities to reference
    search_results = await search_notes("travel")
    existing_entities = [result.title for result in search_results.primary_results]

    # Check if specific entities exist
    packing_tips_exists = "Packing Tips" in existing_entities
    japan_travel_exists = "Japan Travel Guide" in existing_entities

    # Prepare relations section - include both existing and forward references
    relations_section = "## Relations\n"

    # Existing reference - exact match to known entity
    if packing_tips_exists:
        relations_section += "- references [[Packing Tips]]\n"
    else:
        # Forward reference - will be linked when that entity is created later
        relations_section += "- references [[Packing Tips]]\n"

    # Another possible reference
    if japan_travel_exists:
        relations_section += "- part_of [[Japan Travel Guide]]\n"

    # You can also check recently modified notes to reference them
    recent = await recent_activity(timeframe="1 week")
    recent_titles = [item.title for item in recent.primary_results]

    if "Transportation Options" in recent_titles:
        relations_section += "- relates_to [[Transportation Options]]\n"

    # Always include meaningful forward references, even if they don't exist yet
    relations_section += "- located_in [[Tokyo]]\n"
    relations_section += "- visited_during [[Spring 2023 Trip]]\n"

    # Now create the note with both verified and forward relations
    content = f"""# Tokyo Neighborhood Guide

## Overview
Details about different Tokyo neighborhoods and their unique characteristics.

## Observations
- [area] Shibuya is a busy shopping district #shopping
- [transportation] Yamanote Line connects major neighborhoods #transit
- [recommendation] Visit Shimokitazawa for vintage shopping #unique
- [tip] Get a Suica card for easy train travel #convenience

{relations_section}
    """

    result = await write_note(title="Tokyo Neighborhood Guide", content=content, verbose=True)

    # You can check which relations were resolved and which are forward references
    if result and "relations" in result:
        resolved = [r["to_name"] for r in result["relations"] if r.get("target_id")]
        forward_refs = [r["to_name"] for r in result["relations"] if not r.get("target_id")]

        print(f"Resolved relations: {resolved}")
        print(f"Forward references that will be resolved later: {forward_refs}")
```

## Error Handling

Common issues to watch for:

1. **Missing Content**
   ```python
   try:
       content = await read_note("Document")
   except:
       # Try search instead
       results = await search_notes("Document")
       if results and results.primary_results:
           # Found something similar
           content = await read_note(results.primary_results[0].permalink)
   ```

2. **Forward References (Unresolved Relations)**
   ```python
   response = await write_note(..., verbose=True)
   # Check for forward references (unresolved relations)
   forward_refs = []
   for relation in response.get("relations", []):
       if not relation.get("target_id"):
           forward_refs.append(relation.get("to_name"))

   if forward_refs:
       # This is a feature, not an error! Inform the user about forward references
       print(f"Note created with forward references to: {forward_refs}")
       print("These will be automatically linked when those notes are created.")

       # Optionally suggest creating those entities now
       print("Would you like me to create any of these notes now to complete the connections?")
   ```

3. **Sync Issues**
   ```python
   # If information seems outdated
   activity = await recent_activity(timeframe="1 hour")
   if not activity or not activity.primary_results:
       print("It seems there haven't been recent updates. You might need to run 'basic-memory sync'.")
   ```

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
