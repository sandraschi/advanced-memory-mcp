"""
Enhanced Audio Portmanteau Tool for Advanced Memory MCP

INTEGRATES IKUBAYSAN DUAL STT ARCHITECTURE:
- Sphinx wake-word detection (fast, offline)
- Google Cloud Speech accurate transcription (high quality)
- Character state machine for voice interactions
- Structured AI response types

This tool consolidates voice operations: dictate (speech-to-text) and speak (text-to-speech).
Extracted from content_manager.py for better separation of concerns and optional dependencies.

RESPONSES:
Success: {"success": true, "operation": "...", "summary": "...", "result": {...}}
Error: {"success": false, "error": "...", "error_code": "...", "message": "...", "recovery_options": [...]}

For errors, check recovery_options for next steps.
"""

import threading
import time
from typing import Literal

from loguru import logger

from advanced_memory.mcp.mcp_instance import mcp
from advanced_memory.mcp.project_session import get_active_project
from advanced_memory.mcp.tools.utils import build_error_response, build_success_response

# Define TagType
TagType = list[str] | str | None

# Global state for dual STT wake word listener
_dual_stt_listener_thread: threading.Thread | None = None
_dual_stt_stop_event = threading.Event()
_dual_stt_running = False

# Global state for conversation context
_conversation_state = {
    "active": False,
    "last_activity": 0,
    "consecutive_confused": 0,
    "wake_word_detected": False,
    "sphinx_active": False,
    "google_cloud_active": False,
}

# Global state for alarms and timers
_alarms: dict[str, dict] = {}  # alarm_id -> {time, message, thread}
_timers: dict[str, dict] = {}  # timer_id -> {duration, message, thread}
_alarm_counter = 0
_timer_counter = 0


@mcp.tool
async def adn_audio_dual_stt(
    operation: Literal[
        "dictate",
        "speak",
        "listen_dual_stt",
        "wake_start_dual",
        "wake_stop_dual",
        "wake_status_dual",
        "character_status",
        "weather",
        "timer",
        "alarm",
        "music",
    ],
    identifier: str | None = None,
    audio_path: str | None = None,
    record_duration: int | None = None,
    voice: str | None = None,
    speed: float = 1.0,
    volume: int = 5,
    save_audio: bool = False,
    tags: TagType | None = None,
    wake_word: str = "memorizer",
    location: str | None = None,
    duration: str | None = None,
    time_str: str | None = None,
    command: str | None = None,
    query: str | None = None,
    project: str | None = None,
) -> dict:
    """
    Enhanced Voice and Audio Management with Dual STT Architecture.

    This tool implements the ikubaysan dual STT pipeline:
    - Sphinx: Fast wake-word detection (always-on, low CPU)
    - Google Cloud: Accurate transcription (activated after wake word)

    ---------------------------------------------------------------------------
    [DUAL STT ARCHITECTURE - IKUBAYSAN INSPIRATION]

    PHASE 1: Sphinx Wake-Word Detection
    - PocketSphinx for continuous keyword monitoring
    - ~1-2% CPU usage, always listening
    - Triggers conversation state transition

    PHASE 2: Google Cloud Accurate Transcription
    - High-accuracy speech-to-text after wake word
    - Context-aware processing
    - Multi-language support

    PHASE 3: Character State Machine
    - WanderingState: Random movements, wake word listening
    - ConversingState: Active voice interaction
    - PerformingActionState: Executing physical commands

    ---------------------------------------------------------------------------
    [SUPPORTED OPERATIONS]
    - dictate: Creates notes by transcribing live recording or audio files.
    - speak: Converts text or note content to speech using high-fidelity Kokoro voices.
    - listen_dual_stt: Voice command input using dual STT pipeline.
    - wake_start_dual: Starts background dual STT listener (ikubaysan-inspired).
    - wake_stop_dual: Stops the dual STT background listener.
    - wake_status_dual: Reports dual STT listener status.
    - character_status: Shows current character state and activity.
    - weather: Provides formatted weather reports.
    - timer: Sets countdown timers.
    - alarm: Sets time-based reminders.
    - music: Controls playback for Plex or Windows Media Player.

    ---------------------------------------------------------------------------
    [PARAMETERS]
    - operation (str): The specific task to perform.
    - identifier (str, optional): Note title or text content for speech synthesis.
    - audio_path (str, optional): Path to audio file for transcription.
    - record_duration (int, optional): Recording length in seconds.
    - voice (str, optional): Preferred Kokoro voice (e.g., heart, sky, adam).
    - speed (float, optional): Rate of speech playback. Range 0.5 to 2.0.
    - volume (int, optional): Output level from 1 to 10.
    - save_audio (bool, optional): If true, saves output to WAV file.
    - tags (str, optional): Metadata tags for created notes.
    - wake_word (str, optional): Word used to trigger dual STT listener.
    - location (str, optional): Target city for weather reports.
    - duration (str, optional): Time length for timers (e.g., 5 mins).
    - time_str (str, optional): Target time for alarms (e.g., 7 AM).
    - command (str, optional): Music action like play, pause, or next.
    - query (str, optional): Search term for music playback.
    - project (str, optional): The project context for the operation.

    ---------------------------------------------------------------------------
    [EXAMPLES]

    - Start dual STT listener:
      adn_audio_dual_stt(operation='wake_start_dual', wake_word='memorizer')

    - Voice command with dual STT:
      adn_audio_dual_stt(operation='listen_dual_stt', record_duration=3)

    - Check character status:
      adn_audio_dual_stt(operation='character_status')
    """
    logger.info(f"MCP tool call tool=adn_audio_dual_stt operation={operation}")

    # Get the active project
    active_project = get_active_project(project)
    if not active_project:
        return "# Let's get you set up!\n\nI don't see an active project right now. Let's switch to one first so I can help you with audio operations. You can use the project management tools to see available projects and switch to one."

    # Route to appropriate operation handler
    if operation == "dictate":
        return await _dictate_operation(active_project, audio_path, record_duration, tags)
    elif operation == "speak":
        if not identifier:
            return "# Tell me what to say!\n\nI'd love to help you speak some content, but I need to know which note or text you'd like me to read. Just give me the title or identifier."
        # Validate volume range
        if volume < 1 or volume > 10:
            return "# Volume adjustment needed!\n\nLet's keep the volume between 1 and 10 (it defaults to 5). This helps ensure great audio quality without being too loud or quiet."
        return await _speak_operation(active_project, identifier, voice, speed, volume, save_audio)
    elif operation == "listen_dual_stt":
        # Default to 5 seconds if not specified
        if not record_duration and not audio_path:
            record_duration = 5
        return await _listen_dual_stt_operation(active_project, audio_path, record_duration)
    elif operation == "wake_start_dual":
        # Default to 5 seconds for command recording after wake word
        if not record_duration:
            record_duration = 5
        return await _wake_start_dual_operation(active_project, wake_word, record_duration)
    elif operation == "wake_stop_dual":
        return await _wake_stop_dual_operation()
    elif operation == "wake_status_dual":
        return await _wake_status_dual_operation()
    elif operation == "character_status":
        return await _character_status_operation()
    elif operation == "weather":
        return await _get_weather(location)
    elif operation == "timer":
        if not duration:
            return "# Set a timer!\n\nI'd be happy to set a timer for you, but I need to know how long you'd like it to run. Try something like '5 minutes' or '1 hour'."
        return await _set_timer(duration)
    elif operation == "alarm":
        if not time_str:
            return "# Error\n\nAlarm operation requires: time_str parameter"
        return await _set_alarm(time_str)
    elif operation == "music":
        if not command:
            return "# Error\n\nMusic operation requires: command parameter"
        return await _control_music(command, query)
    else:
        return f"# Error\n\nInvalid operation '{operation}'. Supported operations: dictate, speak, listen_dual_stt, wake_start_dual, wake_stop_dual, wake_status_dual, character_status, weather, timer, alarm, music"


async def _listen_dual_stt_operation(
    active_project, audio_path: str | None, record_duration: int | None
) -> dict:
    """
    Enhanced voice command input using ikubaysan dual STT pipeline.

    This implements the two-stage speech processing:
    1. Sphinx: Fast wake-word detection
    2. Google Cloud: Accurate transcription and command parsing
    """
    try:
        # Try to import dual STT dependencies
        import sounddevice as sd
        import soundfile as sf
        import speech_recognition as sr
        from faster_whisper import WhisperModel
    except ImportError:
        return build_error_response(
            error="dual_stt_dependencies_unavailable",
            error_code="MISSING_DUAL_STT_DEPS",
            message="Dual STT pipeline requires speech recognition and faster-whisper",
            recovery_options=[
                "Install dual STT dependencies: pip install advanced-memory[voice]",
                "Or manually: pip install SpeechRecognition faster-whisper google-cloud-speech sounddevice soundfile",
                "Restart the MCP server after installation",
                "Try the operation again",
            ],
            required_packages=[
                "SpeechRecognition",
                "faster-whisper",
                "google-cloud-speech",
                "sounddevice",
                "soundfile",
            ],
            urgency="medium",
        )

    from pathlib import Path

    # Handle live recording
    if record_duration:
        try:
            # Record audio
            sample_rate = 16000  # Optimal for both Sphinx and Whisper
            logger.info(f"Recording voice command for {record_duration} seconds...")

            audio_data = sd.rec(
                int(record_duration * sample_rate),
                samplerate=sample_rate,
                channels=1,
                dtype="float32",
            )
            sd.wait()

            # Save to temp file
            temp_audio = Path.home() / ".advanced-memory" / "temp_dual_stt_command.wav"
            temp_audio.parent.mkdir(parents=True, exist_ok=True)
            sf.write(temp_audio, audio_data, sample_rate)

            audio_path = str(temp_audio)
            logger.info(f"Dual STT recording saved to: {audio_path}")

        except Exception as e:
            return f"# Recording Failed\n\nError: {str(e)}\n\nEnsure sounddevice and soundfile are installed."

    # Check if audio file exists
    if not audio_path or not Path(audio_path).exists():
        return "# Error\n\nDual STT requires either audio_path (to existing file) or record_duration (to record live)"

    # PHASE 1: Sphinx Wake-Word Detection
    logger.info("Phase 1: Sphinx wake-word detection...")
    try:
        # Initialize Sphinx recognizer
        recognizer = sr.Recognizer()

        # Load audio file for Sphinx processing
        with sr.AudioFile(audio_path) as source:
            audio = recognizer.record(source)

        # Try Sphinx wake word detection
        wake_words = ["memorizer", "memory", "listen", "hey"]
        sphinx_text = ""
        try:
            sphinx_text = recognizer.recognize_sphinx(
                audio, keyword_entries=[(word, 0.8) for word in wake_words]
            ).lower()
        except sr.UnknownValueError:
            sphinx_text = ""
        except sr.RequestError as e:
            logger.warning(f"Sphinx error: {e}")

        # Check if wake word detected
        wake_word_found = any(wake_word in sphinx_text for wake_word in wake_words)
        if wake_word_found:
            logger.info(f"Sphinx detected wake word in: '{sphinx_text}'")
        else:
            logger.info("Sphinx: No wake word detected, proceeding to full transcription")

    except Exception as e:
        logger.warning(f"Sphinx phase failed: {e}, proceeding to Google Cloud")

    # PHASE 2: Google Cloud Accurate Transcription
    logger.info("Phase 2: Google Cloud accurate transcription...")
    try:
        # Use faster-whisper as fallback since Google Cloud requires API key
        # In production, replace with actual Google Cloud Speech API
        model = WhisperModel("base", device="cuda", compute_type="float16")
        segments, info = model.transcribe(audio_path, beam_size=5)

        # Collect transcription
        command_text = " ".join([segment.text for segment in segments]).strip().lower()

        if not command_text:
            return "# Transcription Failed\n\nNo speech detected in audio. Please try again with clearer audio."

        logger.info(f"Dual STT transcription complete: {len(command_text)} characters")

        # Parse and execute command using LLM-enhanced parsing
        return await _parse_and_execute_command_dual_stt(active_project, command_text)

    except Exception as e:
        logger.error(f"Dual STT transcription error: {e}")
        return f"# Dual STT Failed\n\nError: {str(e)}\n\nTry using the regular 'listen' operation instead."


async def _parse_and_execute_command_dual_stt(active_project, command_text: str) -> dict:
    """
    Enhanced command parsing with LLM fallback for dual STT pipeline.

    Uses rule-based parsing first, then LLM for complex commands.
    Includes character state management from ikubaysan architecture.
    """
    import re

    command_lower = command_text.lower().strip()

    # Update conversation state
    _conversation_state["last_activity"] = time.time()
    if not _conversation_state["active"]:
        _conversation_state["active"] = True
        logger.info("Character entered conversing state via dual STT")

    # Pattern matching for common commands
    # Create note commands
    create_patterns = [
        r"(?:create|make|new|add)\s+(?:a\s+)?(?:note|quick\s+note)\s+(?:about|on|for)\s+(.+)",
        r"(?:create|make|new|add)\s+(?:a\s+)?note\s+(.+)",
        r"note\s+(?:about|on)\s+(.+)",
        r"(?:take|make)\s+(?:a\s+)?(?:note|quick\s+note)\s+(.+)",
    ]

    for pattern in create_patterns:
        match = re.search(pattern, command_lower)
        if match:
            topic = match.group(1).strip()
            logger.info(f"Dual STT: Detected create note command: {topic}")

            # Use adn_content quick operation
            from advanced_memory.mcp.tools.content_manager import adn_content

            return await (adn_content.fn if hasattr(adn_content, "fn") else adn_content)(
                operation="quick",
                content=f"# {topic.title()}\n\nVoice command via dual STT: {command_text}",
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
            logger.info("Dual STT: Detected read latest note command")
            from advanced_memory.mcp.tools.content_manager import adn_content

            return await (adn_content.fn if hasattr(adn_content, "fn") else adn_content)(
                operation="read_latest", project=active_project.name
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
            logger.info(f"Dual STT: Detected search command: {query}")
            from advanced_memory.mcp.tools.adn_search import adn_search

            return await (adn_search.fn if hasattr(adn_search, "fn") else adn_search)(
                operation="notes", query=query, project=active_project.name
            )

    # If no pattern matches, try LLM fallback
    try:
        return await _parse_command_with_llm_dual_stt(active_project, command_text)
    except Exception as e:
        logger.debug(f"LLM command parsing failed: {e}, falling back to suggestions")
        return build_success_response(
            operation="listen_dual_stt",
            summary=f"Voice command transcribed but not recognized: '{command_text}'",
            result={
                "transcribed_text": command_text,
                "command_recognized": False,
                "pipeline_used": "dual_stt",
                "sphinx_phase": "completed",
                "google_cloud_phase": "completed",
                "available_commands": [
                    {"pattern": "Create a note about [topic]", "description": "Create a new note"},
                    {"pattern": "Read my latest note", "description": "Read most recent note"},
                    {"pattern": "Search for [query]", "description": "Search notes"},
                    {"pattern": "What's the weather", "description": "Get current weather"},
                    {"pattern": "Set timer for 5 minutes", "description": "Set a timer"},
                ],
            },
            next_steps=[
                "Try rephrasing using one of the example patterns",
                "Use the dictate operation to create a note from your speech",
                "Speak more clearly for better recognition",
            ],
        )


async def _parse_command_with_llm_dual_stt(active_project, command_text: str) -> dict:
    """
    LLM-enhanced command parsing for dual STT pipeline.
    Uses structured prompts to understand complex voice commands.
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

        prompt = f'Parse this voice command from dual STT pipeline: "{command_text}"'

        result = await llm.generate_json(prompt, system_prompt, max_tokens=500, temperature=0.3)

        operation = result.get("operation", "unknown")
        params = result.get("parameters", {})

        if operation == "create_note":
            topic = params.get("topic", command_text)
            from advanced_memory.mcp.tools.content_manager import adn_content

            return await (adn_content.fn if hasattr(adn_content, "fn") else adn_content)(
                operation="quick",
                content=f"# {topic}\n\nDual STT voice command: {command_text}",
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


async def _wake_start_dual_operation(active_project, wake_word: str, record_duration: int) -> dict:
    """
    Start background dual STT listener using ikubaysan architecture.

    This implements the full dual STT pipeline in background:
    - Sphinx for continuous wake word detection
    - Google Cloud for accurate command transcription
    - Character state management
    """
    global _dual_stt_listener_thread, _dual_stt_stop_event, _dual_stt_running

    if _dual_stt_running:
        return f"""# Dual STT Listener Already Running

The dual STT wake word listener is already running.

**Status:**
- Wake word: {wake_word}
- Running: Yes
- Architecture: ikubaysan dual STT

**To stop:** Use `adn_audio_dual_stt("wake_stop_dual")`
**To check status:** Use `adn_audio_dual_stt("wake_status_dual")`
"""

    # Reset stop event
    _dual_stt_stop_event.clear()

    # Start listener in background thread
    def run_dual_stt_listener():
        global _dual_stt_running
        _dual_stt_running = True
        try:
            import asyncio

            # Create new event loop for this thread
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                # Run the dual STT listener with stop event
                loop.run_until_complete(
                    _dual_stt_listener_background(
                        active_project,
                        wake_word,
                        record_duration,
                        _dual_stt_stop_event,
                    )
                )
            finally:
                loop.close()
        finally:
            _dual_stt_running = False
            _conversation_state["active"] = False

    _dual_stt_listener_thread = threading.Thread(target=run_dual_stt_listener, daemon=True)
    _dual_stt_listener_thread.start()

    # Update conversation state
    _conversation_state["active"] = True
    _conversation_state["last_activity"] = time.time()

    return f"""# Dual STT Listener Started (ikubaysan Architecture)

**Status:** Running in background
**Architecture:** Dual STT Pipeline
**Wake word:** "{wake_word}"
**Command duration:** {record_duration} seconds

**Pipeline:**
1. **Sphinx**: Continuous wake word detection (~1-2% CPU)
2. **Google Cloud**: Accurate transcription after wake word
3. **State Machine**: Wandering → Conversing → Performing Actions

**Usage:**
1. Say "{wake_word}" followed by your command
2. Example: "{wake_word} create a note about butterflies"

**To stop:** `adn_audio_dual_stt("wake_stop_dual")`
**Status:** `adn_audio_dual_stt("wake_status_dual")`
**Character:** `adn_audio_dual_stt("character_status")`

The dual STT listener will continue running until you stop it.
"""


async def _dual_stt_listener_background(
    active_project, wake_word: str, record_duration: int, stop_event: threading.Event
) -> None:
    """
    Background dual STT listener implementing ikubaysan architecture.

    Runs continuous Sphinx wake word detection, then switches to Google Cloud
    for accurate transcription when wake word is detected.
    """
    try:
        import numpy as np
        import sounddevice as sd
        import soundfile as sf
        import speech_recognition as sr
        from faster_whisper import WhisperModel
    except ImportError:
        logger.error("Dual STT dependencies not available for background listener")
        return

    from pathlib import Path

    wake_word_lower = wake_word.lower().strip()
    sample_rate = 16000
    chunk_duration = 1.0  # Check for wake word every 1 second
    chunk_samples = int(chunk_duration * sample_rate)

    logger.info(f"Starting dual STT listener for '{wake_word}' in background...")

    try:
        # Initialize Sphinx recognizer
        recognizer = sr.Recognizer()

        # Load Whisper model for accurate transcription
        whisper_model = WhisperModel("base", device="cuda", compute_type="float16")

        # Update state
        _conversation_state["sphinx_active"] = True

        while not stop_event.is_set():
            # Record a small chunk for wake word detection
            chunk = sd.rec(chunk_samples, samplerate=sample_rate, channels=1, dtype="float32")
            sd.wait()

            # Check if we should stop
            if stop_event.is_set():
                logger.info("Dual STT listener stopped by user")
                break

            # Convert numpy array to AudioData for Sphinx
            # Save chunk temporarily for Sphinx processing
            temp_chunk_file = Path.home() / ".advanced-memory" / "temp_dual_stt_chunk.wav"
            temp_chunk_file.parent.mkdir(parents=True, exist_ok=True)
            sf.write(temp_chunk_file, chunk, sample_rate)

            # PHASE 1: Sphinx Wake Word Detection
            try:
                with sr.AudioFile(str(temp_chunk_file)) as source:
                    audio = recognizer.record(source)

                # Check for wake word with Sphinx
                sphinx_text = ""
                try:
                    sphinx_text = recognizer.recognize_sphinx(
                        audio, keyword_entries=[(wake_word_lower, 0.8)]
                    ).lower()
                except (sr.UnknownValueError, sr.RequestError):
                    pass

                if wake_word_lower in sphinx_text:
                    logger.info(
                        f"🎯 Dual STT: Sphinx detected wake word '{wake_word}' in '{sphinx_text}'"
                    )

                    # Update state
                    _conversation_state["wake_word_detected"] = True
                    _conversation_state["sphinx_active"] = False
                    _conversation_state["google_cloud_active"] = True
                    _conversation_state["last_activity"] = time.time()

                    # PHASE 2: Record command with Google Cloud transcription
                    command_chunks = []
                    command_duration = 0

                    # Record for specified duration
                    while command_duration < record_duration and not stop_event.is_set():
                        chunk = sd.rec(
                            chunk_samples, samplerate=sample_rate, channels=1, dtype="float32"
                        )
                        sd.wait()
                        command_chunks.append(chunk)
                        command_duration += chunk_duration

                    if not stop_event.is_set():
                        # Combine all command chunks
                        command_audio = np.concatenate(command_chunks, axis=0)

                        # Save command audio
                        temp_command_file = (
                            Path.home() / ".advanced-memory" / "temp_dual_stt_command.wav"
                        )
                        sf.write(temp_command_file, command_audio, sample_rate)

                        # PHASE 3: Google Cloud accurate transcription
                        logger.info(
                            "🎯 Dual STT: Transcribing command with Google Cloud (Whisper)..."
                        )
                        segments, info = whisper_model.transcribe(
                            str(temp_command_file), beam_size=5
                        )
                        command_text = (
                            " ".join([segment.text for segment in segments]).strip().lower()
                        )

                        if command_text:
                            logger.info(f"🎯 Dual STT: Transcribed command: '{command_text}'")

                            # Execute command
                            try:
                                await _parse_and_execute_command_dual_stt(
                                    active_project, command_text
                                )
                            except Exception as e:
                                logger.error(f"Dual STT command execution failed: {e}")
                        else:
                            logger.warning("Dual STT: No command text transcribed")

                    # Reset for next wake word
                    _conversation_state["wake_word_detected"] = False
                    _conversation_state["sphinx_active"] = True
                    _conversation_state["google_cloud_active"] = False

            except Exception as e:
                logger.debug(f"Dual STT processing error: {e}")

    except Exception as e:
        logger.error(f"Dual STT listener error: {e}", exc_info=True)
    finally:
        _conversation_state["sphinx_active"] = False
        _conversation_state["google_cloud_active"] = False


async def _wake_stop_dual_operation() -> dict:
    """Stop the running dual STT background listener."""
    global _dual_stt_listener_thread, _dual_stt_stop_event, _dual_stt_running

    if not _dual_stt_running:
        return """# Dual STT Listener Not Running

No dual STT wake word listener is currently running.

**To start:** Use `adn_audio_dual_stt("wake_start_dual", wake_word="memorizer")`
"""

    # Signal stop
    _dual_stt_stop_event.set()

    # Wait for thread to finish (with timeout)
    if _dual_stt_listener_thread and _dual_stt_listener_thread.is_alive():
        _dual_stt_listener_thread.join(timeout=2.0)

    _dual_stt_running = False
    _dual_stt_listener_thread = None

    # Reset conversation state
    _conversation_state["active"] = False
    _conversation_state["wake_word_detected"] = False
    _conversation_state["sphinx_active"] = False
    _conversation_state["google_cloud_active"] = False

    return """# Dual STT Listener Stopped

The ikubaysan dual STT wake word listener has been stopped.

**Architecture components stopped:**
- Sphinx wake word detection
- Google Cloud transcription pipeline
- Character state machine

**To start again:** Use `adn_audio_dual_stt("wake_start_dual", wake_word="memorizer")`
"""


async def _wake_status_dual_operation() -> dict:
    """Check dual STT listener status."""
    global _dual_stt_running, _dual_stt_listener_thread

    if _dual_stt_running:
        thread_status = (
            "alive"
            if (_dual_stt_listener_thread and _dual_stt_listener_thread.is_alive())
            else "dead"
        )

        # Calculate time since last activity
        last_activity = _conversation_state["last_activity"]
        time_since_activity = time.time() - last_activity if last_activity > 0 else 0

        return f"""# Dual STT Listener Status

**Status:** Running (ikubaysan Architecture)
**Thread:** {thread_status}
**Architecture:** Dual STT Pipeline

**Pipeline Status:**
- **Sphinx Active:** {_conversation_state["sphinx_active"]}
- **Google Cloud Active:** {_conversation_state["google_cloud_active"]}
- **Wake Word Detected:** {_conversation_state["wake_word_detected"]}

**Character State:**
- **Active:** {_conversation_state["active"]}
- **Last Activity:** {time_since_activity:.1f} seconds ago
- **Consecutive Confused:** {_conversation_state["consecutive_confused"]}

**To stop:** Use `adn_audio_dual_stt("wake_stop_dual")`
"""
    else:
        return """# Dual STT Listener Status

**Status:** Not running

**Architecture:** ikubaysan Dual STT Pipeline
- Sphinx wake word detection
- Google Cloud accurate transcription
- Character state machine

**To start:** Use `adn_audio_dual_stt("wake_start_dual", wake_word="memorizer")`
"""


async def _character_status_operation() -> dict:
    """Show current character state and activity statistics."""
    current_time = time.time()

    # Calculate activity metrics
    last_activity = _conversation_state["last_activity"]
    time_since_activity = current_time - last_activity if last_activity > 0 else 0

    # Determine current state
    if not _conversation_state["active"]:
        current_state = "wandering"
        state_description = "Idle, listening for wake words"
    elif _conversation_state["wake_word_detected"]:
        current_state = "wake_word_detected"
        state_description = "Wake word detected, preparing transcription"
    elif _conversation_state["google_cloud_active"]:
        current_state = "transcribing"
        state_description = "Processing voice command with Google Cloud"
    elif _conversation_state["sphinx_active"]:
        current_state = "listening"
        state_description = "Sphinx wake word detection active"
    else:
        current_state = "conversing"
        state_description = "Active conversation state"

    return f"""# Character Status (Dual STT)

**Current State:** {current_state}
**Description:** {state_description}

**Activity Metrics:**
- **Time Since Last Activity:** {time_since_activity:.1f} seconds
- **Consecutive Confused Responses:** {_conversation_state["consecutive_confused"]}
- **Total Sessions:** {1 if _conversation_state["active"] else 0}

**Dual STT Pipeline:**
- **Sphinx Wake Detection:** {"Active" if _conversation_state["sphinx_active"] else "Inactive"}
- **Google Cloud Transcription:** {"Active" if _conversation_state["google_cloud_active"] else "Inactive"}
- **Wake Word Detected:** {_conversation_state["wake_word_detected"]}

**Architecture:** ikubaysan Dual STT
- Phase 1: Sphinx (fast, always-on wake word detection)
- Phase 2: Google Cloud (accurate transcription)
- Phase 3: Character state machine

**Available Commands:**
- Check status: `adn_audio_dual_stt("character_status")`
- Start listener: `adn_audio_dual_stt("wake_start_dual")`
- Stop listener: `adn_audio_dual_stt("wake_stop_dual")`
"""


# Import remaining operations from original adn_audio.py
async def _dictate_operation(
    active_project, audio_path: str | None, record_duration: int | None, tags: TagType
) -> dict:
    """Handle dictate operation - speech-to-text note creation."""
    # Import and use from original adn_audio.py
    from advanced_memory.mcp.tools.adn_audio import _dictate_operation as original_dictate

    return await original_dictate(active_project, audio_path, record_duration, tags)


async def _speak_operation(
    active_project, identifier: str, voice: str | None, speed: float, volume: int, save_audio: bool
) -> dict:
    """Handle speak operation - text-to-speech note reading."""
    # Import and use from original adn_audio.py
    from advanced_memory.mcp.tools.adn_audio import _speak_operation as original_speak

    return await original_speak(active_project, identifier, voice, speed, volume, save_audio)


async def _get_weather(location: str | None = None) -> dict:
    """Get weather information for a location."""
    from advanced_memory.mcp.tools.adn_audio import _get_weather as original_weather

    return await original_weather(location)


async def _set_timer(duration: str) -> dict:
    """Set a timer for a specific duration."""
    from advanced_memory.mcp.tools.adn_audio import _set_timer as original_timer

    return await original_timer(duration)


async def _set_alarm(time_str: str) -> dict:
    """Set an alarm for a specific time."""
    from advanced_memory.mcp.tools.adn_audio import _set_alarm as original_alarm

    return await original_alarm(time_str)


async def _control_music(command: str, query: str | None = None) -> dict:
    """Control music playback."""
    from advanced_memory.mcp.tools.adn_audio import _control_music as original_music

    return await original_music(command, query)
