#!/usr/bin/env python3
"""
Automated release script for Advanced Memory.

This script handles:
1. Version bumping in pyproject.toml
2. Changelog generation
3. Git tagging
4. Release creation on GitHub
"""

import argparse
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional, Tuple


def get_current_version() -> str:
    """Get current version from pyproject.toml"""
    pyproject_path = Path("pyproject.toml")

    if not pyproject_path.exists():
        raise FileNotFoundError("pyproject.toml not found")

    content = pyproject_path.read_text()
    version_match = re.search(r'version = "([^"]+)"', content)

    if not version_match:
        raise ValueError("Could not find version in pyproject.toml")

    return version_match.group(1)


def bump_version(current_version: str, bump_type: str) -> str:
    """Bump version based on type (patch, minor, major)"""
    parts = [int(x) for x in current_version.split(".")]

    if bump_type == "major":
        parts[0] += 1
        parts[1] = 0
        parts[2] = 0
    elif bump_type == "minor":
        parts[1] += 1
        parts[2] = 0
    elif bump_type == "patch":
        parts[2] += 1
    else:
        raise ValueError(f"Invalid bump type: {bump_type}")

    return ".".join(str(x) for x in parts)


def update_version_in_pyproject(new_version: str) -> None:
    """Update version in pyproject.toml"""
    pyproject_path = Path("pyproject.toml")
    content = pyproject_path.read_text()

    # Update version line
    updated_content = re.sub(
        r'version = "[^"]+"',
        f'version = "{new_version}"',
        content
    )

    pyproject_path.write_text(updated_content)
    print(f"Updated version to {new_version} in pyproject.toml")


def generate_changelog(new_version: str) -> str:
    """Generate changelog from recent commits"""
    try:
        # Get recent commits since last tag
        result = subprocess.run(
            ["git", "log", "--oneline", "--since=1 month ago", "--pretty=format:- %s"],
            capture_output=True,
            text=True,
            check=True
        )
        commits = result.stdout.strip()

        if not commits:
            commits = "- No recent commits found"

        changelog = f"""# Release {new_version}

## What's Changed

{commits}

## Full Changelog

See [full changelog](https://github.com/{get_repo_info()}/compare/v{get_previous_version()}...v{new_version})
"""
        return changelog

    except subprocess.CalledProcessError as e:
        print(f"Warning: Could not generate changelog: {e}")
        return f"# Release {new_version}\n\nAutomated release\n"


def get_repo_info() -> str:
    """Get repository info from git remote"""
    try:
        result = subprocess.run(
            ["git", "remote", "get-url", "origin"],
            capture_output=True,
            text=True,
            check=True
        )
        url = result.stdout.strip()

        # Extract owner/repo from URL
        if "github.com" in url:
            parts = url.split("github.com/")[1].rstrip(".git").split("/")
            return f"{parts[0]}/{parts[1]}"

        return "unknown/repo"
    except subprocess.CalledProcessError:
        return "unknown/repo"


def get_previous_version() -> str:
    """Get previous version from git tags"""
    try:
        result = subprocess.run(
            ["git", "describe", "--tags", "--abbrev=0", "HEAD^"],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip().lstrip("v")
    except subprocess.CalledProcessError:
        return "0.0.0"


def create_git_tag(new_version: str) -> None:
    """Create and push git tag"""
    tag_name = f"v{new_version}"

    # Create annotated tag
    subprocess.run([
        "git", "tag", "-a", tag_name,
        "-m", f"Release {new_version}"
    ], check=True)

    # Push tag to remote
    subprocess.run(["git", "push", "origin", tag_name], check=True)

    print(f"Created and pushed tag {tag_name}")


def main():
    parser = argparse.ArgumentParser(description="Release automation script")
    parser.add_argument(
        "bump_type",
        choices=["patch", "minor", "major"],
        help="Type of version bump"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without making changes"
    )

    args = parser.parse_args()

    try:
        # Get current version
        current_version = get_current_version()
        print(f"Current version: {current_version}")

        # Calculate new version
        new_version = bump_version(current_version, args.bump_type)
        print(f"New version: {new_version}")

        if args.dry_run:
            print("DRY RUN - No changes made")
            return

        # Update version in pyproject.toml
        update_version_in_pyproject(new_version)

        # Generate changelog
        changelog = generate_changelog(new_version)
        changelog_file = Path("CHANGELOG.md")
        changelog_file.write_text(changelog)
        print(f"Generated changelog in {changelog_file}")

        # Commit changes
        subprocess.run(["git", "add", "."], check=True)
        subprocess.run([
            "git", "commit", "-m", f"chore: release {new_version}"
        ], check=True)

        print(f"Committed changes for version {new_version}")

        # Create and push tag
        create_git_tag(new_version)

        print("
🎉 Release preparation complete!"        print(f"Version: {new_version}")
        print(f"Tag: v{new_version}")
        print("
Next steps:"        print("1. Push the commit: git push origin main")
        print("2. Create a GitHub release with the tag")
        print("3. The CI/CD will automatically publish to PyPI and build Docker images")

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
