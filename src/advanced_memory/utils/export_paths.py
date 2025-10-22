"""Smart default export paths for Advanced Memory.

Provides sensible defaults for export operations, typically Desktop/advanced-memory-exports.
"""

import platform
from pathlib import Path

from loguru import logger


def get_default_export_path(operation_name: str = "export") -> Path:
    """
    Get smart default export path based on platform.

    Defaults to Desktop/advanced-memory-exports/[operation-name]/
    Falls back to home directory if Desktop not found.

    Args:
        operation_name: Name of operation (pdf, html, docsify, etc.)

    Returns:
        Path object for default export location
    """
    try:
        # Try Desktop first (most user-friendly)
        desktop = _get_desktop_path()

        if desktop and desktop.exists():
            export_root = desktop / "advanced-memory-exports" / operation_name
            export_root.mkdir(parents=True, exist_ok=True)
            logger.info(f"Using export path: {export_root}")
            return export_root

        # Fallback to Documents
        documents = _get_documents_path()
        if documents and documents.exists():
            export_root = documents / "advanced-memory-exports" / operation_name
            export_root.mkdir(parents=True, exist_ok=True)
            logger.info(f"Using export path (Documents): {export_root}")
            return export_root

        # Last resort: home directory
        home_export = Path.home() / "advanced-memory-exports" / operation_name
        home_export.mkdir(parents=True, exist_ok=True)
        logger.warning(f"Using home directory export path: {home_export}")
        return home_export

    except Exception as e:
        logger.error(f"Error determining export path: {e}")
        # Ultimate fallback
        fallback = Path.home() / "advanced-memory-exports" / operation_name
        fallback.mkdir(parents=True, exist_ok=True)
        return fallback


def _get_desktop_path() -> Path | None:
    """Get platform-specific Desktop path."""
    system = platform.system()

    if system == "Windows":
        # Windows: C:\Users\Username\Desktop
        desktop = Path.home() / "Desktop"
        if desktop.exists():
            return desktop

        # Alternative: OneDrive Desktop
        onedrive_desktop = Path.home() / "OneDrive" / "Desktop"
        if onedrive_desktop.exists():
            return onedrive_desktop

    elif system == "Darwin":  # macOS
        # macOS: /Users/username/Desktop
        desktop = Path.home() / "Desktop"
        if desktop.exists():
            return desktop

    elif system == "Linux":
        # Linux: ~/Desktop (if using desktop environment)
        desktop = Path.home() / "Desktop"
        if desktop.exists():
            return desktop

        # XDG standard
        try:
            import subprocess

            result = subprocess.run(
                ["xdg-user-dir", "DESKTOP"],
                capture_output=True,
                text=True,
                check=True,
            )
            xdg_desktop = Path(result.stdout.strip())
            if xdg_desktop.exists():
                return xdg_desktop
        except Exception:
            pass

    return None


def _get_documents_path() -> Path | None:
    """Get platform-specific Documents path."""
    system = platform.system()

    if system == "Windows":
        # Windows: C:\Users\Username\Documents
        docs = Path.home() / "Documents"
        if docs.exists():
            return docs

        # OneDrive Documents
        onedrive_docs = Path.home() / "OneDrive" / "Documents"
        if onedrive_docs.exists():
            return onedrive_docs

    elif system == "Darwin":  # macOS
        docs = Path.home() / "Documents"
        if docs.exists():
            return docs

    elif system == "Linux":
        docs = Path.home() / "Documents"
        if docs.exists():
            return docs

        # XDG standard
        try:
            import subprocess

            result = subprocess.run(
                ["xdg-user-dir", "DOCUMENTS"],
                capture_output=True,
                text=True,
                check=True,
            )
            xdg_docs = Path(result.stdout.strip())
            if xdg_docs.exists():
                return xdg_docs
        except Exception:
            pass

    return None


def format_export_path(export_path: str | None, operation: str = "export") -> str:
    """
    Format and validate export path, using smart default if not provided.

    Args:
        export_path: User-provided path or None
        operation: Operation name for default path

    Returns:
        String path (absolute)
    """
    if export_path and export_path.strip():
        # User provided path - use it
        return str(Path(export_path).resolve())

    # No path provided - use smart default
    default_path = get_default_export_path(operation)
    logger.info(f"No export path specified, using default: {default_path}")

    return str(default_path)



