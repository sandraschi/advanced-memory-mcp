"""Audio namespaced app for Advanced Memory MCP.

Decomposed from the legacy adn_audio portmanteau.
Follows FastMCP 3.2 GA Managed Namespace standards.
"""

import threading
from typing import Annotated, Any, Literal

from fastmcp import FastMCP
from pydantic import Field
from loguru import logger

from advanced_memory.mcp.project_session import get_active_project
from advanced_memory.mcp.tools.utils import build_error_response, build_success_response
from advanced_memory.utils import parse_tags

# Initialize the namespaced app
audio_app = FastMCP("audio")

# Global state for wake word listener
_wake_listener_thread: threading.Thread | None = None
_wake_listener_stop_event = threading.Event()
_wake_listener_running = False

# Global state for alarms and timers
_alarms: dict[str, dict] = {}  # alarm_id -> {time, message, thread}
_timers: dict[str, dict] = {}  # timer_id -> {duration, message, thread}
_alarm_counter = 0
_timer_counter = 0


@audio_app.tool(task=True)
async def dictate(
    audio_path: Annotated[str | None, Field(description="Path to existing audio file for transcription")] = None,
    record_duration: Annotated[int | None, Field(description="Seconds to record from default microphone if audio_path is not provided")] = None,
    tags: Annotated[str | list[str] | None, Field(description="Metadata tags to classify the resulting note")] = None,
    project: Annotated[str | None, Field(description="Project context override")] = None,
) -> Any:
    """Voice Transcription Engine
    
    Converts live audio or files into structured knowledge base notes.
    """
    from advanced_memory.mcp.tools.adn_audio import _dictate_operation
    active_project = get_active_project(project)
    if not active_project:
        return "Active project required for dictation."
    return await _dictate_operation(active_project, audio_path, record_duration, tags)


@audio_app.tool(task=True)
async def speak(
    identifier: Annotated[str, Field(description="Note title, permalink, or raw text to read aloud")],
    voice: Annotated[str | None, Field(description="Specific Kokoro or system voice name")] = None,
    speed: Annotated[float, Field(description="Playback speed multiplier (0.5 to 2.0)", ge=0.5, le=2.0)] = 1.0,
    volume: Annotated[int, Field(description="Output volume level (1 to 10)", ge=1, le=10)] = 5,
    save_audio: Annotated[bool, Field(description="If true, saves as WAV instead of playing locally")] = False,
    project: Annotated[str | None, Field(description="Project context override")] = None,
) -> Any:
    """Voice Synthesis Engine
    
    Synthesizes and plays high-fidelity clones of knowledge base content.
    """
    from advanced_memory.mcp.tools.adn_audio import _speak_operation
    active_project = get_active_project(project)
    if not active_project:
        return "Active project required for speaking."
    return await _speak_operation(active_project, identifier, voice, speed, volume, save_audio)


@audio_app.tool()
async def listen(
    record_duration: Annotated[int, Field(description="Listening window for voice command in seconds")] = 5,
    audio_path: Annotated[str | None, Field(description="Path to existing command recording for debug")] = None,
    project: Annotated[str | None, Field(description="Project context override")] = None,
) -> Any:
    """Voice Command Listener
    
    Listens for a command and executes it using intelligent parsing.
    """
    from advanced_memory.mcp.tools.adn_audio import _listen_command_operation
    active_project = get_active_project(project)
    if not active_project:
        return "Active project required for listening."
    return await _listen_command_operation(active_project, audio_path, record_duration)


@audio_app.tool()
async def wake_start(
    wake_word: Annotated[str, Field(description="Trigger word to activate background listener")] = "memorizer",
    record_duration: Annotated[int, Field(description="Seconds to record after wake word detection")] = 5,
    project: Annotated[str | None, Field(description="Project context override")] = None,
) -> Any:
    """Voice Activation Start
    
    Initializes the background wake word listener for hands-free control.
    """
    from advanced_memory.mcp.tools.adn_audio import _wake_start_operation
    active_project = get_active_project(project)
    if not active_project:
        return "Active project required for wake word listener."
    return await _wake_start_operation(active_project, wake_word, record_duration)


@audio_app.tool()
async def wake_stop() -> Any:
    """Voice Activation Stop
    
    Ceases all background wake word listening and releases audio devices.
    """
    from advanced_memory.mcp.tools.adn_audio import _wake_stop_operation
    return await _wake_stop_operation()


@audio_app.tool()
async def wake_status() -> Any:
    """Voice Activation Status
    
    Reports the current state and health of the background wake listener.
    """
    from advanced_memory.mcp.tools.adn_audio import _wake_status_operation
    return await _wake_status_operation()


@audio_app.tool()
async def weather(
    location: Annotated[str | None, Field(description="City or region for the weather report")] = None,
) -> Any:
    """Environmental Conditions Tool
    
    Fetches and formats current weather and forecasts for a location.
    """
    from advanced_memory.mcp.tools.adn_audio import _get_weather
    return await _get_weather(location)


@audio_app.tool()
async def timer(
    duration: Annotated[str, Field(description="Relative time string (e.g., '5 minutes')")],
) -> Any:
    """Temporal Countdown Tool
    
    Sets an audible countdown timer with automatic alarm notification.
    """
    from advanced_memory.mcp.tools.adn_audio import _set_timer
    return await _set_timer(duration)


@audio_app.tool()
async def alarm(
    time_str: Annotated[str, Field(description="Absolute time string (e.g., '7:00 AM')")],
) -> Any:
    """Temporal Reminder Tool
    
    Configures a time-based alarm for later in the day or next.
    """
    from advanced_memory.mcp.tools.adn_audio import _set_alarm
    return await _set_alarm(time_str)


@audio_app.tool()
async def music(
    command: Annotated[str, Field(description="Playback command: play, pause, next, previous")],
    query: Annotated[str | None, Field(description="Search term for playback (artist, song, album)")] = None,
) -> Any:
    """Media Control Tool
    
    Orchestrates music playback via Plex or system media interfaces.
    """
    from advanced_memory.mcp.tools.adn_audio import _control_music
    return await _control_music(command, query)
