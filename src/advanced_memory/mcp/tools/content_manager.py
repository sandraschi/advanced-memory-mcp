"""Content Manager portmanteau tool for Advanced Memory MCP server.

This tool consolidates all content operations: write, read, view, edit, edit_tags, move, and delete.
It reduces the number of MCP tools while maintaining full functionality.
"""

from loguru import logger

from advanced_memory.mcp.async_client import client
from advanced_memory.mcp.mcp_instance import mcp
from advanced_memory.mcp.project_session import get_active_project
from advanced_memory.mcp.tools.utils import call_get, call_put
from advanced_memory.schemas import EntityResponse
from advanced_memory.schemas.base import Entity
from advanced_memory.utils import parse_tags, validate_project_path

# Define TagType as a Union that can accept either a string or a list of strings or None
TagType = list[str] | str | None


@mcp.tool
async def adn_content(
    operation: str,
    identifier: str | None = None,
    content: str | None = None,
    folder: str | None = None,
    tags: TagType | None = None,
    entity_type: str = "note",
    destination_path: str | None = None,
    edit_operation: str | None = None,
    tag_operation: str | None = None,
    find_text: str | None = None,
    expected_replacements: int = 1,
    section: str | None = None,
    page: int = 1,
    page_size: int = 10,
    audio_path: str | None = None,
    record_duration: int | None = None,
    voice: str | None = None,
    speed: float = 1.0,
    save_audio: bool = False,
    project: str | None = None,
) -> str:
    """Comprehensive content management tool for Advanced Memory knowledge base.

    This portmanteau tool consolidates all content operations into a single interface,
    reducing MCP tool count while maintaining full functionality for Cursor IDE compatibility.

    SUPPORTED OPERATIONS:
    - write: Create new notes or update existing ones with semantic processing
    - read: Retrieve complete note content with intelligent lookup strategies
    - view: Display notes as formatted artifacts for better readability
    - view_rendered: Display notes as HTML artifacts with rendered Mermaid diagrams
    - edit: Perform targeted edits (append, prepend, find_replace, replace_section)
    - edit_tags: Edit tags (add, remove, replace, clear) without full note edits
    - quick: Ultra-fast note creation with smart defaults (auto-folder, auto-title)
    - daily: Create or append to today's daily journal note
    - dictate: Speech-to-text note creation (audio file or live recording)
    - speak: Text-to-speech note reading (play audio or save to file)
    - move: Relocate notes while preserving relationships and updating references
    - delete: Remove notes from knowledge base with relationship cleanup

    CONTENT PROCESSING:
    - Automatic entity recognition and linking ([[Entity Name]] syntax)
    - Relationship extraction and graph building
    - Tag processing and categorization
    - Folder organization and hierarchy
    - Markdown rendering and syntax validation

    Args:
        operation: Operation type (write, read, view, view_rendered, edit, edit_tags, quick, daily, dictate, speak, move, delete)
        identifier: Note title, permalink, or memory:// URL
        content: Full markdown content for write/edit/quick/daily operations
        folder: Target folder path for write/move operations
        tags: Tags for categorization (string, list, or None)
        entity_type: Content type (default: "note")
        destination_path: New path for move operations
        edit_operation: Edit type for edit operations (append, prepend, find_replace, replace_section)
        tag_operation: Tag operation for edit_tags (add, remove, replace, clear)
        find_text: Text to find for find_replace operations
        expected_replacements: Expected replacement count for validation
        section: Target section for replace_section operations
        page: Pagination page for read operations
        page_size: Items per page for paginated content
        audio_path: Path to audio file for dictate operation
        record_duration: Duration in seconds for live recording (dictate operation)
        voice: Voice ID for speak operation (OS-dependent)
        speed: Playback speed for speak operation (0.5 to 2.0, default 1.0)
        save_audio: Save audio to file instead of playing (speak operation)
        project: Optional project name (defaults to active project)

    Returns:
        Operation-specific result with semantic content summary

    Examples:
        # Write a new note
        adn_content("write", identifier="Project Plan", content="# Project Overview...", folder="projects")

        # Read a note
        adn_content("read", identifier="Project Plan")

        # Edit a note (append content)
        adn_content("edit", identifier="Project Plan", edit_operation="append", content="\\n## Updates...")

        # Edit tags (add tags)
        adn_content("edit_tags", identifier="Meeting Notes", tag_operation="add", tags="urgent, follow-up")

        # Edit tags (remove tags)
        adn_content("edit_tags", identifier="Draft", tag_operation="remove", tags=["draft", "wip"])

        # Edit tags (replace all)
        adn_content("edit_tags", identifier="Project Plan", tag_operation="replace", tags="final, approved")

        # Quick capture (ultra-fast note creation)
        adn_content("quick", content="Great insight: use AI for code reviews")

        # Daily journal entry
        adn_content("daily", content="## Meeting Notes\\n\\nDiscussed Q4 roadmap with team")

        # Dictate note from audio file
        adn_content("dictate", audio_path="recording.mp3", tags="voice-note")

        # Dictate by recording live
        adn_content("dictate", record_duration=30, tags="quick-thought")

        # Speak (read note aloud)
        adn_content("speak", identifier="Python Basics", speed=1.5)

        # Speak and save to audio file
        adn_content("speak", identifier="Study Notes", save_audio=True)

        # Move a note
        adn_content("move", identifier="Project Plan", destination_path="archive/completed/project-plan.md")

        # Delete a note
        adn_content("delete", identifier="Project Plan")

        # View note with rendered Mermaid diagrams
        adn_content("view_rendered", identifier="System Architecture")
    """
    logger.info(f"MCP tool call tool=adn_content operation={operation} identifier={identifier}")

    # Get the active project
    active_project = get_active_project(project)
    if not active_project:
        return "# Error\n\nNo active project found. Please switch to a project first."

    # Route to appropriate operation handler
    if operation == "write":
        if not identifier or not content or not folder:
            return "# Error\n\nWrite operation requires: identifier, content, and folder parameters"
        return await _write_operation(
            active_project, identifier, content, folder, tags, entity_type
        )

    elif operation == "read":
        if identifier is None:
            return "# Error\n\nRead operation requires: identifier"
        return await _read_operation(active_project, identifier, page, page_size)

    elif operation == "view":
        if identifier is None:
            return "# Error\n\nView operation requires: identifier"
        return await _view_operation(active_project, identifier)

    elif operation == "view_rendered":
        if identifier is None:
            return "# Error\n\nView rendered operation requires: identifier"
        return await _view_rendered_operation(active_project, identifier)

    elif operation == "edit":
        if identifier is None:
            return "# Error\n\nEdit operation requires: identifier"
        return await _edit_operation(
            active_project,
            identifier,
            edit_operation,
            content,
            section,
            find_text,
            expected_replacements,
        )

    elif operation == "edit_tags":
        if identifier is None:
            return "# Error\n\nEdit tags operation requires: identifier"
        return await _edit_tags_operation(active_project, identifier, tag_operation, tags)

    elif operation == "quick":
        if not content:
            return "# Error\n\nQuick capture requires: content parameter"
        return await _quick_capture_operation(active_project, content, tags)

    elif operation == "daily":
        if not content:
            return "# Error\n\nDaily note operation requires: content parameter"
        return await _daily_note_operation(active_project, content, tags)

    elif operation == "dictate":
        return await _dictate_note_operation(active_project, audio_path, record_duration, tags)

    elif operation == "speak":
        if not identifier:
            return "# Error\n\nSpeak operation requires: identifier parameter"
        return await _speak_note_operation(active_project, identifier, voice, speed, save_audio)

    elif operation == "move":
        if identifier is None or destination_path is None:
            return "# Error\n\nMove operation requires: identifier, destination_path"
        return await _move_operation(active_project, identifier, destination_path)
    elif operation == "delete":
        if identifier is None:
            return "# Error\n\nDelete operation requires: identifier"
        return await _delete_operation(active_project, identifier)
    else:
        return f"# Error\n\nInvalid operation '{operation}'. Supported operations: write, read, view, view_rendered, edit, edit_tags, quick, daily, dictate, speak, move, delete"


async def _write_operation(
    active_project, identifier: str, content: str, folder: str, tags: TagType, entity_type: str
) -> str:
    """Handle write operation."""
    if not identifier or not content or not folder:
        return "# Error\n\nWrite operation requires: identifier, content, and folder parameters"

    # Validate folder path to prevent path traversal attacks
    project_path = active_project.home
    if folder and not validate_project_path(folder, project_path):
        logger.warning(
            "Attempted path traversal attack blocked", folder=folder, project=active_project.name
        )
        return f"# Error\n\nFolder path '{folder}' is not allowed - paths must stay within project boundaries"

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
    logger.debug(f"Creating entity via API permalink={entity.permalink}")
    url = f"{project_url}/knowledge/entities/{entity.permalink}"
    response = await call_put(client, url, json=entity.model_dump())
    result = EntityResponse.model_validate(response.json())

    # Format semantic summary based on status code
    action = "Created" if response.status_code == 201 else "Updated"
    summary = [
        f"# {action} note",
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
            summary.append("\nNote: Unresolved relations point to entities that don't exist yet.")
            summary.append(
                "They will be automatically resolved when target entities are created or during sync operations."
            )

    if tag_list:
        summary.append(f"\n## Tags\n- {', '.join(tag_list)}")

    logger.info(
        f"MCP tool response: tool=content_manager operation=write action={action} permalink={result.permalink} observations_count={len(result.observations)} relations_count={len(result.relations)} resolved_relations={resolved} unresolved_relations={unresolved} status_code={response.status_code}"
    )
    return "\n".join(summary)


async def _read_operation(active_project, identifier: str, page: int, page_size: int) -> str:
    """Handle read operation."""
    if not identifier:
        return "# Error\n\nRead operation requires identifier parameter"

    # Delegate to read_note tool
    from advanced_memory.mcp.tools.read_note import read_note

    return await read_note.fn(
        identifier=identifier, page=page, page_size=page_size, project=active_project.name
    )


async def _view_operation(active_project, identifier: str) -> str:
    """Handle view operation."""
    from advanced_memory.mcp.tools.view_note import view_note

    return await view_note.fn(identifier=identifier, project=active_project.name)


async def _view_rendered_operation(active_project, identifier: str) -> str:
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
        return "# Error\n\nEdit tags operation requires tag_operation parameter (add, remove, replace, clear)"

    # Get current note to read existing tags
    project_url = active_project.project_url
    url = f"{project_url}/knowledge/entities/resolve/{identifier}"

    response = await call_get(client, url)
    if response.status_code == 404:
        return f"# Error\n\nNote not found: {identifier}\n\nPlease provide exact note title or permalink."

    current_entity = EntityResponse.model_validate(response.json())
    current_tags = (
        current_entity.entity_metadata.get("tags", []) if current_entity.entity_metadata else []
    )

    # Parse input tags (unless clear operation)
    if tag_operation != "clear":
        if tags is None and tag_operation != "clear":
            return f"# Error\n\n'{tag_operation}' operation requires tags parameter.\n\nProvide tags as string or list."

        new_tags = parse_tags(tags)

        if not new_tags and tag_operation != "clear":
            return f"# Error\n\nNo valid tags provided.\n\nTags: {tags}"

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

    update_url = f"{project_url}/knowledge/entities/{current_entity.permalink}"
    update_data = {
        "title": current_entity.title,
        "entity_type": current_entity.entity_type,
        "content_type": current_entity.content_type,
        "content": current_entity.content,
        "entity_metadata": metadata,
    }

    update_response = await call_put(client, update_url, json=update_data)
    result = EntityResponse.model_validate(update_response.json())

    # Format response
    response_lines = [
        "# Tag Edit Complete",
        "",
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


async def _move_operation(active_project, identifier: str, destination_path: str) -> str:
    """Handle move operation."""
    from advanced_memory.mcp.tools.move_note import move_note

    return await move_note.fn(
        identifier=identifier, destination_path=destination_path, project=active_project.name
    )


async def _quick_capture_operation(active_project, content: str, tags: TagType) -> str:
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

    # Auto-add capture tag
    tag_list = parse_tags(tags) if tags else []
    tag_list.append("quick-capture")
    tag_list.append(datetime.now().strftime("%Y-%m-%d"))

    # Add timestamp to content
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    formatted_content = f"# {title}\n\n**Captured:** {timestamp}\n\n{content}"

    # Create the note
    return await _write_operation(
        active_project, title, formatted_content, folder, tag_list, "note"
    )


async def _daily_note_operation(active_project, content: str, tags: TagType) -> str:
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
        identifier=f"{folder}/{title}", page=1, page_size=1000, project=active_project.name
    )

    # Check if note exists (not an error message)
    if "# Note Not Found:" in existing_note:
        # Create new daily note
        timestamp = today.strftime("%H:%M")
        formatted_content = f"""# Daily Note: {title}

## {timestamp}

{content}

---

"""
        return await _write_operation(
            active_project, title, formatted_content, folder, tag_list, "note"
        )
    else:
        # Append to existing daily note
        timestamp = today.strftime("%H:%M")
        append_content = f"""

## {timestamp}

{content}

---
"""
        return await edit_note.fn(
            identifier=f"{folder}/{title}",
            operation="append",
            content=append_content,
            project=active_project.name,
        )


async def _dictate_note_operation(
    active_project, audio_path: str | None, record_duration: int | None, tags: TagType
) -> str:
    """Handle dictate operation - speech-to-text note creation."""
    try:
        import whisper
    except ImportError:
        return """# Voice Features Not Available

Speech-to-text (dictate) requires optional voice dependencies.

INSTALL:
pip install advanced-memory[voice]

This installs:
- openai-whisper (speech-to-text)
- pyttsx3 (text-to-speech)
- sounddevice (audio recording)
- soundfile (audio file handling)

Or install manually:
pip install openai-whisper pyttsx3 sounddevice soundfile

Then restart and try again!"""

    from pathlib import Path

    # Handle live recording
    if record_duration:
        try:
            import sounddevice as sd
            import soundfile as sf

            # Record audio
            sample_rate = 16000  # Whisper works best at 16kHz
            logger.info(f"Recording audio for {record_duration} seconds...")

            audio_data = sd.rec(
                int(record_duration * sample_rate),
                samplerate=sample_rate,
                channels=1,
                dtype="float32",
            )
            sd.wait()

            # Save to temp file
            temp_audio = Path.home() / ".advanced-memory" / "temp_recording.wav"
            temp_audio.parent.mkdir(parents=True, exist_ok=True)
            sf.write(temp_audio, audio_data, sample_rate)

            audio_path = str(temp_audio)
            logger.info(f"Recording saved to: {audio_path}")

        except Exception as e:
            return f"# Recording Failed\n\nError: {str(e)}\n\nEnsure sounddevice and soundfile are installed."

    # Check if audio file exists
    if not audio_path or not Path(audio_path).exists():
        return "# Error\n\nDictate requires either audio_path (to existing file) or record_duration (to record live)"

    # Transcribe audio using Whisper
    try:
        logger.info(f"Transcribing audio: {audio_path}")
        model = whisper.load_model("base")  # base model is fast and good enough
        result = model.transcribe(audio_path)
        transcribed_text = result["text"].strip()

        if not transcribed_text:
            return "# Transcription Failed\n\nNo speech detected in audio. Please try again with clearer audio."

        logger.info(f"Transcription complete: {len(transcribed_text)} characters")

        # Use quick capture with transcribed text
        return await _quick_capture_operation(active_project, transcribed_text, tags)

    except Exception as e:
        logger.error(f"Transcription error: {e}")
        return f"# Transcription Failed\n\nError: {str(e)}\n\nTry a different audio file or check Whisper installation."


async def _speak_note_operation(
    active_project,
    identifier: str,
    voice: str | None,
    speed: float,
    save_audio: bool,
) -> str:
    """Handle speak operation - text-to-speech note reading."""
    try:
        import pyttsx3
    except ImportError:
        return """# Voice Features Not Available

Text-to-speech (speak) requires optional voice dependencies.

INSTALL:
pip install advanced-memory[voice]

This installs:
- pyttsx3 (text-to-speech)
- openai-whisper (speech-to-text)
- sounddevice (audio recording)
- soundfile (audio file handling)

Or install manually:
pip install pyttsx3

Then restart and try again!"""

    from datetime import datetime

    # Read the note content
    from advanced_memory.mcp.tools.read_note import read_note

    note_content = await read_note.fn(
        identifier=identifier, page=1, page_size=1000, project=active_project.name
    )

    # Check if note was found
    if "# Note Not Found:" in note_content:
        return note_content  # Return the not found error

    # Clean content for speaking (remove YAML frontmatter, metadata)
    lines = note_content.split("\n")
    clean_lines = []
    in_frontmatter = False

    for line in lines:
        if line.strip() == "---":
            in_frontmatter = not in_frontmatter
            continue
        if not in_frontmatter:
            # Skip metadata lines like "title:", "permalink:", etc.
            if not line.startswith(
                ("title:", "permalink:", "created:", "updated:", "**", "file_path:")
            ):
                clean_lines.append(line)

    text_to_speak = "\n".join(clean_lines).strip()

    if not text_to_speak:
        return f"# No Content to Speak\n\nNote '{identifier}' has no readable content."

    # Initialize TTS engine
    try:
        engine = pyttsx3.init()

        # Set speed (rate)
        current_rate = engine.getProperty("rate")
        engine.setProperty("rate", int(current_rate * speed))

        # Set voice if specified
        if voice:
            voices = engine.getProperty("voices")
            # Try to find matching voice
            for v in voices:
                if voice.lower() in v.id.lower() or voice.lower() in v.name.lower():
                    engine.setProperty("voice", v.id)
                    break

        if save_audio:
            # Save to audio file
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            audio_dir = active_project.home / "audio"
            audio_dir.mkdir(exist_ok=True)

            safe_title = identifier.replace("/", "-").replace("\\", "-")[:50]
            audio_file = audio_dir / f"{safe_title}_{timestamp}.mp3"

            engine.save_to_file(text_to_speak, str(audio_file))
            engine.runAndWait()

            return f"""# Audio Saved

**Note:** {identifier}
**Audio file:** {audio_file}
**Duration:** ~{len(text_to_speak.split()) // 150} minutes
**Speed:** {speed}x

✅ Text-to-speech conversion complete!"""

        else:
            # Play audio directly
            engine.say(text_to_speak)
            engine.runAndWait()

            return f"""# Note Spoken

**Note:** {identifier}
**Word count:** {len(text_to_speak.split())}
**Duration:** ~{len(text_to_speak.split()) // 150} minutes
**Speed:** {speed}x

✅ Text-to-speech playback complete!"""

    except Exception as e:
        logger.error(f"TTS error: {e}")
        return f"# Text-to-Speech Failed\n\nError: {str(e)}\n\nCheck pyttsx3 installation and audio drivers."


async def _delete_operation(active_project, identifier: str) -> str:
    """Handle delete operation."""
    from advanced_memory.mcp.tools.delete_note import delete_note

    return await delete_note.fn(identifier=identifier, project=active_project.name)
