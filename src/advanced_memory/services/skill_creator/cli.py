"""Command line interface for the Advanced Memory skill creator."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from loguru import logger

from .packager import package_skill
from .scaffolder import scaffold_skill
from .upgrader import upgrade_skill
from .validator import validate_skill


def _configure_logger(verbose: bool) -> None:
    if verbose:
        logger.enable(__name__)
    else:
        logger.remove()
        logger.add(sys.stderr, level="INFO")


def _cmd_scaffold(args: argparse.Namespace) -> None:
    path = scaffold_skill(
        args.skill_name,
        args.output_dir,
        category=args.category,
        confidence=args.confidence,
        overwrite=args.overwrite,
    )
    print(json.dumps({"success": True, "skill_path": str(path)}))


def _cmd_validate(args: argparse.Namespace) -> None:
    ok, issues = validate_skill(args.skill_path)
    print(
        json.dumps(
            {
                "success": ok,
                "issues": [
                    {"path": issue.path, "issue": issue.issue, "fix": issue.fix}
                    for issue in issues
                ],
            },
            indent=2,
        )
    )
    if not ok:
        sys.exit(1)


def _cmd_package(args: argparse.Namespace) -> None:
    archive = package_skill(args.skill_path, args.output_dir)
    print(json.dumps({"success": True, "archive": str(archive)}))


def _cmd_upgrade(args: argparse.Namespace) -> None:
    path = upgrade_skill(args.skill_path)
    print(json.dumps({"success": True, "skill_path": str(path)}))


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        prog="am-skill-creator", description="Advanced Memory skill creator utilities."
    )
    parser.add_argument("--verbose", action="store_true", help="Enable verbose logging.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    scaffold = subparsers.add_parser("scaffold", help="Create a new skill scaffold.")
    scaffold.add_argument("skill_name", help="Skill name (hyphen-case preferred).")
    scaffold.add_argument(
        "--output-dir",
        default=Path.cwd(),
        help="Directory in which to create the skill (default: current directory).",
    )
    scaffold.add_argument("--category", default="general", help="Metadata category.")
    scaffold.add_argument(
        "--confidence",
        choices=["low", "medium", "high"],
        default="low",
        help="Initial confidence level.",
    )
    scaffold.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite existing skill directory if present.",
    )
    scaffold.set_defaults(func=_cmd_scaffold)

    validate = subparsers.add_parser(
        "validate", help="Validate a modular skill folder."
    )
    validate.add_argument("skill_path", help="Path to the skill directory.")
    validate.set_defaults(func=_cmd_validate)

    package = subparsers.add_parser("package", help="Package a skill into a zip file.")
    package.add_argument("skill_path", help="Path to the skill directory.")
    package.add_argument(
        "--output-dir",
        default=None,
        help="Destination directory for the zip archive (default: skill parent).",
    )
    package.set_defaults(func=_cmd_package)

    upgrade = subparsers.add_parser(
        "upgrade", help="Upgrade a legacy skill to modular format."
    )
    upgrade.add_argument("skill_path", help="Path to the skill directory.")
    upgrade.set_defaults(func=_cmd_upgrade)

    args = parser.parse_args(argv)
    _configure_logger(args.verbose)
    args.func(args)


if __name__ == "__main__":
    main()

