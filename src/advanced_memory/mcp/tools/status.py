"""Enhanced status tool for Basic Memory MCP server."""

import os
import platform
from pathlib import Path
from typing import Optional

from advanced_memory.mcp.server import mcp
from advanced_memory.services.sync_status_service import sync_status_tracker


@mcp.tool(
    description="""Comprehensive system status and diagnostic monitoring for Basic Memory.

This tool provides detailed insights into system health, performance, and operational status
across multiple diagnostic levels, helping users understand and troubleshoot their knowledge base.

LEVELS:
- basic: Core system status and sync information
- intermediate: Tool availability and configuration details
- advanced: Performance metrics and system resource usage
- diagnostic: Detailed troubleshooting information and error analysis

FOCUS AREAS:
- sync: Synchronization status and background processing
- tools: Tool availability and functional status
- system: System resources and performance metrics
- projects: Project configuration and path validation

PARAMETERS:
- level (str, default="basic"): Status detail level (basic/intermediate/advanced/diagnostic)
- focus (str, optional): Specific area to focus on (sync/tools/system/projects)

USAGE EXAMPLES:
Quick status: status()
Sync details: status("basic", "sync")
Performance: status("advanced", "system")
Troubleshooting: status("diagnostic")
Tool inventory: status("intermediate", "tools")

RETURNS:
Formatted status report with system metrics, configuration details, and actionable insights.

MONITORS:
- File synchronization progress and errors
- Database size and performance metrics
- Project configuration and path validation
- Tool availability and function counts
- Memory usage and resource consumption
- Background process status and health""",
)
async def status(level: str = "basic", focus: Optional[str] = None) -> str:
    """Get comprehensive status information about Basic Memory system.

    This enhanced status tool provides different levels of diagnostic information:

    **Level 1 - "basic"**: Core system status and sync information
    **Level 2 - "intermediate"**: Tool availability and configuration
    **Level 3 - "advanced"**: Performance metrics and system resources
    **Level 4 - "diagnostic"**: Detailed troubleshooting information

    Args:
        level: Status detail level (basic, intermediate, advanced, diagnostic)
        focus: Optional focus area (sync, tools, system, projects)

    Returns:
        Comprehensive status report at requested level

    Examples:
        status() - Basic system overview
        status("intermediate") - Tool and configuration status
        status("advanced", "system") - System performance metrics
        status("diagnostic") - Full diagnostic information
    """

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
    status_lines = ["# Basic Memory Status - Basic Overview", ""]

    # Get sync status
    sync_info = sync_status_tracker.get_summary()
    status_lines.append(sync_info)

    # Add quick system info
    status_lines.extend([
        "",
        "---",
        "",
        "## System Information",
        f"- **Platform**: {platform.system()} {platform.release()}",
        f"- **Python**: {platform.python_version()}",
        f"- **Architecture**: {platform.machine()}",
    ])

    # Add quick tool count
    try:
        from advanced_memory.mcp.tools import __all__ as tools
        status_lines.append(f"- **Available Tools**: {len(tools)}")
    except Exception:
        status_lines.append("- **Available Tools**: Unable to count")

    return "\n".join(status_lines)


async def _get_intermediate_status() -> str:
    """Intermediate status - tool availability and configuration."""
    status_lines = ["# Basic Memory Status - Intermediate", ""]

    # Basic sync status
    sync_info = sync_status_tracker.get_summary()
    status_lines.extend([sync_info, "", "---", ""])

    # Tool inventory
    status_lines.append("## Tool Inventory")
    try:
        from advanced_memory.mcp.tools import __all__ as tools

        # Categorize tools
        import_tools = [t for t in tools if t.startswith(('load_', 'import_'))]
        export_tools = [t for t in tools if t.startswith(('export_', 'save_'))]
        search_tools = [t for t in tools if 'search' in t or 'find' in t]
        editing_tools = [t for t in tools if 'edit' in t or 'typora' in t]
        core_tools = [t for t in tools if t not in import_tools + export_tools + search_tools + editing_tools]

        status_lines.extend([
            f"- **Core Tools** ({len(core_tools)}): {', '.join(core_tools[:5])}{'...' if len(core_tools) > 5 else ''}",
            f"- **Import Tools** ({len(import_tools)}): {', '.join(import_tools[:5])}{'...' if len(import_tools) > 5 else ''}",
            f"- **Export Tools** ({len(export_tools)}): {', '.join(export_tools[:5])}{'...' if len(export_tools) > 5 else ''}",
            f"- **Search Tools** ({len(search_tools)}): {', '.join(search_tools[:5])}{'...' if len(search_tools) > 5 else ''}",
            f"- **Editing Tools** ({len(editing_tools)}): {', '.join(editing_tools[:5])}{'...' if len(editing_tools) > 5 else ''}",
        ])
    except Exception as e:
        status_lines.append(f"- **Tool Inventory**: Error loading - {e}")

    # Configuration summary
    status_lines.extend(["", "## Configuration Summary"])
    try:
        from advanced_memory.config import ConfigManager
        config = ConfigManager().config

        status_lines.extend([
            f"- **Active Projects**: {len(config.projects)}",
            f"- **Default Project**: {config.default_project}",
            f"- **Sync Delay**: {config.sync_delay}ms",
            f"- **Log Level**: {config.log_level}",
        ])
    except Exception as e:
        status_lines.append(f"- **Configuration**: Error loading - {e}")

    # Platform details
    status_lines.extend(["", "## Platform Details"])
    status_lines.extend([
        f"- **OS**: {platform.system()} {platform.release()}",
        f"- **Python**: {platform.python_version()}",
        f"- **Architecture**: {platform.machine()}",
        f"- **Processor**: {platform.processor() or 'Unknown'}",
    ])

    return "\n".join(status_lines)


async def _get_advanced_status() -> str:
    """Advanced status - performance metrics and system resources."""
    status_lines = ["# Basic Memory Status - Advanced", ""]

    # Basic sync status
    sync_info = sync_status_tracker.get_summary()
    status_lines.extend([sync_info, "", "---", ""])

    # Performance metrics
    status_lines.append("## Performance Metrics")
    try:
        import psutil
        import os

        process = psutil.Process(os.getpid())
        memory_mb = process.memory_info().rss / 1024 / 1024
        cpu_percent = process.cpu_percent(interval=0.1)

        status_lines.extend([
            f"- **Memory Usage**: {memory_mb:.1f} MB",
            f"- **CPU Usage**: {cpu_percent:.1f}%",
            f"- **Process ID**: {os.getpid()}",
        ])
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
            db_path = Path(project_path) / "basic_memory.db"
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
        for project_name, project_path in ConfigManager().config.projects.items():
            path_obj = Path(project_path)
            if path_obj.exists():
                total_files = sum(1 for _ in path_obj.rglob('*') if _.is_file())
                total_size_mb = sum(_.stat().st_size for _ in path_obj.rglob('*') if _.is_file()) / 1024 / 1024
                status_lines.append(f"- **{project_name}**: {total_files} files, {total_size_mb:.1f} MB")
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
    status_lines = ["# Basic Memory Status - Diagnostic", ""]

    # Basic sync status
    sync_info = sync_status_tracker.get_summary()
    status_lines.extend([sync_info, "", "---", ""])

    # Environment variables
    status_lines.extend(["## Environment Variables"])
    relevant_vars = ['BASIC_MEMORY_HOME', 'PYTHONPATH', 'PATH']
    for var in relevant_vars:
        value = os.environ.get(var, 'Not set')
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

            status_lines.append(f"- **{project_name}**: Path={project_path}, Exists={exists}, Dir={is_dir}, Writable={writable}")
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

    # Troubleshooting tips
    status_lines.extend(["", "## Troubleshooting Tips"])
    status_lines.extend([
        "- Check project paths exist and are writable",
        "- Verify Python dependencies are installed",
        "- Ensure database files are not corrupted",
        "- Check log files for detailed error messages",
        "- Try restarting the MCP server",
        "- Verify file permissions on project directories",
    ])

    return "\n".join(status_lines)


async def _get_focused_status(focus: str, level: str) -> str:
    """Get status focused on a specific area."""

    focus = focus.lower()

    if focus == "sync":
        return sync_status_tracker.get_summary()
    elif focus == "tools":
        if level == "basic":
            try:
                from advanced_memory.mcp.tools import __all__ as tools
                return f"# Tool Status\n\n- **Total Tools**: {len(tools)}\n- **Tools**: {', '.join(tools)}"
            except Exception as e:
                return f"# Tool Status\n\n**Error**: {e}"
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
                status_lines.append(f"- **{project_name}**: {project_path} ({'Valid' if exists else 'Invalid'})")

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
