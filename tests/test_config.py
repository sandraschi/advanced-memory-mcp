"""Test configuration management."""

import json
from pathlib import Path

from advanced_memory.config import (
    APP_DATABASE_NAME,
    DATA_DIR_NAME,
    VAULT_DIR_NAME,
    AdvancedMemoryConfig,
    ConfigManager,
)


class TestAdvancedMemoryConfig:
    """Test AdvancedMemoryConfig behavior with ADVANCED_MEMORY_HOME environment variable."""

    def test_default_behavior_without_advanced_memory_home(self, config_home, monkeypatch):
        """Test that config uses default path when ADVANCED_MEMORY_HOME is not set."""
        # Ensure ADVANCED_MEMORY_HOME is not set
        monkeypatch.delenv("ADVANCED_MEMORY_HOME", raising=False)

        config = AdvancedMemoryConfig()

        # Default vault is under ~/.advanced-memory/vault (never bare profile root)
        expected_path = str(config_home / DATA_DIR_NAME / VAULT_DIR_NAME)
        assert config.projects["main"] == expected_path

    def test_advanced_memory_home_moves_database_not_default_vault(self, config_home, monkeypatch):
        """``ADVANCED_MEMORY_HOME`` affects ``app_database_path`` only; default vault stays under ``Path.home()``."""
        custom_path = str(config_home / "app" / "data")
        monkeypatch.setenv("ADVANCED_MEMORY_HOME", custom_path)

        config = AdvancedMemoryConfig()

        assert config.projects["main"] == str(config_home / DATA_DIR_NAME / VAULT_DIR_NAME)
        assert config.app_database_path == Path(custom_path) / DATA_DIR_NAME / APP_DATABASE_NAME

    def test_model_post_init_respects_advanced_memory_home(self, config_home, monkeypatch):
        """Test that model_post_init no longer auto-creates main project."""
        custom_path = str(config_home / "custom" / "memory" / "path")
        monkeypatch.setenv("ADVANCED_MEMORY_HOME", custom_path)

        # Create config without main project
        other_path = str(config_home / "some" / "path")
        config = AdvancedMemoryConfig(projects={"other": other_path})

        # model_post_init should NOT auto-create main project anymore
        assert "main" not in config.projects
        assert "other" in config.projects
        # Default should be set to first available project
        assert config.default_project == "other"

    def test_model_post_init_fallback_without_advanced_memory_home(self, config_home, monkeypatch):
        """Test that model_post_init no longer auto-creates main project."""
        # Ensure ADVANCED_MEMORY_HOME is not set
        monkeypatch.delenv("ADVANCED_MEMORY_HOME", raising=False)

        # Create config without main project
        other_path = str(config_home / "some" / "path")
        config = AdvancedMemoryConfig(projects={"other": other_path})

        # model_post_init should NOT auto-create main project anymore
        assert "main" not in config.projects
        assert "other" in config.projects
        # Default should be set to first available project
        assert config.default_project == "other"

    def test_relative_advanced_memory_home_affects_db_only(self, config_home, monkeypatch):
        """Relative ``ADVANCED_MEMORY_HOME`` still does not move the default vault."""
        relative_path = "relative/memory/path"
        monkeypatch.setenv("ADVANCED_MEMORY_HOME", relative_path)

        config = AdvancedMemoryConfig()

        assert config.projects["main"] == str(config_home / DATA_DIR_NAME / VAULT_DIR_NAME)
        assert config.app_database_path == Path(relative_path) / DATA_DIR_NAME / APP_DATABASE_NAME

    def test_advanced_memory_home_overrides_existing_main_project(self, config_home, monkeypatch):
        """Test that ADVANCED_MEMORY_HOME is not used when a map is passed in the constructor."""
        custom_path = str(config_home / "override" / "memory" / "path")
        monkeypatch.setenv("ADVANCED_MEMORY_HOME", custom_path)

        # Try to create config with a different main project path
        original_path = str(config_home / "original" / "path")
        config = AdvancedMemoryConfig(projects={"main": original_path})

        # Explicit ``projects=`` wins over env / defaults
        assert config.projects["main"] == original_path

    def test_load_config_migrates_main_off_profile_root(self, tmp_path, monkeypatch):
        """Legacy ``main`` == profile root is rewritten to the default vault and saved."""
        monkeypatch.setenv("HOME", str(tmp_path))
        monkeypatch.setenv("USERPROFILE", str(tmp_path))
        monkeypatch.delenv("ADVANCED_MEMORY_HOME", raising=False)

        cfg_dir = tmp_path / ".advanced-memory"
        cfg_dir.mkdir(parents=True, exist_ok=True)
        cfg_file = cfg_dir / "config.json"
        cfg_file.write_text(
            json.dumps({"projects": {"main": str(tmp_path)}, "default_project": "main"}),
            encoding="utf-8",
        )

        mgr = ConfigManager()
        mgr.config_dir = cfg_dir
        mgr.config_file = cfg_file

        cfg = mgr.load_config()
        expected = str(tmp_path / DATA_DIR_NAME / VAULT_DIR_NAME)
        assert cfg.projects["main"] == expected
        on_disk = json.loads(cfg_file.read_text(encoding="utf-8"))
        assert on_disk["projects"]["main"] == expected
