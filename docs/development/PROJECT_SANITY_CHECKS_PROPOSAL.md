# Project Sanity Checks - Critical Safety Feature

**PROPOSAL: Add validation to prevent accidentally indexing huge directories**

---

## The Problem

**Currently**: NO sanity checks when adding projects!

**You can do this** (accidentally):
```bash
# Point at entire home directory
advanced-memory project add everything C:/Users/sandr

# Point at entire C drive
advanced-memory project add catastrophe C:/

# Point at network share with 1TB of data
advanced-memory project add disaster \\server\bigshare
```

**What happens**:
1. Command succeeds (no warning!)
2. User runs `advanced-memory sync`
3. Advanced Memory tries to index EVERYTHING
4. Could take hours, crash, fill disk, etc.

**This is a BUG / MISSING FEATURE!**

---

## Proposed Solution

### Level 1: Pre-Scan Validation (Before Adding Project)

**When user runs** `advanced-memory project add <name> <path>`:

**Step 1: Quick estimate**
```python
# Count .md files (fast scan, first 1000 files)
estimated_files = count_markdown_files(path, max_scan=1000)

if estimated_files > 1000:
    # Warn user!
    console.print(f"⚠️  Warning: Found {estimated_files}+ markdown files")
    console.print(f"   This could take a long time to sync!")

    if not typer.confirm("Continue?"):
        raise typer.Abort()
```

---

### Level 2: Dangerous Path Detection

**Detect risky directories**:
```python
dangerous_paths = [
    "C:/",
    "C:/Windows",
    "C:/Program Files",
    "/",
    "/usr",
    "/bin",
    "/etc",
    str(Path.home()),  # Entire home directory
]

if resolved_path in dangerous_paths or is_parent_of(resolved_path, dangerous_paths):
    console.print(f"❌ ERROR: Cannot index system directory: {resolved_path}")
    console.print("   This could index thousands of files and is probably not what you want.")
    raise typer.Exit(1)
```

---

### Level 3: Size Estimation

**Estimate total size**:
```python
total_size = estimate_directory_size(path, extensions=[".md"])

if total_size > 1_000_000_000:  # 1 GB
    console.print(f"⚠️  Warning: Directory contains ~{total_size / 1e9:.1f} GB of markdown")
    console.print("   This is unusually large and may not be what you intended.")

    if not typer.confirm("Continue anyway?"):
        raise typer.Abort()
```

---

### Level 4: Smart Recommendations

**Suggest better approach**:
```python
if estimated_files > 500:
    console.print("\n💡 Tip: Instead of indexing this large directory:")
    console.print("   Consider creating separate projects for subdirectories:")
    console.print(f"   • advanced-memory project add project1 {path}/subdir1")
    console.print(f"   • advanced-memory project add project2 {path}/subdir2")
```

---

## Implementation

### Phase 1: Basic Warnings (Quick Win)

**File**: `src/advanced_memory/services/project_service.py`

```python
async def add_project(self, name: str, path: str, set_default: bool = False) -> None:
    """Add a new project to the configuration and database.

    Args:
        name: The name of the project
        path: The file path to the project directory
        set_default: Whether to set this project as the default

    Raises:
        ValueError: If the project already exists or path is invalid
    """
    # Resolve to absolute path
    resolved_path = os.path.abspath(os.path.expanduser(path))

    # SANITY CHECK 1: Path exists
    if not os.path.exists(resolved_path):
        raise ValueError(f"Path does not exist: {resolved_path}")

    # SANITY CHECK 2: Path is directory
    if not os.path.isdir(resolved_path):
        raise ValueError(f"Path is not a directory: {resolved_path}")

    # SANITY CHECK 3: Dangerous paths
    dangerous_paths = [
        "C:\\",
        "C:\\Windows",
        "C:\\Program Files",
        "C:\\Program Files (x86)",
        "/",
        "/usr",
        "/bin",
        "/etc",
        "/var",
    ]

    if resolved_path.rstrip(os.sep) in [p.rstrip(os.sep) for p in dangerous_paths]:
        raise ValueError(
            f"Cannot index system directory: {resolved_path}\n"
            "This would index thousands of system files."
        )

    # SANITY CHECK 4: Home directory warning
    home_dir = str(Path.home())
    if resolved_path == home_dir:
        raise ValueError(
            f"Cannot index entire home directory: {resolved_path}\n"
            f"Create a specific subdirectory instead:\n"
            f"  advanced-memory project add notes {home_dir}/Documents/Notes"
        )

    # SANITY CHECK 5: Quick file count estimate
    try:
        file_count = estimate_markdown_files(resolved_path, max_scan=1000, timeout=5)

        if file_count >= 1000:
            logger.warning(
                f"Large project detected: {file_count}+ markdown files in {resolved_path}"
            )
            # Note: CLI will need to prompt user for confirmation
            # API will just log warning
    except Exception as e:
        logger.warning(f"Could not estimate file count: {e}")

    # Continue with normal add logic...
    project_config = self.config_manager.add_project(name, resolved_path)
    # ... etc
```

**Helper function**:
```python
def estimate_markdown_files(path: str, max_scan: int = 1000, timeout: int = 5) -> int:
    """Estimate number of markdown files in directory.

    Args:
        path: Directory to scan
        max_scan: Maximum files to scan before stopping
        timeout: Maximum seconds to spend scanning

    Returns:
        Estimated file count (or max_scan if exceeded)
    """
    import time
    from pathlib import Path

    start_time = time.time()
    count = 0

    try:
        for root, dirs, files in os.walk(path):
            # Skip ignored directories
            dirs[:] = [d for d in dirs if d not in IGNORE_PATTERNS]

            # Count .md files
            md_files = [f for f in files if f.endswith('.md')]
            count += len(md_files)

            # Stop if exceeded limits
            if count >= max_scan:
                return max_scan

            if time.time() - start_time > timeout:
                return count

    except (PermissionError, OSError):
        # Can't scan directory, return what we have
        pass

    return count
```

---

### Phase 2: Interactive Warnings (CLI Only)

**File**: `src/advanced_memory/cli/commands/project.py`

```python
@project_app.command("add")
def add_project(
    name: str = typer.Argument(..., help="Name of the project"),
    path: str = typer.Argument(..., help="Path to the project directory"),
    set_default: bool = typer.Option(False, "--default", help="Set as default project"),
    force: bool = typer.Option(False, "--force", help="Skip safety checks"),
) -> None:
    """Add a new project with sanity checks."""
    # Resolve to absolute path
    resolved_path = os.path.abspath(os.path.expanduser(path))

    # Quick validation
    if not os.path.exists(resolved_path):
        console.print(f"[red]Error: Path does not exist: {resolved_path}[/red]")
        raise typer.Exit(1)

    if not os.path.isdir(resolved_path):
        console.print(f"[red]Error: Path is not a directory: {resolved_path}[/red]")
        raise typer.Exit(1)

    # Pre-scan (unless --force)
    if not force:
        console.print(f"\n[cyan]Scanning directory: {resolved_path}[/cyan]")

        try:
            # Quick estimate
            file_count = estimate_markdown_files(resolved_path, max_scan=1000, timeout=5)

            # Show estimate
            if file_count >= 1000:
                console.print(f"[yellow]⚠️  Found 1000+ markdown files[/yellow]")
            elif file_count > 500:
                console.print(f"[yellow]⚠️  Found ~{file_count} markdown files[/yellow]")
            else:
                console.print(f"[green]Found ~{file_count} markdown files[/green]")

            # Warning for large projects
            if file_count > 500:
                console.print("\n[yellow]This is a large project![/yellow]")
                console.print(f"  Estimated sync time: {estimate_sync_time(file_count)}")
                console.print(f"  Estimated database size: {estimate_db_size(file_count)}")
                console.print("\n💡 Consider creating separate projects for subdirectories instead.")

                if not typer.confirm("\nContinue with this large directory?"):
                    console.print("[yellow]Aborted. No project created.[/yellow]")
                    raise typer.Exit(0)

        except Exception as e:
            logger.warning(f"Could not scan directory: {e}")
            console.print(f"[yellow]Warning: Could not scan directory ({e})[/yellow]")

            if not typer.confirm("Continue anyway?"):
                raise typer.Exit(0)

    # Continue with normal add logic...
    try:
        data = {"name": name, "path": resolved_path, "set_default": set_default}
        response = asyncio.run(call_post(client, "/projects/projects", json=data))
        result = ProjectStatusResponse.model_validate(response.json())
        console.print(f"[green]{result.message}[/green]")
    except Exception as e:
        console.print(f"[red]Error adding project: {str(e)}[/red]")
        raise typer.Exit(1) from e
```

---

### Phase 3: Dry-Run Preview

**New command**: `advanced-memory project preview <path>`

```bash
advanced-memory project preview D:/Dev/repos

# Output:
📊 Project Preview: D:/Dev/repos

Scanning directory... (max 5 seconds)

Found:
  • ~487 markdown files
  • Across 50 subdirectories
  • Total size: ~25 MB
  • Deepest nesting: 8 levels

Ignored:
  • 15 node_modules/ directories
  • 50 .git/ directories
  • 100+ __pycache__/ directories

Estimated:
  • Sync time: 30-45 seconds
  • Database size: ~50 MB
  • Memory usage: ~100 MB

⚠️  This is a large project with many repos mixed together.

💡 Recommendation:
   Create separate projects for individual repos:
   • advanced-memory project add repo1 D:/Dev/repos/repo1
   • advanced-memory project add repo2 D:/Dev/repos/repo2

Proceed with adding this as a project? [y/N]:
```

---

## Specific Validations

### 1. System Directories (Block)

**Block these outright**:
```python
BLOCKED_PATHS = [
    # Windows
    "C:\\",
    "C:\\Windows",
    "C:\\Program Files",
    "C:\\Program Files (x86)",
    "D:\\",  # Could be data drive, but risky

    # Linux/macOS
    "/",
    "/usr",
    "/bin",
    "/etc",
    "/var",
    "/sys",
    "/proc",
    "/dev",
]
```

**Error message**:
```
❌ Cannot index system directory: C:/
   This would attempt to index your entire Windows installation.
   Please specify a subdirectory like C:/Users/You/Documents/Notes
```

---

### 2. Home Directory (Warn)

**Detect home directory**:
```python
if resolved_path == str(Path.home()):
    console.print("⚠️  Warning: You're about to index your entire home directory!")
    console.print(f"   This could include:")
    console.print("   • Downloads")
    console.print("   • Desktop")
    console.print("   • Pictures")
    console.print("   • And much more!")
    console.print("\n💡 Did you mean a subdirectory?")
    console.print(f"   • {Path.home()}/Documents/Notes")
    console.print(f"   • {Path.home()}/Documents/Obsidian")

    if not typer.confirm("\nIndex entire home directory anyway?", default=False):
        raise typer.Exit(0)
```

---

### 3. Large File Count (Warn)

**Thresholds**:
```python
# Green (no warning)
if file_count < 100:
    pass

# Yellow (warning)
elif 100 <= file_count < 500:
    console.print(f"[yellow]Found {file_count} files - this is a medium-sized project[/yellow]")

# Orange (strong warning)
elif 500 <= file_count < 1000:
    console.print(f"[yellow]⚠️  Found {file_count} files - this is a large project![/yellow]")
    console.print(f"   Estimated sync time: {estimate_sync_time(file_count)}")
    if not typer.confirm("Continue?"):
        raise typer.Exit(0)

# Red (very strong warning)
elif file_count >= 1000:
    console.print(f"[red]⚠️  Found {file_count}+ files - this is VERY large![/red]")
    console.print("   Syncing could take several minutes and create a large database.")
    console.print("\n💡 Recommendation: Create separate projects for subdirectories")
    if not typer.confirm("Continue anyway?", default=False):
        raise typer.Exit(0)
```

---

### 4. Network Path Detection (Warn)

**Detect UNC paths**:
```python
if resolved_path.startswith("\\\\") or resolved_path.startswith("//"):
    console.print(f"⚠️  Network path detected: {resolved_path}")
    console.print("   Warning: Network filesystems are slower and less reliable")
    console.print("   Auto-sync may not work correctly on network paths")
    console.print("\n   Recommendation: Use local paths or disable auto-sync")

    if not typer.confirm("Continue with network path?"):
        raise typer.Exit(0)
```

---

### 5. Parent Directory Check (Warn)

**Detect if parent of existing projects**:
```python
# Check if this path is a parent of existing projects
existing_projects = config_manager.projects
for existing_name, existing_path in existing_projects.items():
    if Path(existing_path).is_relative_to(Path(resolved_path)):
        console.print(f"⚠️  Warning: This path contains existing project '{existing_name}'")
        console.print(f"   Existing: {existing_path}")
        console.print(f"   New: {resolved_path}")
        console.print("\n   This will create overlapping projects (not recommended)")

        if not typer.confirm("Continue anyway?"):
            raise typer.Exit(0)
```

---

## Estimation Functions

### File Count Estimator

```python
def estimate_markdown_files(
    path: str,
    max_scan: int = 1000,
    timeout: int = 5
) -> int:
    """Estimate number of markdown files (fast scan)."""
    import time

    start_time = time.time()
    count = 0

    try:
        for root, dirs, files in os.walk(path):
            # Filter ignored directories IN-PLACE (prevents descending)
            dirs[:] = [
                d for d in dirs
                if d not in IGNORE_PATTERNS and not d.startswith('.')
            ]

            # Count .md files
            md_files = [f for f in files if f.endswith('.md')]
            count += len(md_files)

            # Stop conditions
            if count >= max_scan:
                return max_scan  # Return "at least this many"

            if time.time() - start_time > timeout:
                return count  # Return "found this many so far"

    except (PermissionError, OSError) as e:
        logger.warning(f"Could not scan directory: {e}")

    return count
```

---

### Sync Time Estimator

```python
def estimate_sync_time(file_count: int) -> str:
    """Estimate how long sync will take."""
    # Rough estimate: 100ms per file (parsing + DB insert)
    seconds = file_count * 0.1

    if seconds < 60:
        return f"~{int(seconds)} seconds"
    elif seconds < 3600:
        return f"~{int(seconds / 60)} minutes"
    else:
        return f"~{int(seconds / 3600)} hours"
```

---

### Database Size Estimator

```python
def estimate_db_size(file_count: int) -> str:
    """Estimate database size."""
    # Rough estimate: 100 KB per file (entities + relations + search index)
    bytes_size = file_count * 100 * 1024

    if bytes_size < 1_000_000:
        return f"~{int(bytes_size / 1024)} KB"
    elif bytes_size < 1_000_000_000:
        return f"~{int(bytes_size / (1024 * 1024))} MB"
    else:
        return f"~{int(bytes_size / (1024 * 1024 * 1024))} GB"
```

---

## User Experience

### Example 1: Small Project (No Warning)

```bash
advanced-memory project add notes ~/Documents/Notes

# Output:
Scanning directory: /home/user/Documents/Notes
Found ~42 markdown files

✅ Project 'notes' added successfully
```

---

### Example 2: Large Project (Warning)

```bash
advanced-memory project add everything ~/Documents

# Output:
Scanning directory: /home/user/Documents
⚠️  Found 1000+ markdown files
   This could take a long time to sync!

   Estimated sync time: ~2 minutes
   Estimated database size: ~100 MB

💡 Tip: Consider creating separate projects for subdirectories:
   • advanced-memory project add notes ~/Documents/Notes
   • advanced-memory project add research ~/Documents/Research

Continue? [y/N]: n

❌ Aborted. No project created.
```

---

### Example 3: System Directory (Blocked)

```bash
advanced-memory project add everything C:/

# Output:
❌ ERROR: Cannot index system directory: C:/
   This would index thousands of files and is probably not what you want.

   Please specify a subdirectory like:
   • C:/Users/Sandra/Documents/Notes
   • C:/Users/Sandra/Projects
```

---

### Example 4: Home Directory (Strong Warning)

```bash
advanced-memory project add home C:/Users/sandr

# Output:
⚠️  Warning: You're about to index your entire home directory!
   This could include:
   • Downloads
   • Desktop
   • Pictures
   • AppData
   • And much more!

💡 Did you mean a subdirectory?
   • C:/Users/sandr/Documents/Notes
   • C:/Users/sandr/Documents/Obsidian

Index entire home directory anyway? [y/N]: n

❌ Aborted. No project created.
```

---

### Example 5: Using --force to Skip Checks

```bash
# For power users who know what they're doing
advanced-memory project add large ~/Documents --force

# Output:
✅ Project 'large' added successfully
⚠️  Safety checks skipped (--force flag used)
```

---

## Migration Plan

### Step 1: Add Validation Functions

**Files to create**:
- `src/advanced_memory/services/project_validator.py`

**Includes**:
- `estimate_markdown_files()`
- `estimate_sync_time()`
- `estimate_db_size()`
- `is_dangerous_path()`
- `is_network_path()`

---

### Step 2: Update ProjectService

**File**: `src/advanced_memory/services/project_service.py`

**Changes**:
- Add validation to `add_project()` method
- Raise `ValueError` with helpful messages
- Log warnings for large projects

---

### Step 3: Update CLI Command

**File**: `src/advanced_memory/cli/commands/project.py`

**Changes**:
- Catch `ValueError` from service
- Display user-friendly error messages
- Add interactive prompts for warnings
- Add `--force` flag to skip checks

---

### Step 4: Add Tests

**File**: `tests/services/test_project_validator.py`

**Test cases**:
- Test estimation functions
- Test dangerous path detection
- Test warnings for large directories
- Test `--force` flag

---

### Step 5: Add Preview Command

**File**: `src/advanced_memory/cli/commands/project.py`

**New command**:
```bash
advanced-memory project preview <path>
```

**Shows**:
- File count
- Size estimate
- Sync time estimate
- Recommendations

---

## Backward Compatibility

**Existing projects**: No change (already added)

**New projects**: Validation applies

**API**: Can still bypass via API (but logs warnings)

**CLI**: Interactive prompts (can skip with `--force`)

---

## Configuration

**New config option** (optional):
```json
{
  "project_validation": {
    "enabled": true,
    "max_files_no_warning": 100,
    "max_files_strong_warning": 500,
    "block_system_paths": true,
    "warn_network_paths": true
  }
}
```

**Defaults**: Validation enabled, reasonable limits

---

## Priority

**Urgency**: ⚠️ **HIGH** (prevents user foot-guns)

**Impact**: 🔥 **HIGH** (improves UX significantly)

**Effort**: 📅 ~4-6 hours (validation + tests + docs)

**Should implement**: ✅ **YES, ASAP!**

---

## Summary

### Current State

❌ **No validation** - user can accidentally index C:/ or entire home directory
❌ **No warnings** - no indication that sync will take forever
❌ **No preview** - can't see what you're about to index

### Proposed State

✅ **Smart validation** - blocks dangerous paths
✅ **Interactive warnings** - alerts for large projects
✅ **Helpful suggestions** - recommends better approaches
✅ **Preview command** - see before committing
✅ **Force flag** - power users can skip

### User Impact

**Before**:
```bash
advanced-memory project add oops C:/Users/sandr
advanced-memory sync
# Indexes 10,000+ files, takes 10 minutes, crashes
```

**After**:
```bash
advanced-memory project add oops C:/Users/sandr

⚠️  Warning: You're about to index your entire home directory!
   Found 10,000+ markdown files
   This could take ~15 minutes to sync

💡 Did you mean a subdirectory?
   • C:/Users/sandr/Documents/Notes

Continue? [y/N]: n
❌ Aborted. No project created.
```

**Result**: Prevents footgun! 🎯

---

## Next Steps

1. Create `project_validator.py` service
2. Add validation to `ProjectService.add_project()`
3. Update CLI with interactive prompts
4. Add `--force` flag
5. Create `project preview` command
6. Add tests
7. Update documentation

---

*Proposal created: 2025-10-17*
*Status: Ready for implementation*
*Priority: HIGH (prevents major UX issues)*
