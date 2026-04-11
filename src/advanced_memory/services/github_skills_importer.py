"""GitHub-based skills importer for Advanced Memory.

This module provides functionality to import Claude Skills from GitHub repositories,
enabling integration with SkillsMP.com and other GitHub-hosted skill collections.
"""

import re
import tempfile
from pathlib import Path
from typing import Any

import requests
from git import Repo
from loguru import logger


class GitHubSkillsImporter:
    """Import Claude Skills from GitHub repositories."""

    def __init__(self, github_token: str | None = None):
        """Initialize GitHub skills importer.

        Args:
            github_token: Optional GitHub token for authenticated requests
                (increases rate limits, enables private repos)
        """
        self.github_token = github_token
        self.base_url = "https://api.github.com"
        self.headers = {"Accept": "application/vnd.github.v3+json"}
        if github_token:
            self.headers["Authorization"] = f"token {github_token}"

    def _parse_repo_url(self, repository: str) -> tuple[str, str]:
        """Parse repository identifier into owner and repo name.

        Args:
            repository: Repository identifier (e.g., "user/repo" or full URL)

        Returns:
            Tuple of (owner, repo_name)

        Raises:
            ValueError: If repository identifier is invalid
        """
        # Handle full URLs
        if "github.com" in repository:
            match = re.search(r"github\.com[/:]([\w\-\.]+)/([\w\-\.]+)", repository)
            if match:
                return match.group(1), match.group(2).replace(".git", "")
            raise ValueError(f"Invalid GitHub URL format: {repository}")

        # Handle owner/repo format
        if "/" in repository:
            parts = repository.split("/")
            if len(parts) == 2:
                return parts[0], parts[1]
            raise ValueError(f"Invalid repository format: {repository}. Use 'owner/repo'")

        raise ValueError(f"Invalid repository identifier: {repository}")

    def get_repo_info(self, repository: str) -> dict[str, Any]:
        """Get repository information from GitHub API.

        Args:
            repository: Repository identifier (e.g., "user/repo")

        Returns:
            Dictionary with repository information

        Raises:
            Exception: If repository cannot be accessed
        """
        try:
            owner, repo_name = self._parse_repo_url(repository)
            url = f"{self.base_url}/repos/{owner}/{repo_name}"

            logger.info(f"Fetching repo info: {owner}/{repo_name}")
            response = requests.get(url, headers=self.headers, timeout=30)

            if response.status_code == 404:
                raise ValueError(f"Repository not found: {repository}")
            response.raise_for_status()

            return response.json()
        except requests.RequestException as e:
            logger.error(f"Error fetching repo info: {e}")
            raise ValueError(f"Failed to access repository {repository}: {e!s}") from e

    def find_skills_in_repo(
        self, repository: str, branch: str = "main", pattern: str = "**/SKILL.md"
    ) -> list[dict[str, Any]]:
        """Find all SKILL.md files in a repository.

        Args:
            repository: Repository identifier (e.g., "user/repo")
            branch: Branch to search (default: "main")
            pattern: Glob pattern to search for (default: "**/SKILL.md")

        Returns:
            List of dictionaries with skill information:
            - path: Path to SKILL.md in repo
            - folder: Folder containing the skill
            - name: Skill name (from path)
        """
        try:
            owner, repo_name = self._parse_repo_url(repository)
            url = f"{self.base_url}/repos/{owner}/{repo_name}/git/trees/{branch}?recursive=1"

            logger.info(f"Searching for skills in {owner}/{repo_name}:{branch}")
            response = requests.get(url, headers=self.headers, timeout=30)
            response.raise_for_status()

            tree = response.json()
            skills = []

            for item in tree.get("tree", []):
                if item["type"] == "blob" and item["path"].endswith("/SKILL.md"):
                    # Extract skill folder and name
                    skill_path = Path(item["path"])
                    skill_folder = str(skill_path.parent)
                    skill_name = skill_folder.split("/")[-1] if "/" in skill_folder else skill_folder

                    skills.append(
                        {
                            "path": item["path"],
                            "folder": skill_folder,
                            "name": skill_name,
                            "sha": item["sha"],
                        }
                    )

            logger.info(f"Found {len(skills)} skills in repository")
            return skills
        except requests.RequestException as e:
            logger.error(f"Error searching repository: {e}")
            return []

    def get_file_content(self, repository: str, file_path: str, branch: str = "main") -> str:
        """Get file content from GitHub repository.

        Args:
            repository: Repository identifier (e.g., "user/repo")
            file_path: Path to file in repository
            branch: Branch to fetch from (default: "main")

        Returns:
            File content as string

        Raises:
            ValueError: If file cannot be accessed
        """
        try:
            owner, repo_name = self._parse_repo_url(repository)
            url = f"{self.base_url}/repos/{owner}/{repo_name}/contents/{file_path}"
            params = {"ref": branch}

            logger.info(f"Fetching file: {file_path} from {owner}/{repo_name}")
            response = requests.get(url, headers=self.headers, params=params, timeout=30)

            if response.status_code == 404:
                raise ValueError(f"File not found: {file_path} in {repository}")
            response.raise_for_status()

            file_data = response.json()

            # Decode base64 content
            import base64

            content = base64.b64decode(file_data["content"]).decode("utf-8")
            return content
        except requests.RequestException as e:
            logger.error(f"Error fetching file: {e}")
            raise ValueError(f"Failed to fetch file {file_path}: {e!s}") from e

    def clone_repo(self, repository: str, branch: str = "main") -> Path:
        """Clone repository to temporary directory.

        Args:
            repository: Repository identifier (e.g., "user/repo")
            branch: Branch to clone (default: "main")

        Returns:
            Path to cloned repository directory

        Raises:
            ValueError: If clone fails
        """
        try:
            owner, repo_name = self._parse_repo_url(repository)
            repo_url = f"https://github.com/{owner}/{repo_name}.git"

            # Create temporary directory
            temp_dir = Path(tempfile.mkdtemp(prefix=f"advanced-memory-github-{repo_name}-"))

            logger.info(f"Cloning {owner}/{repo_name} to {temp_dir}")

            # Clone repository
            if self.github_token:
                # Use authenticated URL for private repos
                repo_url = repo_url.replace("https://", f"https://{self.github_token}@")

            Repo.clone_from(repo_url, str(temp_dir), branch=branch, depth=1)

            logger.info(f"Successfully cloned repository to {temp_dir}")
            return temp_dir
        except Exception as e:
            logger.error(f"Error cloning repository: {e}")
            raise ValueError(f"Failed to clone repository {repository}: {e!s}") from e

    def import_skill_from_repo(
        self, repository: str, skill_path: str | None = None, branch: str = "main"
    ) -> dict[str, Any]:
        """Import a skill from GitHub repository.

        Args:
            repository: Repository identifier (e.g., "user/repo")
            skill_path: Path to skill folder in repo (optional, will search if not provided)
            branch: Branch to import from (default: "main")

        Returns:
            Dictionary with skill information:
            - skill_path: Path to skill directory
            - skill_md_path: Path to SKILL.md file
            - content: SKILL.md content
            - resources: Paths to scripts/, references/, assets/ if present
        """
        if skill_path:
            # Import specific skill
            skill_md_path = f"{skill_path}/SKILL.md" if not skill_path.endswith("SKILL.md") else skill_path

            try:
                content = self.get_file_content(repository, skill_md_path, branch)
                return {
                    "skill_path": skill_path,
                    "skill_md_path": skill_md_path,
                    "content": content,
                    "resources": {},
                }
            except ValueError as e:
                logger.error(f"Failed to import skill: {e}")
                raise

        # Find all skills in repo
        skills = self.find_skills_in_repo(repository, branch)
        if not skills:
            raise ValueError(f"No skills found in repository {repository}")

        # For now, return first skill found
        # TODO: Support multiple skills in single import
        skill = skills[0]
        content = self.get_file_content(repository, skill["path"], branch)

        return {
            "skill_path": skill["folder"],
            "skill_md_path": skill["path"],
            "content": content,
            "resources": {},
        }
