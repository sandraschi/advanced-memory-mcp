"""Test configuration management."""

from advanced_memory.config import AdvancedMemoryConfig


class TestAdvancedMemoryConfig:
    """Test AdvancedMemoryConfig behavior with ADVANCED_MEMORY_HOME environment variable."""

    def test_default_behavior_without_advanced_memory_home(self, config_home, monkeypatch):
        """Test that config uses default path when ADVANCED_MEMORY_HOME is not set."""
        # Ensure ADVANCED_MEMORY_HOME is not set
        monkeypatch.delenv("ADVANCED_MEMORY_HOME", raising=False)

        config = AdvancedMemoryConfig()

        # Should use the default path (home/advanced-memory)
        # Note: config_home fixture sets HOME to tmp_path, so Path.home() returns tmp_path
        expected_path = str(config_home / "advanced-memory")
        assert config.projects["main"] == expected_path

    def test_respects_advanced_memory_home_environment_variable(self, config_home, monkeypatch):
        """Test that config respects ADVANCED_MEMORY_HOME environment variable."""
        custom_path = str(config_home / "app" / "data")
        monkeypatch.setenv("ADVANCED_MEMORY_HOME", custom_path)

        config = AdvancedMemoryConfig()

        # Should use the custom path from environment variable
        assert config.projects["main"] == custom_path

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

    def test_advanced_memory_home_with_relative_path(self, config_home, monkeypatch):
        """Test that ADVANCED_MEMORY_HOME works with relative paths."""
        relative_path = "relative/memory/path"
        monkeypatch.setenv("ADVANCED_MEMORY_HOME", relative_path)

        config = AdvancedMemoryConfig()

        # Should use the exact value from environment variable
        # Note: Path conversion may change separators on Windows
        import os
        expected_path = os.path.normpath(relative_path)
        assert config.projects["main"] == expected_path

    def test_advanced_memory_home_overrides_existing_main_project(self, config_home, monkeypatch):
        """Test that ADVANCED_MEMORY_HOME is not used when a map is passed in the constructor."""
        custom_path = str(config_home / "override" / "memory" / "path")
        monkeypatch.setenv("ADVANCED_MEMORY_HOME", custom_path)

        # Try to create config with a different main project path
        original_path = str(config_home / "original" / "path")
        config = AdvancedMemoryConfig(projects={"main": original_path})

        # The default_factory should override with ADVANCED_MEMORY_HOME value
        # Note: This tests the current behavior where default_factory takes precedence
        assert config.projects["main"] == original_path
