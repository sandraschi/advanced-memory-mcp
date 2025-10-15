# Release Strategy & Testing Requirements

## 🎯 Release Types

### Beta Releases (e.g., v1.0.0b2)
**Purpose**: Testing and validation before stable release

**Requirements**:
- ✅ All code quality checks pass (type, lint, format)
- ✅ All workflows functional (CI/CD, security, build)
- ✅ Core functionality tested
- ✅ GitHub Release created with assets

**Published To**:
- ✅ GitHub Releases (with MCPB package)
- ❌ PyPI (skipped for beta)

**Installation**:
```bash
# From GitHub release
pip install https://github.com/sandraschi/advanced-memory-mcp/releases/download/v1.0.0b2/advanced_memory_mcp-1.0.0b2-py3-none-any.whl
```

---

### Stable Releases (e.g., v1.0.0)
**Purpose**: Production-ready public release

**Requirements**:
- ✅ All beta testing complete
- ✅ Megatest suite passes (all 5 levels)
- ✅ Integration tests pass
- ✅ Manual testing complete
- ✅ Documentation reviewed
- ✅ Security scans clean
- ✅ Performance validated

**Published To**:
- ✅ GitHub Releases (with MCPB package)
- ✅ PyPI (public installation)
- ✅ Homebrew (via formula update)

**Installation**:
```bash
# From PyPI (preferred)
pip install advanced-memory==1.0.0

# From GitHub
pip install https://github.com/sandraschi/advanced-memory-mcp/releases/download/v1.0.0/advanced_memory_mcp-1.0.0-py3-none-any.whl
```

---

## 🧪 Testing Requirements for Stable Release

### 1. Megatest Suite (Required)

Run all 5 levels of the megatest:

```bash
# Level 1: Smoke Test (5 min)
pytest tests/megatest/ -v -m megatest_smoke

# Level 2: Standard Test (15 min)
pytest tests/megatest/ -v -m megatest_standard

# Level 3: Advanced Test (30 min)
pytest tests/megatest/ -v -m megatest_advanced

# Level 4: Integration Test (45 min)
pytest tests/megatest/ -v -m megatest_integration

# Level 5: Full Blast (60+ min)
pytest tests/megatest/ -v -m megatest_full
```

**Pass Criteria**: 
- All levels must pass
- No critical failures
- Performance within acceptable limits

### 2. Integration Tests (Required)

```bash
pytest tests/integration/ -v
```

**Pass Criteria**:
- All integration tests pass
- API endpoints functional
- MCP tools working correctly
- Cross-component communication verified

### 3. Manual Testing Checklist

- [ ] Create project via CLI
- [ ] Write notes via MCP
- [ ] Search notes
- [ ] Export to various formats (PDF, HTML, Docsify)
- [ ] Import from external sources (Obsidian, Notion, etc.)
- [ ] Test onboarding wizard
- [ ] Verify MCPB package in Claude Desktop
- [ ] Test all 8 portmanteau tools
- [ ] Verify sync functionality
- [ ] Check error handling

### 4. Performance Testing

- [ ] Large knowledge base (1000+ notes)
- [ ] Complex queries (search performance)
- [ ] Concurrent operations
- [ ] Memory usage under load
- [ ] Startup time

### 5. Security Validation

```bash
# Run full security scan
bandit -r src/ -f json -o security-report.json
safety check --json --output safety-report.json

# Check results
cat security-report.json
cat safety-report.json
```

**Pass Criteria**:
- No critical vulnerabilities
- No high-severity issues
- All medium/low issues documented

---

## 📋 Release Checklist

### For Beta Release (v1.0.0b2)

- [x] All type errors fixed (0 errors)
- [x] All linting errors fixed (0 errors)
- [x] All formatting issues fixed (0 errors)
- [x] All workflows functional
- [x] Dependencies managed
- [x] Documentation updated
- [x] GitHub Release created
- [ ] Beta testing feedback collected
- [ ] Known issues documented

### For Stable Release (v1.0.0)

- [ ] All beta requirements met
- [ ] All megatest levels pass
- [ ] Integration tests pass
- [ ] Manual testing complete
- [ ] Performance validated
- [ ] Security scans clean
- [ ] Documentation complete
- [ ] CHANGELOG updated
- [ ] Migration guide (if needed)
- [ ] PyPI publishing verified

---

## 🚀 Release Process

### Beta Release

1. **Tag the release**:
   ```bash
   git tag -a v1.0.0b2 -m "Beta release v1.0.0b2"
   git push origin v1.0.0b2
   ```

2. **Verify GitHub Actions**:
   - Check CI/CD passes
   - Verify release created
   - Download MCPB package

3. **Test the release**:
   - Install from GitHub release
   - Run basic functionality tests
   - Collect feedback

4. **Document issues**:
   - Create GitHub issues for bugs
   - Update CHANGELOG with known issues

### Stable Release

1. **Complete all testing**:
   - Run megatest suite
   - Run integration tests
   - Complete manual testing
   - Validate performance
   - Verify security

2. **Update documentation**:
   ```bash
   # Update version numbers
   vim pyproject.toml  # version = "1.0.0"
   vim src/advanced_memory/__init__.py  # __version__ = "1.0.0"
   vim mcpb/manifest.json  # "version": "1.0.0"
   
   # Update CHANGELOG
   vim CHANGELOG.md  # Add [1.0.0] entry
   ```

3. **Tag the release**:
   ```bash
   git add -A
   git commit -m "chore: bump version to 1.0.0"
   git push origin master
   
   git tag -a v1.0.0 -m "Stable release v1.0.0"
   git push origin v1.0.0
   ```

4. **Verify publishing**:
   - GitHub Release ✅
   - PyPI Package ✅ (wait 5-10 min)
   - Homebrew Formula ✅ (automatic)

5. **Announce**:
   - GitHub Discussions
   - Discord announcement
   - Social media (if applicable)

---

## 🔄 Version Numbering

### Format: MAJOR.MINOR.PATCH

- **MAJOR**: Breaking changes
- **MINOR**: New features (backward compatible)
- **PATCH**: Bug fixes (backward compatible)

### Pre-release Suffixes

- `alpha` (a): Early testing (e.g., v1.0.0a1)
- `beta` (b): Feature complete, testing (e.g., v1.0.0b2)
- `rc`: Release candidate (e.g., v1.0.0rc1)

---

## 📊 Current Status

**v1.0.0b2** (Current):
- ✅ GitHub Release: Published
- ✅ MCPB Package: Available
- ❌ PyPI: Correctly skipped (beta)
- ⏳ Testing: In progress
- ⏳ Feedback: Collecting

**v1.0.0** (Upcoming):
- ⏳ Megatest: Pending
- ⏳ Integration tests: Pending
- ⏳ Manual testing: Pending
- ⏳ PyPI: Will publish when ready

---

## 🎯 Next Steps

1. **Beta Testing** (v1.0.0b2):
   - [ ] Test MCPB package in Claude Desktop
   - [ ] Test all MCP tools
   - [ ] Test starter Zettelkasten onboarding
   - [ ] Collect user feedback
   - [ ] Document any issues

2. **Megatest Implementation**:
   - [ ] Complete megatest framework
   - [ ] Add test cases for all 5 levels
   - [ ] Run full suite
   - [ ] Fix any failures

3. **Stable Release** (v1.0.0):
   - [ ] Address beta feedback
   - [ ] Pass all tests
   - [ ] Update documentation
   - [ ] Publish to PyPI

---

## 📝 Notes

- **Beta releases** are for testing - PyPI publishing is correctly disabled
- **Stable releases** require full testing - never skip megatest
- **Security** is validated at every release
- **Documentation** must be current before stable release
- **Breaking changes** require MAJOR version bump

---

**Remember**: Better to delay a release than publish untested code! 🛡️

