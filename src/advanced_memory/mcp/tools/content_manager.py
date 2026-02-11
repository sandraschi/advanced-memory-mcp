"""Content Manager portmanteau tool for Advanced Memory MCP server.

PORTMANTEAU PATTERN RATIONALE:
Consolidates 7 content operations into one tool to prevent tool explosion while maintaining full functionality.

Supported Operations:
- write: Create new notes with semantic processing and relations
- read: Retrieve complete note content with knowledge graph awareness
- read_latest: Get the most recently updated note in the project
- view: Display notes as formatted artifacts for better readability
- view_rendered: Display notes as HTML artifacts with rendered Mermaid diagrams
- edit: Perform targeted edits (append, prepend, find_replace, replace_section, insert_*)
- edit_tags: Edit tags (add, remove, replace, clear) without full note edits
- quick: Ultra-fast note creation with smart defaults (auto-folder, auto-title, auto-tags)
- daily: Create or append to today's daily journal note
- move: Relocate notes while preserving relationships and updating references
- delete: Remove notes from knowledge base with relationship cleanup
- suggest_tags: LLM-powered semantic tag suggestions for notes
- summarize: LLM-powered note summarization
- enhance: LLM-powered note enhancement (update_content, update_style, add_examples, add_context, expand_sections, add_bibliography)
- generate: LLM-powered content generation for new notes

Prerequisites:
- Active project session established via adn_project tool
- Write access to local filesystem for project storage

Args:
    operation (Literal, required): The content operation to perform. Must be one of:
        "write", "read", "read_latest", "view", "view_rendered", "edit", "edit_tags", "quick",
        "daily", "move", "delete", "suggest_tags", "summarize", "enhance", "generate".

    identifier (str | None): Note title, permalink, or memory:// URL. Required for:
        read, view, view_rendered, edit, edit_tags, move, delete, suggest_tags, summarize, enhance.

    content (str | None): Markdown content or edit payload. Required for:
        write, edit (some operations), quick, daily, generate.

    folder (str | None): Target folder path relative to project root. Default: "inbox".
        Used by: write, quick operations.

    tags (TagType | None): Tags for categorization. Used by: write, edit_tags operations.

    entity_type (str): Type of document. Default: "note". Used by: write operation.

    destination_path (str | None): New path for move operations. Required for: move.

    edit_operation (str | None): Edit type for edit operations. Required for: edit.

    tag_operation (str | None): Tag operation type. Required for: edit_tags.

    find_text (str | None): Text to search for in find_replace. Required when edit_operation="find_replace".

    new_string (str | None): Replacement text for find_replace. Required when edit_operation="find_replace".

    section (str | None): Section header for replace_section. Required when edit_operation="replace_section".

    expected_replacements (int): Expected matches for find_replace validation. Default: 1.

    use_regex (bool): Whether find_text is regex. Default: False.

    page (int): Pagination page. Default: 1.

    page_size (int): Items per page. Default: 10.

Returns:
    FastMCP 2.14.3 Conversational Response Structure:

    Success Response:
    - success (bool): True if operation succeeded
    - operation (str): Operation that was performed
    - summary (str): Conversational description of what happened
    - result (dict): Operation-specific return data
    - next_steps (list[str]): Suggested actions user can take next
    - context (dict): Additional contextual information
    - suggestions (list[str]): AI-friendly follow-up suggestions
    - follow_up_questions (list[str]): Questions to engage user in dialogue

    Error Recovery Response:
    - success (bool): Always false for errors
    - error (str): Detailed, conversational error description
    - error_code (str): Machine-readable error code
    - message (str): Human-friendly explanation with context
    - recovery_options (list[str]): Step-by-step recovery instructions
    - diagnostic_info (dict): Technical details for debugging
    - alternative_solutions (list[str]): Alternative approaches
    - estimated_resolution_time (str): Time estimate for resolution
    - urgency (str): Priority level (low/medium/high)

Examples:
    # Basic usage
    result = await adn_content("read", identifier="Meeting Notes")
    # Returns: {"success": true, "summary": "Retrieved note content", ...}

    # Error handling
    result = await adn_content("read", identifier="nonexistent")
    # Returns: {"success": false, "error": "Note not found", ...}

Errors:
    NO_ACTIVE_PROJECT: No active project session found
    MISSING_IDENTIFIER: Required identifier parameter not provided
    MISSING_CONTENT: Required content parameter not provided
    NOTE_NOT_FOUND: Specified note does not exist in project
    PERMISSION_DENIED: No write access to project directory
    INVALID_OPERATION: Specified operation is not supported
"""

import json
import re
from typing import Literal

from loguru import logger

from advanced_memory.mcp.async_client import client
from advanced_memory.mcp.mcp_instance import mcp
from advanced_memory.mcp.project_session import get_active_project
from advanced_memory.mcp.tools.utils import call_get, call_put
from advanced_memory.schemas import EntityResponse
from advanced_memory.schemas.base import Entity
from advanced_memory.schemas.memory import GraphContext
from advanced_memory.utils import parse_tags, validate_project_path

# Define TagType as a Union that can accept either a string or a list of strings or None
TagType = list[str] | str | None


# FastMCP 2.14.3 Conversational Response Builders
def build_success_response(operation: str, summary: str, **kwargs) -> dict:
    """Build structured success response for MCP clients."""
    return {"success": True, "operation": operation, "summary": summary, **kwargs}


def build_error_response(error: str, error_code: str, message: str, **kwargs) -> dict:
    """Build structured error response with recovery guidance for MCP clients."""
    return {
        "success": False,
        "error": error,
        "error_code": error_code,
        "message": message,
        **kwargs,
    }


@mcp.tool
async def adn_content(
    operation: Literal[
        "write",
        "read",
        "read_latest",
        "view",
        "view_rendered",
        "edit",
        "edit_tags",
        "quick",
        "daily",
        "move",
        "delete",
        "suggest_tags",
        "summarize",
        "enhance",
        "generate",
        "find_runts",
        "find_junk",
    ],
    identifier: str | None = None,
    content: str | None = None,
    folder: str | None = None,
    tags: TagType | None = None,
    entity_type: str = "note",
    destination_path: str | None = None,
    edit_operation: Literal[
        "append",
        "prepend",
        "find_replace",
        "replace_section",
        "insert_mermaid",
        "insert_ascii_art",
        "insert_kilroy",
        "insert_kanban",
        "insert_changelog",
    ]
    | None = None,
    tag_operation: Literal["add", "remove", "replace", "clear"] | None = None,
    find_text: str | None = None,
    expected_replacements: int = 1,
    use_regex: bool = False,
    section: str | None = None,
    page: int = 1,
    page_size: int = 10,
    results_per_page: int
    | None = None,  # Alias for page_size (compatibility with standalone search_notes)
    project: str | None = None,
    # Enhance operation options (batch-upgrade weak-LLM notes with SOTA LLM)
    update_content: bool = True,  # Fix typos, factual errors, biographical updates (death dates)
    update_style: bool = True,  # Improve clarity, structure, readability
    add_bibliography: bool = False,  # Add references/sources section if applicable
    add_examples: bool = False,  # Add concrete examples, illustrations
    add_context: bool = False,  # Add background, definitions, "why it matters"
    expand_sections: bool = False,  # Turn bullet points into full paragraphs
    update_stale_tech: bool = False,  # Update outdated lib/tool versions; flag uncertainty
    # find_runts / find_junk (adn_knowledge_bulk delegates)
    max_content_length: int = 500,  # find_runts: notes under this char count
    assessment_format: Literal["narrative", "structured"] = "narrative",  # find_junk output
    # Parameter aliases for common mistakes (deprecated, will map to content)
    new_string: str | None = None,  # DEPRECATED: Use 'content' instead
    replacement: str | None = None,  # DEPRECATED: Use 'content' instead (for find_replace)
    new_content: str | None = None,  # DEPRECATED: Use 'content' instead
) -> dict:
    """
    Knowledge content management with conversational responses.

    OPERATIONS:
    - write: Create/update notes (requires: identifier, content)
    - read: Get note content (requires: identifier)
    - view: Display formatted note (requires: identifier)
    - edit: Modify existing notes (requires: identifier, edit_operation)
    - quick: Fast note creation (requires: content)
    - daily: Add to today's journal (requires: content)
    - delete: Remove notes (requires: identifier)

    RESPONSES:
    Success: {"success": true, "operation": "...", "summary": "...", "result": {...}}
    Error: {"success": false, "error": "...", "message": "...", "recovery_options": [...]}

    For errors, check recovery_options for next steps. Use adn_project first to set context.
    """
    # Parameter aliasing for compatibility with standalone tools
    # results_per_page -> page_size (for compatibility with search_notes tool)
    if results_per_page is not None and page_size == 10:  # Only if default value
        page_size = results_per_page
        logger.debug(f"Using 'results_per_page' alias as page_size: {page_size}")

    # Parameter aliasing for common mistakes: map deprecated parameter names to 'content'
    # This prevents errors when AI agents use wrong parameter names
    content_aliases = {
        "new_string": new_string,
        "replacement": replacement,
        "new_content": new_content,
    }

    # Map aliases to content if content is not set but alias is
    for alias_name, alias_value in content_aliases.items():
        if alias_value is not None and content is None:
            content = alias_value
            logger.warning(
                f"Parameter '{alias_name}' is deprecated. Use 'content' instead. "
                f"Automatically mapped for this call."
            )
            # Log for analytics
            logger.info(
                "adn_content_parameter_alias_used",
                alias=alias_name,
                operation=operation,
                edit_operation=edit_operation,
            )

    logger.info(f"MCP tool call tool=adn_content operation={operation} identifier={identifier}")

    original_operation = operation
    normalized_operation = re.sub(r"(?<!^)(?=[A-Z])", "_", operation)
    normalized_operation = normalized_operation.replace("-", "_").replace(" ", "_").lower()
    alias_map: dict[
        str,
        Literal[
            "write",
            "read",
            "read_latest",
            "view",
            "view_rendered",
            "edit",
            "edit_tags",
            "quick",
            "daily",
            "move",
            "delete",
        ],
    ] = {
        "createnote": "write",
        "newnote": "write",
        "appendnote": "edit",
        "modifytags": "edit_tags",
        "readnote": "read",
        "readlatest": "read_latest",
        "latest": "read_latest",
        "last": "read_latest",
        "lastnote": "read_latest",
        "latestnote": "read_latest",
        "showlatest": "read_latest",
        "viewnote": "view",
        "previewnote": "view",
        "viewlatest": "view",
        "previewlatest": "view",
    }
    # Type-safe operation mapping with fallback to original
    mapped_operation = alias_map.get(normalized_operation)
    if mapped_operation:
        operation = mapped_operation  # type: ignore[assignment]

    # Get the active project
    active_project = get_active_project(project)
    if not active_project:
        return build_error_response(
            error="No active project context",
            error_code="NO_ACTIVE_PROJECT",
            message="You need an active project to work with notes",
            recovery_options=[
                "Use adn_project('list') to see available projects",
                "Use adn_project('switch', project_name='your-project') to switch projects",
                "Use adn_project('create', project_name='new-project', project_path='/path') to create one",
            ],
            urgency="high",
        )

    # Route to appropriate operation handler
    if operation == "write":
        missing = []
        if not identifier:
            missing.append("identifier (note title)")
        if not content:
            missing.append("content")
        if missing:
            error_msg = f"""# Error: Missing Required Parameters

The `write` operation requires the following parameters:
- **identifier** (note title): The title of the note
- **content**: The markdown content of the note
- **folder** (optional): The folder path where the note should be saved (defaults to "inbox" if not specified)

**Missing parameters:** {", ".join(missing)}

**Example usage:**
```python
# With folder specified
adn_content("write",
    identifier="My Note Title",
    content="# My Note\\n\\nContent here...",
    folder="notes")

# Without folder (defaults to "inbox")
adn_content("write",
    identifier="My Note Title",
    content="# My Note\\n\\nContent here...")
```

**Alternative: Quick Note Creation**
If you just want to quickly capture content without specifying title and folder, use the `quick` operation instead:
```python
adn_content("quick", content="Your content here...")
```
The `quick` operation automatically:
- Generates a title from your content
- Saves to the "inbox" folder
- Adds timestamp and "quick-capture" tag
"""
            return error_msg
        # Use default folder if not specified
        if not folder:
            folder = "inbox"
        # Type narrowing: we've validated these are not None above
        assert identifier is not None
        assert content is not None
        assert folder is not None
        return await _write_operation(
            active_project, identifier, content, folder, tags, entity_type
        )

    elif operation == "read":
        latest_aliases = {
            "",
            "latest",
            "last",
            "__latest__",
            "latest_note",
            "last_note",
        }
        identifier_key = (identifier or "").strip().lower().replace(" ", "_")

        if not identifier or identifier_key in latest_aliases:
            logger.info(
                "adn_content_auto_read_latest",
                original_operation=original_operation,
                identifier=identifier,
            )
            return await _read_latest_operation(active_project)

        return await _read_operation(active_project, identifier, page, page_size)

    elif operation == "read_latest":
        # Get and read the single most recent note (regardless of date)
        return await _read_latest_operation(active_project)

    elif operation == "view":
        latest_aliases = {
            "",
            "latest",
            "last",
            "__latest__",
            "latest_note",
            "last_note",
        }
        identifier_key = (identifier or "").strip().lower().replace(" ", "_")

        if not identifier or identifier_key in latest_aliases:
            latest_identifier, error_message = await _get_latest_identifier(active_project)
            if not latest_identifier:
                return error_message or "# No Recent Activity\n\nNo notes found to display."
            identifier = latest_identifier

        return await _view_operation(active_project, identifier)

    elif operation == "view_rendered":
        latest_aliases = {
            "",
            "latest",
            "last",
            "__latest__",
            "latest_note",
            "last_note",
        }
        identifier_key = (identifier or "").strip().lower().replace(" ", "_")

        if not identifier or identifier_key in latest_aliases:
            latest_identifier, error_message = await _get_latest_identifier(active_project)
            if not latest_identifier:
                return error_message or "# No Recent Activity\n\nNo notes found to display."
            identifier = latest_identifier

        return await _view_rendered_operation(active_project, identifier)

    elif operation == "edit":
        if identifier is None:
            return '# Error\n\nEdit operation requires: identifier parameter\n\n**Example:**\n```python\nadn_content("edit",\n    identifier="My Note",\n    edit_operation="append",\n    content="\\n## New Section")\n```'
        if not edit_operation:
            return '# Error\n\nEdit operation requires: edit_operation parameter\n\n**Valid operations:** append, prepend, find_replace, replace_section\n\n**Example:**\n```python\nadn_content("edit",\n    identifier="My Note",\n    edit_operation="append",\n    content="New content")\n```'

        # Check for find_replace specific requirements
        if edit_operation == "find_replace":
            if not find_text:
                return """# Error: Missing Required Parameter for find_replace

The `find_replace` operation requires:
- `find_text`: The text to find (REQUIRED)
- `content`: The replacement text (REQUIRED)

**Common mistakes:**
- Using `new_string` instead of `content` [ERROR]
- Using `replacement` instead of `content` [ERROR]

**Correct usage:**
```python
adn_content("edit",
    identifier="My Note",
    edit_operation="find_replace",
    find_text="old text",
    content="new text"  # [SUCCESS] Use 'content', not 'new_string'
)
```

**Note:** If you used `new_string`, `replacement`, or `new_content`, these are now automatically mapped to `content`.
However, please use `content` directly in future calls.
"""
            if not content:
                return """# Error: Missing Required Parameter for find_replace

The `find_replace` operation requires:
- `find_text`: The text to find (REQUIRED) [PROVIDED] You provided this
- `content`: The replacement text (REQUIRED) [MISSING] Missing

**Common mistakes:**
- Using `new_string` instead of `content` [ERROR]
- Using `replacement` instead of `content` ❌

**Correct usage:**
```python
adn_content("edit",
    identifier="My Note",
    edit_operation="find_replace",
    find_text="old text",
    content="new text"  # [SUCCESS] Use 'content', not 'new_string'
)
```

**Note:** If you used `new_string`, `replacement`, or `new_content`, these are now automatically mapped to `content`.
However, please use `content` directly in future calls.
"""

        if not content and edit_operation in ["append", "prepend", "replace_section"]:
            return f"""# Error: Missing Required Parameter

Edit operation '{edit_operation}' requires: `content` parameter

**Common mistakes:**
- Using `new_string` instead of `content` [ERROR]
- Using `replacement` instead of `content` ❌

**Correct usage:**
```python
adn_content("edit",
    identifier="My Note",
    edit_operation="{edit_operation}",
    content="Content to {edit_operation}"  # [SUCCESS] Use 'content', not 'new_string'
)
```

**Note:** If you used `new_string`, `replacement`, or `new_content`, these are now automatically mapped to `content`.
However, please use `content` directly in future calls.
"""
        return await _edit_operation(
            active_project,
            identifier,
            edit_operation,
            content,
            section,
            find_text,
            expected_replacements,
            use_regex,
        )

    elif operation == "edit_tags":
        if identifier is None:
            return '# Error\n\nEdit_tags operation requires: identifier parameter\n\n**Example:**\n```python\nadn_content("edit_tags",\n    identifier="My Note",\n    tag_operation="add",\n    tags="tag1, tag2")\n```'
        if not tag_operation:
            return '# Error\n\nEdit_tags operation requires: tag_operation parameter\n\n**Valid operations:** add, remove, replace, clear\n\n**Example:**\n```python\nadn_content("edit_tags",\n    identifier="My Note",\n    tag_operation="add",\n    tags="important")\n```'
        return await _edit_tags_operation(active_project, identifier, tag_operation, tags)

    elif operation == "quick":
        if not content:
            return """# Error: Missing Required Parameter

The `quick` operation requires the `content` parameter.

**Example usage:**
```python
adn_content("quick", content="Your note content here...")
```

The `quick` operation automatically:
- Generates a title from your content (first line or first few words)
- Saves to the "inbox" folder
- Extracts relevant tags from content (e.g., "butterflies" -> adds "butterflies", "biology", "insects")
- Adds timestamp and "quick-capture" tag
- Perfect for quick note capture without specifying all details

**Important: Include Appropriate Tags**
While the `quick` operation auto-extracts some tags from content, you should **always include relevant tags** that match your content for better organization and searchability:

```python
# Good: Include relevant tags
adn_content("quick",
    content="# Butterflies\\n\\nButterflies are insects...",
    tags="butterflies, biology, insects, nature")

# Also good: Let auto-extraction work, but you can add more
adn_content("quick",
    content="# Python Tutorial\\n\\nLearn Python basics...",
    tags="python, programming, tutorial")
```

**Alternative: Full Note Creation**
If you need to specify title and folder explicitly, use the `write` operation:
```python
adn_content("write",
    identifier="My Note Title",
    content="# My Note\\n\\nContent here...",
    folder="notes")
```
"""
        return await _quick_capture_operation(active_project, content, tags)

    elif operation == "daily":
        if not content:
            return build_error_response(
                error="Missing content for daily note",
                error_code="MISSING_CONTENT",
                message="Daily operation requires content parameter",
                recovery_options=[
                    "Provide content parameter with your daily note text",
                    "Use quick operation if you want auto-generated title",
                ],
                urgency="medium",
            )
        return await _daily_note_operation(active_project, content, tags)

    elif operation == "dictate" or operation == "speak":
        return f"""# Audio Operations Moved

The '{operation}' operation has been moved to the adn_audio tool for better separation of concerns.

**New Usage**:
- For dictate: adn_audio("dictate", audio_path="recording.mp3", tags=["voice"])
- For speak: adn_audio("speak", identifier="Note Title", speed=1.5)

**Why the change**:
Audio operations require heavy optional dependencies (Whisper, pyttsx3) and are better
separated from core content operations.

**Install voice dependencies** (if needed):
pip install advanced-memory[voice]
"""

    elif operation == "move":
        if identifier is None or destination_path is None:
            return build_error_response(
                error="Missing move parameters",
                error_code="MISSING_MOVE_PARAMS",
                message="Move operation requires both identifier and destination_path",
                recovery_options=[
                    "Specify identifier (note title or permalink)",
                    "Specify destination_path (new folder location)",
                    "Use read operation first to verify note exists",
                ],
                urgency="medium",
            )
        return await _move_operation(active_project, identifier, destination_path)
    elif operation == "delete":
        if identifier is None:
            return build_error_response(
                error="Missing identifier for delete",
                error_code="MISSING_IDENTIFIER",
                message="Delete operation requires identifier parameter",
                recovery_options=[
                    "Provide note title, permalink, or memory:// URL",
                    "Use read operation first to verify note exists",
                ],
                urgency="medium",
            )
        return await _delete_operation(active_project, identifier)

    elif operation == "suggest_tags":
        if identifier is None:
            return '# Error\n\nSuggest_tags operation requires: identifier parameter\n\n**Example:**\n```python\nadn_content("suggest_tags", identifier="My Note")\n```'
        return await _suggest_tags_operation(active_project, identifier)

    elif operation == "summarize":
        if identifier is None:
            return '# Error\n\nSummarize operation requires: identifier parameter\n\n**Example:**\n```python\nadn_content("summarize", identifier="My Note")\n```'
        return await _summarize_operation(active_project, identifier)

    elif operation == "enhance":
        if identifier is None:
            return '# Error\n\nEnhance operation requires: identifier parameter\n\n**Example:**\n```python\nadn_content("enhance", identifier="My Note")\n```'
        return await _enhance_operation(
            active_project,
            identifier,
            content,
            update_content,
            update_style,
            add_bibliography,
            add_examples,
            add_context,
            expand_sections,
            update_stale_tech,
        )

    elif operation == "generate":
        if not content:
            return '# Error\n\nGenerate operation requires: content parameter (topic/prompt)\n\n**Example:**\n```python\nadn_content("generate", content="Python functions tutorial", folder="tutorials")\n```'
        return await _generate_operation(active_project, content, folder, tags, entity_type)

    elif operation == "find_runts":
        from advanced_memory.mcp.tools.knowledge_operations import _handle_find_runts

        filters = {"max_content_length": max_content_length}
        if folder:
            filters["folder"] = folder
        result = await _handle_find_runts(filters, 50, project)
        return build_success_response(
            "find_runts", result, content=result, max_content_length=max_content_length
        )

    elif operation == "find_junk":
        from advanced_memory.mcp.tools.knowledge_operations import _handle_find_junk

        filters = {}
        if folder:
            filters["folder"] = folder
        action = {"format": assessment_format}
        result = await _handle_find_junk(filters, action, 20, project)
        return build_success_response("find_junk", result, content=result, format=assessment_format)

    else:
        return build_error_response(
            error="Invalid operation",
            error_code="INVALID_OPERATION",
            message=f"Operation '{operation}' is not supported",
            recovery_options=[
                "Use supported operations: write, read, view, view_rendered, edit, edit_tags, quick, daily, move, delete, suggest_tags, summarize, enhance, generate, find_runts, find_junk",
                "For audio operations (dictate, speak), use the adn_audio tool instead",
                "Check operation spelling and try again",
            ],
            diagnostic_info={
                "provided_operation": operation,
                "supported_operations": [
                    "write",
                    "read",
                    "view",
                    "view_rendered",
                    "edit",
                    "edit_tags",
                    "quick",
                    "daily",
                    "move",
                    "delete",
                    "suggest_tags",
                    "summarize",
                    "enhance",
                    "generate",
                ],
            },
            urgency="low",
        )


async def _write_operation(
    active_project,
    identifier: str,
    content: str,
    folder: str,
    tags: TagType,
    entity_type: str,
) -> str:
    """Handle write operation with auto-skill detection."""
    if not identifier or not content or not folder:
        return build_error_response(
            error="Missing write parameters",
            error_code="MISSING_WRITE_PARAMS",
            message="Write operation requires identifier and content",
            recovery_options=[
                "Provide identifier (note title)",
                "Provide content (markdown text)",
                "Use folder parameter to specify location (optional, defaults to inbox)",
            ],
            urgency="medium",
        )

    # Validate folder path to prevent path traversal attacks
    project_path = active_project.home
    if folder and not validate_project_path(folder, project_path):
        logger.warning(
            "Attempted path traversal attack blocked",
            folder=folder,
            project=active_project.name,
        )
        return build_error_response(
            error="Invalid folder path",
            error_code="INVALID_PATH",
            message=f"Folder path '{folder}' is not allowed",
            recovery_options=[
                "Use relative paths within project boundaries",
                "Avoid '..' or absolute paths",
                "Default folder is 'inbox' if not specified",
            ],
            diagnostic_info={"folder": folder, "project_path": str(project_path)},
            urgency="medium",
        )

    # AUTO-DETECT SKILLS: If writing to skills/ folder, ensure proper frontmatter
    from advanced_memory.mcp.tools.skill_helpers import (
        detect_skill_path,
        generate_skill_frontmatter,
        parse_skill_frontmatter,
        title_to_skill_name,
    )

    if detect_skill_path(folder):
        logger.info(
            f"Detected skills folder: {folder}. Auto-generating skill frontmatter if needed."
        )

        # Check if content already has frontmatter
        fm, body, errors = parse_skill_frontmatter(content)

        if fm is None:
            # No frontmatter found - auto-generate it
            logger.info("No frontmatter detected. Auto-generating Claude Skills frontmatter.")

            # Extract metadata from tags if present
            tag_list = parse_tags(tags) if tags else []
            category = None
            difficulty = None

            # Try to extract category from folder path (skills/developer -> developer)
            if "/" in folder:
                parts = folder.split("/")
                if len(parts) >= 2:
                    category = parts[1]

            # Generate skill name from title
            skill_name = title_to_skill_name(identifier)

            # Create description (use first paragraph from body if available)
            description = f"Expert guidance for {identifier}. Use when working with {identifier.lower()} or related topics."

            # Generate frontmatter
            try:
                frontmatter_yaml = generate_skill_frontmatter(
                    name=skill_name,
                    description=description,
                    category=category,
                    difficulty=difficulty,
                )

                # Prepend frontmatter to content
                content = frontmatter_yaml + "\n" + content

                logger.info(f"Auto-generated skill frontmatter for '{skill_name}'")

            except Exception as e:
                logger.warning(f"Failed to auto-generate skill frontmatter: {e}")
                # Continue without frontmatter - will be caught by validation later

        # Ensure entity_type is 'skill' when writing to skills/ folder
        if entity_type == "note":
            entity_type = "skill"
            logger.info("Changed entity_type from 'note' to 'skill' for skills folder")

    # Process tags using the helper function
    tag_list = parse_tags(tags)

    # Create the entity request
    metadata = {"tags": tag_list} if tag_list else None
    entity = Entity(
        title=identifier,
        folder=folder,
        entity_type=entity_type,
        content_type="text/markdown",
        content=content,
        entity_metadata=metadata,
    )
    project_url = active_project.project_url

    # Create or update via knowledge API
    try:
        logger.debug(f"Creating entity via API permalink={entity.permalink}")
        url = f"{project_url}/knowledge/entities/{entity.permalink}"
        response = await call_put(client, url, json=entity.model_dump())

        if response.status_code not in (200, 201):
            return f"""# Error: Failed to Create/Update Note

The API request failed with status code {response.status_code}.

**Details:**
- **Title:** {identifier}
- **Folder:** {folder}
- **URL:** {url}

**Possible causes:**
- Project not found or not accessible
- Invalid folder path
- Network connectivity issue
- Server error

**Response:** {response.text[:200] if hasattr(response, "text") else "No response text"}
"""

        result = EntityResponse.model_validate(response.json())

        # Format semantic summary based on status code
        action = "Created" if response.status_code == 201 else "Updated"
        summary = [
            f"# {action} note",
            f"project: {active_project.name}",
            f"file_path: {result.file_path}",
            f"permalink: {result.permalink}",
            f"checksum: {result.checksum[:8] if result.checksum else 'unknown'}",
        ]

        # Count observations by category
        categories: dict[str, int] = {}
        if result.observations:
            for obs in result.observations:
                if obs.category:  # Only count observations with categories
                    categories[obs.category] = categories.get(obs.category, 0) + 1

            summary.append("\n## Observations")
            for category, count in sorted(categories.items()):
                summary.append(f"- {category}: {count}")

        # Count resolved/unresolved relations
        unresolved = 0
        resolved = 0
        if result.relations:
            unresolved = sum(1 for r in result.relations if not r.to_id)
            resolved = len(result.relations) - unresolved

            summary.append("\n## Relations")
            summary.append(f"- Resolved: {resolved}")
            if unresolved:
                summary.append(f"- Unresolved: {unresolved}")
                summary.append(
                    "\nNote: Unresolved relations point to entities that don't exist yet."
                )
                summary.append(
                    "They will be automatically resolved when target entities are created or during sync operations."
                )

        if tag_list:
            summary.append(f"\n## Tags\n- {', '.join(tag_list)}")

        logger.info(
            f"MCP tool response: tool=content_manager operation=write action={action} permalink={result.permalink} observations_count={len(result.observations)} relations_count={len(result.relations)} resolved_relations={resolved} unresolved_relations={unresolved} status_code={response.status_code}"
        )
        return build_success_response(
            operation="write",
            summary=f"Note '{identifier}' {'created' if action == 'created' else 'updated'} successfully",
            result={
                "title": identifier,
                "permalink": result.permalink,
                "folder": folder,
                "observations_count": len(result.observations),
                "relations_count": len(result.relations),
                "resolved_relations": resolved,
                "unresolved_relations": unresolved,
                "tags": tag_list,
            },
            next_steps=[
                "Read the note to verify content"
                if action == "created"
                else "Review the updated content",
                "Add related notes or concepts",
                "Consider enhancing with AI suggestions",
            ],
        )
    except Exception as e:
        logger.error(f"Error creating/updating note: {e}", exc_info=True)
        return build_error_response(
            error="Failed to create/update note",
            error_code="WRITE_FAILED",
            message=f"Could not create or update note '{identifier}'",
            recovery_options=[
                "Check project is active with adn_project('list')",
                "Verify folder path is valid and within project boundaries",
                "Try again if it was a temporary network issue",
                "Check server logs for detailed error information",
            ],
            diagnostic_info={
                "title": identifier,
                "folder": folder,
                "error_details": str(e),
                "project": active_project.name if active_project else None,
            },
            urgency="medium",
        )


async def _read_operation(active_project, identifier: str, page: int, page_size: int) -> dict:
    """Handle read operation."""
    if not identifier:
        return build_error_response(
            error="Missing identifier for read",
            error_code="MISSING_IDENTIFIER",
            message="Read operation requires identifier parameter",
            recovery_options=[
                "Provide note title, permalink, or memory:// URL",
                "Use adn_search to find available notes",
                "Use read_latest to get the most recent note",
            ],
            urgency="medium",
        )

    # Delegate to read_note tool
    from advanced_memory.mcp.tools.read_note import read_note

    return await read_note.fn(
        identifier=identifier,
        page=page,
        page_size=page_size,
        project=active_project.name,
    )


async def _get_latest_identifier(active_project) -> tuple[str | None, str | None]:
    from loguru import logger

    try:
        from advanced_memory.mcp.tools.recent_activity import recent_activity

        raw_context = await recent_activity.fn(
            type_filter=["entity", "observation"],
            depth=1,
            timeframe="365d",
            page=1,
            page_size=1,
            max_related=0,
            project=active_project.name,
        )

        if isinstance(raw_context, GraphContext):
            result = raw_context
        else:
            result = GraphContext.model_validate(raw_context)

    except Exception as exc:  # pragma: no cover
        logger.error("adn_content_latest_identifier_error", exc_info=True)
        return None, (
            "# Error\n\n"
            "Unable to load recent activity to determine the latest note.\n"
            f"Details: {exc}"
        )

    context_results = getattr(result, "results", [])
    if not context_results:
        return None, "# No Recent Activity\n\nNo notes found in the past year."

    ctx_result = context_results[0]
    if getattr(ctx_result, "primary_result", None):
        item = ctx_result.primary_result
    elif getattr(ctx_result, "observations", None):
        item = ctx_result.observations[0]
    else:
        item = ctx_result

    identifier = getattr(item, "permalink", None) or getattr(item, "file_path", None)
    if not identifier:
        return None, (
            "# Error\n\n"
            "Could not determine identifier for most recent note.\n"
            f"Item attributes: {dir(item)}"
        )

    logger.debug(f"Extracted latest identifier: {identifier}")
    return identifier, None


async def _read_latest_operation(active_project) -> dict:
    """Handle read_latest operation - read the single most recent note."""
    identifier, error_message = await _get_latest_identifier(active_project)
    if not identifier:
        return error_message or "# No Recent Activity\n\nNo notes found in the past year."

    from advanced_memory.mcp.tools.read_note import read_note

    return await read_note.fn(identifier=identifier, project=active_project.name)


async def _view_operation(active_project, identifier: str) -> dict:
    """Handle view operation."""
    from advanced_memory.mcp.tools.view_note import view_note

    return await view_note.fn(identifier=identifier, project=active_project.name)


async def _view_rendered_operation(active_project, identifier: str) -> dict:
    """Handle view_rendered operation."""
    from advanced_memory.mcp.tools.view_note_rendered import view_note_rendered

    return await view_note_rendered.fn(identifier=identifier, project=active_project.name)


async def _edit_operation(
    active_project,
    identifier: str,
    edit_operation: str | None,
    content: str | None,
    section: str | None,
    find_text: str | None,
    expected_replacements: int,
    use_regex: bool,
) -> str:
    """Handle edit operation."""
    from advanced_memory.mcp.tools.edit_note import edit_note

    return await edit_note.fn(
        identifier=identifier,
        operation=edit_operation or "replace",
        content=content or "",
        section=section,
        find_text=find_text,
        expected_replacements=expected_replacements,
        use_regex=use_regex,
        project=active_project.name,
    )


async def _edit_tags_operation(
    active_project,
    identifier: str,
    tag_operation: str | None,
    tags: TagType,
) -> str:
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
            return f"# Error\n\n'{tag_operation}' operation requires tags parameter.\n\nProvide tags as string or list."

        new_tags = parse_tags(tags)

        if not new_tags and tag_operation != "clear":
            return f"# Error\n\nNo valid tags provided.\n\nTags: {tags}"
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
        return f"# Error\n\nInvalid tag_operation: {tag_operation}\n\nSupported: add, remove, replace, clear"

    # Update the entity with new tags
    metadata = current_entity.entity_metadata or {}
    metadata["tags"] = updated_tags

    # Fetch the existing note content so we don't overwrite it with None
    resource_url = f"{project_url}/resource/{current_entity.permalink}"
    resource_response = await call_get(client, resource_url)
    if resource_response.status_code != 200:
        return (
            "# Error\n\n"
            f"Failed to retrieve current note content for '{identifier}'.\n"
            "Tag update aborted to avoid overwriting content.\n"
            f"Details: HTTP {resource_response.status_code}"
        )

    current_content = resource_response.text

    # Validate permalink exists
    if not current_entity.permalink:
        return (
            "# Error\n\n"
            f"Entity '{identifier}' has no permalink.\n"
            "Cannot update tags without a valid permalink.\n"
            "This may indicate a corrupted entity in the database."
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

    return "\n".join(response_lines)


async def _move_operation(active_project, identifier: str, destination_path: str) -> dict:
    """Handle move operation."""
    from advanced_memory.mcp.tools.move_note import move_note

    return await move_note.fn(
        identifier=identifier,
        destination_path=destination_path,
        project=active_project.name,
    )


def _extract_content_tags(content: str, title: str) -> list[str]:
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


async def _quick_capture_operation(active_project, content: str, tags: TagType) -> dict:
    """Handle quick capture operation - ultra-fast note creation with smart defaults."""
    from datetime import datetime

    # Generate smart title from content (first line or timestamp)
    content_lines = content.strip().split("\n")
    first_line = content_lines[0].strip()

    # If first line is a heading, use it as title
    if first_line.startswith("#"):
        title = first_line.lstrip("#").strip()
        # Remove the heading from content since we're using it as title
        content = "\n".join(content_lines[1:]).strip()
    else:
        # Use first few words as title
        words = first_line.split()[:6]
        title = " ".join(words)
        if len(first_line.split()) > 6:
            title += "..."

    # Auto-select folder (inbox or quick-notes)
    folder = "inbox"

    # Start with user-provided tags
    tag_list = parse_tags(tags) if tags else []

    # Auto-extract relevant tags from content
    extracted_tags = _extract_content_tags(content, title)
    for tag in extracted_tags:
        if tag not in tag_list:
            tag_list.append(tag)

    # Always add quick-capture and date tags
    tag_list.append("quick-capture")
    tag_list.append(datetime.now().strftime("%Y-%m-%d"))

    # Add timestamp to content
    # Use string concatenation to avoid f-string parsing of JSON curly braces in content
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    formatted_content = f"# {title}\n\n**Captured:** {timestamp}\n\n" + content

    # Create the note
    return await _write_operation(
        active_project, title, formatted_content, folder, tag_list, "note"
    )


async def _daily_note_operation(active_project, content: str, tags: TagType) -> dict:
    """Handle daily note operation - create or append to today's journal."""
    from datetime import datetime

    from advanced_memory.mcp.tools.edit_note import edit_note

    # Generate today's date-based title and folder
    today = datetime.now()
    title = today.strftime("%Y-%m-%d")
    folder = "journal"

    # Auto-add daily tag
    tag_list = parse_tags(tags) if tags else []
    tag_list.extend(["daily", "journal", today.strftime("%Y"), today.strftime("%Y-%m")])

    # Try to read existing daily note
    from advanced_memory.mcp.tools.read_note import read_note

    existing_note = await read_note.fn(
        identifier=f"{folder}/{title}",
        page=1,
        page_size=1000,
        project=active_project.name,
    )

    # Check if note exists (not an error message)
    if "# Note Not Found:" in existing_note:
        # Create new daily note
        # Use string concatenation to avoid f-string parsing of JSON curly braces in content
        timestamp = today.strftime("%H:%M")
        formatted_content = f"# Daily Note: {title}\n\n## {timestamp}\n\n" + content + "\n\n---\n\n"
        return await _write_operation(
            active_project, title, formatted_content, folder, tag_list, "note"
        )
    else:
        # Append to existing daily note
        # Use string concatenation to avoid f-string parsing of JSON curly braces in content
        timestamp = today.strftime("%H:%M")
        append_content = f"\n\n## {timestamp}\n\n" + content + "\n\n---\n"
        return await edit_note.fn(
            identifier=f"{folder}/{title}",
            operation="append",
            content=append_content,
            project=active_project.name,
        )


async def _delete_operation(active_project, identifier: str) -> dict:
    """Handle delete operation."""
    from advanced_memory.mcp.tools.delete_note import delete_note

    result = await delete_note.fn(identifier=identifier, project=active_project.name)

    # delete_note returns bool | str, convert to string for consistency
    if isinstance(result, bool):
        if result:
            return f"# Delete Complete\n\n**Note deleted:** {identifier}\n\nSuccessfully removed from project '{active_project.name}'."
        else:
            return f"# Delete Failed\n\n**Note not deleted:** {identifier}\n\nThe delete operation completed but the note was not removed."
    else:
        # Already a formatted error string
        return result


async def _suggest_tags_operation(active_project, identifier: str) -> dict:
    """Suggest semantic tags for a note using LLM."""
    try:
        # Read the note first
        from advanced_memory.mcp.tools.read_note import read_note

        note_content = await read_note.fn(identifier=identifier, project=active_project.name)

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


async def _summarize_operation(active_project, identifier: str) -> dict:
    """Summarize a note using LLM."""
    try:
        # Read the note first
        from advanced_memory.mcp.tools.read_note import read_note

        note_content = await read_note.fn(identifier=identifier, project=active_project.name)

        if not note_content or note_content.startswith("# Error"):
            return f"# Error\n\nCould not read note: {identifier}\n\n{note_content}"

        # Use LLM to summarize
        from advanced_memory.services.llm_client import get_llm_client

        llm = get_llm_client()

        system_prompt = """You are a summarization assistant. Create a concise, informative summary of the note content.

The summary should:
1. Capture the main points and key information
2. Be clear and well-structured
3. Preserve important details and context
4. Use markdown formatting for readability

Return the summary as plain text (not JSON)."""

        # Use string concatenation to avoid f-string parsing of JSON curly braces in content
        note_preview = note_content[:4000]
        prompt = f"Summarize this note:\n\n{note_preview}"

        summary = await llm.generate(prompt, system_prompt, max_tokens=1000, temperature=0.3)

        return f"""# Note Summary

**Note:** {identifier}

---

## Summary

{summary}

---

**Original note length:** {len(note_content)} characters
**Summary length:** {len(summary)} characters
"""

    except Exception as e:
        logger.error(f"Summarization error: {e}", exc_info=True)
        return build_error_response(
            error="LLM service unavailable",
            error_code="LLM_UNAVAILABLE",
            message="Could not generate note summary",
            recovery_options=[
                "Configure an LLM provider using adn_llm('select_model', provider='ollama', model='llama3')",
                "Check LLM service is running (ollama serve, LMStudio, etc.)",
                "Try again if it's a temporary service issue",
            ],
            diagnostic_info={"error_details": str(e), "operation": "summarize"},
            urgency="medium",
        )


async def _enhance_operation(
    active_project,
    identifier: str,
    enhancement_instruction: str | None,
    update_content: bool = True,
    update_style: bool = True,
    add_bibliography: bool = False,
    add_examples: bool = False,
    add_context: bool = False,
    expand_sections: bool = False,
    update_stale_tech: bool = False,
) -> str:
    """Enhance a note using LLM. Supports batch-upgrading weak-LLM notes with SOTA LLM."""
    try:
        # Read the note first
        from advanced_memory.mcp.tools.read_note import read_note

        note_content = await read_note.fn(identifier=identifier, project=active_project.name)

        if not note_content or note_content.startswith("# Error"):
            return build_error_response(
                error="Could not read note",
                error_code="NOTE_NOT_FOUND",
                message=f"Failed to read note '{identifier}' before enhancement",
                recovery_options=[
                    "Verify identifier with adn_content('read', identifier='...')",
                    "Use full permalink if note is in a folder",
                ],
                diagnostic_info={"identifier": identifier},
                urgency="medium",
            )

        # Use LLM to enhance
        from advanced_memory.services.llm_client import get_llm_client

        llm = get_llm_client()

        from datetime import datetime

        instruction = enhancement_instruction or ""
        enhancement_tasks = []
        if update_content:
            enhancement_tasks.append(
                "Fix typos, spelling, and factual errors (e.g. Paris is capital of France not Spain)"
            )
            enhancement_tasks.append(
                "Update biographical info if relevant: if the note mentions a person who died after "
                "the note was written, add their death date and any notable later-life events"
            )
        if update_style:
            enhancement_tasks.append("Improve structure, clarity, readability, and organization")
        if add_examples:
            enhancement_tasks.append(
                "Add concrete examples, illustrations, or case studies where relevant"
            )
        if add_context:
            enhancement_tasks.append(
                "Add background, definitions, and explain why the topic matters"
            )
        if expand_sections:
            enhancement_tasks.append(
                "Expand bullet points and skeletal sections into full paragraphs; turn outlines into complete notes"
            )
        if update_stale_tech:
            enhancement_tasks.append(
                "Stale tech/version check: if the note references specific software versions (e.g. FastMCP 2.10, "
                "Python 3.11) that you know are outdated, update version references and add a brief migration note "
                "for breaking changes. If uncertain, add a prominent callout: 'Note: verify against current docs.' "
                "Prefer flagging uncertainty over guessing version numbers."
            )
        if add_bibliography:
            enhancement_tasks.append(
                "Add a References/Bibliography section with relevant sources if applicable"
            )
        if not enhancement_tasks:
            enhancement_tasks.append(
                "Improve the note while preserving all original content and meaning"
            )
        if instruction:
            enhancement_tasks.append(f"Additional instruction: {instruction}")

        today = datetime.now().strftime("%Y-%m-%d")
        system_prompt = f"""You are a content enhancement assistant. Today's date: {today}. Enhance notes by:
{chr(10).join(f"{i + 1}. {t}" for i, t in enumerate(enhancement_tasks))}

Always preserve the original meaning and key information. For biographical updates, use current knowledge (today is {today}) to add death dates or life events that occurred after the note was written. Return the enhanced note body in markdown format (no frontmatter)."""

        # Use string concatenation to avoid f-string parsing of JSON curly braces in content
        note_preview = note_content[:4000]
        custom_instruction = f"\n\nCustom instruction: {instruction}" if instruction else ""
        prompt = f"Enhance this note:\n\n{note_preview}{custom_instruction}\n\nReturn the complete enhanced note body (markdown, no YAML frontmatter)."

        enhanced_content = await llm.generate(
            prompt, system_prompt, max_tokens=4000, temperature=0.5
        )

        # Strip frontmatter from LLM response if present (we preserve existing frontmatter)
        from advanced_memory.file_utils import has_frontmatter, remove_frontmatter

        if has_frontmatter(enhanced_content):
            try:
                enhanced_content = remove_frontmatter(enhanced_content)
            except Exception:
                pass  # Use as-is if parse fails

        # Update the note with enhanced content (replace_body preserves frontmatter)
        from advanced_memory.mcp.tools.edit_note import edit_note

        edit_result = await edit_note.fn(
            identifier=identifier,
            operation="replace_body",
            content=enhanced_content,
            project=active_project.name,
        )

        # edit_note returns error string on failure (does not raise)
        if isinstance(edit_result, str) and (
            edit_result.startswith("# Edit Failed") or edit_result.startswith("# Error")
        ):
            return build_error_response(
                error="Could not persist enhanced content",
                error_code="EDIT_FAILED",
                message=f"LLM generated enhanced content ({len(enhanced_content)} chars) but edit_note failed to write it",
                recovery_options=[
                    "Check the note exists with adn_content('read', identifier='...')",
                    "Use full permalink (e.g. content/strawberry-facts-test)",
                    "Restart MCP server to ensure replace_body fix is loaded",
                ],
                diagnostic_info={"identifier": identifier, "edit_error": edit_result[:500]},
                urgency="medium",
            )

        return build_success_response(
            operation="enhance",
            summary=f"Note '{identifier}' enhanced and updated ({len(note_content)} -> {len(enhanced_content)} chars)",
            content=f"""# Note Enhanced

**Note:** {identifier}

The note has been enhanced and updated with improved structure, clarity, and readability.

**Original length:** {len(note_content)} characters
**Enhanced length:** {len(enhanced_content)} characters
""",
            identifier=identifier,
            original_length=len(note_content),
            enhanced_length=len(enhanced_content),
        )

    except Exception as e:
        logger.error(f"Enhancement error: {e}", exc_info=True)
        return build_error_response(
            error="LLM service unavailable",
            error_code="LLM_UNAVAILABLE",
            message="Could not enhance note content",
            recovery_options=[
                "Configure an LLM provider using adn_llm('select_model', provider='ollama', model='llama3')",
                "Check LLM service is running (ollama serve, LMStudio, etc.)",
                "Try again if it's a temporary service issue",
            ],
            diagnostic_info={"error_details": str(e), "operation": "enhance"},
            urgency="medium",
        )


async def _generate_operation(
    active_project, topic: str, folder: str | None, tags: TagType, entity_type: str
) -> str:
    """Generate new note content using LLM."""
    try:
        from advanced_memory.services.llm_client import get_llm_client

        llm = get_llm_client()

        system_prompt = """You are a content generation assistant for a knowledge management system.

Generate comprehensive, well-structured note content on the given topic. The content should:
1. Be informative and accurate
2. Use proper markdown formatting
3. Include clear headings and structure
4. Be suitable for a knowledge base (Zettelkasten-style)
5. Include relevant details and examples

Return the complete note content in markdown format."""

        prompt = f"""Generate a comprehensive note on: {topic}

Create a well-structured markdown note with:
- Clear title/heading
- Introduction
- Main content sections
- Examples if applicable
- Key takeaways

Make it informative and useful for a knowledge base."""

        generated_content = await llm.generate(
            prompt, system_prompt, max_tokens=3000, temperature=0.7
        )

        # Extract title from first line
        first_line = generated_content.split("\n")[0].lstrip("#").strip()
        title = first_line if first_line else topic.title()

        # Use default folder if not provided
        target_folder = folder or "inbox"

        # Parse tags
        tag_list = parse_tags(tags) if tags else []

        # Create the note
        return await _write_operation(
            active_project,
            title,
            generated_content,
            target_folder,
            tag_list,
            entity_type,
        )

    except Exception as e:
        logger.error(f"Content generation error: {e}", exc_info=True)
        return build_error_response(
            error="LLM service unavailable",
            error_code="LLM_UNAVAILABLE",
            message="Could not generate note content",
            recovery_options=[
                "Configure an LLM provider using adn_llm('select_model', provider='ollama', model='llama3')",
                "Check LLM service is running (ollama serve, LMStudio, etc.)",
                "Try again if it's a temporary service issue",
            ],
            diagnostic_info={"error_details": str(e), "operation": "generate"},
            urgency="medium",
        )
