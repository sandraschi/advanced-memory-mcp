"""Test UTF-8 character handling in file operations."""

import pytest

from advanced_memory import file_utils
from advanced_memory.file_utils import compute_checksum, write_file_atomic


@pytest.mark.asyncio
async def test_write_utf8_characters(tmp_path):
    """Test writing files with UTF-8 characters."""
    # Create a test file with various UTF-8 characters
    test_path = tmp_path / "utf8_test.md"

    # Include characters from various scripts
    utf8_content = """# UTF-8 Test Document

## Cyrillic
Привет мир! (Hello world in Russian)

## Greek
Γειά σου Κόσμε! (Hello world in Greek)

## Chinese
你好世界! (Hello world in Chinese)

## Japanese
こんにちは世界! (Hello world in Japanese)

## Arabic
مرحبا بالعالم! (Hello world in Arabic)

## Emoji
🌍 🌎 🌏 🌐 🗺️ 🧭
"""

    # Test the atomic write function with UTF-8 content
    await write_file_atomic(test_path, utf8_content)

    # Verify the file was written correctly
    assert test_path.exists()

    # Read the file back and verify content
    content = test_path.read_text(encoding="utf-8")
    assert "Привет мир!" in content
    assert "Γειά σου Κόσμε!" in content
    assert "你好世界" in content
    assert "こんにちは世界" in content
    assert "مرحبا بالعالم" in content
    assert "🌍 🌎 🌏" in content

    # Verify checksums match
    checksum1 = await compute_checksum(utf8_content)
    checksum2 = await compute_checksum(content)
    assert checksum1 == checksum2


@pytest.mark.asyncio
async def test_frontmatter_with_utf8(tmp_path):
    """Test handling of frontmatter with UTF-8 characters."""
    # Create a test file with frontmatter containing UTF-8
    test_path = tmp_path / "frontmatter_utf8.md"

    # Create content with UTF-8 in frontmatter
    content = """---
title: UTF-8 测试文件 (Test File)
author: José García
keywords:
  - тестирование
  - 테스트
  - 测试
---

# UTF-8 Support Test

This file has UTF-8 characters in the frontmatter.
"""

    # Write the file
    await write_file_atomic(test_path, content)

    # Update frontmatter with more UTF-8
    await file_utils.update_frontmatter(
        test_path,
        {
            "description": "这是一个测试文件 (This is a test file)",
            "tags": ["国际化", "юникод", "🔤"],
        },
    )

    # Read back and check
    updated_content = test_path.read_text(encoding="utf-8")

    # Original values should be preserved
    assert "title: UTF-8 测试文件" in updated_content
    assert "author: José García" in updated_content

    # New values should be added
    assert "description: 这是一个测试文件" in updated_content
    assert "国际化" in updated_content
    assert "юникод" in updated_content
    assert "🔤" in updated_content


@pytest.mark.asyncio
async def test_utf8_in_entity_sync(sync_service, project_config):
    """Test syncing an entity with UTF-8 content."""
    project_dir = project_config.home

    # Create a test file with UTF-8 characters
    test_file = project_dir / "utf8_entity.md"
    utf8_content = """---
type: knowledge
permalink: i18n/utf8-document
---
# UTF-8 测试文档

## Observations
- [language] العربية (Arabic) is written right-to-left
- [language] 日本語 (Japanese) uses three writing systems
- [encoding] UTF-8 可以编码所有 Unicode 字符

## Relations
- relates_to [[i18n/Ελληνικά]]
- relates_to [[i18n/Русский]]
"""

    # Write the file
    test_file.parent.mkdir(parents=True, exist_ok=True)
    test_file.write_text(utf8_content, encoding="utf-8")

    # Sync the file
    await sync_service.sync(project_config.home)

    # Verify entity was created
    entity = await sync_service.entity_service.get_by_permalink("i18n/utf8-document")
    assert entity is not None

    # Verify observations were created with UTF-8 content
    assert len(entity.observations) == 3

    # Check observation content
    obs_categories = [o.category for o in entity.observations]
    obs_content = [o.content for o in entity.observations]

    assert "language" in obs_categories
    assert "encoding" in obs_categories
    assert any("العربية" in c for c in obs_content)
    assert any("日本語" in c for c in obs_content)
    assert any("Unicode" in c for c in obs_content)

    # Check relations
    assert len(entity.relations) == 2
    relation_names = [r.to_name for r in entity.relations]
    assert "i18n/Ελληνικά" in relation_names
    assert "i18n/Русский" in relation_names


@pytest.mark.asyncio
async def test_write_file_service_utf8(sync_service, project_config):
    """Test FileService handling of UTF-8 content."""
    file_service = sync_service.file_service

    # Test writing UTF-8 content through the file service
    test_path = "utf8_service_test.md"
    utf8_content = """---
title: FileService UTF-8 Test
---
# UTF-8 通过 FileService 测试

Testing FileService with UTF-8:
* Português: Olá mundo!
* Thai: สวัสดีชาวโลก
* Korean: 안녕하세요 세계
* Hindi: नमस्ते दुनिया
"""

    # Use the file service to write the file
    checksum = await file_service.write_file(test_path, utf8_content)

    # Verify file exists
    full_path = file_service.base_path / test_path
    assert full_path.exists()

    # Read back content and verify
    content, read_checksum = await file_service.read_file(test_path)

    assert "通过" in content
    assert "Português" in content
    assert "สวัสดีชาวโลก" in content
    assert "안녕하세요" in content
    assert "नमस्ते" in content

    # Checksums should match
    assert checksum == read_checksum
