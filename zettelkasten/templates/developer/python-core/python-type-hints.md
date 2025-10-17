# Python Type Hints

Type hints provide optional static typing to Python, enabling better tooling and error detection.

## Why Type Hints?

### Benefits
1. **Early Error Detection**: Catch type errors before runtime
2. **Better IDE Support**: Autocomplete, inline docs, refactoring
3. **Self-Documenting**: Types clarify function contracts
4. **Refactoring Safety**: Type checker catches breaking changes
5. **Team Communication**: Clear expectations for function inputs/outputs

## Basic Syntax

### Variables
```python
name: str = "Alice"
age: int = 30
height: float = 5.7
is_active: bool = True
```

### Functions
```python
def add(a: int, b: int) -> int:
    return a + b

def greet(name: str, enthusiastic: bool = False) -> str:
    greeting = f"Hello, {name}!"
    return greeting + "!" if enthusiastic else greeting
```

## Collection Types

### Modern Syntax (Python 3.9+)
```python
# Lists
numbers: list[int] = [1, 2, 3]
names: list[str] = ["Alice", "Bob"]

# Dictionaries
scores: dict[str, float] = {"math": 95.5, "english": 88.0}
config: dict[str, Any] = {"debug": True, "port": 8000}

# Sets
tags: set[str] = {"python", "programming", "tutorial"}
```

### Legacy Syntax (Python 3.5-3.8)
```python
from typing import List, Dict, Set

numbers: List[int] = [1, 2, 3]
scores: Dict[str, float] = {"math": 95.5}
tags: Set[str] = {"python"}
```

## Optional and Union Types

### Optional (value or None)
```python
from typing import Optional

def find_user(user_id: int) -> Optional[str]:
    # Returns str or None
    user = database.get(user_id)
    return user.name if user else None

# Modern syntax (Python 3.10+)
def find_user(user_id: int) -> str | None:
    return database.get(user_id)
```

### Union (multiple possible types)
```python
from typing import Union

def process_id(id_value: Union[int, str]) -> str:
    return str(id_value)

# Modern syntax (Python 3.10+)
def process_id(id_value: int | str) -> str:
    return str(id_value)
```

## Advanced Types

### Generic Types
```python
from typing import TypeVar, Generic

T = TypeVar('T')

class Box(Generic[T]):
    def __init__(self, content: T):
        self.content = content

    def get(self) -> T:
        return self.content

# Usage
int_box: Box[int] = Box(42)
str_box: Box[str] = Box("hello")
```

### Callable Types
```python
from typing import Callable

def apply_operation(x: int, operation: Callable[[int], int]) -> int:
    return operation(x)

# Usage
result = apply_operation(5, lambda x: x * 2)  # 10
```

### Protocol (Structural Subtyping)
```python
from typing import Protocol

class Drawable(Protocol):
    def draw(self) -> None: ...

def render(obj: Drawable) -> None:
    obj.draw()  # Any object with draw() method works
```

## Type Checking Tools

### Mypy
```bash
pip install mypy
mypy src/
```

### Pyright (Microsoft)
```bash
pip install pyright
pyright src/
```

### Configuration
```toml
# pyproject.toml
[tool.pyright]
include = ["src/"]
pythonVersion = "3.11"

[tool.mypy]
python_version = "3.11"
warn_return_any = true
strict = true
```

## Best Practices

1. **Always type function signatures**
   ```python
   def process(data: dict[str, Any]) -> list[str]:  # ✅
   def process(data):  # ❌ No types
   ```

2. **Use specific types over Any**
   ```python
   data: dict[str, int]  # ✅ Specific
   data: dict[str, Any]  # ⚠️ Less helpful
   ```

3. **Type complex structures**
   ```python
   from typing import TypedDict

   class UserDict(TypedDict):
       name: str
       age: int
       email: str

   def create_user(data: UserDict) -> User:
       ...
   ```

4. **Use type: ignore sparingly**
   ```python
   # Only when necessary, with specific error code
   result = complex_operation()  # type: ignore[return-value]
   ```

## Common Patterns

### Type Aliases
```python
UserId = int
UserName = str
UserData = dict[str, Any]

def get_user(user_id: UserId) -> UserData:
    ...
```

### Literal Types
```python
from typing import Literal

def set_mode(mode: Literal["dev", "prod", "test"]) -> None:
    ...
```

### TypedDict for Structured Data
```python
from typing import TypedDict

class Config(TypedDict):
    host: str
    port: int
    debug: bool

config: Config = {"host": "localhost", "port": 8000, "debug": True}
```

## Related Concepts
- [[Python Fundamentals]]
- [[Static vs Dynamic Typing]]
- [[Type-Driven Development]]
- [[Python Best Practices]]
- [[Python Testing]]

*Type hints are optional but invaluable - they're living documentation that never goes stale.*
