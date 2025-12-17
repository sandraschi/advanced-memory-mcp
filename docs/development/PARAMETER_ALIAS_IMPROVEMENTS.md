# Parameter Alias Improvements for adn_content Tool

**Problem**: AI agents repeatedly use wrong parameter names (e.g., `new_string` instead of `content`), causing many failed tool calls.

**Solution**: Add parameter aliases and better error messages.

---

## Current Issue

**Wrong usage** (repeated 15+ times):
```python
adn_content("edit", 
    identifier="...",
    edit_operation="find_replace",
    find_text="...",
    new_string="..."  # ❌ Wrong parameter name
)
```

**Correct usage**:
```python
adn_content("edit",
    identifier="...",
    edit_operation="find_replace", 
    find_text="...",
    content="..."  # ✅ Correct parameter name
)
```

---

## Solution 1: Add Parameter Aliases (Recommended)

### Implementation

Modify `src/advanced_memory/mcp/tools/content_manager.py`:

```python
@mcp.tool
async def adn_content(
    operation: Literal[...],
    identifier: str | None = None,
    content: str | None = None,
    # ... other parameters ...
) -> str:
    """Comprehensive content management tool..."""
    
    # Parameter aliasing at function start
    # Handle common mistakes and aliases
    import inspect
    frame = inspect.currentframe()
    if frame:
        local_vars = frame.f_back.f_locals if frame.f_back else {}
        
        # Alias handling: new_string -> content
        if 'new_string' in local_vars and 'content' not in local_vars:
            content = local_vars.get('new_string')
            logger.warning("Parameter 'new_string' is deprecated. Use 'content' instead.")
        
        # Alias handling: replacement -> content (for find_replace)
        if edit_operation == "find_replace":
            if 'replacement' in local_vars and 'content' not in local_vars:
                content = local_vars.get('replacement')
                logger.warning("Parameter 'replacement' is deprecated. Use 'content' instead.")
```

**Better approach using Pydantic Field aliases** (if FastMCP supports it):

```python
from pydantic import Field

@mcp.tool
async def adn_content(
    operation: Literal[...],
    identifier: str | None = None,
    content: str | None = Field(
        None,
        alias="new_string",  # Accept new_string as alias
        alias_priority=2,    # Prefer 'content', but accept alias
        description="Content to write/replace. Alias: new_string, replacement"
    ),
    # ... other parameters ...
) -> str:
```

**Note**: FastMCP may not support Pydantic Field aliases directly. Check FastMCP documentation.

---

## Solution 2: Manual Parameter Mapping (Works Now)

Add parameter normalization at the start of the function:

```python
async def adn_content(
    operation: Literal[...],
    identifier: str | None = None,
    content: str | None = None,
    # Accept aliases via **kwargs
    **kwargs
) -> str:
    """Comprehensive content management tool..."""
    
    # Parameter alias mapping
    alias_map = {
        "new_string": "content",
        "replacement": "content",  # For find_replace operations
        "new_content": "content",
        "text": "content",  # Common mistake
    }
    
    # Map aliases to correct parameters
    for alias, correct_param in alias_map.items():
        if alias in kwargs and locals().get(correct_param) is None:
            # Set the correct parameter from alias
            if correct_param == "content":
                content = kwargs[alias]
            logger.warning(
                f"Parameter '{alias}' is deprecated. Use '{correct_param}' instead. "
                f"Automatically mapped for this call."
            )
    
    # Remove aliases from kwargs to avoid conflicts
    for alias in alias_map.keys():
        kwargs.pop(alias, None)
    
    # Continue with normal processing...
```

**Problem**: FastMCP tools don't accept `**kwargs` directly. Need to check FastMCP API.

---

## Solution 3: Better Error Messages (Immediate Fix)

Improve validation error messages to suggest correct parameter:

```python
# In content_manager.py, around line 400-450 where validation happens

if operation == "edit" and edit_operation == "find_replace":
    if not content and not find_text:
        return f"""# Error: Missing Required Parameters

For `find_replace` operation, you need:
- `find_text`: The text to find (REQUIRED)
- `content`: The replacement text (REQUIRED)

**Common mistakes:**
- Using `new_string` instead of `content` ❌
- Using `replacement` instead of `content` ❌

**Correct usage:**
```python
adn_content("edit",
    identifier="My Note",
    edit_operation="find_replace",
    find_text="old text",
    content="new text"  # ✅ Use 'content', not 'new_string'
)
```

**If you used `new_string`, change it to `content` and try again.**
"""
```

---

## Solution 4: Pre-Validation Hook (FastMCP Feature)

If FastMCP supports pre-validation hooks, add parameter normalization:

```python
# In content_manager.py

def normalize_parameters(kwargs: dict) -> dict:
    """Normalize parameter names before validation."""
    alias_map = {
        "new_string": "content",
        "replacement": "content",
        "new_content": "content",
    }
    
    normalized = kwargs.copy()
    for alias, correct in alias_map.items():
        if alias in normalized and correct not in normalized:
            normalized[correct] = normalized.pop(alias)
            logger.warning(f"Mapped '{alias}' -> '{correct}'")
    
    return normalized

# Apply before tool execution (if FastMCP supports this)
```

---

## Recommended Implementation

**Immediate fix** (Solution 3): Improve error messages to catch and suggest fixes.

**Long-term fix** (Solution 1 or 2): Add parameter aliases if FastMCP supports it.

### Step 1: Add Better Error Messages

```python
# In content_manager.py, find validation section

def _validate_edit_parameters(operation, edit_operation, content, find_text, **kwargs):
    """Validate edit operation parameters with helpful error messages."""
    
    # Check for common wrong parameter names
    wrong_params = {
        "new_string": "content",
        "replacement": "content", 
        "new_content": "content",
    }
    
    for wrong, correct in wrong_params.items():
        if wrong in kwargs:
            return f"""# Parameter Error

You used `{wrong}` but the correct parameter name is `{correct}`.

**Fix:**
Change `{wrong}="..."` to `{correct}="..."` in your tool call.

**Example:**
```python
# ❌ Wrong
adn_content("edit", edit_operation="find_replace", {wrong}="new text")

# ✅ Correct  
adn_content("edit", edit_operation="find_replace", {correct}="new text")
```
"""
    
    # Continue with normal validation...
```

### Step 2: Check FastMCP for Alias Support

Check if FastMCP 2.13+ supports:
- Pydantic Field aliases
- Parameter normalization hooks
- Custom validation decorators

If yes, implement Solution 1 or 2.

---

## Testing

After implementation, test with:

```python
# Should work (with warning)
adn_content("edit", 
    identifier="test",
    edit_operation="find_replace",
    find_text="old",
    new_string="new"  # Should map to content
)

# Should provide helpful error
adn_content("edit",
    identifier="test", 
    edit_operation="find_replace",
    new_string="new"  # Should suggest using 'content'
)
```

---

## Related Files

- `src/advanced_memory/mcp/tools/content_manager.py` - Main tool implementation
- `src/advanced_memory/services/entity_service.py` - Edit validation
- FastMCP documentation - Check for alias support

---

**Status**: Proposal - Needs implementation  
**Priority**: Medium (reduces failed tool calls)  
**Effort**: Low (error messages) to Medium (aliases if supported)




























