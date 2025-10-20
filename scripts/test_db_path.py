"""Test what database path is actually being used."""
import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from advanced_memory.config import ConfigManager

config = ConfigManager().config

print("Environment Variables:")
print(f"  ADVANCED_MEMORY_HOME: {os.getenv('ADVANCED_MEMORY_HOME', 'NOT SET')}")
print(f"  Path.home(): {Path.home()}")
print()

print("Configuration:")
print(f"  Default project: {config.default_project}")
print(f"  Projects: {config.projects}")
print()

print("Database Paths:")
print(f"  app_config.database_path: {config.database_path}")
print(f"  app_config.app_database_path: {config.app_database_path}")
print()

print("Files exist:")
print(f"  {config.database_path}: {config.database_path.exists()}")
print(f"  {config.app_database_path}: {config.app_database_path.exists()}")




