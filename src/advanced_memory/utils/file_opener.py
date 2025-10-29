"""Cross-platform file and folder opener utility for Advanced Memory exports."""

import os
import platform
import subprocess
import webbrowser
from pathlib import Path

from loguru import logger


def open_file_or_folder(path: str | Path) -> tuple[bool, str]:
    """
    Open a file or folder in the default application/file explorer.

    Cross-platform support for:
    - Windows: os.startfile() for files, explorer for folders
    - macOS: 'open' command
    - Linux: 'xdg-open' command

    Args:
        path: Path to file or folder to open

    Returns:
        Tuple of (success: bool, message: str)
    """
    path_obj = Path(path).resolve()

    if not path_obj.exists():
        return False, f"Path does not exist: {path_obj}"

    system = platform.system()

    try:
        if system == "Windows":
            if path_obj.is_file():
                os.startfile(str(path_obj))
            else:
                os.startfile(str(path_obj))  # Opens folder in Explorer
            return True, f"Opened in default application: {path_obj}"

        elif system == "Darwin":  # macOS
            subprocess.run(["open", str(path_obj)], check=True)
            return True, f"Opened with macOS 'open': {path_obj}"

        elif system == "Linux":
            subprocess.run(["xdg-open", str(path_obj)], check=True)
            return True, f"Opened with xdg-open: {path_obj}"

        else:
            logger.warning(f"Unsupported platform for auto-open: {system}")
            return False, f"Auto-open not supported on {system}"

    except Exception as e:
        logger.error(f"Failed to open {path_obj}: {e}")
        return False, f"Failed to open: {e}"


def open_url_in_browser(url: str) -> tuple[bool, str]:
    """
    Open a URL in the default web browser.

    Args:
        url: URL to open

    Returns:
        Tuple of (success: bool, message: str)
    """
    try:
        webbrowser.open(url)
        return True, f"Opened in browser: {url}"
    except Exception as e:
        logger.error(f"Failed to open URL {url}: {e}")
        return False, f"Failed to open browser: {e}"


def format_open_result(success: bool, message: str, path: str | Path | None = None) -> str:
    """
    Format the result of an open operation for user-friendly display.

    Args:
        success: Whether the operation succeeded
        message: Success or error message
        path: Optional path to include in output

    Returns:
        Formatted markdown message
    """
    if success:
        return f"""## 🚀 Opened After Export

✅ {message}

**Tip**: The file/folder remains on your system even after closing."""
    else:
        manual_msg = ""
        if path:
            path_obj = Path(path).resolve()
            if path_obj.is_file():
                manual_msg = f"\n\n**Open manually**: Double-click `{path_obj}`"
            else:
                manual_msg = (
                    f"\n\n**Open manually**: Navigate to `{path_obj}` in your file explorer"
                )

        return f"""## ⚠️ Auto-Open Failed

{message}{manual_msg}"""

