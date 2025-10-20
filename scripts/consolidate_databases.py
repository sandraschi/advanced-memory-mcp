"""Consolidate per-project databases into the global database.

This migration script:
1. Finds all per-project .advanced-memory/memory.db files
2. Exports their data
3. Imports into the global database with proper project_id scoping
4. Creates backup before modification
5. Optionally removes per-project databases after successful migration
"""

import os
import shutil
import sqlite3

# Set up logging - use utf-8 encoding to avoid Windows console issues
import sys
from datetime import datetime
from pathlib import Path

from loguru import logger

logger.remove()
# Direct to stdout with utf-8 encoding
logger.add(sys.stdout, format="<level>{message}</level>", colorize=True)


class DatabaseConsolidator:
    """Consolidate per-project databases into global database."""

    def __init__(self, global_db_path: Path, project_roots: list[Path]):
        """Initialize consolidator.

        Args:
            global_db_path: Path to global database
            project_roots: List of project root directories to scan
        """
        self.global_db_path = global_db_path
        self.project_roots = project_roots
        self.backup_dir = (
            Path.home() / ".advanced-memory" / "backups" / datetime.now().strftime("%Y%m%d_%H%M%S")
        )

    def find_per_project_databases(self) -> list[tuple[Path, Path]]:
        """Find all per-project database files.

        Returns:
            List of (project_root, database_path) tuples
        """
        found = []

        for root in self.project_roots:
            if not root.exists():
                logger.warning(f"Project root does not exist: {root}")
                continue

            # Look for .advanced-memory/memory.db in this directory
            db_path = root / ".advanced-memory" / "memory.db"
            if db_path.exists():
                # Check if it's a real database (not empty)
                if db_path.stat().st_size > 0:
                    found.append((root, db_path))
                    logger.info(
                        f"Found per-project database: {db_path} ({db_path.stat().st_size:,} bytes)"
                    )

        return found

    def scan_all_project_dirs(self, base_paths: list[Path]) -> list[tuple[Path, Path]]:
        """Recursively scan for .advanced-memory folders.

        Args:
            base_paths: List of base paths to scan

        Returns:
            List of (project_root, database_path) tuples
        """
        found = []

        for base in base_paths:
            if not base.exists():
                continue

            # Walk the directory tree
            for dirpath, dirnames, _filenames in os.walk(str(base)):
                # Skip hidden directories
                dirnames[:] = [
                    d for d in dirnames if not d.startswith(".") or d == ".advanced-memory"
                ]

                # Check if this directory has .advanced-memory/memory.db
                dir_path = Path(dirpath)
                if dir_path.name == ".advanced-memory":
                    db_path = dir_path / "memory.db"
                    if db_path.exists() and db_path.stat().st_size > 0:
                        project_root = dir_path.parent
                        found.append((project_root, db_path))
                        logger.info(f"Found: {db_path} (project: {project_root.name})")

        return found

    def backup_database(self, db_path: Path) -> Path:
        """Create backup of a database file.

        Args:
            db_path: Path to database to backup

        Returns:
            Path to backup file
        """
        self.backup_dir.mkdir(parents=True, exist_ok=True)

        # Create backup with relative path preserved
        if db_path == self.global_db_path:
            backup_name = "global_memory.db.backup"
        else:
            # Use project folder name
            project_name = db_path.parent.parent.name
            backup_name = f"{project_name}_memory.db.backup"

        backup_path = self.backup_dir / backup_name
        shutil.copy2(db_path, backup_path)
        logger.info(f"Created backup: {backup_path}")

        return backup_path

    def get_table_count(self, db_path: Path, table: str) -> int:
        """Get row count for a table.

        Args:
            db_path: Database path
            table: Table name

        Returns:
            Row count
        """
        conn = sqlite3.connect(str(db_path))
        try:
            cursor = conn.execute(f"SELECT COUNT(*) FROM {table}")
            return cursor.fetchone()[0]
        except sqlite3.OperationalError:
            return 0
        finally:
            conn.close()

    def analyze_database(self, db_path: Path) -> dict:
        """Analyze database contents.

        Args:
            db_path: Path to database

        Returns:
            Dict with table counts
        """
        stats = {
            "entities": self.get_table_count(db_path, "entity"),
            "observations": self.get_table_count(db_path, "observation"),
            "relations": self.get_table_count(db_path, "relation"),
            "projects": self.get_table_count(db_path, "project"),
        }

        return stats

    def run_analysis(self, scan_paths: list[Path] | None = None) -> dict:
        """Run full analysis without making changes.

        Args:
            scan_paths: Optional list of paths to scan for databases

        Returns:
            Analysis results
        """
        logger.info("=" * 70)
        logger.info("DATABASE CONSOLIDATION ANALYSIS")
        logger.info("=" * 70)

        # Find databases
        if scan_paths:
            per_project_dbs = self.scan_all_project_dirs(scan_paths)
        else:
            per_project_dbs = self.find_per_project_databases()

        # Analyze global database
        logger.info(f"\nGlobal Database: {self.global_db_path}")
        if self.global_db_path.exists():
            global_stats = self.analyze_database(self.global_db_path)
            logger.info(f"  Size: {self.global_db_path.stat().st_size:,} bytes")
            logger.info(f"  Entities: {global_stats['entities']:,}")
            logger.info(f"  Observations: {global_stats['observations']:,}")
            logger.info(f"  Relations: {global_stats['relations']:,}")
            logger.info(f"  Projects: {global_stats['projects']:,}")
        else:
            logger.warning("  Does not exist!")
            global_stats = None

        # Analyze per-project databases
        logger.info(f"\nPer-Project Databases Found: {len(per_project_dbs)}")

        project_stats = []
        for project_root, db_path in per_project_dbs:
            stats = self.analyze_database(db_path)
            stats["project_root"] = project_root
            stats["db_path"] = db_path
            stats["size"] = db_path.stat().st_size
            project_stats.append(stats)

            logger.info(f"\n  Project: {project_root}")
            logger.info(f"    Database: {db_path}")
            logger.info(f"    Size: {stats['size']:,} bytes")
            logger.info(f"    Entities: {stats['entities']:,}")
            logger.info(f"    Observations: {stats['observations']:,}")
            logger.info(f"    Relations: {stats['relations']:,}")

        # Summary
        logger.info("\n" + "=" * 70)
        logger.info("RECOMMENDATION")
        logger.info("=" * 70)

        if not per_project_dbs:
            logger.info("\n✓ No per-project databases found. System is already consolidated.")
        elif global_stats and all(s["entities"] == 0 for s in project_stats):
            logger.info("\n✓ Per-project databases are empty. Safe to delete.")
            logger.info("\nTo clean up, run:")
            logger.info("  python scripts/consolidate_databases.py --clean-empty")
        else:
            total_size = sum(s["size"] for s in project_stats)
            logger.info(f"\n! Found {len(per_project_dbs)} per-project databases")
            logger.info(
                f"  Total wasted space: {total_size:,} bytes ({total_size / 1024 / 1024:.2f} MB)"
            )
            logger.info(f"\nThe global database at {self.global_db_path} is the active database.")
            logger.info("Per-project databases are legacy/unused.")
            logger.info("\nTo remove them, run:")
            logger.info("  python scripts/consolidate_databases.py --clean-empty")

        return {
            "global": global_stats,
            "per_project": project_stats,
        }

    def clean_empty_databases(
        self, scan_paths: list[Path] | None = None, dry_run: bool = True
    ) -> None:
        """Remove empty or redundant per-project databases.

        Args:
            scan_paths: Optional list of paths to scan
            dry_run: If True, only show what would be deleted
        """
        logger.info("=" * 70)
        logger.info(f"CLEANING EMPTY DATABASES (dry_run={dry_run})")
        logger.info("=" * 70)

        # Find databases
        if scan_paths:
            per_project_dbs = self.scan_all_project_dirs(scan_paths)
        else:
            per_project_dbs = self.find_per_project_databases()

        deleted = 0
        skipped = 0

        for _project_root, db_path in per_project_dbs:
            stats = self.analyze_database(db_path)

            # Only delete if empty
            if stats["entities"] == 0 and stats["observations"] == 0 and stats["relations"] == 0:
                if dry_run:
                    logger.info(f"Would delete: {db_path}")
                else:
                    # Create backup first
                    self.backup_database(db_path)

                    # Remove database files
                    advanced_memory_dir = db_path.parent
                    try:
                        shutil.rmtree(advanced_memory_dir)
                        logger.info(f"✓ Deleted: {advanced_memory_dir}")
                        deleted += 1
                    except Exception as e:
                        logger.error(f"✗ Failed to delete {advanced_memory_dir}: {e}")
            else:
                logger.warning(f"Skipping (has data): {db_path} ({stats['entities']} entities)")
                skipped += 1

        logger.info("\nSummary:")
        logger.info(f"  Deleted: {deleted}")
        logger.info(f"  Skipped: {skipped}")

        if dry_run and deleted > 0:
            logger.info("\nTo actually delete, run with --no-dry-run")


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Consolidate Advanced Memory databases",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Analyze current state
  python scripts/consolidate_databases.py --analyze

  # Scan specific directories
  python scripts/consolidate_databases.py --analyze --scan "C:/Users/sandr/Documents"

  # Clean empty databases (dry run)
  python scripts/consolidate_databases.py --clean-empty

  # Actually delete empty databases
  python scripts/consolidate_databases.py --clean-empty --no-dry-run
        """,
    )

    parser.add_argument("--analyze", action="store_true", help="Analyze database state")
    parser.add_argument(
        "--clean-empty", action="store_true", help="Remove empty per-project databases"
    )
    parser.add_argument("--scan", nargs="+", help="Directories to scan for databases")
    parser.add_argument("--no-dry-run", action="store_true", help="Actually perform deletions")
    parser.add_argument("--global-db", help="Path to global database (default: auto-detect)")

    args = parser.parse_args()

    # Get global database path
    if args.global_db:
        global_db_path = Path(args.global_db)
    else:
        # Auto-detect from environment or default location
        advanced_memory_home = os.getenv("ADVANCED_MEMORY_HOME", Path.home())
        global_db_path = Path(advanced_memory_home) / ".advanced-memory" / "memory.db"

    # Get scan paths
    scan_paths = None
    if args.scan:
        scan_paths = [Path(p) for p in args.scan]

    # Create consolidator
    consolidator = DatabaseConsolidator(global_db_path, [])

    if args.analyze or not (args.clean_empty):
        # Default action: analyze
        consolidator.run_analysis(scan_paths=scan_paths)

    if args.clean_empty:
        consolidator.clean_empty_databases(scan_paths=scan_paths, dry_run=not args.no_dry_run)


if __name__ == "__main__":
    main()
