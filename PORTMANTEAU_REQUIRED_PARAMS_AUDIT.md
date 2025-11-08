# Portmanteau Tools Required Parameters Audit

**Date:** 2025-10-30  
**Issue:** Parameters marked as optional when they're actually required for specific operations

## Problem

Portmanteau tools make all parameters optional (`str | None = None`) because they route to different operations. However, this:
- ❌ Hides type safety - can't tell what's required
- ❌ Confuses Claude - doesn't know what to provide
- ❌ Bad API design - unclear contracts
- ❌ Late validation - errors only found at runtime

## Current State Analysis

### adn_content
```python
identifier: str | None = None,  # ❌ Required for write, read, edit, delete, move
content: str | None = None,     # ❌ Required for write, edit
folder: str | None = None,      # ❌ Required for write, move
```

**Operations:**
- `write`: REQUIRES identifier, content, folder
- `read`: REQUIRES identifier
- `edit`: REQUIRES identifier, content (depending on edit_operation)
- `delete`: REQUIRES identifier
- `move`: REQUIRES identifier, destination_path
- `edit_tags`: REQUIRES identifier, tag_operation

### adn_export
```python
export_path: str | None = None,  # ⚠️ Has smart default but unclear
book_title: str | None = None,   # ❌ Required for pdf_book operation
```

**Operations:**
- `pandoc`: export_path has smart default (OK)
- `pdf_book`: book_title REQUIRED but marked optional
- `docsify`: export_path has smart default (OK)

### adn_import
```python
source_path: str,  # ✅ Correctly required!
destination_folder: str | None = None,  # Has default, OK
```

### adn_project
```python
project_name: str | None = None,  # ❌ Required for create, switch, delete, sync, status
project_path: str | None = None,  # ❌ Required for create
```

**Operations:**
- `create`: REQUIRES project_name, project_path
- `switch`: REQUIRES project_name
- `delete`: REQUIRES project_name
- `sync`: REQUIRES project_name
- `status`: REQUIRES project_name

### adn_skills
```python
identifier: str | None = None,    # ❌ Required for read, update, delete, package, to_zettel
skill_name: str | None = None,    # ❌ Required for create
description: str | None = None,   # ❌ Required for create, from_zettel
source_path: str | None = None,   # ❌ Required for import
```

### adn_zettelmaker
```python
category: str | None = None,  # ❌ Required for generate
topic: str | None = None,     # ❌ Required for generate
```

**Operations:**
- `generate`: REQUIRES category, topic

## Solution Strategy

Since Python/FastMCP doesn't support conditional required parameters based on operation, we need to:

1. **Document clearly** - Explicitly state in docstrings what's required for each operation
2. **Better error messages** - Show what's missing and provide examples
3. **Type hints where possible** - At least mark truly required params as non-optional
4. **Validation early** - Check required params immediately after routing

## Recommendations

### High Priority Fixes

1. **adn_content write operation:**
   - Document that identifier, content, folder are REQUIRED
   - Better error message showing all missing params
   - Example in docstring showing required params

2. **adn_export pdf_book operation:**
   - Document that book_title is REQUIRED
   - Better error message

3. **adn_project operations:**
   - Document required params for each operation
   - Better error messages per operation

4. **adn_zettelmaker generate:**
   - Document that category and topic are REQUIRED
   - Better error message

## Implementation Plan

1. Update docstrings with clear "Required for X operation" notes
2. Enhance error messages to be more helpful
3. Add examples showing required params for each operation
4. Consider runtime validation with helpful error messages

