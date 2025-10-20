"""Diagnostic script to help debug sync issues.

This script helps identify why markdown files might not be getting picked up during sync.
"""

import os
import sys
from pathlib import Path

# Fix Windows console encoding issues
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

# Ignored patterns (copied from sync_service.py)
IGNORE_PATTERNS = {
    # Node.js
    "node_modules",
    # Build outputs
    "dist",
    "build",
    "target",
    "out",
    ".next",
    ".nuxt",
    # Python
    "__pycache__",
    ".pytest_cache",
    ".tox",
    "venv",
    ".venv",
    # Other package managers / build tools
    "vendor",
    ".gradle",
    ".cargo",
    "coverage",
    # IDE and editor files
    ".vscode",
    ".idea",
    # OS files
    ".DS_Store",
    "Thumbs.db",
}

# Archive patterns (copied from sync_service.py)
ARCHIVE_PATTERNS = {
    # Backup folders (timestamped)
    "-backup-",
    ".backup",
    "_backup",
    # Obsolete markers
    ".obsolete",
    "-obsolete",
    "_obsolete",
    # Archive folders
    ".archived",
    "-archived",
    "_archived",
}


def diagnose_directory(directory_path: str) -> None:
    """Diagnose a directory to see what files would be picked up during sync."""
    directory = Path(directory_path)

    if not directory.exists():
        print(f"ERROR: Directory does not exist: {directory}")
        return

    if not directory.is_dir():
        print(f"ERROR: Path is not a directory: {directory}")
        return

    print(f"Diagnosing directory: {directory}")
    print(f"Absolute path: {directory.absolute()}")
    print()

    markdown_files = []
    skipped_folders = set()
    skipped_non_md_files = []

    for root, dirnames, filenames in os.walk(str(directory)):
        # Track original directories
        original_dirnames = dirnames.copy()

        # Filter directories (same logic as sync_service.py)
        dirnames[:] = [
            d
            for d in dirnames
            if not d.startswith(".")
            and d not in IGNORE_PATTERNS
            and not any(pattern in d.lower() for pattern in ARCHIVE_PATTERNS)
        ]

        # Track skipped directories
        for d in original_dirnames:
            if d not in dirnames:
                skipped_folders.add(d)
                rel_path = os.path.relpath(os.path.join(root, d), directory)
                print(f"  SKIPPED FOLDER: {rel_path} (reason: {_get_skip_reason(d)})")

        # Check files
        for filename in filenames:
            # Skip dot files and ignored patterns
            if filename.startswith(".") or filename in IGNORE_PATTERNS:
                print(f"  SKIPPED FILE: {filename} (hidden or in ignore list)")
                continue

            # Check if markdown
            if filename.endswith(".md"):
                file_path = Path(root) / filename
                rel_path = file_path.relative_to(directory)
                markdown_files.append(str(rel_path))
                print(f"  FOUND MARKDOWN: {rel_path}")
            else:
                skipped_non_md_files.append(filename)

    print()
    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Markdown files found: {len(markdown_files)}")
    print(f"Folders skipped: {len(skipped_folders)}")
    print(f"Non-.md files skipped: {len(skipped_non_md_files)}")
    print()

    if len(markdown_files) == 0:
        print("WARNING: No markdown files found!")
        print()
        print("Possible reasons:")
        print("1. No files have .md extension")
        print("2. All .md files are in ignored folders")
        print("3. Directory is empty")
        print()

        if skipped_folders:
            print(f"Skipped folders: {', '.join(sorted(skipped_folders))}")

        if skipped_non_md_files:
            print(f"\nNon-.md files found: {len(skipped_non_md_files)}")
            print("Sample non-.md files:")
            for f in list(skipped_non_md_files)[:5]:
                print(f"  - {f}")
    else:
        print("Markdown files that will be indexed:")
        for f in markdown_files:
            print(f"  - {f}")


def _get_skip_reason(folder_name: str) -> str:
    """Get the reason why a folder was skipped."""
    if folder_name.startswith("."):
        return "starts with dot"
    if folder_name in IGNORE_PATTERNS:
        return "in ignore list"
    if any(pattern in folder_name.lower() for pattern in ARCHIVE_PATTERNS):
        return "archive/obsolete pattern"
    return "unknown"


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python diagnose_sync.py <directory_path>")
        print()
        print("Example:")
        print('  python diagnose_sync.py "C:\\Users\\sandr\\Documents\\chitchat"')
        sys.exit(1)

    directory_path = sys.argv[1]
    diagnose_directory(directory_path)
