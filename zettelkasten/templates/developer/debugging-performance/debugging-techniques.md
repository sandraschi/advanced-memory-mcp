# Debugging Techniques

Systematic approaches to finding and fixing bugs in code.

## The Debugging Mindset

### Core Principles
1. **Reproduce**: Make bug happen reliably
2. **Isolate**: Narrow down to specific code
3. **Understand**: Know what should happen
4. **Fix**: Change code to match expectation
5. **Verify**: Ensure bug is gone and nothing broke

## Debugging Tools

### Print Debugging
Simple but effective.

```python
def calculate_total(items):
    print(f"DEBUG: items = {items}")  # What we got
    total = sum(item['price'] for item in items)
    print(f"DEBUG: total = {total}")  # What we calculated
    return total
```

**Better**: Use logging
```python
import logging

logger = logging.getLogger(__name__)

def calculate_total(items):
    logger.debug(f"Calculating total for {len(items)} items")
    total = sum(item['price'] for item in items)
    logger.debug(f"Total: {total}")
    return total
```

### Python Debugger (pdb)
Interactive debugging.

```python
import pdb

def problematic_function(data):
    processed = transform(data)
    pdb.set_trace()  # Execution stops here
    result = calculate(processed)
    return result
```

**Commands**:
- `n` (next): Execute current line
- `s` (step): Step into function
- `c` (continue): Continue execution
- `p variable`: Print variable value
- `l` (list): Show source code
- `q` (quit): Exit debugger

### IDE Debuggers
Visual debugging with breakpoints.

**VS Code**:
- Click left of line number to set breakpoint
- F5 to start debugging
- F10 to step over
- F11 to step into
- Hover over variables to inspect

### Post-Mortem Debugging
Inspect state after crash.

```python
import pdb

try:
    result = risky_operation()
except Exception:
    pdb.post_mortem()  # Debug at point of failure
```

## Systematic Debugging

### Binary Search Method
Divide and conquer to find bug location.

```
1. Check middle of suspect code
2. Determine if bug is before or after
3. Repeat in relevant half
4. Continue until isolated
```

### Rubber Duck Debugging
Explain code line-by-line to rubber duck (or colleague).

**Why It Works**: Articulating logic reveals flaws.

### Git Bisect
Find commit that introduced bug.

```bash
git bisect start
git bisect bad  # Current commit has bug
git bisect good v1.0.0  # This version worked

# Git checks out middle commit
# Test it, then:
git bisect good  # or 'bad'

# Repeat until bug-introducing commit found
```

## Common Bug Patterns

### Off-by-One Errors
```python
# ❌ Bug: Misses last element
for i in range(len(items) - 1):
    process(items[i])

# ✅ Fix
for i in range(len(items)):
    process(items[i])

# ✅ Better: Use direct iteration
for item in items:
    process(item)
```

### Null/None Reference
```python
# ❌ Bug: Crashes if user is None
name = user.name

# ✅ Fix: Check first
name = user.name if user else "Unknown"

# ✅ Better: Explicit handling
if user is None:
    raise ValueError("User not found")
name = user.name
```

### Mutable Default Arguments
```python
# ❌ Bug: List is shared between calls!
def add_item(item, items=[]):
    items.append(item)
    return items

add_item(1)  # [1]
add_item(2)  # [1, 2] - Unexpected!

# ✅ Fix: Use None as default
def add_item(item, items=None):
    if items is None:
        items = []
    items.append(item)
    return items
```

### Race Conditions
```python
# ❌ Bug: Two threads modify same data
counter = 0

def increment():
    global counter
    counter += 1  # Not atomic!

# ✅ Fix: Use lock
import threading

counter = 0
lock = threading.Lock()

def increment():
    global counter
    with lock:
        counter += 1
```

## Debugging Async Code

### Common Issues

**Forgotten await**:
```python
# ❌ Bug: Returns coroutine, doesn't execute
async def get_data():
    result = fetch_from_api()  # Missing await!
    return result

# ✅ Fix
async def get_data():
    result = await fetch_from_api()
    return result
```

**Blocking in async**:
```python
# ❌ Bug: Blocks event loop
async def process():
    time.sleep(1)  # Blocks!

# ✅ Fix: Use async sleep
async def process():
    await asyncio.sleep(1)
```

## Logging Best Practices

### Log Levels
```python
import logging

logger = logging.getLogger(__name__)

logger.debug("Detailed diagnostic info")
logger.info("Informational messages")
logger.warning("Warning - something unexpected")
logger.error("Error - operation failed")
logger.critical("Critical - system unstable")
```

### Structured Logging
```python
# ✅ Good: Structured data
logger.error(
    "User authentication failed",
    extra={
        "user_id": user_id,
        "ip_address": request.ip,
        "attempt_count": attempts
    }
)
```

### Conditional Logging
```python
# Avoid expensive operations in debug logs
if logger.isEnabledFor(logging.DEBUG):
    logger.debug(f"Complex data: {expensive_operation()}")
```

## Testing as Debugging

### Write Test to Reproduce Bug
```python
def test_bug_reproduction():
    # Minimal case that triggers bug
    result = problematic_function(edge_case_input)
    assert result == expected_output  # Fails

# Fix code until test passes
```

### Use Tests to Prevent Regression
After fixing bug, keep the test to ensure it doesn't return.

## Performance Debugging

### Profiling
```python
import cProfile

cProfile.run('slow_function()')

# Or with context manager
import profile

profiler = profile.Profile()
profiler.enable()
slow_function()
profiler.disable()
profiler.print_stats(sort='cumulative')
```

### Memory Profiling
```python
from memory_profiler import profile

@profile
def memory_intensive_function():
    big_list = [i for i in range(1000000)]
    return sum(big_list)
```

## Prevention

### Assertions
Catch bugs early in development.

```python
def divide(a: float, b: float) -> float:
    assert b != 0, "Division by zero"
    return a / b
```

### Type Hints
Catch type errors before runtime.

```python
def process(data: dict[str, int]) -> list[int]:
    return list(data.values())

# Type checker catches: process("wrong type")
```

### Code Review
Second pair of eyes catches issues.

## Related Concepts
- [[Python Testing]]
- [[Logging Best Practices]]
- [[Error Handling]]
- [[Code Review]]
- [[Performance Optimization]]

*Debugging is twice as hard as writing code - write simple code to make debugging easier.*
