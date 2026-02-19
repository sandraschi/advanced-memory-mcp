"""Portmanteau tool for AI observability and Entire.io Checkpoints.

PORTMANTEAU PATTERN RATIONALE: Consolidates observability, audit, and provenance
operations including session recording, repository checkpointing, and rewinding
into a single tool. This ensures a clean interface for agentic audit trails.
"""

import subprocess
from typing import Annotated, Literal

from loguru import logger
from pydantic import Field

from advanced_memory.mcp.mcp_instance import mcp
from advanced_memory.mcp.tools.utils import build_error_response, build_success_response


@mcp.tool
async def adn_observability(
    operation: Annotated[
        Literal[
            "enable",
            "disable",
            "list",
            "rewind",
            "clean",
            "status",
        ],
        Field(description="Observability operation to perform"),
    ],
    checkpoint_id: Annotated[
        str | None, Field(description="Checkpoint ID for rewind operation")
    ] = None,
    repo_path: Annotated[str | None, Field(description="Path to the repository")] = None,
) -> dict:
    """Unified tool for AI agent observability and provenance via Entire.io Checkpoints.

    This tool wraps the @entire/checkpoints-cli to provide:
    - Session recording and Git-linked audit trails
    - Repository state checkpointing
    - Workspace rewinding to known-good states
    - Observability status monitoring

    Args:
        operation: The specific observability operation
        checkpoint_id: Unique ID for identifying a specific state
        repo_path: Target repository path (defaults to current)

    Returns:
        Operation result or checkpoint list
    """
    try:
        cwd = repo_path or "."

        if operation == "enable":
            result = subprocess.run(
                ["checkpoints", "enable"], cwd=cwd, capture_output=True, text=True, check=False
            )
            if result.returncode != 0:
                return build_error_response("CLI_ERROR", "ENABLE_FAILED", result.stderr)
            return build_success_response(
                "enable", {"message": "Entire.io Checkpoints enabled successfully"}
            )

        elif operation == "disable":
            result = subprocess.run(
                ["checkpoints", "disable"], cwd=cwd, capture_output=True, text=True, check=False
            )
            if result.returncode != 0:
                return build_error_response("CLI_ERROR", "DISABLE_FAILED", result.stderr)
            return build_success_response(
                "disable", {"message": "Entire.io Checkpoints disabled successfully"}
            )

        elif operation == "list":
            # For now, simulate listing if CLI doesn't support structured output yet
            # Real implementation would parse 'checkpoints list' (assuming it exists or reading the branch)
            # Since we are SOTA, we'll try to get real data if possible
            result = subprocess.run(
                ["git", "log", "entire/checkpoints/v1", "--pretty=format:%H|%an|%s|%at"],
                cwd=cwd,
                capture_output=True,
                text=True,
                check=False,
            )

            if result.returncode != 0:
                # If branch doesn't exist, return empty or mock if in development
                return build_success_response("list", {"checkpoints": []})

            checkpoints = []
            for line in result.stdout.strip().split("\n"):
                if not line:
                    continue
                parts = line.split("|")
                if len(parts) >= 4:
                    checkpoints.append(
                        {
                            "id": parts[0][:8],
                            "commitHash": parts[0][:7],
                            "agentName": parts[1],
                            "summary": parts[2],
                            "timestamp": parts[3],  # Unix timestamp
                            "tokens": 0,  # Placeholder until we parse metadata
                            "files": [],  # Placeholder
                        }
                    )
            return build_success_response("list", {"checkpoints": checkpoints})

        elif operation == "rewind":
            if not checkpoint_id:
                return build_error_response(
                    "VALIDATION_ERROR", "MISSING_ID", "Checkpoint ID required for rewind"
                )

            result = subprocess.run(
                ["checkpoints", "rewind", checkpoint_id],
                cwd=cwd,
                capture_output=True,
                text=True,
                check=False,
            )
            if result.returncode != 0:
                return build_error_response("CLI_ERROR", "REWIND_FAILED", result.stderr)
            return build_success_response(
                "rewind", {"message": f"Workspace rewound to {checkpoint_id}"}
            )

        elif operation == "clean":
            result = subprocess.run(
                ["checkpoints", "clean"], cwd=cwd, capture_output=True, text=True, check=False
            )
            if result.returncode != 0:
                return build_error_response("CLI_ERROR", "CLEAN_FAILED", result.stderr)
            return build_success_response("clean", {"message": "Checkpoint data cleaned"})

        elif operation == "status":
            # Check if enabled by looking for the branch or CLI status
            result = subprocess.run(
                ["git", "branch", "--list", "entire/checkpoints/v1"],
                cwd=cwd,
                capture_output=True,
                text=True,
                check=False,
            )
            is_enabled = "entire/checkpoints/v1" in result.stdout
            return build_success_response("status", {"enabled": is_enabled, "protocol": "v1"})

        else:
            return build_error_response(
                "VALIDATION_ERROR", "UNKNOWN_OP", f"Unknown operation: {operation}"
            )

    except Exception as e:
        logger.error(f"Observability operation '{operation}' failed: {e}")
        return build_error_response("SYSTEM_ERROR", "OPERATION_FAILED", str(e))
