# 📦 PyPI Publishing Complete Guide for Advanced Memory MCP

**Complete walkthrough for publishing Advanced Memory MCP to PyPI with GitHub Actions automation**

---

## 🎯 Current Status

**Repository**: advanced-memory-mcp  
**Current Version**: 1.0.0b3 (Beta 3)  
**Release Automation**: ✅ Partially configured  
**PyPI Publishing**: ❌ **NOT WORKING - Needs Setup**

---

## 🚨 Problem Identified

Your release v1.0.0b3 successfully created a GitHub release, but **did NOT publish to PyPI**. Here's why:

### Issue 1: Beta Releases Are Excluded from PyPI

In `.github/workflows/release.yml` line 154:
```yaml
if: startsWith(github.ref, 'refs/tags/v') && !contains(github.ref, 'alpha') && !contains(github.ref, 'beta') && !contains(github.ref, 'rc')
```

**This condition BLOCKS beta releases** (like v1.0.0b3) from publishing to PyPI!

### Issue 2: Missing Artifact Upload/Download

The `publish-pypi` job tries to download artifacts:
```yaml
- name: Download build artifacts
  uses: actions/download-artifact@v4
  with:
    name: dist
```

But the `release` job **never uploads these artifacts**, so the download fails!

### Issue 3: Missing PyPI API Token

Even if the above issues are fixed, you need a `PYPI_API_TOKEN` secret configured in GitHub.

---

## ✅ Complete Setup Process

### Step 1: Create PyPI Account

#### A. Register on PyPI

1. **Production PyPI** (for stable releases):
   - Go to: https://pypi.org/account/register/
   - Fill in:
     - Username: `sandraschi` (or your preferred username)
     - Email address
     - Password (strong!)
     - Full name
   - ✅ Verify email (check inbox)

2. **Test PyPI** (for testing):
   - Go to: https://test.pypi.org/account/register/
   - Same process as above
   - **Separate account** from production!

#### B. Enable Two-Factor Authentication (2FA) - REQUIRED!

**PyPI requires 2FA for all package uploads**

1. Log in to PyPI: https://pypi.org
2. Go to: https://pypi.org/manage/account/
3. Click **"Add 2FA with authentication application"**
4. Options:
   - **Authenticator app** (Google Authenticator, Authy, Microsoft Authenticator, 1Password, etc.)
   - **Security key** (YubiKey, etc.)
5. Scan QR code with your app
6. Enter verification code
7. ✅ **Save recovery codes somewhere safe!** (You'll need them if you lose your phone)

**⚠️ CRITICAL**: Without 2FA, you CANNOT upload packages to PyPI!

---

### Step 2: Create API Token

#### A. Generate Token on PyPI

1. Log in to https://pypi.org
2. Go to: https://pypi.org/manage/account/token/
3. Click **"Add API token"**
4. Fill in:
   - **Token name**: `advanced-memory-mcp-github-actions` (descriptive name)
   - **Scope**: 
     - ⭐ **Recommended**: "Entire account" (can upload any package)
     - Alternative: "Project" → Will need to create project first
5. Click **"Add token"**
6. ✅ **COPY THE TOKEN IMMEDIATELY!** (shown only once)

**Token format**:
```
pypi-AgEIcHlwaS5vcmcCJGFiY2RlZi0xMjM0LTU2NzgtOTBhYi1jZGVmMTIzNDU2NzgAAA...
```

**⚠️ CRITICAL**: Save this token immediately! You can't see it again!

---

#### B. Add Token to GitHub Secrets

1. Go to your GitHub repository: https://github.com/sandraschi/advanced-memory-mcp
2. Click **Settings** → **Secrets and variables** → **Actions**
3. Click **"New repository secret"**
4. Fill in:
   - **Name**: `PYPI_API_TOKEN`
   - **Secret**: Paste your PyPI token (starts with `pypi-AgEI...`)
5. Click **"Add secret"**
6. ✅ **Done!** GitHub Actions can now publish to PyPI

---

### Step 3: Fix GitHub Workflow

The current workflow has issues. Here's what needs to be fixed:

#### Option 1: Publish Beta Releases to PyPI (Recommended for Testing)

Update `.github/workflows/release.yml` to allow beta releases:

**Change line 154 from:**
```yaml
if: startsWith(github.ref, 'refs/tags/v') && !contains(github.ref, 'alpha') && !contains(github.ref, 'beta') && !contains(github.ref, 'rc')
```

**To:**
```yaml
if: startsWith(github.ref, 'refs/tags/v')
```

This will publish **all** tagged releases (including beta) to PyPI.

#### Option 2: Separate Beta and Stable Publishing

Keep stable releases going to PyPI, beta releases to Test PyPI:

**Add a new job** for beta releases:
```yaml
publish-test-pypi:
  name: Publish Beta to Test PyPI
  runs-on: ubuntu-latest
  needs: release
  if: startsWith(github.ref, 'refs/tags/v') && (contains(github.ref, 'alpha') || contains(github.ref, 'beta') || contains(github.ref, 'rc'))
  environment: test-pypi
  steps:
    - name: Checkout code
      uses: actions/checkout@v4
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: "3.12"
    
    - name: Install uv
      uses: astral-sh/setup-uv@v3
      with:
        version: "latest"
    
    - name: Build package
      run: uv build
    
    - name: Publish to Test PyPI
      uses: pypa/gh-action-pypi-publish@release/v1
      with:
        password: ${{ secrets.TEST_PYPI_API_TOKEN }}
        repository-url: https://test.pypi.org/legacy/
```

---

### Step 4: Update Workflow to Upload/Download Artifacts Correctly

The current workflow builds packages but doesn't save them for the publishing job.

**Add to the `release` job** (after line 48):
```yaml
- name: Upload build artifacts
  uses: actions/upload-artifact@v4
  with:
    name: dist
    path: dist/
```

**Update the `publish-pypi` job** (replace lines 157-163):
```yaml
- name: Checkout code
  uses: actions/checkout@v4

- name: Set up Python
  uses: actions/setup-python@v4
  with:
    python-version: "3.12"

- name: Install uv
  uses: astral-sh/setup-uv@v3
  with:
    version: "latest"

- name: Build package
  run: uv build

- name: Publish to PyPI
  uses: pypa/gh-action-pypi-publish@release/v1
  with:
    password: ${{ secrets.PYPI_API_TOKEN }}
```

---

## 🔧 Quick Fix for Current Release (v1.0.0b3)

Your release is already tagged, so here's how to manually publish it to PyPI:

### Option A: Manual Publishing from Local Machine

```powershell
# 1. Make sure you're on the v1.0.0b3 tag
git checkout v1.0.0b3

# 2. Clean previous builds
Remove-Item -Recurse dist -ErrorAction SilentlyContinue

# 3. Build package
uv build

# 4. Check package
uv run twine check dist/*

# 5. Upload to PyPI
uv run twine upload dist/*

# When prompted:
# Username: __token__
# Password: pypi-AgEI... (your PyPI token)
```

### Option B: Trigger GitHub Actions Manually

1. Fix the workflow issues (see Step 3 above)
2. Commit the changes
3. Go to: https://github.com/sandraschi/advanced-memory-mcp/actions/workflows/release.yml
4. Click **"Run workflow"**
5. Enter version: `v1.0.0b3`
6. Click **"Run workflow"**

---

## 📊 Testing Before Production

**Always test on Test PyPI first!**

### 1. Upload to Test PyPI

```powershell
# Build package
uv build

# Upload to Test PyPI
uv run twine upload --repository-url https://test.pypi.org/legacy/ dist/*
```

### 2. Test Installation from Test PyPI

```powershell
# Create test environment
python -m venv test-env
.\test-env\Scripts\activate

# Install from Test PyPI
pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ advanced-memory-mcp

# Test it works
advanced-memory --version
python -m advanced_memory.mcp.server

# If works: ✅ Ready for production!
```

---

## 🎯 Recommended Workflow

### For Beta Releases (v1.0.0b1, v1.0.0b2, etc.)

1. **Push to Test PyPI** (for testing)
   ```bash
   uv build
   uv run twine upload --repository-url https://test.pypi.org/legacy/ dist/*
   ```

2. **Verify installation** from Test PyPI

3. **If testing passes**, optionally push to **Production PyPI**:
   ```bash
   uv run twine upload dist/*
   ```

### For Stable Releases (v1.0.0, v1.1.0, etc.)

1. **Run all quality checks**:
   ```bash
   just check  # Runs lint, format, type-check, tests
   ```

2. **Create release**:
   ```bash
   just release v1.0.0
   ```

3. **GitHub Actions automatically**:
   - Creates GitHub release
   - Builds packages
   - Publishes to PyPI
   - Updates Homebrew formula

---

## ⚠️ Common Errors & Solutions

### Error 1: "File already exists"

```
ERROR: HTTPError: 400 Bad Request
File already exists. See https://pypi.org/help/#file-name-reuse
```

**Cause**: Trying to upload same version again  
**Solution**: Increment version number in `src/advanced_memory/__init__.py`:
```python
__version__ = "1.0.0b4"  # Increment this!
```

---

### Error 2: "Invalid authentication credentials"

```
ERROR: HTTPError: 403 Forbidden
Invalid or non-existent authentication information
```

**Cause**: Wrong token or username  
**Solution**: 
- Username must be `__token__` (with underscores!)
- Password is your API token starting with `pypi-AgEI...`
- Verify token is correct in GitHub Secrets

---

### Error 3: "Package name already taken"

```
ERROR: The name 'advanced-memory-mcp' is already claimed
```

**Cause**: Someone else registered this name (unlikely for this project)  
**Solution**: 
- Check if YOU own it: https://pypi.org/project/advanced-memory-mcp/
- If you own it, use your account token
- If someone else owns it, contact PyPI admins

---

### Error 4: "Two-factor authentication required"

```
ERROR: PyPI requires two-factor authentication
```

**Cause**: 2FA not enabled on your PyPI account  
**Solution**: Enable 2FA (see Step 1B above)

---

### Error 5: "Build artifacts not found"

```
ERROR: Unable to download artifact(s): Artifact 'dist' not found
```

**Cause**: The `release` job didn't upload artifacts  
**Solution**: Add artifact upload step (see Step 4 above)

---

## 🚀 Complete Fixed Workflow

Here's the complete fixed `publish-pypi` job:

```yaml
publish-pypi:
  name: Publish to PyPI
  runs-on: ubuntu-latest
  needs: release
  # Allow all tagged releases (including beta)
  if: startsWith(github.ref, 'refs/tags/v')
  environment: pypi
  permissions:
    id-token: write
  steps:
    - name: Checkout code
      uses: actions/checkout@v4

    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: "3.12"

    - name: Install uv
      uses: astral-sh/setup-uv@v3
      with:
        version: "latest"

    - name: Install dependencies
      run: uv sync --dev

    - name: Build package
      run: uv build

    - name: Check package
      run: uv run twine check dist/*

    - name: Publish to PyPI
      uses: pypa/gh-action-pypi-publish@release/v1
      with:
        password: ${{ secrets.PYPI_API_TOKEN }}
```

---

## 📝 Checklist for First PyPI Release

### Before First Upload
- [ ] Create PyPI account (https://pypi.org/account/register/)
- [ ] Enable 2FA on PyPI account
- [ ] Create API token on PyPI
- [ ] Add `PYPI_API_TOKEN` to GitHub Secrets
- [ ] Fix workflow issues (see Step 3 & 4 above)
- [ ] Test on Test PyPI first
- [ ] Verify LICENSE file exists
- [ ] Update `pyproject.toml` metadata
- [ ] Write comprehensive README.md

### For Each Release
- [ ] Increment version number in `src/advanced_memory/__init__.py`
- [ ] Update CHANGELOG.md
- [ ] Run quality checks: `just check`
- [ ] Commit changes
- [ ] Create git tag: `git tag v1.0.0`
- [ ] Push tag: `git push origin v1.0.0`
- [ ] Monitor GitHub Actions
- [ ] Verify PyPI publication
- [ ] Test installation: `pip install advanced-memory-mcp`
- [ ] Update documentation with new version

---

## 🎉 After Successful Publication

**Your package will be live at**:
- **PyPI URL**: https://pypi.org/project/advanced-memory-mcp/
- **Installation**: `pip install advanced-memory-mcp`
- **Pre-releases**: `pip install advanced-memory-mcp --pre` (for beta versions)

**Add badges to README.md**:
```markdown
[![PyPI version](https://img.shields.io/pypi/v/advanced-memory-mcp.svg)](https://pypi.org/project/advanced-memory-mcp/)
[![Python versions](https://img.shields.io/pypi/pyversions/advanced-memory-mcp.svg)](https://pypi.org/project/advanced-memory-mcp/)
[![Downloads](https://pepy.tech/badge/advanced-memory-mcp)](https://pepy.tech/project/advanced-memory-mcp)
```

---

## 📚 Additional Resources

**Official Docs**:
- PyPI: https://pypi.org
- Test PyPI: https://test.pypi.org
- Packaging Guide: https://packaging.python.org
- Twine: https://twine.readthedocs.io
- GitHub Actions: https://docs.github.com/en/actions

**Tools**:
- `uv`: https://docs.astral.sh/uv/
- `twine`: https://twine.readthedocs.io
- `build`: https://pypa-build.readthedocs.io

**Security**:
- 2FA Setup: https://pypi.org/help/#twofa
- API Tokens: https://pypi.org/help/#apitoken
- Trusted Publishers: https://docs.pypi.org/trusted-publishers/

---

## 🎯 Next Steps

1. **Immediate**: Create PyPI account and enable 2FA
2. **Next**: Create API token and add to GitHub Secrets
3. **Then**: Fix workflow (apply fixes from Step 3 & 4)
4. **Finally**: Re-release v1.0.0b3 or create v1.0.0b4

---

**Created**: October 17, 2025  
**For**: Advanced Memory MCP v1.0.0b3+  
**Status**: Ready to implement

**Happy publishing!** 🚀📦

