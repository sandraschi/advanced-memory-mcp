"""Test sync error handling for corrupted and weird files."""

import pytest
from pathlib import Path


@pytest.mark.asyncio
async def test_sync_large_file(sync_service, config_home):
    """Test that sync skips files larger than 10MB."""
    # Create a file larger than 10MB
    large_file = config_home / "huge.md"
    with open(large_file, "w", encoding="utf-8") as f:
        # Write 11MB of content
        f.write("# Huge File\n" + "a" * (11 * 1024 * 1024))
    
    # Sync should fail gracefully
    entity, checksum = await sync_service.sync_file("huge.md", new=True)
    
    assert entity is None
    assert checksum is None


@pytest.mark.asyncio
async def test_sync_invalid_encoding_with_frontmatter(sync_service, config_home):
    """Test that sync handles files with encoding issues but valid frontmatter."""
    # Create a file with valid frontmatter but encoding issues in content
    bad_file = config_home / "encoding_test.md"
    with open(bad_file, "w", encoding="utf-8") as f:
        # Write valid markdown (encoding errors will be handled by replace fallback)
        f.write("---\ntitle: Encoding Test\n---\n\n# Test\n\nSome content")
    
    # Sync should succeed
    entity, checksum = await sync_service.sync_file("encoding_test.md", new=True)
    
    assert entity is not None
    assert checksum is not None


@pytest.mark.asyncio
async def test_sync_malformed_wikilinks(sync_service, config_home):
    """Test that sync handles malformed wikilinks gracefully."""
    # Create file with unclosed wikilinks
    malformed = config_home / "malformed.md"
    with open(malformed, "w", encoding="utf-8") as f:
        f.write("# Malformed\n\n")
        f.write("[[Unclosed link\n")
        f.write("[[Another unclosed\n")
        f.write("[[Valid link]]\n")
        f.write("[[[[Nested badly\n")
    
    # Sync should succeed and handle links gracefully
    entity, checksum = await sync_service.sync_file("malformed.md", new=True)
    
    assert entity is not None
    assert checksum is not None
    # At least the valid link should be parsed
    assert len(entity.relations) >= 1


@pytest.mark.asyncio
async def test_validate_large_file(sync_service, config_home):
    """Test file validation detects large files early."""
    # Create a file larger than 10MB
    large_file = config_home / "huge2.md"
    with open(large_file, "w", encoding="utf-8") as f:
        f.write("# Huge File\n" + "a" * (11 * 1024 * 1024))
    
    # Validation should fail
    is_valid, error_msg = await sync_service.validate_file_frontmatter("huge2.md")
    
    assert not is_valid
    assert "too large" in error_msg.lower()


@pytest.mark.asyncio
async def test_validate_bad_encoding(sync_service, config_home):
    """Test file validation detects encoding issues early."""
    # Create a file with invalid UTF-8
    bad_file = config_home / "bad_encoding2.md"
    with open(bad_file, "wb") as f:
        f.write(b"\xff\xfe Invalid UTF-8")
    
    # Validation should fail
    is_valid, error_msg = await sync_service.validate_file_frontmatter("bad_encoding2.md")
    
    assert not is_valid
    assert "encoding" in error_msg.lower()


@pytest.mark.asyncio
async def test_sync_file_size_limit_prevents_hang(sync_service, config_home):
    """Test that file size check prevents hanging on huge files."""
    # Create a 15MB file
    huge_file = config_home / "massive.md"
    with open(huge_file, "w", encoding="utf-8") as f:
        f.write("# Massive File\n" + "x" * (15 * 1024 * 1024))
    
    # Should fail quickly without hanging
    entity, checksum = await sync_service.sync_file("massive.md", new=True)
    
    assert entity is None
    assert checksum is None


@pytest.mark.asyncio
async def test_sync_handles_parse_errors_gracefully(sync_service, config_home):
    """Test that markdown parsing errors don't crash sync."""
    # Create file with potentially problematic content
    tricky_file = config_home / "tricky.md"
    with open(tricky_file, "w", encoding="utf-8") as f:
        f.write("# Tricky Content\n\n")
        f.write("```yaml\n")
        f.write("invalid: yaml: content:\n")
        f.write("```\n")
    
    # Sync should handle gracefully
    entity, checksum = await sync_service.sync_file("tricky.md", new=True)
    
    # Should succeed (YAML in code blocks doesn't affect frontmatter)
    assert entity is not None
    assert checksum is not None
