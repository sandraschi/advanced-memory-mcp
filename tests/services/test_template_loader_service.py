"""Tests for template loader service"""

from advanced_memory.services.template_loader import (
    get_content_templates,
    get_template_loader,
)


def test_template_loader_singleton():
    """Test that get_template_loader returns same instance"""
    loader1 = get_template_loader()
    loader2 = get_template_loader()

    assert loader1 is loader2


def test_template_loader_finds_templates_dir():
    """Test that template loader finds zettelkasten/templates directory"""
    loader = get_template_loader()

    assert loader.templates_dir.exists()
    assert loader.templates_dir.name == "templates"
    assert (
        loader.templates_dir.parent.name == "zettelkasten"
        or loader.templates_dir.parent.name == "advanced_memory"
    )


def test_load_all_categories():
    """Test loading all template categories"""
    loader = get_template_loader()
    all_templates = loader.load_all_categories()

    # Should have multiple categories
    assert len(all_templates) >= 10

    # Should have expected categories
    expected_categories = [
        "developer",
        "researcher",
        "writer",
        "knowledge-worker",
        "creative",
        "devops",
        "data-scientist",
        "uiux-designer",
        "product-manager",
        "entrepreneur",
    ]

    for category in expected_categories:
        assert category in all_templates, f"Missing category: {category}"


def test_load_category():
    """Test loading specific category"""
    loader = get_template_loader()
    developer_templates = loader.load_category("developer")

    assert isinstance(developer_templates, dict)
    assert len(developer_templates) > 0

    # Check structure
    for topic_name, templates in developer_templates.items():
        assert isinstance(topic_name, str)
        assert isinstance(templates, list)

        for template in templates:
            assert "title" in template
            assert "folder" in template
            assert "content" in template


def test_load_topic():
    """Test loading specific topic"""
    loader = get_template_loader()

    # Load python-core topic from developer category
    templates = loader.load_topic("developer", "python")

    assert isinstance(templates, list)
    assert len(templates) > 0

    # Verify template structure
    for template in templates:
        assert "title" in template
        assert "folder" in template
        assert "content" in template
        assert isinstance(template["content"], str)
        assert len(template["content"]) > 0


def test_list_available():
    """Test listing all available templates"""
    loader = get_template_loader()
    available = loader.list_available()

    assert isinstance(available, dict)
    assert len(available) >= 10

    # Each category should have topics
    for _category, topics in available.items():
        assert isinstance(topics, list)
        assert len(topics) > 0


def test_get_content_templates_helper():
    """Test backward-compatible helper function"""
    templates = get_content_templates()

    assert isinstance(templates, dict)
    assert len(templates) >= 10

    # Should match loader.load_all_categories()
    loader = get_template_loader()
    expected = loader.load_all_categories()

    assert set(templates.keys()) == set(expected.keys())


def test_template_content_valid():
    """Test that loaded templates have valid markdown content"""
    loader = get_template_loader()
    templates = loader.load_topic("developer", "python")

    for template in templates:
        content = template["content"]

        # Should have heading
        assert content.startswith("#") or "# " in content[:100]

        # Should have substantive content
        assert len(content) > 100

        # Should not have Python dictionary artifacts
        assert "DEVELOPER_TEMPLATES" not in content
        assert "'title':" not in content


def test_fallback_to_python_templates():
    """Test fallback to Python templates for categories without markdown"""
    loader = get_template_loader()

    # This should still work even if some categories are Python-only
    all_templates = loader.load_all_categories()

    # We should have at least the markdown-extracted ones
    assert "developer" in all_templates
    assert "creative" in all_templates


def test_nonexistent_category():
    """Test handling of nonexistent category"""
    loader = get_template_loader()

    result = loader.load_category("nonexistent-category")

    # Should return empty dict or fallback gracefully
    assert isinstance(result, dict)


def test_nonexistent_topic():
    """Test handling of nonexistent topic"""
    loader = get_template_loader()

    result = loader.load_topic("developer", "nonexistent-topic")

    # Should return empty list or fallback gracefully
    assert isinstance(result, list)


def test_template_folder_structure():
    """Test that templates follow expected folder structure"""
    loader = get_template_loader()
    templates = loader.load_topic("developer", "python")

    for template in templates:
        folder = template["folder"]

        # Should have category/topic structure
        assert "/" in folder or folder in ["developer", "python", "developer/python"]
