"""Audio portmanteau tool for Advanced Memory MCP server.

This tool consolidates voice operations: dictate (speech-to-text) and speak (text-to-speech).
Extracted from content_manager.py for better separation of concerns and optional dependencies.

RESPONSES:
Success: {"success": true, "operation": "...", "summary": "...", "result": {...}}
Error: {"success": false, "error": "...", "error_code": "...", "message": "...", "recovery_options": [...]}

For errors, check recovery_options for next steps.
"""

import threading

from loguru import logger

from advanced_memory.mcp.mcp_instance import mcp
from advanced_memory.mcp.models.portmanteau import AudioOperation
from advanced_memory.mcp.project_session import get_active_project
from advanced_memory.mcp.tools.utils import build_error_response, build_success_response
from advanced_memory.utils import parse_tags

# Define TagType
TagType = list[str] | str | None

# Global state for wake word listener
_wake_listener_thread: threading.Thread | None = None
_wake_listener_stop_event = threading.Event()
_wake_listener_running = False

# Global state for alarms and timers
_alarms: dict[str, dict] = {}  # alarm_id -> {time, message, thread}
_timers: dict[str, dict] = {}  # timer_id -> {duration, message, thread}
_alarm_counter = 0
_timer_counter = 0


@mcp.tool()
async def adn_audio(op: AudioOperation) -> dict:
    """
    Voice and audio management for Advanced Memory.

    This tool provides a unified interface for all audio operations, including
    transcription, speech synthesis, and media control.

    ---------------------------------------------------------------------------
    [RATIONALE]
    By consolidating audio operations into one tool, we centralize dependencies
    like faster-whisper, Kokoro, and onnxruntime-gpu. This ensures consistent
    handling of audio devices and background threads while providing a rich
    set of features through a single entry point.

    ---------------------------------------------------------------------------
    [SUPPORTED OPERATIONS]
    - dictate: Creates notes by transcribing live recording or audio files.
    - speak: Converts text or note content to speech using high-fidelity Kokoro voices.
    - listen: Records a short audio clip and executes interpreted voice commands.
    - wake_start: Starts a background listener for hands-free activation.
    - wake_stop: Stops the background wake word listener.
    - wake_status: Reports the current status of the background listener.
    - weather: Provides a formatted weather report for any location.
    - timer: Sets a countdown timer with a specified duration.
    - alarm: Sets a time-based reminder or wake-up alarm.
    - music: Controls playback for Plex or Windows Media Player.

    ---------------------------------------------------------------------------
    [PLEX AUTHENTICATION]
    To use Plex music control, configure the following environment variables:
    - PLEX_SERVER_URL: The URL of your Plex server (e.g., http://localhost:32400).
    - PLEX_TOKEN: Your private Plex authentication token.

    ---------------------------------------------------------------------------
    [AUDIO SOUL 2026 STACK]
    This tool uses the latest audio libraries:
    - Kokoro: For expressive and natural speech synthesis.
    - faster-whisper: For rapid and accurate speech-to-text.
    - GPU Acceleration: Optimized for high-end GPUs like the RTX 4090 using CUDA.

    ---------------------------------------------------------------------------
    [PREREQUISITES]
    Install the optional voice dependencies:
    pip install advanced-memory[voice]

    ---------------------------------------------------------------------------
    [PARAMETERS]
    - operation (str): The specific task to perform.
    - identifier (str, optional): Note title or text content for speech synthesis.
    - audio_path (str, optional): Path to a file for transcription. Defaults to microphone.
    - record_duration (int, optional): Recording length in seconds.
    - voice (str, optional): Preferred Kokoro voice (e.g., heart, sky, adam).
    - speed (float, optional): Rate of speech playback. Range 0.5 to 2.0.
    - volume (int, optional): Output level from 1 to 10.
    - save_audio (bool, optional): If true, writes output to a WAV file instead of playing.
    - tags (str, optional): Metadata tags for created notes.
    - wake_word (str, optional): Word used to trigger the background listener.
    - location (str, optional): Target city for weather reports.
    - duration (str, optional): Time length for timers (e.g., 5 mins).
    - time_str (str, optional): Target time for alarms (e.g., 7 AM).
    - command (str, optional): Music action like play, pause, or next.
    - query (str, optional): Search term for music playback.
    - project (str, optional): The project context for the operation.

    ---------------------------------------------------------------------------
    [EXAMPLES]

    - Record a note with tags:
      adn_audio(operation='dictate', record_duration=10, tags='ideas')

    - Speak a specific project note:
      adn_audio(operation='speak', identifier='Meeting Summary', speed=1.2)

    - Get the weather in Vienna:
      adn_audio(operation='weather', location='Vienna')

    - Set a five minute timer:
      adn_audio(operation='timer', duration='5 minutes')

    - Start playing music on Plex:
      adn_audio(operation='music', command='play', query='Bach')
    """
    operation = op.operation
    project = getattr(op, "project", None)

    logger.info(f"MCP tool call tool=adn_audio operation={operation}")

    # Get the active project
    active_project = get_active_project(project)
    if not active_project:
        return "# Let's get you set up!\n\nI don't see an active project right now. Let's switch to one first so I can help you with audio operations. You can use the project management tools to see available projects and switch to one."

    # Route to appropriate operation handler
    if operation == "dictate":
        return await _dictate_operation(active_project, op.audio_path, op.record_duration, op.tags)
    elif operation == "speak":
        # Validate volume range
        if op.volume < 1 or op.volume > 10:
            return "# Volume adjustment needed!\n\nLet's keep the volume between 1 and 10 (it defaults to 5). This helps ensure great audio quality without being too loud or quiet."
        return await _speak_operation(active_project, op.identifier, op.voice, op.speed, op.volume, op.save_audio)
    elif operation == "listen":
        return await _listen_command_operation(active_project, op.audio_path, op.record_duration)
    elif operation == "wake_start":
        return await _wake_start_operation(active_project, op.wake_word, op.record_duration)
    elif operation == "wake_stop":
        return await _wake_stop_operation()
    elif operation == "wake_status":
        return await _wake_status_operation()
    elif operation == "weather":
        return await _get_weather(op.location)
    elif operation == "timer":
        return await _set_timer(op.duration)
    elif operation == "alarm":
        return await _set_alarm(op.time_str)
    elif operation == "music":
        return await _control_music(op.command, op.query)
    else:
        return f"# Error\n\nInvalid operation '{operation}'. Supported operations: dictate, speak, listen, wake_start, wake_stop, wake_status, weather, timer, alarm, music"


async def _dictate_operation(
    active_project, audio_path: str | None, record_duration: int | None, tags: TagType
) -> dict:
    """Handle dictate operation - speech-to-text note creation."""
    try:
        from faster_whisper import WhisperModel
    except ImportError:
        return build_error_response(
            error="voice_features_unavailable",
            error_code="MISSING_VOICE_DEPENDENCIES",
            message="Speech-to-text (dictate) requires optional voice dependencies",
            recovery_options=[
                "Install voice dependencies: pip install advanced-memory[voice]",
                "Or manually: pip install faster-whisper kokoro onnxruntime-gpu sounddevice soundfile",
                "Restart the MCP server after installation",
                "Try the operation again",
            ],
            required_packages=[
                "faster-whisper",
                "kokoro",
                "onnxruntime-gpu",
                "sounddevice",
                "soundfile",
            ],
            urgency="medium",
        )

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
            return f"# Recording Failed\n\nError: {e!s}\n\nEnsure sounddevice and soundfile are installed."

    # Check if audio file exists
    if not audio_path or not Path(audio_path).exists():
        return "# Error\n\nDictate requires either audio_path (to existing file) or record_duration (to record live)"

    # Transcribe audio using faster-whisper
    try:
        logger.info(f"Transcribing audio: {audio_path}")
        # Use GPU (cuda) with float16 for maximum performance on 4090
        model = WhisperModel("base", device="cuda", compute_type="float16")
        segments, info = model.transcribe(audio_path, beam_size=5)

        # Collect segments into a single string
        transcribed_text = " ".join([segment.text for segment in segments]).strip()

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

        return await (write_note.fn if hasattr(write_note, "fn") else write_note)(
            title=title,
            content=formatted_content,
            folder=folder,
            tags=tag_list,
            entity_type="note",
            project=active_project.name,
        )

    except Exception as e:
        logger.error(f"Transcription error: {e}")
        return f"# Transcription Failed\n\nError: {e!s}\n\nTry a different audio file or check Whisper installation."


async def _speak_operation(
    active_project,
    identifier: str,
    voice: str | None,
    speed: float,
    volume: int,
    save_audio: bool,
) -> dict:
    """Handle speak operation - text-to-speech note reading."""
    try:
        import sounddevice as sd
        from kokoro import KPipeline
    except ImportError:
        return build_error_response(
            error="voice_features_unavailable",
            error_code="MISSING_VOICE_DEPENDENCIES",
            message="Text-to-speech (speak) requires optional voice dependencies (Kokoro)",
            recovery_options=[
                "Install voice dependencies: pip install advanced-memory[voice]",
                "Or manually: pip install kokoro onnxruntime-gpu sounddevice soundfile",
                "Restart the MCP server after installation",
                "Try the operation again",
            ],
            required_packages=["kokoro", "onnxruntime-gpu", "sounddevice", "soundfile"],
            urgency="medium",
        )

    from datetime import datetime

    # Read the note content
    from advanced_memory.mcp.tools.read_note import read_note

    note_content = await (read_note.fn if hasattr(read_note, "fn") else read_note)(
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
            if not line.startswith(("title:", "permalink:", "created:", "updated:", "**", "file_path:")):
                clean_lines.append(line)

    text_to_speak = "\n".join(clean_lines).strip()

    if not text_to_speak:
        return f"# No Content to Speak\n\nNote '{identifier}' has no readable content."

    # Initialize Kokoro pipeline
    try:
        logger.info(f"Synthesizing speech with Kokoro: {identifier}")
        # Initialize pipeline (American English default)
        pipeline = KPipeline(lang_code="a")

        # Map voice parameter to Kokoro voice IDs
        # Default Kokoro voices: af_heart, af_bella, af_nicole, af_sky, am_adam, am_michael
        kokoro_voice = "af_heart"  # Default soulful female voice
        if voice:
            voice_lower = voice.lower()
            if "adam" in voice_lower or "male" in voice_lower:
                kokoro_voice = "am_adam"
            elif "michael" in voice_lower or "man" in voice_lower:
                kokoro_voice = "am_michael"
            elif "sky" in voice_lower:
                kokoro_voice = "af_sky"
            elif "bella" in voice_lower:
                kokoro_voice = "af_bella"
            elif "nicole" in voice_lower:
                kokoro_voice = "af_nicole"

        # Generate audio using Kokoro
        generator = pipeline(text_to_speak, voice=kokoro_voice, speed=speed, split_pattern=r"\n+")

        audio_segments = []
        for _gs, _ps, audio in generator:
            audio_segments.append(audio)

        import numpy as np

        full_audio = np.concatenate(audio_segments)

        if save_audio:
            import soundfile as sf

            # Save to audio file
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            audio_dir = active_project.home / "audio"
            audio_dir.mkdir(exist_ok=True)

            safe_title = identifier.replace("/", "-").replace("\\", "-")[:50]
            audio_file = audio_dir / f"{safe_title}_{timestamp}.wav"

            # Kokoro output is 24kHz
            sf.write(str(audio_file), full_audio, 24000)

            return build_success_response(
                operation="speak",
                summary=f"Audio saved for note '{identifier}' using Kokoro voice synthesis",
                result={
                    "note_title": identifier,
                    "audio_file": str(audio_file),
                    "voice": kokoro_voice,
                    "estimated_duration_minutes": len(text_to_speak.split()) // 150,
                    "speed": speed,
                    "volume": f"{volume}/10",
                    "audio_format": "WAV",
                    "sample_rate": 24000,
                },
                next_steps=[
                    "Play the audio file to verify quality",
                    "Adjust voice/speed/volume parameters if needed",
                    "Use the audio for presentations or accessibility",
                ],
            )

        else:
            # Play audio directly using sounddevice
            logger.info(f"Playing audio through sounddevice (24kHz, voice={kokoro_voice})")
            sd.play(full_audio, 24000)
            sd.wait()

            return build_success_response(
                operation="speak",
                summary=f"Note '{identifier}' spoken using Kokoro voice synthesis",
                result={
                    "note_title": identifier,
                    "voice": kokoro_voice,
                    "word_count": len(text_to_speak.split()),
                    "estimated_duration_minutes": len(text_to_speak.split()) // 150,
                    "speed": speed,
                    "volume": f"{volume}/10",
                    "playback_method": "sounddevice",
                    "sample_rate": 24000,
                },
                next_steps=[
                    "Adjust voice/speed/volume for better results",
                    "Use save_audio=True to save audio files",
                    "Try different voices for variety",
                ],
            )

    except Exception as e:
        logger.error(f"Kokoro TTS error: {e}")
        # Fallback to pyttsx3 if Kokoro fails
        try:
            import pyttsx3

            logger.info("Falling back to pyttsx3 (SAPI5)...")
            engine = pyttsx3.init()
            current_rate = engine.getProperty("rate")
            engine.setProperty("rate", int(current_rate * speed))
            volume_normalized = volume / 10.0
            engine.setProperty("volume", volume_normalized)
            engine.say(text_to_speak)
            engine.runAndWait()
            return build_success_response(
                operation="speak",
                summary="Text spoken using system fallback (pyttsx3) after Kokoro failure",
                result={
                    "method": "fallback_pyttsx3",
                    "kokoro_error": str(e),
                    "fallback_success": True,
                },
                next_steps=[
                    "Install Kokoro dependencies for better quality",
                    "Consider adjusting audio settings",
                ],
            )
        except Exception as _:
            return build_error_response(
                error="text_to_speech_failed",
                error_code="TTS_ALL_METHODS_FAILED",
                message="Both Kokoro and fallback (pyttsx3) text-to-speech failed",
                recovery_options=[
                    "Install voice dependencies: pip install advanced-memory[voice]",
                    "Check audio drivers and system audio",
                    "Try with different voice parameters",
                    "Restart the MCP server",
                ],
                diagnostic_info={"kokoro_error": str(e)},
                urgency="medium",
            )


async def _listen_command_operation(active_project, audio_path: str | None, record_duration: int | None) -> dict:
    """Handle listen operation - voice command input with intelligent parsing.

    Records voice, transcribes it, parses the command intent, and executes it.
    Uses rule-based parsing for common commands, with LLM fallback for complex ones.
    """
    try:
        from faster_whisper import WhisperModel
    except ImportError:
        return build_error_response(
            error="voice_features_unavailable",
            error_code="MISSING_VOICE_DEPENDENCIES",
            message="Voice command (listen) requires optional voice dependencies (faster-whisper)",
            recovery_options=[
                "Install voice dependencies: pip install advanced-memory[voice]",
                "Or manually: pip install faster-whisper onnxruntime-gpu sounddevice soundfile",
                "Restart the MCP server after installation",
                "Try the operation again",
            ],
            required_packages=["faster-whisper", "onnxruntime-gpu", "sounddevice", "soundfile"],
            urgency="medium",
        )

    from pathlib import Path

    # Handle live recording
    if record_duration:
        try:
            import sounddevice as sd
            import soundfile as sf

            # Record audio
            sample_rate = 16000  # Whisper works best at 16kHz
            logger.info(f"Recording voice command for {record_duration} seconds...")

            audio_data = sd.rec(
                int(record_duration * sample_rate),
                samplerate=sample_rate,
                channels=1,
                dtype="float32",
            )
            sd.wait()

            # Save to temp file
            temp_audio = Path.home() / ".advanced-memory" / "temp_command.wav"
            temp_audio.parent.mkdir(parents=True, exist_ok=True)
            sf.write(temp_audio, audio_data, sample_rate)

            audio_path = str(temp_audio)
            logger.info(f"Recording saved to: {audio_path}")

        except Exception as e:
            return f"# Recording Failed\n\nError: {e!s}\n\nEnsure sounddevice and soundfile are installed."

    # Check if audio file exists
    if not audio_path or not Path(audio_path).exists():
        return "# Error\n\nListen requires either audio_path (to existing file) or record_duration (to record live)"

    # Transcribe audio using faster-whisper
    try:
        logger.info(f"Transcribing voice command: {audio_path}")
        model = WhisperModel("base", device="cuda", compute_type="float16")
        segments, info = model.transcribe(audio_path, beam_size=5)
        command_text = " ".join([segment.text for segment in segments]).strip().lower()

        if not command_text:
            return "# Transcription Failed\n\nNo speech detected in audio. Please try again with clearer audio."

        logger.info(f"Transcribed command: {command_text}")

        # Parse and execute command
        return await _parse_and_execute_command(active_project, command_text)

    except Exception as e:
        logger.error(f"Voice command error: {e}", exc_info=True)
        return f"# Voice Command Failed\n\nError: {e!s}\n\nTry again or check your audio setup."


async def _parse_and_execute_command(active_project, command_text: str) -> dict:
    """Parse voice command and execute appropriate action.

    Uses intelligent rule-based parsing with LLM fallback for complex commands.
    """
    import re

    command_lower = command_text.lower().strip()

    # Pattern matching for common commands
    # Create note commands
    create_patterns = [
        r"(?:create|make|new|add)\s+(?:a\s+)?(?:note|quick\s+note)\s+(?:about|on|for)\s+(.+)",
        r"(?:create|make|new|add)\s+(?:a\s+)?note\s+(.+)",
        r"note\s+(?:about|on)\s+(.+)",
        r"quick\s+note\s+(?:about|on)\s+(.+)",
    ]

    for pattern in create_patterns:
        match = re.search(pattern, command_lower)
        if match:
            topic = match.group(1).strip()
            logger.info(f"Detected create note command: {topic}")
            # Use adn_content quick operation
            from advanced_memory.mcp.tools.content_manager import adn_content

            return await (adn_content.fn if hasattr(adn_content, "fn") else adn_content)(
                operation="quick",
                content=f"# {topic.title()}\n\nVoice command: {command_text}",
                project=active_project.name,
            )

    # Read note commands
    read_patterns = [
        r"(?:read|show|open|get)\s+(?:my\s+)?(?:latest|last|recent)\s+note",
        r"(?:read|show|open|get)\s+(?:the\s+)?(?:latest|last|recent)\s+note",
        r"latest\s+note",
        r"last\s+note",
        r"recent\s+note",
    ]

    for pattern in read_patterns:
        if re.search(pattern, command_lower):
            logger.info("Detected read latest note command")
            from advanced_memory.mcp.tools.content_manager import adn_content

            return await (adn_content.fn if hasattr(adn_content, "fn") else adn_content)(
                operation="read_latest", project=active_project.name
            )

    # Read specific note
    read_specific_patterns = [
        r"(?:read|show|open|get)\s+(?:note\s+)?(?:called|named|titled)?\s+(.+)",
        r"read\s+(.+)",
    ]

    for pattern in read_specific_patterns:
        match = re.search(pattern, command_lower)
        if match:
            note_title = match.group(1).strip()
            logger.info(f"Detected read note command: {note_title}")
            from advanced_memory.mcp.tools.content_manager import adn_content

            return await (adn_content.fn if hasattr(adn_content, "fn") else adn_content)(
                operation="read", identifier=note_title, project=active_project.name
            )

    # Search commands
    search_patterns = [
        r"(?:search|find|look\s+for)\s+(?:notes?\s+)?(?:about|on|for)?\s+(.+)",
        r"search\s+(.+)",
        r"find\s+(.+)",
    ]

    for pattern in search_patterns:
        match = re.search(pattern, command_lower)
        if match:
            query = match.group(1).strip()
            logger.info(f"Detected search command: {query}")
            from advanced_memory.mcp.tools.adn_search import adn_search

            return await (adn_search.fn if hasattr(adn_search, "fn") else adn_search)(
                operation="notes", query=query, project=active_project.name
            )

    # Weather commands
    weather_patterns = [
        r"(?:what'?s|what\s+is)\s+(?:the\s+)?weather\s+(?:like\s+)?(?:in|at|for)?\s*(.+)",
        r"weather\s+(?:in|at|for)?\s*(.+)",
        r"(?:tell\s+me|show\s+me|get)\s+(?:the\s+)?weather\s+(?:in|at|for)?\s*(.+)",
        r"(?:what'?s|what\s+is)\s+(?:the\s+)?weather",
        r"weather",
    ]

    for pattern in weather_patterns:
        match = re.search(pattern, command_lower)
        if match:
            location = match.group(1).strip() if match.groups() and match.group(1) else None
            logger.info(f"Detected weather command: location={location}")
            return await _get_weather(location)

    # Alarm commands
    alarm_patterns = [
        r"(?:set|create|add)\s+(?:an?\s+)?alarm\s+(?:for|at)?\s*(.+)",
        r"alarm\s+(?:for|at)?\s*(.+)",
        r"wake\s+me\s+up\s+(?:at|for)?\s*(.+)",
        r"remind\s+me\s+(?:at|in)?\s*(.+)",
    ]

    for pattern in alarm_patterns:
        match = re.search(pattern, command_lower)
        if match:
            time_str = match.group(1).strip()
            logger.info(f"Detected alarm command: {time_str}")
            return await _set_alarm(time_str)

    # Timer commands
    timer_patterns = [
        r"(?:set|create|start)\s+(?:a\s+)?timer\s+(?:for)?\s*(.+)",
        r"timer\s+(?:for)?\s*(.+)",
        r"countdown\s+(?:for)?\s*(.+)",
    ]

    for pattern in timer_patterns:
        match = re.search(pattern, command_lower)
        if match:
            duration_str = match.group(1).strip()
            logger.info(f"Detected timer command: {duration_str}")
            return await _set_timer(duration_str)

    # Music control commands
    music_patterns = [
        r"(?:play|start)\s+(?:music|song|track)?\s*(?:by|from)?\s*(.+)",
        r"play\s+(.+)",
        r"(?:pause|stop)\s+(?:music|song|track)?",
        r"(?:resume|continue)\s+(?:music|song|track)?",
        r"(?:next|skip)\s+(?:song|track)?",
        r"(?:previous|back)\s+(?:song|track)?",
        r"(?:volume|set\s+volume)\s+(?:to|at)?\s*(\d+)",
        r"music\s+(?:on|off|play|pause|stop)",
    ]

    for pattern in music_patterns:
        match = re.search(pattern, command_lower)
        if match:
            query = match.group(1).strip() if match.groups() and match.group(1) else None
            logger.info(f"Detected music command: {command_lower}, query={query}")
            return await _control_music(command_lower, query)

    # If no pattern matches, try LLM fallback
    try:
        return await _parse_command_with_llm(active_project, command_text)
    except Exception as e:
        logger.debug(f"LLM command parsing failed: {e}, falling back to suggestions")
        return build_success_response(
            operation="listen",
            summary=f"Voice command transcribed but not recognized: '{command_text}'",
            result={
                "transcribed_text": command_text,
                "command_recognized": False,
                "available_commands": [
                    {"pattern": "Create a note about [topic]", "description": "Create a new note"},
                    {"pattern": "Read my latest note", "description": "Read most recent note"},
                    {"pattern": "Read [note title]", "description": "Read specific note"},
                    {"pattern": "Search for [query]", "description": "Search notes"},
                    {"pattern": "Find [query]", "description": "Search notes"},
                    {"pattern": "What's the weather", "description": "Get current weather"},
                    {
                        "pattern": "Weather in [city]",
                        "description": "Get weather for specific location",
                    },
                    {"pattern": "Set alarm for 7 AM", "description": "Set an alarm"},
                    {"pattern": "Set timer for 5 minutes", "description": "Set a timer"},
                    {"pattern": "Play music", "description": "Start playing music"},
                    {"pattern": "Play [song/artist]", "description": "Play specific music"},
                    {"pattern": "Pause music", "description": "Pause playback"},
                    {"pattern": "Next song", "description": "Skip to next track"},
                ],
                "example_commands": [
                    "Create a note about butterflies",
                    "Read my latest note",
                    "Search for epstein scandal",
                    "What's the weather in Vienna",
                    "Set alarm for 8:30 AM",
                    "Set timer for 10 minutes",
                    "Play music",
                    "Play Pink Floyd",
                    "Pause music",
                ],
            },
            next_steps=[
                "Try rephrasing using one of the example patterns",
                "Use the dictate operation to create a note from your speech",
                "Speak more clearly for better recognition",
                "Try shorter, simpler commands first",
            ],
            suggestions=[
                "Use 'dictate' operation for creating notes from speech",
                "Try speaking more slowly and clearly",
                "Use specific note titles when reading",
            ],
        )


async def _parse_command_with_llm(active_project, command_text: str) -> dict:
    """Parse voice command using LLM when rule-based parsing fails.

    Uses the selected LLM provider to understand complex or ambiguous commands.
    """
    try:
        from advanced_memory.services.llm_client import get_llm_client

        llm = get_llm_client()

        system_prompt = """You are a voice command parser for Advanced Memory, a knowledge management system.

Available operations:
1. Create note: "create note about X", "make a note about X"
2. Read note: "read my latest note", "read [note title]"
3. Search: "search for X", "find notes about X"
4. Weather: "what's the weather", "weather in [city]"
5. Alarm: "set alarm for [time]", "wake me up at [time]"
6. Timer: "set timer for [duration]", "timer for 5 minutes"
7. Music: "play music", "play [artist]", "pause music", "next song"

Parse the user's voice command and respond with JSON:
{
  "operation": "create_note|read_note|search|weather|alarm|timer|music|unknown",
  "parameters": {
    "topic": "...",  // for create_note
    "note_title": "...",  // for read_note
    "query": "...",  // for search
    "location": "...",  // for weather
    "time": "...",  // for alarm
    "duration": "...",  // for timer
    "action": "play|pause|next|previous",  // for music
    "query": "..."  // for music play
  }
}

If the command is unclear or doesn't match any operation, use "unknown"."""

        prompt = f'Parse this voice command: "{command_text}"'

        result = await llm.generate_json(prompt, system_prompt, max_tokens=500, temperature=0.3)

        operation = result.get("operation", "unknown")
        params = result.get("parameters", {})

        if operation == "create_note":
            topic = params.get("topic", command_text)
            from advanced_memory.mcp.tools.content_manager import adn_content

            return await (adn_content.fn if hasattr(adn_content, "fn") else adn_content)(
                operation="quick",
                content=f"# {topic}\n\nVoice command: {command_text}",
                project=active_project.name,
            )

        elif operation == "read_note":
            note_title = params.get("note_title")
            if note_title:
                from advanced_memory.mcp.tools.content_manager import adn_content

                return await (adn_content.fn if hasattr(adn_content, "fn") else adn_content)(
                    operation="read", identifier=note_title, project=active_project.name
                )
            else:
                from advanced_memory.mcp.tools.content_manager import adn_content

                return await (adn_content.fn if hasattr(adn_content, "fn") else adn_content)(
                    operation="read_latest", project=active_project.name
                )

        elif operation == "search":
            query = params.get("query", command_text)
            from advanced_memory.mcp.tools.adn_search import adn_search

            return await (adn_search.fn if hasattr(adn_search, "fn") else adn_search)(
                operation="notes", query=query, project=active_project.name
            )

        elif operation == "weather":
            location = params.get("location")
            return await _get_weather(location)

        elif operation == "alarm":
            time_str = params.get("time", command_text)
            return await _set_alarm(time_str)

        elif operation == "timer":
            duration_str = params.get("duration", command_text)
            return await _set_timer(duration_str)

        elif operation == "music":
            action = params.get("action", "play")
            query = params.get("query")
            return await _control_music(f"{action} music", query)

        else:
            # Unknown command, return suggestions
            raise ValueError("Command not recognized by LLM")

    except Exception as e:
        logger.debug(f"LLM parsing failed: {e}")
        raise


async def _get_weather(location: str | None = None) -> dict:
    """Get weather information for a location.

    Uses wttr.in API (free, no API key required) to fetch weather data.

    Args:
        location: City name or location (e.g., "Vienna", "New York", "London").
                 If None, uses IP-based location detection.

    Returns:
        Formatted weather report as markdown string.
    """
    import re

    try:
        import httpx

        # Use wttr.in API (free, no API key needed)
        if location:
            # Clean up location string (remove common words)
            location_clean = location.strip()
            # Remove trailing words like "please", "now", etc.
            location_clean = re.sub(
                r"\s+(please|now|today|right\s+now)$",
                "",
                location_clean,
                flags=re.IGNORECASE,
            )
            url = f"https://wttr.in/{location_clean}?format=j1"
            logger.info(f"Fetching weather for: {location_clean}")
        else:
            url = "https://wttr.in/?format=j1"
            logger.info("Fetching weather for: current location")

        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url)
            if response.status_code == 200:
                data = response.json()

                # Parse wttr.in JSON format
                current = data.get("current_condition", [{}])[0]
                location_info = data.get("nearest_area", [{}])[0]
                area_name = location_info.get("areaName", [{}])[0].get("value", "Unknown")
                country = location_info.get("country", [{}])[0].get("value", "")

                temp_c = current.get("temp_C", "N/A")
                temp_f = current.get("temp_F", "N/A")
                condition = current.get("weatherDesc", [{}])[0].get("value", "Unknown")
                humidity = current.get("humidity", "N/A")
                wind_speed = current.get("windspeedKmph", "N/A")
                wind_dir = current.get("winddir16Point", "N/A")
                feels_like_c = current.get("FeelsLikeC", "N/A")
                feels_like_f = current.get("FeelsLikeF", "N/A")

                # Get today's forecast
                today = data.get("weather", [{}])[0]
                max_temp_c = today.get("maxtempC", "N/A")
                min_temp_c = today.get("mintempC", "N/A")
                max_temp_f = today.get("maxtempF", "N/A")
                min_temp_f = today.get("mintempF", "N/A")

                location_str = f"{area_name}, {country}" if country else area_name

                return build_success_response(
                    operation="weather",
                    summary=f"Current weather for {location_str}",
                    result={
                        "location": location_str,
                        "observation_time": current.get("localObsDateTime", "N/A"),
                        "current_conditions": {
                            "temperature_c": temp_c,
                            "temperature_f": temp_f,
                            "feels_like_c": feels_like_c,
                            "feels_like_f": feels_like_f,
                            "condition": condition,
                            "humidity_percent": humidity,
                            "wind_speed_kmh": wind_speed,
                            "wind_direction": wind_dir,
                        },
                        "today_forecast": {
                            "high_c": max_temp_c,
                            "low_c": min_temp_c,
                            "high_f": max_temp_f,
                            "low_f": min_temp_f,
                        },
                        "data_source": "wttr.in",
                    },
                    next_steps=[
                        "Weather data is current as of observation time",
                        "Use location parameter to check weather in other cities",
                        "Forecast covers today's high and low temperatures",
                    ],
                )
            else:
                return build_error_response(
                    error="weather_fetch_failed",
                    error_code="WEATHER_API_ERROR",
                    message=f"Could not fetch weather data. HTTP status: {response.status_code}",
                    recovery_options=[
                        "Try again in a few moments",
                        "Check the location spelling",
                        "Try a different location",
                        "Verify internet connectivity",
                    ],
                    diagnostic_info={"http_status": response.status_code},
                    urgency="low",
                )

    except httpx.RequestError as e:
        logger.error(f"Weather API error: {e}", exc_info=True)
        return f"# Weather Error\n\nFailed to connect to weather service: {e!s}\n\nPlease check your internet connection and try again."
    except Exception as e:
        logger.error(f"Weather error: {e}", exc_info=True)
        return f"# Weather Error\n\nUnexpected error fetching weather: {e!s}\n\nPlease try again."


async def _set_alarm(time_str: str) -> dict:
    """Set an alarm for a specific time.

    Parses time strings like "7 AM", "8:30 PM", "14:00", etc. and sets an alarm.

    Args:
        time_str: Time string to parse (e.g., "7 AM", "8:30 PM", "14:00")

    Returns:
        Confirmation message with alarm details.
    """
    import re
    from datetime import datetime, timedelta

    global _alarms, _alarm_counter

    try:
        # Parse time string
        time_str_clean = time_str.strip().lower()

        # Try to parse various time formats
        alarm_time = None
        now = datetime.now()

        # Pattern: "7 AM", "8 PM", "7:30 AM", "8:45 PM"
        time_pattern = r"(\d{1,2})(?::(\d{2}))?\s*(am|pm)?"
        match = re.search(time_pattern, time_str_clean)

        if match:
            hour = int(match.group(1))
            minute = int(match.group(2)) if match.group(2) else 0
            am_pm = match.group(3)

            # Convert to 24-hour format
            if am_pm:
                if am_pm == "pm" and hour != 12:
                    hour += 12
                elif am_pm == "am" and hour == 12:
                    hour = 0

            # Set alarm time for today
            alarm_time = now.replace(hour=hour, minute=minute, second=0, microsecond=0)

            # If time has passed today, set for tomorrow
            if alarm_time <= now:
                alarm_time += timedelta(days=1)
        else:
            # Try parsing as 24-hour format "14:00", "8:30"
            time_pattern_24 = r"(\d{1,2}):(\d{2})"
            match_24 = re.search(time_pattern_24, time_str_clean)
            if match_24:
                hour = int(match_24.group(1))
                minute = int(match_24.group(2))
                alarm_time = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
                if alarm_time <= now:
                    alarm_time += timedelta(days=1)

        if not alarm_time:
            return f"""# Alarm Error

Could not parse time: "{time_str}"

**Supported formats:**
- "7 AM" or "7:00 AM"
- "8:30 PM" or "8:30 PM"
- "14:00" (24-hour format)
- "8:30" (24-hour format)

**Examples:**
- "Set alarm for 7 AM"
- "Set alarm for 8:30 PM"
- "Wake me up at 14:00"
"""

        # Calculate seconds until alarm
        seconds_until = (alarm_time - now).total_seconds()

        if seconds_until < 0:
            return build_error_response(
                error="alarm_time_past",
                error_code="ALARM_TIME_PASSED",
                message="The specified alarm time has already passed today",
                recovery_options=[
                    "Specify a future time for the alarm",
                    "Use 24-hour format (e.g., '14:30' for 2:30 PM)",
                    "Check current time and add hours if needed",
                ],
                urgency="low",
            )

        # Create alarm ID
        _alarm_counter += 1
        alarm_id = f"alarm_{_alarm_counter}"

        # Format alarm message
        time_display = alarm_time.strftime("%I:%M %p")
        hours_until = int(seconds_until // 3600)
        minutes_until = int((seconds_until % 3600) // 60)

        # Create background thread for alarm
        def alarm_thread():
            import time

            try:
                time.sleep(seconds_until)
                # Alarm triggered!
                logger.info(f"Alarm {alarm_id} triggered at {alarm_time}")

                # Try to speak the alarm
                try:
                    import pyttsx3

                    engine = pyttsx3.init()
                    engine.say(f"Alarm! It's {time_display}")
                    engine.runAndWait()
                except Exception as e:
                    logger.warning(f"Could not speak alarm: {e}")

                # Remove from active alarms
                _alarms.pop(alarm_id, None)
            except Exception as e:
                logger.error(f"Alarm thread error: {e}", exc_info=True)
                _alarms.pop(alarm_id, None)

        thread = threading.Thread(target=alarm_thread, daemon=True)
        thread.start()

        # Store alarm
        _alarms[alarm_id] = {
            "time": alarm_time,
            "message": f"Alarm for {time_display}",
            "thread": thread,
        }

        return build_success_response(
            operation="alarm",
            summary=f"Alarm set for {time_display} ({alarm_id})",
            result={
                "alarm_id": alarm_id,
                "alarm_time": time_display,
                "hours_until": hours_until,
                "minutes_until": minutes_until,
                "total_seconds_until": seconds_until,
                "status": "active",
            },
            next_steps=[
                "Alarm will sound at the specified time",
                "Use alarm ID to manage this alarm if needed",
                "Alarm will announce the time when triggered",
            ],
        )

    except Exception as e:
        logger.error(f"Alarm error: {e}", exc_info=True)
        return build_error_response(
            error="alarm_setup_failed",
            error_code="ALARM_ERROR",
            message=f"Failed to set alarm: {e!s}",
            recovery_options=[
                "Check time format (use HH:MM or descriptive like '7 AM')",
                "Ensure time is in the future",
                "Try again with a different time",
                "Check system audio settings",
            ],
            diagnostic_info={"error": str(e)},
            urgency="medium",
        )


async def _set_timer(duration_str: str) -> dict:
    """Set a timer for a specific duration.

    Parses duration strings like "5 minutes", "30 seconds", "1 hour", etc. and sets a timer.

    Args:
        duration_str: Duration string to parse (e.g., "5 minutes", "30 seconds", "1 hour")

    Returns:
        Confirmation message with timer details.
    """
    import re

    global _timers, _timer_counter

    try:
        # Parse duration string
        duration_str_clean = duration_str.strip().lower()

        # Pattern: "5 minutes", "30 seconds", "1 hour", "2 hours", etc.
        duration_pattern = r"(\d+)\s*(second|minute|hour|sec|min|hr)s?"
        match = re.search(duration_pattern, duration_str_clean)

        if not match:
            return f"""# Timer Error

Could not parse duration: "{duration_str}"

**Supported formats:**
- "5 minutes" or "5 mins"
- "30 seconds" or "30 secs"
- "1 hour" or "1 hr"
- "2 hours" or "2 hrs"

**Examples:**
- "Set timer for 5 minutes"
- "Timer for 30 seconds"
- "Countdown for 1 hour"
"""

        value = int(match.group(1))
        unit = match.group(2).lower()

        # Convert to seconds
        if unit in ["second", "sec"]:
            seconds = value
        elif unit in ["minute", "min"]:
            seconds = value * 60
        elif unit in ["hour", "hr"]:
            seconds = value * 3600
        else:
            return build_error_response(
                error="invalid_time_unit",
                error_code="TIMER_INVALID_UNIT",
                message=f"Unknown time unit: {unit}",
                recovery_options=[
                    "Use supported units: seconds, minutes, hours",
                    "Examples: '5 minutes', '30 seconds', '1 hour'",
                    "Use singular or plural forms",
                ],
                supported_units=["second", "sec", "minute", "min", "hour", "hr"],
                urgency="low",
            )

        if seconds <= 0:
            return build_error_response(
                error="invalid_duration",
                error_code="TIMER_ZERO_DURATION",
                message="Timer duration must be greater than 0",
                recovery_options=[
                    "Specify a positive duration",
                    "Use formats like '5 minutes' or '30 seconds'",
                    "Minimum duration is 1 second",
                ],
                urgency="low",
            )

        # Create timer ID
        _timer_counter += 1
        timer_id = f"timer_{_timer_counter}"

        # Format duration display
        if seconds < 60:
            display = f"{seconds} second{'s' if seconds != 1 else ''}"
        elif seconds < 3600:
            minutes = seconds // 60
            display = f"{minutes} minute{'s' if minutes != 1 else ''}"
        else:
            hours = seconds // 3600
            minutes = (seconds % 3600) // 60
            if minutes > 0:
                display = f"{hours} hour{'s' if hours != 1 else ''} and {minutes} minute{'s' if minutes != 1 else ''}"
            else:
                display = f"{hours} hour{'s' if hours != 1 else ''}"

        # Create background thread for timer
        def timer_thread():
            import time

            try:
                time.sleep(seconds)
                # Timer triggered!
                logger.info(f"Timer {timer_id} triggered after {display}")

                # Try to speak the timer
                try:
                    import pyttsx3

                    engine = pyttsx3.init()
                    engine.say(f"Timer complete! {display} have passed.")
                    engine.runAndWait()
                except Exception as e:
                    logger.warning(f"Could not speak timer: {e}")

                # Remove from active timers
                _timers.pop(timer_id, None)
            except Exception as e:
                logger.error(f"Timer thread error: {e}", exc_info=True)
                _timers.pop(timer_id, None)

        thread = threading.Thread(target=timer_thread, daemon=True)
        thread.start()

        # Store timer
        _timers[timer_id] = {
            "duration": seconds,
            "message": f"Timer for {display}",
            "thread": thread,
        }

        return build_success_response(
            operation="timer",
            summary=f"Timer set for {display} ({timer_id})",
            result={
                "timer_id": timer_id,
                "duration_display": display,
                "duration_seconds": seconds,
                "status": "running",
            },
            next_steps=[
                "Timer will sound after the specified duration",
                "Use timer ID to manage this timer if needed",
                "Timer will announce completion when triggered",
            ],
        )

    except Exception as e:
        logger.error(f"Timer error: {e}", exc_info=True)
        return build_error_response(
            error="timer_setup_failed",
            error_code="TIMER_ERROR",
            message=f"Failed to set timer: {e!s}",
            recovery_options=[
                "Check duration format (use '5 minutes', '30 seconds', etc.)",
                "Ensure duration is greater than 0",
                "Try again with a different duration",
                "Check system audio settings",
            ],
            diagnostic_info={"error": str(e)},
            urgency="medium",
        )


async def _control_music(command: str, query: str | None = None) -> dict:
    """Control music playback using available music player.

    Supports multiple backends:
    - Plex Media Server API (via python-plexapi) - controls Plexamp and other Plex clients
    - Windows Media Player (via COM) - Windows only
    - Generic system audio controls

    Args:
        command: The voice command (e.g., "play music", "pause", "next")
        query: Optional query for play commands (e.g., artist name, song title)

    Returns:
        Status message about the music control action.
    """
    import platform

    command_lower = command.lower().strip()

    try:
        # Try Plex Media Server API first (controls Plexamp and other Plex clients)
        try:
            return await _control_music_plex(command_lower, query)
        except ImportError:
            # python-plexapi not installed, continue to other backends
            pass
        except Exception as e:
            # Plex API failed, log and try other backends
            logger.debug(f"Plex API not available: {e}")

        # Try Windows Media Player (Windows only)
        if platform.system() == "Windows":
            return await _control_music_windows(command_lower, query)

        # Fallback: Generic message
        return f"""# Music Control

**Status:** Music player not configured

**Available Options:**
1. **Plex Media Server API**: Install `plexapi` to control Plexamp/Plex clients
   - `pip install plexapi`
   - Requires Plex Media Server running and configured
   - Can control Plexamp and other Plex clients
2. **Windows Media Player**: Available on Windows (automatic)
3. **Other Players**: Configure your preferred music player

**Command:** {command}
**Query:** {query if query else "None"}

**To use Plex:**
- Install: `pip install plexapi`
- Configure Plex server connection (auto-detected if on same network)
- Plexamp or other Plex clients will be controlled via the server

**Supported Commands:**
- "Play music" - Start playback
- "Play [artist/song]" - Play specific music
- "Pause music" - Pause playback
- "Resume music" - Resume playback
- "Next song" - Skip to next track
- "Previous song" - Go to previous track
"""

    except Exception as e:
        logger.error(f"Music control error: {e}", exc_info=True)
        return (
            f"# Music Control Error\n\nFailed to control music: {e!s}\n\nPlease check your music player configuration."
        )


async def _control_music_plex(command: str, query: str | None) -> dict:
    """Control music using Plex Media Server API (controls Plexamp and other Plex clients)."""
    try:
        import os

        from plexapi.server import PlexServer

        # Try to connect to Plex server
        # First, try to discover server on local network
        try:
            # Try to find server automatically (requires server name or baseurl)
            # Use environment variables if available
            server_url = os.getenv("PLEX_SERVER_URL", "http://localhost:32400")
            token = os.getenv("PLEX_TOKEN")

            # Try configured/default URL
            try:
                logger.info(f"Connecting to Plex server at {server_url}...")
                server = PlexServer(server_url, token)
            except Exception:
                server = None

            # If that fails, try to discover
            if not server:
                # Note: This requires additional configuration
                # User would need to provide server URL and token
                return """# Plex Configuration Needed

**Status:** Plex server connection not configured

**Setup Required:**
1. Install: `pip install plexapi`
2. Configure Plex server connection:
   - Server URL (e.g., http://localhost:32400)
   - Authentication token (get from Plex web interface)

**Quick Setup:**
- Get token from: https://www.plex.tv/desktop/
- Or use environment variables: PLEX_SERVER_URL, PLEX_TOKEN

**Note:** Plexamp and other Plex clients are controlled via the Plex Media Server API.
"""

            # Find music clients (Plexamp, Plex clients, etc.)
            clients = server.clients()
            music_clients = [c for c in clients if c.product in ["Plexamp", "Plex Web", "Plex Media Player"]]

            if not music_clients:
                return """# No Plex Clients Found

**Status:** No Plex music clients available

**To use:**
1. Open Plexamp or another Plex client
2. Make sure it's connected to your Plex server
3. Try the command again

**Supported Clients:**
- Plexamp
- Plex Web
- Plex Media Player
"""

            # Use first available client (or could let user choose)
            client = music_clients[0]

            if "play" in command:
                if query:
                    # Search for music and play
                    results = server.search(query, mediatype="track", limit=10)
                    if not results:
                        # Try artist search
                        artists = server.search(query, mediatype="artist", limit=5)
                        if artists:
                            # Play artist's music
                            client.playMedia(artists[0])
                            return f"""# Music Playing

**Player:** {client.product} ({client.title})
**Action:** Playing "{artists[0].title}"

Started playing music by {artists[0].title}.
"""
                        return f"""# Music Not Found

Could not find music matching "{query}".

**Try:**
- Artist name
- Song title
- Album name
"""
                    # Play first result
                    client.playMedia(results[0])
                    return f"""# Music Playing

**Player:** {client.product} ({client.title})
**Action:** Playing "{results[0].title}" by {results[0].artist().title if hasattr(results[0], "artist") else "Unknown"}

Started playing: {results[0].title}
"""
                else:
                    # Resume playback
                    client.play()
                    return f"""# Music Playing

**Player:** {client.product} ({client.title})
**Action:** Resumed playback

Playback resumed.
"""

            elif "pause" in command or "stop" in command:
                client.pause()
                return f"""# Music Paused

**Player:** {client.product} ({client.title})
**Action:** Paused playback

Playback paused.
"""

            elif "resume" in command or "continue" in command:
                client.play()
                return f"""# Music Resumed

**Player:** {client.product} ({client.title})
**Action:** Resumed playback

Playback resumed.
"""

            elif "next" in command or "skip" in command:
                client.skipNext()
                return f"""# Music Skipped

**Player:** {client.product} ({client.title})
**Action:** Skipped to next track

Skipped to next track.
"""

            elif "previous" in command or "back" in command:
                client.skipPrevious()
                return f"""# Music Previous

**Player:** {client.product} ({client.title})
**Action:** Previous track

Went to previous track.
"""

            else:
                return f"# Music Command Not Recognized\n\nCommand: {command}\n\nSupported: play, pause, resume, next, previous"

        except ImportError:
            raise ImportError("plexapi not installed")
        except Exception as e:
            logger.error(f"Plex API error: {e}", exc_info=True)
            raise

    except ImportError:
        raise  # Re-raise to be caught by caller
    except Exception as e:
        logger.error(f"Plex control error: {e}", exc_info=True)
        return (
            f"# Music Error\n\nFailed to control Plex: {e!s}\n\nMake sure Plex Media Server is running and accessible."
        )


async def _control_music_windows(command: str, query: str | None) -> dict:
    """Control music using Windows Media Player COM interface."""
    try:
        import win32com.client

        # Try to get Windows Media Player
        try:
            wmp = win32com.client.Dispatch("WMPlayer.OCX")
        except Exception:
            return """# Music Control

**Status:** Windows Media Player not available

**Options:**
1. Install Windows Media Player (usually pre-installed)
2. Use Plexamp CLI instead
3. Configure another music player

**Note:** This feature requires Windows Media Player COM interface.
"""

        if "play" in command:
            if query:
                # Try to play specific media (this is limited with WMP)
                return f"""# Music Control

**Player:** Windows Media Player
**Action:** Play "{query}"

**Note:** Windows Media Player COM doesn't support direct search/play by query.
Please use Plexamp CLI for better control, or manually select the media in WMP.

**Alternative:** Use "Play music" to resume current playlist.
"""
            else:
                # Play/resume
                wmp.controls.play()
                return """# Music Playing

**Player:** Windows Media Player
**Action:** Resumed playback

Playback has been resumed.
"""

        elif "pause" in command or "stop" in command:
            wmp.controls.pause()
            return """# Music Paused

**Player:** Windows Media Player
**Action:** Paused playback

Playback has been paused.
"""

        elif "resume" in command or "continue" in command:
            wmp.controls.play()
            return """# Music Resumed

**Player:** Windows Media Player
**Action:** Resumed playback

Playback has been resumed.
"""

        elif "next" in command or "skip" in command:
            wmp.controls.next()
            return """# Music Skipped

**Player:** Windows Media Player
**Action:** Skipped to next track

Skipped to next track.
"""

        elif "previous" in command or "back" in command:
            wmp.controls.previous()
            return """# Music Previous

**Player:** Windows Media Player
**Action:** Previous track

Went to previous track.
"""

        else:
            return f"# Music Command Not Recognized\n\nCommand: {command}\n\nSupported: play, pause, resume, next, previous"

    except ImportError:
        return """# Music Control

**Status:** Windows Media Player control requires pywin32

**Install:**
pip install pywin32

**Or use Plexamp CLI instead** (recommended for better control).
"""
    except Exception as e:
        logger.error(f"Windows Media Player control error: {e}", exc_info=True)
        return f"# Music Error\n\nFailed to control Windows Media Player: {e!s}\n\nTry using Plexamp CLI instead."


async def _wake_word_operation(active_project, wake_word: str, record_duration: int) -> dict:
    """Handle wake word operation - continuously listens for wake word, then records and executes command.

    Monitors audio input for the wake word (e.g., "memorizer"), and when detected,
    records the following command and executes it.
    """
    try:
        import numpy as np
        import sounddevice as sd
        import soundfile as sf
        from faster_whisper import WhisperModel
    except ImportError:
        return """# Voice Features Not Available

Wake word listening requires optional voice dependencies (faster-whisper).

INSTALL:
pip install faster-whisper onnxruntime-gpu sounddevice soundfile numpy

Then restart and try again!"""

    from pathlib import Path

    wake_word_lower = wake_word.lower().strip()
    sample_rate = 16000  # Whisper works best at 16kHz
    chunk_duration = 1.0  # Check for wake word every 1 second
    chunk_samples = int(chunk_duration * sample_rate)

    logger.info(f"Starting wake word listener for '{wake_word}'...")
    logger.info("Listening... (say the wake word followed by your command)")

    try:
        # Load Whisper model once
        model = WhisperModel("base", device="cuda", compute_type="float16")

        # Continuous listening loop
        wake_word_detected = False
        command_audio_chunks = []

        while True:
            # Record a small chunk
            chunk = sd.rec(chunk_samples, samplerate=sample_rate, channels=1, dtype="float32")
            sd.wait()

            if wake_word_detected:
                # We're recording the command
                command_audio_chunks.append(chunk)
                logger.debug(f"Recording command chunk {len(command_audio_chunks)}...")

                # Check if we should stop recording (after record_duration)
                if len(command_audio_chunks) * chunk_duration >= record_duration:
                    # Process the command
                    logger.info("Wake word detected, processing command...")

                    # Combine all chunks
                    command_audio = np.concatenate(command_audio_chunks, axis=0)

                    # Save to temp file
                    temp_audio = Path.home() / ".advanced-memory" / "temp_wake_command.wav"
                    temp_audio.parent.mkdir(parents=True, exist_ok=True)
                    sf.write(temp_audio, command_audio, sample_rate)

                    # Transcribe and execute
                    segments, info = model.transcribe(str(temp_audio), beam_size=5)
                    command_text = " ".join([segment.text for segment in segments]).strip().lower()

                    if command_text:
                        logger.info(f"Transcribed command: {command_text}")
                        return await _parse_and_execute_command(active_project, command_text)
                    else:
                        return "# No Command Detected\n\nWake word detected but no command was heard. Try again."

            else:
                # Check for wake word in this chunk
                temp_chunk_file = Path.home() / ".advanced-memory" / "temp_wake_check.wav"
                temp_chunk_file.parent.mkdir(parents=True, exist_ok=True)
                sf.write(temp_chunk_file, chunk, sample_rate)

                # Quick transcription to check for wake word
                segments, info = model.transcribe(str(temp_chunk_file), beam_size=5)
                transcribed = " ".join([segment.text for segment in segments]).strip().lower()

                if wake_word_lower in transcribed:
                    logger.info(f"Wake word '{wake_word}' detected!")
                    wake_word_detected = True
                    command_audio_chunks = []  # Start fresh recording
                    # Continue to next iteration to start recording command

    except KeyboardInterrupt:
        return "# Wake Word Listener Stopped\n\nWake word listening was interrupted."
    except Exception as e:
        logger.error(f"Wake word error: {e}", exc_info=True)
        return f"# Wake Word Error\n\nError: {e!s}\n\nCheck your audio setup and try again."


async def _wake_start_operation(active_project, wake_word: str, record_duration: int) -> dict:
    """Start wake word listener in background thread."""
    global _wake_listener_thread, _wake_listener_stop_event, _wake_listener_running

    if _wake_listener_running:
        return f"""# Wake Word Listener Already Running

The wake word listener is already running.

**Status:**
- Wake word: {wake_word}
- Running: Yes

**To stop:** Use `adn_audio("wake_stop")`
**To check status:** Use `adn_audio("wake_status")`
"""

    # Reset stop event
    _wake_listener_stop_event.clear()

    # Start listener in background thread
    def run_listener():
        global _wake_listener_running
        _wake_listener_running = True
        try:
            import asyncio

            # Create new event loop for this thread
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                # Run the wake word operation with stop event
                loop.run_until_complete(
                    _wake_word_operation_background(
                        active_project,
                        wake_word,
                        record_duration,
                        _wake_listener_stop_event,
                    )
                )
            finally:
                loop.close()
        finally:
            _wake_listener_running = False

    _wake_listener_thread = threading.Thread(target=run_listener, daemon=True)
    _wake_listener_thread.start()

    return f"""# Wake Word Listener Started

**Status:** Running in background
**Wake word:** "{wake_word}"
**Command duration:** {record_duration} seconds

**Usage:**
1. Say "{wake_word}" followed by your command
2. Example: "{wake_word} create a note about butterflies"

**To stop:** `adn_audio("wake_stop")`
**To check status:** `adn_audio("wake_status")`

The listener will continue running until you stop it.
"""


async def _wake_stop_operation() -> dict:
    """Stop the running wake word listener."""
    global _wake_listener_thread, _wake_listener_stop_event, _wake_listener_running

    if not _wake_listener_running:
        return """# Wake Word Listener Not Running

No wake word listener is currently running.

**To start:** Use `adn_audio("wake_start", wake_word="memorizer")`
"""

    # Signal stop
    _wake_listener_stop_event.set()

    # Wait for thread to finish (with timeout)
    if _wake_listener_thread and _wake_listener_thread.is_alive():
        _wake_listener_thread.join(timeout=2.0)

    _wake_listener_running = False
    _wake_listener_thread = None

    return """# Wake Word Listener Stopped

The wake word listener has been stopped.

**To start again:** Use `adn_audio("wake_start", wake_word="memorizer")`
"""


async def _wake_status_operation() -> dict:
    """Check wake word listener status."""
    global _wake_listener_running, _wake_listener_thread

    if _wake_listener_running:
        thread_status = "alive" if (_wake_listener_thread and _wake_listener_thread.is_alive()) else "dead"
        return f"""# Wake Word Listener Status

**Status:** Running
**Thread:** {thread_status}

**To stop:** Use `adn_audio("wake_stop")`
"""
    else:
        return """# Wake Word Listener Status

**Status:** Not running

**To start:** Use `adn_audio("wake_start", wake_word="memorizer")`
"""


async def _wake_word_operation_background(
    active_project, wake_word: str, record_duration: int, stop_event: threading.Event
) -> None:
    """Background wake word listener that respects stop event."""
    try:
        import numpy as np
        import sounddevice as sd
        import soundfile as sf
        from faster_whisper import WhisperModel
    except ImportError:
        logger.error("Voice dependencies not available for wake word listener")
        return

    from pathlib import Path

    wake_word_lower = wake_word.lower().strip()
    sample_rate = 16000
    chunk_duration = 1.0
    chunk_samples = int(chunk_duration * sample_rate)

    logger.info(f"Starting wake word listener for '{wake_word}' in background...")

    try:
        # Load Whisper model once
        model = WhisperModel("base", device="cuda", compute_type="float16")

        wake_word_detected = False
        command_audio_chunks = []

        while not stop_event.is_set():
            # Record a small chunk
            chunk = sd.rec(chunk_samples, samplerate=sample_rate, channels=1, dtype="float32")
            sd.wait()

            # Check if we should stop
            if stop_event.is_set():
                logger.info("Wake word listener stopped by user")
                break

            if wake_word_detected:
                # We're recording the command
                command_audio_chunks.append(chunk)
                logger.debug(f"Recording command chunk {len(command_audio_chunks)}...")

                # Check if we should stop recording (after record_duration)
                if len(command_audio_chunks) * chunk_duration >= record_duration:
                    # Process the command
                    logger.info("Wake word detected, processing command...")

                    # Combine all chunks
                    command_audio = np.concatenate(command_audio_chunks, axis=0)

                    # Save to temp file
                    temp_audio = Path.home() / ".advanced-memory" / "temp_wake_command.wav"
                    temp_audio.parent.mkdir(parents=True, exist_ok=True)
                    sf.write(temp_audio, command_audio, sample_rate)

                    # Transcribe and execute
                    segments, info = model.transcribe(str(temp_audio), beam_size=5)
                    command_text = " ".join([segment.text for segment in segments]).strip().lower()

                    if command_text:
                        logger.info(f"Transcribed command: {command_text}")
                        # Execute command (this will run in the background thread's event loop)
                        await _parse_and_execute_command(active_project, command_text)

                    # Reset for next wake word
                    wake_word_detected = False
                    command_audio_chunks = []

            else:
                # Check for wake word in this chunk
                temp_chunk_file = Path.home() / ".advanced-memory" / "temp_wake_check.wav"
                temp_chunk_file.parent.mkdir(parents=True, exist_ok=True)
                sf.write(temp_chunk_file, chunk, sample_rate)

                # Quick transcription to check for wake word
                segments, info = model.transcribe(str(temp_chunk_file), beam_size=5)
                transcribed = " ".join([segment.text for segment in segments]).strip().lower()

                if wake_word_lower in transcribed:
                    logger.info(f"Wake word '{wake_word}' detected!")
                    wake_word_detected = True
                    command_audio_chunks = []

    except Exception as e:
        logger.error(f"Wake word listener error: {e}", exc_info=True)
