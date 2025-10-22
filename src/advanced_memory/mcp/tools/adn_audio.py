"""Audio portmanteau tool for Advanced Memory MCP server.

This tool consolidates voice operations: dictate (speech-to-text) and speak (text-to-speech).
Extracted from content_manager.py for better separation of concerns and optional dependencies.
"""

from loguru import logger

from advanced_memory.mcp.mcp_instance import mcp
from advanced_memory.mcp.project_session import get_active_project
from advanced_memory.utils import parse_tags

# Define TagType
TagType = list[str] | str | None


@mcp.tool
async def adn_audio(
    operation: str,
    identifier: str | None = None,
    audio_path: str | None = None,
    record_duration: int | None = None,
    voice: str | None = None,
    speed: float = 1.0,
    save_audio: bool = False,
    tags: TagType | None = None,
    project: str | None = None,
) -> str:
    '''Voice operations for Advanced Memory knowledge base.

    Audio and voice operations with optional dependencies (Whisper, pyttsx3).

    OPERATIONS:
    - dictate: Speech-to-text note creation (audio file or live recording)
    - speak: Text-to-speech note reading (play audio or save to file)

    INSTALLATION:
    These operations require optional voice dependencies:
    pip install advanced-memory[voice]

    This installs:
    - openai-whisper (speech-to-text)
    - pyttsx3 (text-to-speech)
    - sounddevice (audio recording)
    - soundfile (audio file handling)

    Args:
        operation: Operation type (dictate, speak)
        identifier: Note title/permalink for speak operation
        audio_path: Path to audio file for dictate operation
        record_duration: Duration in seconds for live recording (dictate)
        voice: Voice ID for speak operation (OS-dependent)
        speed: Playback speed for speak operation (0.5 to 2.0, default 1.0)
        save_audio: Save audio to file instead of playing (speak operation)
        tags: Tags for categorization (dictate operation)
        project: Optional project name (defaults to active project)

    Returns:
        Operation-specific result with audio processing details

    Examples:
        # Dictate note from audio file
        adn_audio("dictate", audio_path="recording.mp3", tags="voice-note")

        # Dictate by recording live (30 seconds)
        adn_audio("dictate", record_duration=30, tags="quick-thought")

        # Speak (read note aloud)
        adn_audio("speak", identifier="Python Basics", speed=1.5)

        # Speak and save to audio file
        adn_audio("speak", identifier="Study Notes", save_audio=True)
    '''
    logger.info(f"MCP tool call tool=adn_audio operation={operation}")

    # Get the active project
    active_project = get_active_project(project)
    if not active_project:
        return "# Error\n\nNo active project found. Please switch to a project first."

    # Route to appropriate operation handler
    if operation == "dictate":
        return await _dictate_operation(active_project, audio_path, record_duration, tags)
    elif operation == "speak":
        if not identifier:
            return "# Error\n\nSpeak operation requires: identifier parameter"
        return await _speak_operation(active_project, identifier, voice, speed, save_audio)
    else:
        return f"# Error\n\nInvalid operation '{operation}'. Supported operations: dictate, speak"


async def _dictate_operation(
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

        # Create note using quick capture pattern
        from datetime import datetime

        # Generate smart title from content (first line or timestamp)
        content_lines = transcribed_text.strip().split("\n")
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
            content = transcribed_text

        # Auto-select folder (inbox or quick-notes)
        folder = "inbox"

        # Auto-add capture tag
        tag_list = parse_tags(tags) if tags else []
        tag_list.append("voice-dictation")
        tag_list.append(datetime.now().strftime("%Y-%m-%d"))

        # Add timestamp to content
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        formatted_content = f"# {title}\n\n**Dictated:** {timestamp}\n\n{content}"

        # Create the note
        from advanced_memory.mcp.tools.write_note import write_note

        return await write_note.fn(
            title=title,
            content=formatted_content,
            folder=folder,
            tags=tag_list,
            entity_type="note",
            project=active_project.name,
        )

    except Exception as e:
        logger.error(f"Transcription error: {e}")
        return f"# Transcription Failed\n\nError: {str(e)}\n\nTry a different audio file or check Whisper installation."


async def _speak_operation(
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

