"""Content tagging services — tag editing, keyword extraction, LLM suggestions.

Extracted verbatim from content_manager.py (lines 1487-1696, 1708-1893,
2007-2103) during Phase 1 of the 2.0 migration (ARCHITECTURE_2_0.md).
Pure move, no behavior changes. Legacy names: _edit_tags_operation,
_extract_content_tags, _suggest_tags_operation. Known quirk preserved:
suggest_tags is annotated -> dict but returns markdown strings on the
success paths, exactly as the original did; normalizing that is a
post-extraction change, not part of the pure move.
"""

import json

from loguru import logger

from advanced_memory.mcp.async_client import client
from advanced_memory.mcp.tools.utils import (
    build_error_response,
    build_success_response,
    call_get,
    call_put,
)
from advanced_memory.schemas import EntityResponse
from advanced_memory.utils import parse_tags

TagType = list[str] | str | None


async def edit_tags(
    active_project,
    identifier: str,
    tag_operation: str | None,
    tags: TagType,
) -> dict:
    """Handle edit_tags operation."""
    if not tag_operation:
        return build_error_response(
            error="Missing tag operation",
            error_code="MISSING_TAG_OPERATION",
            message="edit_tags operation requires tag_operation parameter",
            recovery_options=[
                "Specify tag_operation: 'add', 'remove', 'replace', or 'clear'",
                "Provide tags parameter with tag list",
                "Provide identifier to specify which note",
            ],
            urgency="medium",
        )

    # Get current note to read existing tags
    project_url = active_project.project_url
    url = f"{project_url}/knowledge/entities/{identifier}"

    response = await call_get(client, url)
    if response.status_code == 404:
        return build_error_response(
            error="Note not found",
            error_code="NOTE_NOT_FOUND",
            message=f"Could not find note '{identifier}'",
            recovery_options=[
                "Check spelling of note title",
                "Use permalink format (e.g., 'folder/note-title')",
                "Use adn_search to find available notes",
                "Use read_latest to get the most recent note",
            ],
            diagnostic_info={"identifier": identifier, "operation": "read"},
            alternative_solutions=[
                "Use adn_search('query') to find similar notes",
                "Use read_latest to get the most recent note",
                "Check if note was moved or deleted",
            ],
            urgency="medium",
        )

    current_entity = EntityResponse.model_validate(response.json())

    # Normalize current tags to a list[str]
    existing_tags_raw = (
        current_entity.entity_metadata.get("tags", []) if current_entity.entity_metadata else []
    )
    if isinstance(existing_tags_raw, str):
        # Try to parse string representation of list (e.g., "['tag1', 'tag2']")
        import ast

        try:
            parsed = ast.literal_eval(existing_tags_raw)
            if isinstance(parsed, list):
                current_tags = [str(tag) for tag in parsed]
            else:
                current_tags = [existing_tags_raw]
        except (ValueError, SyntaxError):
            # Not a list representation, treat as single tag
            current_tags = [existing_tags_raw]
    elif isinstance(existing_tags_raw, list):
        current_tags = [str(tag) for tag in existing_tags_raw]
    else:
        current_tags = []

    # Parse input tags (unless clear operation)
    if tag_operation != "clear":
        if tags is None and tag_operation != "clear":
            return build_error_response(
                error="Missing tags",
                error_code="MISSING_TAGS",
                message=f"'{tag_operation}' operation requires tags parameter",
                recovery_options=["Provide tags as string or list"],
            )

        new_tags = parse_tags(tags)

        if not new_tags and tag_operation != "clear":
            return build_error_response(
                error="No valid tags",
                error_code="NO_VALID_TAGS",
                message="No valid tags were provided after parsing",
                recovery_options=["Provide a comma-separated string or a list of tag names"],
                diagnostic_info={"provided_tags": tags},
            )
    else:
        new_tags = []

    # Perform the operation
    if tag_operation == "add":
        # Add tags (preserve existing, no duplicates)
        updated_tags = list(set(current_tags + new_tags))
        added_tags = [tag for tag in new_tags if tag not in current_tags]
        operation_summary = (
            f"Added {len(added_tags)} tag(s): {', '.join(added_tags)}"
            if added_tags
            else "No new tags added (all tags already exist)"
        )

    elif tag_operation == "remove":
        # Remove specific tags
        updated_tags = [tag for tag in current_tags if tag not in new_tags]
        removed_tags = [tag for tag in new_tags if tag in current_tags]
        operation_summary = (
            f"Removed {len(removed_tags)} tag(s): {', '.join(removed_tags)}"
            if removed_tags
            else "No tags removed (specified tags not found)"
        )

    elif tag_operation == "replace":
        # Replace all tags
        updated_tags = new_tags
        operation_summary = f"Replaced all tags with {len(new_tags)} new tag(s)"

    elif tag_operation == "clear":
        # Clear all tags
        updated_tags = []
        operation_summary = f"Cleared all {len(current_tags)} tag(s)"

    else:
        return build_error_response(
            error="Invalid tag operation",
            error_code="INVALID_TAG_OP",
            message=f"Unsupported tag operation: {tag_operation}",
            recovery_options=["Use: add, remove, replace, clear"],
        )

    # Update the entity with new tags
    metadata = current_entity.entity_metadata or {}
    metadata["tags"] = updated_tags

    # Fetch the existing note content so we don't overwrite it with None
    resource_url = f"{project_url}/resource/{current_entity.permalink}"
    resource_response = await call_get(client, resource_url)
    if resource_response.status_code != 200:
        return build_error_response(
            error="Content retrieval failed",
            error_code="CONTENT_FETCH_FAILED",
            message=f"Failed to retrieve current note content for '{identifier}'",
            recovery_options=[
                "Try again later",
                "Check note existence with read operation",
            ],
            diagnostic_info={"status_code": resource_response.status_code},
        )

    current_content = resource_response.text

    # Validate permalink exists
    if not current_entity.permalink:
        return build_error_response(
            error="Missing permalink",
            error_code="MISSING_PERMALINK",
            message=f"Entity '{identifier}' has no permalink",
            recovery_options=["Check if the note is correctly indexed"],
        )

    # Extract folder from permalink (everything except the last part)
    permalink_parts = current_entity.permalink.split("/")
    folder = "/".join(permalink_parts[:-1]) if len(permalink_parts) > 1 else ""

    update_url = f"{project_url}/knowledge/entities/{current_entity.permalink}"
    update_data = {
        "title": current_entity.title,
        "entity_type": current_entity.entity_type,
        "content_type": current_entity.content_type,
        "content": current_content,
        "folder": folder,
        "entity_metadata": metadata,
    }

    update_response = await call_put(client, update_url, json=update_data)
    result = EntityResponse.model_validate(update_response.json())

    # Format response
    response_lines = [
        "# Tag Edit Complete",
        "",
        f"**Project:** {active_project.name}",
        f"**Note:** {result.title}",
        f"**Permalink:** {result.permalink}",
        "",
        "## Operation",
        f"**Action:** {tag_operation}",
        f"**Summary:** {operation_summary}",
        "",
        "## Tags",
        f"**Before:** {', '.join(current_tags) if current_tags else '(no tags)'}",
        f"**After:** {', '.join(updated_tags) if updated_tags else '(no tags)'}",
        f"**Total tags:** {len(updated_tags)}",
    ]

    logger.info(
        f"MCP tool response: tool=adn_content operation=edit_tags tag_operation={tag_operation} identifier={identifier} tags_before={len(current_tags)} tags_after={len(updated_tags)}"
    )

    return build_success_response(
        "edit_tags",
        "\n".join(response_lines),
        note=result.title,
        permalink=result.permalink,
        tags_before=current_tags,
        tags_after=updated_tags,
    )


def extract_content_tags(content: str, title: str) -> list[str]:
    """Extract relevant tags from content and title using keyword extraction.

    Extracts:
    - All significant words from title (not just first)
    - Topics mentioned after "about", "on", "regarding", etc.
    - Common subject keywords (biology, science, technology, etc.)
    - Important nouns and concepts from content
    """
    import re

    # Combine title and content for analysis
    # Use string concatenation to avoid f-string parsing of JSON curly braces in content
    text = (title + " " + content).lower()
    title_lower = title.lower()

    # Common stop words to skip
    skip_words = {
        "the",
        "a",
        "an",
        "about",
        "notes",
        "note",
        "quick",
        "my",
        "on",
        "in",
        "at",
        "to",
        "for",
        "of",
        "with",
        "by",
        "from",
        "as",
        "is",
        "are",
        "was",
        "were",
        "be",
        "been",
        "being",
        "have",
        "has",
        "had",
        "do",
        "does",
        "did",
        "will",
        "would",
        "could",
        "should",
        "this",
        "that",
        "these",
        "those",
        "it",
        "its",
        "they",
        "them",
        "their",
        "make",
        "making",
        "current",
        "developments",
        "development",
        "and",
        "or",
        "but",
    }

    extracted_tags = []

    # Extract all significant words from title (not just first)
    title_words = re.findall(r"\b\w+\b", title_lower)
    for word in title_words:
        if word not in skip_words and len(word) > 2:
            # Convert to tag format (lowercase, hyphenated if needed)
            tag = word.lower().replace("_", "-")
            if tag not in extracted_tags:
                extracted_tags.append(tag)

    # Look for "about X" or "on X" patterns to extract topics
    about_patterns = [
        r"about\s+([a-z]+(?:\s+[a-z]+){0,3})",  # "about epstein scandal"
        r"on\s+([a-z]+(?:\s+[a-z]+){0,3})",  # "on current developments"
        r"regarding\s+([a-z]+(?:\s+[a-z]+){0,3})",  # "regarding X"
        r"concerning\s+([a-z]+(?:\s+[a-z]+){0,3})",  # "concerning X"
    ]

    for pattern in about_patterns:
        matches = re.findall(pattern, title_lower)
        for match in matches:
            # Extract individual words from the match
            words = match.split()
            for word in words:
                if word not in skip_words and len(word) > 2:
                    tag = word.lower().replace("_", "-")
                    if tag not in extracted_tags:
                        extracted_tags.append(tag)

    # Common subject/category keywords
    subject_keywords = {
        "biology": [
            "biology",
            "biological",
            "organism",
            "species",
            "animal",
            "plant",
            "insect",
            "butterfly",
            "caterpillar",
        ],
        "science": ["science", "scientific", "research", "study", "experiment"],
        "technology": [
            "technology",
            "tech",
            "software",
            "programming",
            "code",
            "computer",
        ],
        "history": ["history", "historical", "ancient", "medieval", "war", "battle"],
        "literature": ["literature", "book", "novel", "poetry", "author", "writing"],
        "art": ["art", "artistic", "painting", "drawing", "sculpture", "design"],
        "music": ["music", "musical", "song", "instrument", "composer"],
        "philosophy": ["philosophy", "philosophical", "ethics", "morality", "theory"],
        "psychology": [
            "psychology",
            "psychological",
            "mental",
            "behavior",
            "cognitive",
        ],
        "mathematics": [
            "mathematics",
            "math",
            "mathematical",
            "equation",
            "formula",
            "theorem",
        ],
        "politics": [
            "politics",
            "political",
            "government",
            "election",
            "scandal",
            "corruption",
        ],
        "news": ["news", "current", "developments", "breaking", "update"],
    }

    # Check for subject keywords
    for subject, keywords in subject_keywords.items():
        if any(keyword in text for keyword in keywords):
            if subject not in extracted_tags:
                extracted_tags.append(subject)

    # Special handling for common patterns
    if "butterflies" in text or "butterfly" in text:
        if "insects" not in extracted_tags and "insect" in text:
            extracted_tags.append("insects")
        if "biology" not in extracted_tags:
            extracted_tags.append("biology")

    if "insects" in text or "insect" in text:
        if "biology" not in extracted_tags:
            extracted_tags.append("biology")

    if "scandal" in text:
        if "politics" not in extracted_tags:
            extracted_tags.append("politics")
        if "news" not in extracted_tags and ("current" in text or "developments" in text):
            extracted_tags.append("news")

    # Look for other common patterns
    if "life cycle" in text or "metamorphosis" in text:
        if "biology" not in extracted_tags:
            extracted_tags.append("biology")

    return extracted_tags


async def suggest_tags(active_project, identifier: str) -> dict:
    """Suggest semantic tags for a note using LLM."""
    try:
        # Read the note first
        from advanced_memory.mcp.tools.read_note import read_note

        note_content = await (read_note.fn if hasattr(read_note, "fn") else read_note)(
            identifier=identifier, project=active_project.name
        )

        if not note_content or note_content.startswith("# Error"):
            return f"# Error\n\nCould not read note: {identifier}\n\n{note_content}"

        # Extract title and content
        lines = note_content.split("\n")
        title = lines[0].lstrip("#").strip() if lines else identifier
        content = "\n".join(lines[1:]) if len(lines) > 1 else note_content

        # Use LLM to suggest tags
        from advanced_memory.services.llm_client import get_llm_client

        llm = get_llm_client()

        system_prompt = """You are a semantic tagging assistant for a knowledge management system.

Analyze the note content and suggest relevant tags that:
1. Capture the main topics and themes
2. Include subject categories (e.g., biology, technology, history)
3. Include specific entities mentioned (people, places, concepts)
4. Include content type (tutorial, analysis, reference, etc.)
5. Are useful for search and organization

Respond with JSON array of tag strings (lowercase, hyphenated):
["tag1", "tag2", "tag3"]

Return 5-10 relevant tags."""

        prompt = f"""Note Title: {title}

Note Content:
{content[:2000]}

Suggest semantic tags for this note."""

        suggested_tags = await llm.generate_json(
            prompt, system_prompt, max_tokens=300, temperature=0.5
        )

        if isinstance(suggested_tags, list):
            tags_list = [str(tag).lower().replace(" ", "-") for tag in suggested_tags if tag]
        else:
            tags_list = []

        if not tags_list:
            return f"""# Tag Suggestions

**Note:** {identifier}

**Status:** No tags suggested

The LLM could not generate tag suggestions. Try using the current keyword-based tag extraction instead.
"""

        return f"""# Tag Suggestions

**Note:** {identifier}

**Suggested Tags:**
{", ".join(f"`{tag}`" for tag in tags_list)}

**To apply these tags:**
```python
adn_content("edit_tags",
    identifier="{identifier}",
    tag_operation="add",
    tags={json.dumps(tags_list)})
```

**Total:** {len(tags_list)} tags suggested
"""

    except Exception as e:
        logger.error(f"Tag suggestion error: {e}", exc_info=True)
        return build_error_response(
            error="LLM service unavailable",
            error_code="LLM_UNAVAILABLE",
            message="Could not generate tag suggestions",
            recovery_options=[
                "Configure an LLM provider using adn_llm('select_model', provider='ollama', model='llama3')",
                "Check LLM service is running (ollama serve, LMStudio, etc.)",
                "Try again if it's a temporary service issue",
            ],
            diagnostic_info={"error_details": str(e), "operation": "suggest_tags"},
            urgency="medium",
        )
