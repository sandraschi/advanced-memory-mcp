# 🔴 CRITICAL: Inbox Folder Created in Wrong Location (Outside Project Directory)

**Severity:** 🔴 **CRITICAL**
**Type:** Bug
**Component:** File Service / Path Resolution
**Date Discovered:** 2025-12-07

## Summary

Advanced Memory created an `inbox` folder at `D:\Dev\repos\inbox\` instead of within the project directory structure (`C:\Users\sandr\Documents\claude-depot\inbox\`). This violates project boundaries and can cause files to be created in unintended locations, leading to data loss and confusion.

## Problem Description

When creating notes with `folder="inbox"` (or when folder defaults to "inbox"), files are being created in the current working directory instead of the project directory.

**Actual Behavior:**
- Files created at: `D:\Dev\repos\inbox\` (5 files found)
- Files created on: 2025-12-07

**Expected Behavior:**
- Files should be created at: `{project_home}/inbox/`
- For project `claude-depot-consolidated`: `C:\Users\sandr\Documents\claude-depot\inbox\`

## Affected Files

The following files were created in the wrong location:
1. `Documentation_Discipline_-_Keep_Docs_Current_Daily.md`
2. `Emergent_Value_-_Building_Tools_Without_Knowing_All_Use_Cases.md`
3. `Incremental_Extension_-_Adding_Tools_As_Needed.md`
4. `MCP_Server_Composition_-_SOTA_Architectural_Pattern.md`
5. `Robotics_MCP_-_Comprehensive_Progress_Report.md`

## Root Cause Analysis

### Code Flow

1. **Entity Schema** (`src/advanced_memory/schemas/base.py:187-191`):
   ```python
   @property
   def file_path(self):
       return f"{self.folder}/{sanitized_title}.md"  # Returns: "inbox/title.md"
   ```

2. **EntityService** (`src/advanced_memory/services/entity_service.py:128`):
   ```python
   file_path = Path(schema.file_path)  # Path("inbox/title.md")
   ```

3. **FileService** (`src/advanced_memory/services/file_service.py:137`):
   ```python
   full_path = path_obj if path_obj.is_absolute() else self.base_path / path_obj
   ```

### The Problem

The `FileService` should correctly combine relative paths with `base_path` (which is set to `project_config.home` in `src/advanced_memory/deps.py:233`). However, if:

1. **Path is resolved before reaching FileService**: If `Path("inbox/title.md").resolve()` is called somewhere, it would resolve relative to the current working directory (`D:\Dev\repos`), making it an absolute path that bypasses `base_path`.

2. **Incorrect base_path**: If `project_config.home` is `None` or not set correctly, `base_path` might default to the current working directory.

3. **Working Directory Issue**: If the Advanced Memory server is started from `D:\Dev\repos` and the project path resolution fails, paths might fall back to the current working directory.

## Impact

- **Data Loss Risk**: Files created in wrong location may not be indexed or synced
- **Project Boundary Violation**: Files created outside project directories
- **User Confusion**: Users may not find their notes
- **Data Integrity**: Notes may be lost or orphaned
- **Security**: Path traversal vulnerabilities if not properly validated

## Steps to Reproduce

1. Start Advanced Memory server from a directory other than the project directory (e.g., `D:\Dev\repos`)
2. Create a note with `folder="inbox"` (or use default inbox folder)
3. Check if the file is created in the current working directory instead of the project directory

## Recommended Fix

### 1. Add Explicit Path Validation in EntityService

```python
# src/advanced_memory/services/entity_service.py:128
file_path = Path(schema.file_path)

# Ensure file_path is always relative to project
if file_path.is_absolute():
    # Extract relative path or raise error
    raise ValueError(f"File path must be relative to project: {file_path}")

# Always combine with project path explicitly
full_path = project_config.home / file_path
```

### 2. Add Safety Check in FileService.write_file()

```python
# src/advanced_memory/services/file_service.py:137
full_path = path_obj if path_obj.is_absolute() else self.base_path / path_obj

# Ensure path is within base_path
if path_obj.is_absolute():
    try:
        path_obj.relative_to(self.base_path)
    except ValueError:
        raise FileOperationError(
            f"Absolute path outside project: {path_obj} (project: {self.base_path})"
        )
```

### 3. Add Logging to Track Path Resolution

```python
logger.debug(
    f"FileService.write_file: path={path}, base_path={self.base_path}, resolved={full_path}"
)
```

### 4. Validate project_config.home Before Creating FileService

```python
# src/advanced_memory/deps.py:227
async def get_file_service(
    project_config: ProjectConfigDep, markdown_processor: MarkdownProcessorDep
) -> FileService:
    if not project_config.home or not project_config.home.exists():
        raise ValueError(
            f"Project home path is invalid: {project_config.home} for project {project_config.name}"
        )
    logger.debug(
        f"Creating FileService for project: {project_config.name}, base_path: {project_config.home}"
    )
    file_service = FileService(project_config.home, markdown_processor)
    return file_service
```

## Files to Investigate

- `src/advanced_memory/services/entity_service.py` (line 128)
- `src/advanced_memory/services/file_service.py` (line 137)
- `src/advanced_memory/deps.py` (line 233 - FileService initialization)
- `src/advanced_memory/schemas/base.py` (line 187 - file_path property)

## Environment

- **OS**: Windows 10 (Build 28000)
- **Python Version**: 3.11+
- **Advanced Memory Version**: 1.0.0b8
- **Project**: claude-depot-consolidated
- **Project Path**: `C:\Users\sandr\Documents\claude-depot\`
- **Current Working Directory**: `D:\Dev\repos` (when bug occurred)

## Related Code

- Path traversal validation exists (`validate_project_path`) but may not catch this case
- Default folder "inbox" may need special handling to ensure it's always within project

## Workaround

Until fixed, users should:
1. Always start Advanced Memory from the project directory
2. Manually move orphaned files from wrong locations to correct project folders
3. Verify file locations after creation
