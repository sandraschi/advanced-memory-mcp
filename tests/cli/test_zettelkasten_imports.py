"""Test that all zettelkasten template modules import correctly."""

import pytest


def test_import_all_templates():
    """Test that all template modules can be imported."""
    try:
        from advanced_memory.cli.zettelkasten_content import (
            CREATIVE_TEMPLATES,
            DATA_SCIENTIST_TEMPLATES,
            DEVELOPER_TEMPLATES,
            DEVOPS_TEMPLATES,
            ENTREPRENEUR_TEMPLATES,
            KNOWLEDGE_WORKER_TEMPLATES,
            PRODUCT_MANAGER_TEMPLATES,
            RESEARCHER_TEMPLATES,
            UIUX_DESIGNER_TEMPLATES,
            WRITER_TEMPLATES,
        )

        # Verify they're dictionaries
        assert isinstance(DEVELOPER_TEMPLATES, dict)
        assert isinstance(RESEARCHER_TEMPLATES, dict)
        assert isinstance(WRITER_TEMPLATES, dict)
        assert isinstance(KNOWLEDGE_WORKER_TEMPLATES, dict)
        assert isinstance(DEVOPS_TEMPLATES, dict)
        assert isinstance(DATA_SCIENTIST_TEMPLATES, dict)
        assert isinstance(UIUX_DESIGNER_TEMPLATES, dict)
        assert isinstance(PRODUCT_MANAGER_TEMPLATES, dict)
        assert isinstance(ENTREPRENEUR_TEMPLATES, dict)
        assert isinstance(CREATIVE_TEMPLATES, dict)

        # Verify they have content
        assert len(DEVELOPER_TEMPLATES) > 0
        assert len(DEVOPS_TEMPLATES) > 0

    except ImportError as e:
        pytest.fail(f"Failed to import templates: {e}")


def test_onboard_command_imports():
    """Test that onboard command imports successfully."""
    try:
        from advanced_memory.cli.commands.onboard import CONTENT_TEMPLATES

        # Should have all 10 categories
        assert len(CONTENT_TEMPLATES) == 10
        assert "developer" in CONTENT_TEMPLATES
        assert "devops" in CONTENT_TEMPLATES
        assert "data-scientist" in CONTENT_TEMPLATES
        assert "uiux-designer" in CONTENT_TEMPLATES
        assert "product-manager" in CONTENT_TEMPLATES
        assert "entrepreneur" in CONTENT_TEMPLATES
        assert "creative" in CONTENT_TEMPLATES

    except ImportError as e:
        pytest.fail(f"Failed to import onboard command: {e}")
