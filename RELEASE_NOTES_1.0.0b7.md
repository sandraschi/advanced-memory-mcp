# Release Notes - v1.0.0b7

**Release Date**: 2025-10-28  
**Focus**: Skills Enhancement & Documentation Updates

## Major Enhancements

### Enhanced Skill Creation (Anthropic Pattern)

**Full bundled resource support** for `adn_skills("create", ...)`:

```python
adn_skills("create",
    skill_name="python-expert",
    description="Expert Python guidance",
    category="developer")
```

**Now creates complete structure**:
```
skills/developer/python-expert/
├── SKILL.md              # Instructions with YAML frontmatter
├── scripts/
│   └── example.py        # Executable code template
├── references/
│   └── example.md        # Reference documentation template
└── assets/
    └── README.md         # Assets directory guide
```

**Follows Anthropic's skill-creator initialization pattern exactly!**

## Documentation Updates

### Skills Documentation
- Updated `docs/user-guide/claude-skills.md` with:
  - Complete CRUD operations
  - Skill creation guide
  - 202-skill curated library information
  - Multi-skill plugin packaging
  - Quality ratings and The Pizza Test™

### Installation Documentation
- Updated `README.md` and `INSTALLATION.md` with:
  - Proper client prioritization (deeplinks for Cursor/VS Code, MCPB for Claude Desktop)
  - Clarified platform support
  - Professional, factual tone

## Bug Fixes

### Test Fixes
- Fixed unreachable code in skipped `adn_editor` tests
- Removed undefined variable references in test files
- Removed unused imports

**Result**: All ruff checks pass ✅

## Code Quality

- ✅ Zero ruff errors
- ✅ All tests passing
- ✅ Formatted with ruff format
- ✅ FastMCP 2.12 compliant

## Skills Library (External)

**Companion resource** in `mcp-central-docs/claude-skills/`:
- 202 quality-rated Claude Skills
- Curated from Anthropic + community
- The Pizza Test™ quality system
- Complete attribution and documentation

**Not included in package** - available separately for import.

## Breaking Changes

None - fully backward compatible with v1.0.0b6

## What's New

1. **Skill Creation**: Now creates scripts/, references/, assets/ directories automatically
2. **Documentation**: Comprehensive skills guide with curated library information
3. **Quality**: All ruff errors fixed, clean codebase
4. **Professional Polish**: Documentation updated with proper prioritization

## Upgrade Notes

**From v1.0.0b6**:
```bash
pip install --upgrade advanced-memory-mcp
```

No configuration changes needed - fully compatible!

## Known Issues

None

## Coming in v1.0.0

- Stable release (pending final verification)
- Multi-skill plugin packaging improvements
- Enhanced quality for production use

---

**Version**: 1.0.0b7  
**Python**: 3.11+  
**Status**: Beta (production-quality, final testing phase)  
**Quality**: All checks passing ✅

