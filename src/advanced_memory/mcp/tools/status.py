"""Enhanced status tool for Advanced Memory MCP server."""

import os
import platform
from pathlib import Path
from typing import Annotated

from pydantic import Field

from advanced_memory.config import ConfigManager
from advanced_memory.mcp.mcp_instance import mcp
from advanced_memory.services.sync_status_service import sync_status_tracker


# @mcp.tool  # Decommissioned in favor of namespaced adn_system portmanteau
async def status(
    level: Annotated[
        str, Field(description="Detail level: basic, intermediate, advanced, diagnostic")
    ] = "basic",
    focus: Annotated[
        str | None, Field(description="Focus area: sync, tools, system, projects")
    ] = None,
) -> str:
    """Get system status and diagnostic information."""

    if focus:
        return await _get_focused_status(focus, level)

    if level == "basic":
        return await _get_basic_status()
    elif level == "intermediate":
        return await _get_intermediate_status()
    elif level == "advanced":
        return await _get_advanced_status()
    elif level == "diagnostic":
        return await _get_diagnostic_status()
    else:
        return f"""# Status - Invalid Level

Unknown status level: "{level}"

Available levels:
- **basic**: Core system status and sync information
- **intermediate**: Tool availability and configuration
- **advanced**: Performance metrics and system resources
- **diagnostic**: Detailed troubleshooting information

Try: `status("basic")`"""


async def _get_basic_status() -> str:
    """Basic status - core system information."""
    status_lines = ["# Advanced Memory Status - Basic Overview", ""]

    # Get sync status
    sync_info = sync_status_tracker.get_summary()
    status_lines.append(sync_info)

    # Add quick system info
    status_lines.extend(
        [
            "",
            "---",
            "",
            "## System Information",
            f"- **Platform**: {platform.system()} {platform.release()}",
            f"- **Python**: {platform.python_version()}",
            f"- **Architecture**: {platform.machine()}",
        ]
    )

    status_lines.append(
        "- **Tool surface**: FastMCP 3.2 GA managed namespaces plus root tools "
        "(~79 tools on a typical build). Use MCP **`tools/list`** for the exact set."
    )

    return "\n".join(status_lines)


async def _get_intermediate_status() -> str:
    """Intermediate status - tool availability and configuration."""
    status_lines = ["# Advanced Memory Status - Intermediate", ""]

    # Basic sync status
    sync_info = sync_status_tracker.get_summary()
    status_lines.extend([sync_info, "", "---", ""])

    status_lines.extend(
        [
            "## Tool Inventory",
            "- **Managed namespaces** (12): `audio`, `inbox`, `skills`, `zettel`, `nav`, "
            "`notes`, `search`, `knowledge`, `project`, `system`, `mcp`, `typora`",
            "- **Wire names**: `namespace_operation` (for example `nav_recent`, `notes_write`).",
            "- **Authoritative list**: MCP **`tools/list`** (names, descriptions, JSON Schemas).",
            "",
        ]
    )

    # Configuration summary
    status_lines.extend(["", "## Configuration Summary"])
    try:
        from advanced_memory.config import ConfigManager

        config = ConfigManager().config

        status_lines.extend(
            [
                f"- **Active Projects**: {len(config.projects)}",
                f"- **Default Project**: {config.default_project}",
                f"- **Sync Delay**: {config.sync_delay}ms",
                f"- **Log Level**: {config.log_level}",
            ]
        )
    except Exception as e:
        status_lines.append(f"- **Configuration**: Error loading - {e}")

    # Platform details
    status_lines.extend(["", "## Platform Details"])
    status_lines.extend(
        [
            f"- **OS**: {platform.system()} {platform.release()}",
            f"- **Python**: {platform.python_version()}",
            f"- **Architecture**: {platform.machine()}",
            f"- **Processor**: {platform.processor() or 'Unknown'}",
        ]
    )

    return "\n".join(status_lines)


async def _get_advanced_status() -> str:
    """Advanced status - performance metrics and system resources."""
    status_lines = ["# Advanced Memory Status - Advanced", ""]

    # Basic sync status
    sync_info = sync_status_tracker.get_summary()
    status_lines.extend([sync_info, "", "---", ""])

    # Performance metrics
    status_lines.append("## Performance Metrics")
    try:
        import os

        import psutil

        process = psutil.Process(os.getpid())
        memory_mb = process.memory_info().rss / 1024 / 1024
        cpu_percent = process.cpu_percent(interval=0.1)

        status_lines.extend(
            [
                f"- **Memory Usage**: {memory_mb:.1f} MB",
                f"- **CPU Usage**: {cpu_percent:.1f}%",
                f"- **Process ID**: {os.getpid()}",
            ]
        )
    except ImportError:
        status_lines.append("- **Performance Metrics**: psutil not available")
    except Exception as e:
        status_lines.append(f"- **Performance Metrics**: Error - {e}")

    # Database information
    status_lines.extend(["", "## Database Information"])
    try:
        from advanced_memory.config import ConfigManager

        config = ConfigManager().config

        for project_name, project_path in config.projects.items():
            db_path = Path(project_path) / "advanced_memory.db"
            if db_path.exists():
                size_mb = db_path.stat().st_size / 1024 / 1024
                status_lines.append(f"- **{project_name} DB**: {size_mb:.1f} MB")
            else:
                status_lines.append(f"- **{project_name} DB**: Not found")
    except Exception as e:
        status_lines.append(f"- **Database Information**: Error - {e}")

    # File system information
    status_lines.extend(["", "## File System Information"])
    try:
        config_mgr = ConfigManager()  # type: ignore[possibly-unbound]
        for project_name, project_path in config_mgr.config.projects.items():
            path_obj = Path(project_path)
            if path_obj.exists():
                total_files = sum(1 for _ in path_obj.rglob("*") if _.is_file())
                total_size_mb = (
                    sum(_.stat().st_size for _ in path_obj.rglob("*") if _.is_file()) / 1024 / 1024
                )
                status_lines.append(
                    f"- **{project_name}**: {total_files} files, {total_size_mb:.1f} MB"
                )
            else:
                status_lines.append(f"- **{project_name}**: Path not found")
    except Exception as e:
        status_lines.append(f"- **File System Information**: Error - {e}")

    # Network and connectivity
    status_lines.extend(["", "## Connectivity Status"])
    try:
        import socket

        hostname = socket.gethostname()
        status_lines.append(f"- **Hostname**: {hostname}")
        status_lines.append("- **MCP Connection**: Active (stdio)")
    except Exception as e:
        status_lines.append(f"- **Connectivity**: Error - {e}")

    return "\n".join(status_lines)


async def _get_diagnostic_status() -> str:
    """Diagnostic status - detailed troubleshooting information."""
    status_lines = ["# Advanced Memory Status - Diagnostic", ""]

    # Basic sync status
    from advanced_memory.services.sync_status_service import SyncStatusTracker

    sync_status_tracker = SyncStatusTracker()
    sync_info = sync_status_tracker.get_summary()
    status_lines.extend([sync_info, "", "---", ""])

    # Environment variables
    status_lines.extend(["## Environment Variables"])
    relevant_vars = ["ADVANCED_MEMORY_HOME", "PYTHONPATH", "PATH"]
    for var in relevant_vars:
        value = os.environ.get(var, "Not set")
        # Truncate long paths
        if len(value) > 100:
            value = value[:97] + "..."
        status_lines.append(f"- **{var}**: {value}")

    # Python packages
    status_lines.extend(["", "## Key Dependencies"])
    try:
        import fastmcp

        status_lines.append(f"- **FastMCP**: {fastmcp.__version__}")
    except Exception:
        status_lines.append("- **FastMCP**: Not found")

    try:
        import sqlalchemy

        status_lines.append(f"- **SQLAlchemy**: {sqlalchemy.__version__}")
    except Exception:
        status_lines.append("- **SQLAlchemy**: Not found")

    try:
        import pydantic

        status_lines.append(f"- **Pydantic**: {pydantic.VERSION}")
    except Exception:
        status_lines.append("- **Pydantic**: Not found")

    # Log file information
    status_lines.extend(["", "## Log Configuration"])
    try:
        from advanced_memory.config import ConfigManager

        config = ConfigManager().config
        status_lines.append(f"- **Log Level**: {config.log_level}")
        status_lines.append("- **Logging**: Enabled via loguru")
    except Exception as e:
        status_lines.append(f"- **Log Configuration**: Error - {e}")

    # Project paths validation
    status_lines.extend(["", "## Project Path Validation"])
    try:
        from advanced_memory.config import ConfigManager

        config = ConfigManager().config

        for project_name, project_path in config.projects.items():
            path_obj = Path(project_path)
            exists = path_obj.exists()
            is_dir = path_obj.is_dir() if exists else False
            writable = os.access(path_obj, os.W_OK) if exists else False

            status_lines.append(
                f"- **{project_name}**: Path={project_path}, Exists={exists}, Dir={is_dir}, Writable={writable}"
            )
    except Exception as e:
        status_lines.append(f"- **Project Validation**: Error - {e}")

    # Recent errors or warnings
    status_lines.extend(["", "## Recent Activity Summary"])
    try:
        from advanced_memory.services.sync_status_service import sync_status_tracker

        summary = sync_status_tracker.get_summary()
        status_lines.append(f"- **Sync Summary**: {summary}")

        # Get failed projects
        all_projects = sync_status_tracker.get_all_projects()
        failed_projects = [p for p in all_projects.values() if p.status.value == "failed"]
        if failed_projects:
            status_lines.append(f"- **Failed Projects**: {len(failed_projects)}")
            for project in failed_projects:
                status_lines.append(f"  - {project.project_name}: {project.error}")
    except Exception as e:
        status_lines.append(f"- **Activity Summary**: Error - {e}")

    # Watch service health monitoring
    status_lines.extend(["", "## Watch Service Health"])
    try:
        from advanced_memory.config import WATCH_STATUS_JSON

        watch_status_file = Path.home() / ".advanced-memory" / WATCH_STATUS_JSON
        if watch_status_file.exists():
            import json
            from datetime import datetime

            with open(watch_status_file) as f:
                watch_data = json.load(f)

            # Check if watch service is running
            pid = watch_data.get("pid")
            running = watch_data.get("running", False)
            error_count = watch_data.get("error_count", 0)
            start_time_str = watch_data.get("start_time")

            status_lines.append(f"- **Watch Service**: {'Running' if running else 'Stopped'}")
            status_lines.append(f"- **Process ID**: {pid or 'None'}")
            status_lines.append(f"- **Error Count**: {error_count}")

            if start_time_str:
                try:
                    # Parse ISO format datetime
                    start_time = datetime.fromisoformat(start_time_str.replace("Z", "+00:00"))
                    uptime_seconds = (datetime.now() - start_time).total_seconds()
                    uptime_str = f"{uptime_seconds / 3600:.1f} hours"
                    status_lines.append(f"- **Uptime**: {uptime_str}")
                except Exception:
                    status_lines.append(f"- **Start Time**: {start_time_str}")

            # Check for stability issues
            if error_count > 5:
                status_lines.append(f"- **⚠️ Stability Issue**: High error count ({error_count})")
            if not running and pid:
                status_lines.append("- **⚠️ Stability Issue**: Service stopped unexpectedly")

            # Recent events
            recent_events = watch_data.get("recent_events", [])
            if recent_events:
                status_lines.append(f"- **Recent Events**: {len(recent_events)} events")
                # Show last 3 events
                for event in recent_events[-3:]:
                    timestamp = event.get("timestamp", "Unknown")
                    action = event.get("action", "Unknown")
                    status = event.get("status", "Unknown")
                    path = event.get("path", "")[:50]  # Truncate long paths
                    status_lines.append(f"  - {timestamp[:19]}: {action} {path} ({status})")
        else:
            status_lines.append("- **Watch Status File**: Not found")

    except Exception as e:
        status_lines.append(f"- **Watch Service Health**: Error reading status - {e}")

    # Troubleshooting tips
    status_lines.extend(["", "## Troubleshooting Tips"])
    status_lines.extend(
        [
            "- Check project paths exist and are writable",
            "- Verify Python dependencies are installed",
            "- Ensure database files are not corrupted",
            "- Check log files for detailed error messages",
            "- Try restarting the MCP server",
            "- Verify file permissions on project directories",
        ]
    )

    return "\n".join(status_lines)


async def _get_focused_status(focus: str, level: str) -> str:
    """Get status focused on a specific area."""

    focus = focus.lower()

    if focus == "sync":
        return sync_status_tracker.get_summary()
    elif focus == "tools":
        if level == "basic":
            return (
                "# Tool Status\n\n"
                "- **Layout**: 12 mounted namespace apps plus additional root-level tools "
                "(see `advanced_memory/mcp/server.py`).\n"
                "- **Discovery**: Use MCP **`tools/list`** for the full tool catalog on this process."
            )
        else:
            return await _get_intermediate_status()
    elif focus == "system":
        return await _get_advanced_status()
    elif focus == "projects":
        try:
            from advanced_memory.config import ConfigManager

            config = ConfigManager().config

            status_lines = ["# Project Status"]
            for project_name, project_path in config.projects.items():
                path_obj = Path(project_path)
                exists = path_obj.exists()
                status_lines.append(
                    f"- **{project_name}**: {project_path} ({'Valid' if exists else 'Invalid'})"
                )

            return "\n".join(status_lines)
        except Exception as e:
            return f"# Project Status\n\n**Error**: {e}"
    else:
        return f"""# Status - Unknown Focus

Unknown focus area: "{focus}"

Available focus areas:
- **sync**: Synchronization status and progress
- **tools**: Tool availability and function
- **system**: System resources and performance
- **projects**: Project configuration and paths

Try: `status("basic", "sync")`"""
