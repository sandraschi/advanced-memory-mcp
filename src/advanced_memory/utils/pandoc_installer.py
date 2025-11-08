"""Auto-install Pandoc binary on first use."""

from pathlib import Path

from loguru import logger


def ensure_pandoc_installed() -> str:
    """
    Ensure Pandoc is installed and return path to executable.

    Uses pypandoc to auto-download Pandoc binary if not found.

    Returns:
        Path to pandoc executable
    """
    try:
        import pypandoc

        # Check if pandoc is already available
        try:
            pandoc_path = pypandoc.get_pandoc_path()
            logger.info(f"Pandoc found at: {pandoc_path}")
            return pandoc_path
        except OSError:
            # Pandoc not found, download it
            logger.info("Pandoc not found. Downloading Pandoc binary...")

            # Download pandoc to user's home directory
            target_folder = Path.home() / ".advanced-memory" / "bin"
            target_folder.mkdir(parents=True, exist_ok=True)

            pypandoc.download_pandoc(targetfolder=str(target_folder))

            # Get the path after download
            pandoc_path = pypandoc.get_pandoc_path()
            logger.info(f"Pandoc installed successfully at: {pandoc_path}")

            return pandoc_path

    except Exception as e:
        error_msg = f"Failed to install Pandoc: {e}"
        logger.error(error_msg)
        raise RuntimeError(
            f"{error_msg}\n\n"
            "Advanced Memory tried to auto-install Pandoc but failed.\n"
            "Please install Pandoc manually from: https://pandoc.org/installing.html"
        )


def get_pandoc_command() -> list[str]:
    """
    Get the pandoc command with proper executable path.

    Returns:
        List with pandoc executable path (for subprocess)
    """
    pandoc_path = ensure_pandoc_installed()
    return [pandoc_path]













