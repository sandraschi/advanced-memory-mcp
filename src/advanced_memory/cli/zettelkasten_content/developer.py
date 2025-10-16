"""Developer Zettelkasten Templates - 15 excellent, interconnected notes."""

DEVELOPER_TEMPLATES = {
    "python-core": [
        {
            "title": "Python Fundamentals",
            "folder": "development/python",
            "content": r'''# Python Fundamentals

Python is a high-level, interpreted, general-purpose programming language emphasizing code readability.

## Core Philosophy

> "There should be one-- and preferably only one --obvious way to do it." - The Zen of Python

Python values:
- **Readability**: Code is read more than written
- **Simplicity**: Simple is better than complex
- **Explicitness**: Explicit is better than implicit

## Essential Data Types

### Numbers
```python
integer = 42
floating = 3.14159
complex_num = 3 + 4j
```

### Strings
```python
single = 'Hello'
double = "World"
multiline = '''Multiple
lines'''
f_string = f"Value: {42}"
```

### Collections
```python
# List - ordered, mutable
fruits = ['apple', 'banana', 'cherry']

# Tuple - ordered, immutable
coordinates = (10, 20)

# Dictionary - key-value pairs
person = {'name': 'Alice', 'age': 30}

# Set - unordered, unique elements
unique_nums = {1, 2, 3, 3}  # {1, 2, 3}
```

## Control Flow

### Conditionals
```python
if temperature > 30:
    print("Hot")
elif temperature > 20:
    print("Warm")
else:
    print("Cold")
```

### Loops
```python
# For loop
for fruit in fruits:
    print(fruit)

# While loop
count = 0
while count < 5:
    print(count)
    count += 1

# List comprehension
squares = [x**2 for x in range(10)]
```

## Functions
```python
def greet(name: str, greeting: str = "Hello") -> str:
    """Greet someone with a custom or default greeting."""
    return f"{greeting}, {name}!"

# Lambda functions
square = lambda x: x**2
```

## Modules and Imports
```python
# Standard library
import os
from pathlib import Path
import json

# Third-party
import requests
import pandas as pd

# Local imports
from mymodule import myfunction
```

## Error Handling
```python
try:
    result = risky_operation()
except ValueError as e:
    print(f"Value error: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
finally:
    cleanup()
```

## Related Concepts
- [[Python Type Hints]]
- [[Python Virtual Environments]]
- [[Object-Oriented Programming]]
- [[Python Best Practices]]
- [[Python Testing]]
- [[Python Async Programming]]

*Master the fundamentals before diving into frameworks and libraries.*
''',
        },
        {
            "title": "Python Type Hints",
            "folder": "development/python",
            "content": r'''# Python Type Hints

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
''',
        },
        {
            "title": "Python Virtual Environments",
            "folder": "development/python",
            "content": r'''# Python Virtual Environments

Virtual environments isolate project dependencies, preventing conflicts between projects.

## Why Virtual Environments?

### The Problem
```bash
# Project A needs requests 2.25.0
pip install requests==2.25.0

# Project B needs requests 2.31.0
pip install requests==2.31.0  # ❌ Breaks Project A!
```

### The Solution
Each project gets its own isolated environment with its own dependencies.

## Creating Virtual Environments

### Using venv (Built-in)
```bash
# Create environment
python -m venv .venv

# Activate (Windows)
.venv\\Scripts\\activate

# Activate (Unix/Mac)
source .venv/bin/activate

# Deactivate
deactivate
```

### Using UV (Modern, Fast)
```bash
# Create and sync dependencies
uv sync

# Activate
source .venv/bin/activate  # Unix/Mac
.venv\\Scripts\\activate  # Windows

# Run command in venv without activating
uv run python script.py
```

### Using Poetry
```bash
# Create environment and install deps
poetry install

# Run in environment
poetry run python script.py

# Activate shell
poetry shell
```

## Managing Dependencies

### requirements.txt
```bash
# Generate
pip freeze > requirements.txt

# Install
pip install -r requirements.txt
```

### pyproject.toml (Modern)
```toml
[project]
dependencies = [
    "requests>=2.31.0",
    "pandas>=2.0.0",
]

[tool.uv]
dev-dependencies = [
    "pytest>=8.0.0",
    "ruff>=0.1.0",
]
```

```bash
# Install with uv
uv sync
uv sync --dev  # Include dev dependencies
```

## Best Practices

1. **One venv per project**
   ```
   project/
   ├── .venv/          # Virtual environment
   ├── src/            # Source code
   ├── tests/          # Tests
   └── pyproject.toml  # Dependencies
   ```

2. **Add .venv to .gitignore**
   ```gitignore
   .venv/
   venv/
   *.pyc
   __pycache__/
   ```

3. **Document Python version**
   ```toml
   [project]
   requires-python = ">=3.11"
   ```

4. **Lock dependencies**
   ```bash
   # UV automatically creates uv.lock
   uv lock
   
   # Poetry creates poetry.lock
   poetry lock
   ```

5. **Use consistent tool across team**
   - Choose: venv, UV, Poetry, or conda
   - Document in README
   - Stick with it

## Common Workflows

### Starting New Project
```bash
# With UV (recommended)
mkdir myproject && cd myproject
uv init
uv add requests pandas
uv sync

# With venv
mkdir myproject && cd myproject
python -m venv .venv
source .venv/bin/activate
pip install requests pandas
pip freeze > requirements.txt
```

### Joining Existing Project
```bash
# With UV
git clone repo
cd repo
uv sync --dev

# With venv
git clone repo
cd repo
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Updating Dependencies
```bash
# With UV
uv lock --upgrade
uv sync

# With pip
pip install --upgrade package-name
pip freeze > requirements.txt
```

## Troubleshooting

### "Command not found" after install
```bash
# Ensure venv is activated
which python  # Should show .venv/bin/python

# Or use uv run
uv run python script.py
```

### Conflicting dependencies
```bash
# Check what's installed
pip list

# Create fresh environment
rm -rf .venv
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Different Python versions
```bash
# Specify Python version
python3.11 -m venv .venv

# Or with UV
uv python install 3.11
uv python pin 3.11
```

## Related Concepts
- [[Python Fundamentals]]
- [[Package Management]]
- [[Dependency Management]]
- [[Python Project Structure]]
- [[Reproducible Builds]]

*Virtual environments are not optional - they're essential for professional Python development.*
''',
        },
    ],
    "git-version-control": [
        {
            "title": "Git Fundamentals",
            "folder": "development/tools",
            "content": r'''# Git Fundamentals

Git is a distributed version control system for tracking changes in source code during software development.

## Core Concepts

### Repository (Repo)
A directory tracked by Git containing your project's history.

### Commit
A snapshot of your project at a specific point in time.

### Branch
An independent line of development.

### Remote
A version of your repository hosted on a server (e.g., GitHub).

## Basic Workflow

### Initialize Repository
```bash
# Create new repo
git init

# Clone existing repo
git clone https://github.com/user/repo.git
```

### Stage and Commit
```bash
# Check status
git status

# Stage files
git add file.py
git add .  # Stage all changes

# Commit
git commit -m "Add new feature"

# Stage and commit in one step
git commit -am "Update existing files"
```

### View History
```bash
# Show commits
git log
git log --oneline  # Compact view
git log --graph --oneline --all  # Visual branch history

# Show changes
git diff  # Unstaged changes
git diff --staged  # Staged changes
git show commit-hash  # Specific commit
```

## Branching

### Create and Switch Branches
```bash
# Create new branch
git branch feature-name

# Switch to branch
git checkout feature-name

# Create and switch in one command
git checkout -b feature-name

# Modern syntax (Git 2.23+)
git switch feature-name
git switch -c feature-name  # Create and switch
```

### Merge Branches
```bash
# Switch to target branch
git checkout main

# Merge feature branch
git merge feature-name

# Delete merged branch
git branch -d feature-name
```

## Working with Remotes

### Basic Remote Operations
```bash
# Add remote
git remote add origin https://github.com/user/repo.git

# View remotes
git remote -v

# Fetch changes
git fetch origin

# Pull changes (fetch + merge)
git pull origin main

# Push changes
git push origin main
git push -u origin feature-name  # Set upstream
```

## Undoing Changes

### Before Commit
```bash
# Discard unstaged changes
git checkout -- file.py
git restore file.py  # Modern syntax

# Unstage files
git reset HEAD file.py
git restore --staged file.py  # Modern syntax
```

### After Commit
```bash
# Amend last commit
git commit --amend -m "New message"

# Reset to previous commit (keep changes)
git reset --soft HEAD~1

# Reset to previous commit (discard changes)
git reset --hard HEAD~1  # ⚠️ Destructive!

# Revert commit (create new commit)
git revert commit-hash  # ✅ Safe for shared branches
```

## Best Practices

1. **Commit Often**: Small, focused commits
2. **Write Good Messages**: Clear, descriptive commit messages
3. **Use Branches**: Feature branches for new work
4. **Pull Before Push**: Avoid conflicts
5. **Don't Commit Secrets**: Use .gitignore
6. **Review Before Commit**: `git diff --staged`

## Commit Message Convention
```
type(scope): subject

body (optional)

footer (optional)
```

**Types**: feat, fix, docs, style, refactor, test, chore

**Example**:
```
feat(auth): add user login functionality

Implement JWT-based authentication with refresh tokens.
Includes login, logout, and token refresh endpoints.

Closes #123
```

## Common .gitignore Patterns
```gitignore
# Python
__pycache__/
*.pyc
.venv/
*.egg-info/

# IDEs
.vscode/
.idea/
*.swp

# OS
.DS_Store
Thumbs.db

# Project-specific
config.local.py
*.log
.env
```

## Related Concepts
- [[Git Branching Strategies]]
- [[Git Workflows]]
- [[GitHub Pull Requests]]
- [[Code Review Best Practices]]
- [[Version Control Philosophy]]

*Git is not just a tool - it's a time machine for your code.*
''',
        },
        {
            "title": "Python Testing",
            "folder": "development/python",
            "content": r'''# Python Testing

Automated testing ensures code quality, catches bugs early, and enables confident refactoring.

## Why Test?

### Benefits
1. **Catch Bugs Early**: Before they reach production
2. **Enable Refactoring**: Change code with confidence
3. **Document Behavior**: Tests show how code should work
4. **Faster Development**: Less time debugging
5. **Better Design**: Testable code is usually better code

## Testing Frameworks

### pytest (Recommended)
```python
# test_math.py
def test_addition():
    assert 2 + 2 == 4

def test_subtraction():
    assert 5 - 3 == 2

# Run tests
# pytest test_math.py
```

### unittest (Built-in)
```python
import unittest

class TestMath(unittest.TestCase):
    def test_addition(self):
        self.assertEqual(2 + 2, 4)
    
    def test_subtraction(self):
        self.assertEqual(5 - 3, 2)

if __name__ == '__main__':
    unittest.main()
```

## Test Types

### Unit Tests
Test individual functions or methods in isolation.

```python
def calculate_total(items: list[float], tax_rate: float) -> float:
    subtotal = sum(items)
    return subtotal * (1 + tax_rate)

def test_calculate_total():
    items = [10.0, 20.0, 30.0]
    total = calculate_total(items, 0.1)
    assert total == 66.0  # 60 * 1.1
```

### Integration Tests
Test how components work together.

```python
def test_user_registration_flow():
    # Create user
    user = create_user("alice@example.com", "password123")
    
    # Verify in database
    stored_user = db.get_user(user.id)
    assert stored_user.email == "alice@example.com"
    
    # Verify can login
    token = login(user.email, "password123")
    assert token is not None
```

### Functional/End-to-End Tests
Test complete user workflows.

```python
def test_complete_checkout_process(client):
    # Add items to cart
    response = client.post("/cart/add", json={"item_id": 123})
    assert response.status_code == 200
    
    # Proceed to checkout
    response = client.post("/checkout")
    assert response.status_code == 200
    
    # Verify order created
    orders = client.get("/orders").json()
    assert len(orders) == 1
```

## pytest Features

### Fixtures
```python
import pytest

@pytest.fixture
def sample_data():
    return [1, 2, 3, 4, 5]

def test_sum(sample_data):
    assert sum(sample_data) == 15

@pytest.fixture
def database():
    db = Database()
    db.connect()
    yield db  # Provide to test
    db.disconnect()  # Cleanup
```

### Parametrize
```python
@pytest.mark.parametrize("input,expected", [
    (2, 4),
    (3, 9),
    (4, 16),
])
def test_square(input, expected):
    assert input ** 2 == expected
```

### Markers
```python
@pytest.mark.slow
def test_large_dataset():
    ...

@pytest.mark.skip(reason="Not implemented yet")
def test_future_feature():
    ...

# Run specific markers
# pytest -m slow
# pytest -m "not slow"
```

## Test Organization

### Directory Structure
```
project/
├── src/
│   └── mypackage/
│       ├── __init__.py
│       └── module.py
├── tests/
│   ├── __init__.py
│   ├── conftest.py  # Shared fixtures
│   ├── test_module.py
│   └── integration/
│       └── test_workflows.py
└── pyproject.toml
```

### Naming Conventions
- Test files: `test_*.py` or `*_test.py`
- Test functions: `test_*`
- Test classes: `Test*`

## Mocking and Patching

### unittest.mock
```python
from unittest.mock import Mock, patch

def test_api_call():
    with patch('requests.get') as mock_get:
        mock_get.return_value.json.return_value = {"status": "ok"}
        
        result = fetch_data()
        assert result["status"] == "ok"
        mock_get.assert_called_once()
```

### pytest-mock
```python
def test_file_operation(mocker):
    mock_open = mocker.patch('builtins.open')
    
    read_file("test.txt")
    mock_open.assert_called_with("test.txt", "r")
```

## Coverage

### pytest-cov
```bash
# Install
pip install pytest-cov

# Run with coverage
pytest --cov=src --cov-report=html

# View report
open htmlcov/index.html
```

### Coverage Goals
- **80%+**: Good coverage
- **90%+**: Excellent coverage
- **100%**: Probably over-testing

Focus on critical paths, not arbitrary coverage numbers.

## Test-Driven Development (TDD)

### Red-Green-Refactor Cycle
1. **Red**: Write failing test
2. **Green**: Write minimal code to pass
3. **Refactor**: Improve code quality

```python
# 1. Red - Write test first
def test_user_validation():
    assert validate_email("user@example.com") == True
    assert validate_email("invalid") == False

# 2. Green - Implement
def validate_email(email: str) -> bool:
    return "@" in email  # Minimal implementation

# 3. Refactor - Improve
import re

def validate_email(email: str) -> bool:
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))
```

## Best Practices

1. **Test One Thing**: Each test should verify one behavior
2. **Independent Tests**: Tests shouldn't depend on each other
3. **Fast Tests**: Unit tests should run in milliseconds
4. **Clear Names**: Test name describes what's being tested
5. **Arrange-Act-Assert**: Structure tests clearly
   ```python
   def test_user_creation():
       # Arrange
       email = "user@example.com"
       password = "secure123"
       
       # Act
       user = create_user(email, password)
       
       # Assert
       assert user.email == email
       assert user.is_active == True
   ```

## Common Pitfalls

❌ **Testing Implementation Details**
```python
def test_internal_method():
    obj._private_method()  # Don't test private methods
```

❌ **Slow Tests**
```python
def test_with_sleep():
    time.sleep(5)  # Avoid delays in unit tests
```

❌ **Flaky Tests**
```python
def test_random():
    assert random.randint(1, 10) == 5  # Non-deterministic
```

✅ **Test Public Interface**
```python
def test_public_behavior():
    result = obj.public_method()
    assert result == expected_value
```

## Related Concepts
- [[Test-Driven Development]]
- [[Continuous Integration]]
- [[Code Coverage]]
- [[Mocking and Stubbing]]
- [[Python Best Practices]]

*Tests are not overhead - they're the foundation of confident development.*
''',
        },
    ],
    "web-apis": [
        {
            "title": "RESTful API Design",
            "folder": "development/web",
            "content": r'''# RESTful API Design

REST (Representational State Transfer) is an architectural style for designing networked applications.

## REST Principles

### 1. Client-Server Architecture
- Clear separation between client and server
- Server provides resources, client consumes them
- Independent evolution of each side

### 2. Stateless
- Each request contains all information needed
- Server doesn't store client state between requests
- Improves scalability and reliability

### 3. Cacheable
- Responses explicitly indicate if they can be cached
- Improves performance and scalability

### 4. Uniform Interface
- Consistent way to interact with resources
- Standard HTTP methods
- Resource identification through URIs

### 5. Layered System
- Client doesn't know if connected directly to server
- Allows for load balancers, proxies, caches

## HTTP Methods

### GET - Retrieve Resource
```http
GET /api/users/123
Response: 200 OK
{
  "id": 123,
  "name": "Alice",
  "email": "alice@example.com"
}
```

### POST - Create Resource
```http
POST /api/users
Body: {
  "name": "Bob",
  "email": "bob@example.com"
}
Response: 201 Created
Location: /api/users/124
```

### PUT - Update/Replace Resource
```http
PUT /api/users/123
Body: {
  "name": "Alice Smith",
  "email": "alice.smith@example.com"
}
Response: 200 OK
```

### PATCH - Partial Update
```http
PATCH /api/users/123
Body: {
  "email": "newemail@example.com"
}
Response: 200 OK
```

### DELETE - Remove Resource
```http
DELETE /api/users/123
Response: 204 No Content
```

## Resource Naming

### Good Practices
```
✅ /api/users              # Collection
✅ /api/users/123          # Specific resource
✅ /api/users/123/posts    # Nested resource
✅ /api/posts?author=123   # Query parameters
```

### Bad Practices
```
❌ /api/getUsers           # Verb in URL
❌ /api/user               # Singular for collection
❌ /api/users/delete/123   # Action in URL
❌ /api/users_posts        # Underscore instead of nesting
```

## Status Codes

### Success (2xx)
- **200 OK**: Request succeeded
- **201 Created**: Resource created
- **204 No Content**: Success, no response body

### Client Errors (4xx)
- **400 Bad Request**: Invalid request format
- **401 Unauthorized**: Authentication required
- **403 Forbidden**: Authenticated but not authorized
- **404 Not Found**: Resource doesn't exist
- **422 Unprocessable Entity**: Validation failed

### Server Errors (5xx)
- **500 Internal Server Error**: Server-side error
- **502 Bad Gateway**: Upstream server error
- **503 Service Unavailable**: Server temporarily down

## Request/Response Format

### JSON (Most Common)
```json
{
  "data": {
    "id": 123,
    "type": "user",
    "attributes": {
      "name": "Alice",
      "email": "alice@example.com"
    }
  }
}
```

### Headers
```http
Content-Type: application/json
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
Accept: application/json
```

## Pagination

### Offset-Based
```http
GET /api/users?offset=20&limit=10
Response: {
  "data": [...],
  "pagination": {
    "offset": 20,
    "limit": 10,
    "total": 150
  }
}
```

### Cursor-Based
```http
GET /api/users?cursor=eyJpZCI6MTIzfQ&limit=10
Response: {
  "data": [...],
  "pagination": {
    "next_cursor": "eyJpZCI6MTMzfQ",
    "has_more": true
  }
}
```

## Filtering and Sorting

```http
# Filtering
GET /api/posts?status=published&author=123

# Sorting
GET /api/posts?sort=-created_at,title
# - prefix for descending, + or no prefix for ascending

# Field selection
GET /api/users?fields=id,name,email
```

## Error Responses

### Structured Error Format
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid email format",
    "details": [
      {
        "field": "email",
        "issue": "Must be valid email address"
      }
    ]
  }
}
```

## Versioning

### URI Versioning (Common)
```
/api/v1/users
/api/v2/users
```

### Header Versioning
```http
GET /api/users
Accept: application/vnd.myapi.v2+json
```

## Authentication

### Bearer Token
```http
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### API Key
```http
X-API-Key: your-api-key-here
```

### Basic Auth
```http
Authorization: Basic base64(username:password)
```

## Best Practices

1. **Use Nouns, Not Verbs**: `/users` not `/getUsers`
2. **Plural for Collections**: `/users` not `/user`
3. **Consistent Naming**: Stick to one convention
4. **Version Your API**: Plan for changes
5. **Document Everything**: OpenAPI/Swagger specs
6. **Handle Errors Gracefully**: Clear error messages
7. **Use HTTPS**: Always in production
8. **Rate Limiting**: Protect against abuse
9. **CORS Configuration**: Allow cross-origin requests appropriately

## Tools

- **FastAPI**: Modern Python API framework
- **Flask**: Lightweight Python framework
- **Postman**: API testing and documentation
- **Swagger/OpenAPI**: API specification and docs
- **HTTPie**: Command-line HTTP client

## Related Concepts
- [[HTTP Protocol]]
- [[API Authentication]]
- [[API Documentation]]
- [[Web Development Fundamentals]]
- [[Microservices Architecture]]

*Good API design is about making developers' lives easier - including future you.*
''',
        },
    ],
    "oop-design": [
        {
            "title": "Object-Oriented Programming",
            "folder": "development/concepts",
            "content": r'''# Object-Oriented Programming

OOP is a programming paradigm based on the concept of "objects" containing data and code.

## Four Pillars of OOP

### 1. Encapsulation
Bundle data and methods that operate on that data within a single unit (class).

```python
class BankAccount:
    def __init__(self, balance: float = 0):
        self._balance = balance  # Private attribute
    
    def deposit(self, amount: float) -> None:
        if amount > 0:
            self._balance += amount
    
    def get_balance(self) -> float:
        return self._balance  # Controlled access
```

**Benefits**:
- Data hiding and protection
- Controlled access through methods
- Implementation can change without affecting users

### 2. Inheritance
Create new classes based on existing classes, inheriting their attributes and methods.

```python
class Animal:
    def __init__(self, name: str):
        self.name = name
    
    def speak(self) -> str:
        return f"{self.name} makes a sound"

class Dog(Animal):
    def speak(self) -> str:
        return f"{self.name} barks!"

class Cat(Animal):
    def speak(self) -> str:
        return f"{self.name} meows!"
```

**Benefits**:
- Code reuse
- Hierarchical relationships
- Polymorphic behavior

### 3. Polymorphism
Objects of different classes can be treated as objects of a common base class.

```python
def make_animals_speak(animals: list[Animal]) -> None:
    for animal in animals:
        print(animal.speak())  # Different behavior for each type

animals = [Dog("Buddy"), Cat("Whiskers"), Dog("Max")]
make_animals_speak(animals)
# Output:
# Buddy barks!
# Whiskers meows!
# Max barks!
```

**Benefits**:
- Flexible code
- Easy to extend
- Common interface for different implementations

### 4. Abstraction
Hide complex implementation details, expose only essential features.

```python
from abc import ABC, abstractmethod

class Shape(ABC):
    @abstractmethod
    def area(self) -> float:
        pass
    
    @abstractmethod
    def perimeter(self) -> float:
        pass

class Rectangle(Shape):
    def __init__(self, width: float, height: float):
        self.width = width
        self.height = height
    
    def area(self) -> float:
        return self.width * self.height
    
    def perimeter(self) -> float:
        return 2 * (self.width + self.height)
```

**Benefits**:
- Simplified interface
- Implementation flexibility
- Reduced complexity

## SOLID Principles

### Single Responsibility Principle (SRP)
A class should have only one reason to change.

```python
# ❌ Bad - Multiple responsibilities
class User:
    def save_to_database(self): ...
    def send_email(self): ...
    def generate_report(self): ...

# ✅ Good - Single responsibility
class User:
    def __init__(self, name, email): ...

class UserRepository:
    def save(self, user): ...

class EmailService:
    def send(self, user, message): ...

class ReportGenerator:
    def generate(self, user): ...
```

### Open/Closed Principle (OCP)
Open for extension, closed for modification.

```python
# ✅ Good - Extend through inheritance
class PaymentProcessor(ABC):
    @abstractmethod
    def process(self, amount): ...

class CreditCardProcessor(PaymentProcessor):
    def process(self, amount):
        # Credit card logic

class PayPalProcessor(PaymentProcessor):
    def process(self, amount):
        # PayPal logic
```

### Liskov Substitution Principle (LSP)
Subtypes must be substitutable for their base types.

```python
# ✅ Good - Subclass maintains base class contract
class Bird:
    def move(self) -> str:
        return "Flying"

class Penguin(Bird):
    def move(self) -> str:
        return "Swimming"  # Still moving, just differently
```

### Interface Segregation Principle (ISP)
Many specific interfaces better than one general interface.

```python
# ✅ Good - Specific interfaces
class Printable(Protocol):
    def print(self) -> None: ...

class Saveable(Protocol):
    def save(self) -> None: ...

class Document(Printable, Saveable):
    def print(self) -> None: ...
    def save(self) -> None: ...
```

### Dependency Inversion Principle (DIP)
Depend on abstractions, not concrete implementations.

```python
# ✅ Good - Depend on abstract Database
class UserService:
    def __init__(self, db: Database):  # Abstract interface
        self.db = db
    
    def get_user(self, id: int):
        return self.db.find_by_id(id)

# Can use any database implementation
service = UserService(PostgresDatabase())
service = UserService(MongoDatabase())
```

## Design Patterns

### Creational Patterns
- **Factory**: Object creation logic
- **Singleton**: One instance only
- **Builder**: Step-by-step object construction

### Structural Patterns
- **Adapter**: Make incompatible interfaces work together
- **Decorator**: Add behavior without modifying class
- **Facade**: Simplified interface to complex system

### Behavioral Patterns
- **Observer**: Event notification system
- **Strategy**: Interchangeable algorithms
- **Command**: Encapsulate requests as objects

## Composition vs Inheritance

### Favor Composition
```python
# ✅ Composition - More flexible
class Engine:
    def start(self): ...

class Car:
    def __init__(self):
        self.engine = Engine()  # Has-a relationship
    
    def start(self):
        self.engine.start()
```

### When to Use Inheritance
```python
# ✅ Inheritance - Clear is-a relationship
class Vehicle:
    def move(self): ...

class Car(Vehicle):  # Car is-a Vehicle
    def move(self):
        return "Driving"
```

## Best Practices

1. **Prefer composition over inheritance**
2. **Keep classes focused (SRP)**
3. **Program to interfaces, not implementations**
4. **Favor immutability when possible**
5. **Use descriptive names**
6. **Don't over-engineer - YAGNI (You Aren't Gonna Need It)**

## Related Concepts
- [[Python Fundamentals]]
- [[Design Patterns]]
- [[SOLID Principles]]
- [[Clean Code]]
- [[Software Architecture]]

*OOP is a tool for organizing code - use it when it makes code clearer, not because you must.*
''',
        },
    ],
    "async-programming": [
        {
            "title": "Python Async Programming",
            "folder": "development/python",
            "content": r'''# Python Async Programming

Asynchronous programming allows concurrent execution of tasks without blocking.

## Why Async?

### The Problem: Blocking I/O
```python
# Synchronous - blocks for each request
def fetch_data():
    response1 = requests.get(url1)  # Wait...
    response2 = requests.get(url2)  # Wait...
    response3 = requests.get(url3)  # Wait...
    # Total time: sum of all requests
```

### The Solution: Async/Await
```python
# Asynchronous - concurrent requests
async def fetch_data():
    async with aiohttp.ClientSession() as session:
        tasks = [
            session.get(url1),
            session.get(url2),
            session.get(url3),
        ]
        responses = await asyncio.gather(*tasks)
    # Total time: longest single request
```

## Core Concepts

### Coroutines
Functions defined with `async def` that can be paused and resumed.

```python
async def greet(name: str) -> str:
    await asyncio.sleep(1)  # Simulated I/O
    return f"Hello, {name}!"
```

### Event Loop
Manages and executes async tasks.

```python
import asyncio

async def main():
    result = await greet("Alice")
    print(result)

# Run the event loop
asyncio.run(main())
```

### Awaitable Objects
Objects that can be used with `await`:
- Coroutines
- Tasks
- Futures

## Basic Syntax

### Async Function
```python
async def fetch_user(user_id: int) -> User:
    async with db.session() as session:
        user = await session.get(User, user_id)
        return user
```

### Await Expression
```python
# Await a coroutine
result = await some_async_function()

# Await multiple coroutines
results = await asyncio.gather(
    fetch_user(1),
    fetch_user(2),
    fetch_user(3),
)
```

## Common Patterns

### Running Multiple Tasks Concurrently
```python
async def main():
    # Create tasks
    task1 = asyncio.create_task(fetch_data(1))
    task2 = asyncio.create_task(fetch_data(2))
    task3 = asyncio.create_task(fetch_data(3))
    
    # Wait for all
    results = await asyncio.gather(task1, task2, task3)
```

### Async Context Managers
```python
class AsyncDatabase:
    async def __aenter__(self):
        await self.connect()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.disconnect()

# Usage
async with AsyncDatabase() as db:
    await db.query("SELECT * FROM users")
```

### Async Iterators
```python
class AsyncRange:
    def __init__(self, n):
        self.n = n
        self.i = 0
    
    def __aiter__(self):
        return self
    
    async def __anext__(self):
        if self.i >= self.n:
            raise StopAsyncIteration
        await asyncio.sleep(0.1)
        self.i += 1
        return self.i

# Usage
async for i in AsyncRange(5):
    print(i)
```

## Async Libraries

### aiohttp - HTTP Client/Server
```python
import aiohttp

async def fetch(url: str) -> str:
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.text()
```

### aiofiles - File I/O
```python
import aiofiles

async def read_file(path: str) -> str:
    async with aiofiles.open(path, 'r') as f:
        return await f.read()
```

### asyncpg - PostgreSQL
```python
import asyncpg

async def get_users():
    conn = await asyncpg.connect(dsn)
    users = await conn.fetch('SELECT * FROM users')
    await conn.close()
    return users
```

## Common Pitfalls

### Mixing Sync and Async
```python
# ❌ Bad - Blocking call in async function
async def bad_example():
    result = requests.get(url)  # Blocks event loop!
    return result

# ✅ Good - Use async library
async def good_example():
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.text()
```

### Forgetting await
```python
# ❌ Bad - Returns coroutine object, doesn't execute
async def bad():
    result = async_function()  # Forgot await!
    return result

# ✅ Good - Actually executes
async def good():
    result = await async_function()
    return result
```

### Not Handling Exceptions
```python
# ✅ Good - Handle exceptions in tasks
async def safe_task():
    try:
        return await risky_operation()
    except Exception as e:
        logger.error(f"Task failed: {e}")
        return None

tasks = [asyncio.create_task(safe_task()) for _ in range(10)]
results = await asyncio.gather(*tasks)
```

## When to Use Async

### Good Use Cases ✅
- I/O-bound operations (network, file, database)
- Many concurrent connections
- Web servers and APIs
- Web scraping
- Real-time applications

### Bad Use Cases ❌
- CPU-bound operations (use multiprocessing instead)
- Simple scripts with sequential logic
- When libraries don't support async

## Performance Considerations

### Async is NOT Always Faster
```python
# For CPU-bound work, async adds overhead
async def calculate():  # ❌ No benefit
    return sum(range(1000000))

# Use regular function or multiprocessing
def calculate():  # ✅ Better
    return sum(range(1000000))
```

### Async Shines for I/O
```python
# Async excels at concurrent I/O
async def fetch_all_users():
    tasks = [fetch_user(id) for id in range(100)]
    return await asyncio.gather(*tasks)
    # 100x faster than sequential!
```

## Testing Async Code

### pytest-asyncio
```python
import pytest

@pytest.mark.asyncio
async def test_async_function():
    result = await async_operation()
    assert result == expected
```

## Related Concepts
- [[Python Fundamentals]]
- [[Concurrency vs Parallelism]]
- [[Event Loop Architecture]]
- [[Async Best Practices]]
- [[Performance Optimization]]

*Async is powerful for I/O-bound work, but adds complexity - use when benefits outweigh costs.*
''',
        },
    ],
    "databases": [
        {
            "title": "Database Fundamentals",
            "folder": "development/databases",
            "content": r'''# Database Fundamentals

Databases store, organize, and retrieve data efficiently and reliably.

## Types of Databases

### Relational (SQL)
Structured data in tables with relationships.

**Examples**: PostgreSQL, MySQL, SQLite
**Best for**: Structured data, complex queries, transactions

```sql
-- Tables with relationships
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    email VARCHAR(100) UNIQUE
);

CREATE TABLE posts (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    title VARCHAR(200),
    content TEXT
);
```

### Document (NoSQL)
Flexible schema, JSON-like documents.

**Examples**: MongoDB, CouchDB
**Best for**: Flexible schemas, rapid development, hierarchical data

```javascript
// Document structure
{
  "_id": "507f1f77bcf86cd799439011",
  "name": "Alice",
  "email": "alice@example.com",
  "posts": [
    {
      "title": "First Post",
      "content": "Hello world!"
    }
  ]
}
```

### Key-Value
Simple key-value pairs, extremely fast.

**Examples**: Redis, Memcached
**Best for**: Caching, sessions, real-time data

```python
# Redis example
redis.set("user:123:name", "Alice")
name = redis.get("user:123:name")
```

### Graph
Nodes and relationships, optimized for connected data.

**Examples**: Neo4j, ArangoDB
**Best for**: Social networks, recommendation engines, knowledge graphs

## SQL Basics

### CRUD Operations

#### Create
```sql
INSERT INTO users (name, email) 
VALUES ('Alice', 'alice@example.com');
```

#### Read
```sql
-- Select all
SELECT * FROM users;

-- Select specific columns
SELECT name, email FROM users;

-- Filter with WHERE
SELECT * FROM users WHERE age > 18;

-- Join tables
SELECT users.name, posts.title
FROM users
JOIN posts ON users.id = posts.user_id;
```

#### Update
```sql
UPDATE users 
SET email = 'newemail@example.com'
WHERE id = 123;
```

#### Delete
```sql
DELETE FROM users WHERE id = 123;
```

### Filtering and Sorting
```sql
-- WHERE clause
SELECT * FROM users WHERE age >= 18 AND country = 'US';

-- ORDER BY
SELECT * FROM users ORDER BY created_at DESC;

-- LIMIT and OFFSET (pagination)
SELECT * FROM users LIMIT 10 OFFSET 20;
```

### Aggregation
```sql
-- Count
SELECT COUNT(*) FROM users;

-- Sum, Average, Min, Max
SELECT 
    COUNT(*) as total_users,
    AVG(age) as average_age,
    MIN(created_at) as first_user,
    MAX(created_at) as latest_user
FROM users;

-- Group By
SELECT country, COUNT(*) as user_count
FROM users
GROUP BY country
HAVING COUNT(*) > 100;
```

## Database Design

### Normalization
Organizing data to reduce redundancy.

**1NF (First Normal Form)**:
- Atomic values (no lists in cells)
- Unique column names
- No duplicate rows

**2NF (Second Normal Form)**:
- 1NF + No partial dependencies
- All non-key attributes depend on entire primary key

**3NF (Third Normal Form)**:
- 2NF + No transitive dependencies
- Non-key attributes depend only on primary key

### Relationships

#### One-to-Many
```sql
-- One user has many posts
CREATE TABLE users (id PRIMARY KEY, name);
CREATE TABLE posts (
    id PRIMARY KEY,
    user_id REFERENCES users(id),  -- Foreign key
    title
);
```

#### Many-to-Many
```sql
-- Users can like many posts, posts can be liked by many users
CREATE TABLE users (id PRIMARY KEY, name);
CREATE TABLE posts (id PRIMARY KEY, title);
CREATE TABLE likes (
    user_id REFERENCES users(id),
    post_id REFERENCES posts(id),
    PRIMARY KEY (user_id, post_id)
);
```

#### One-to-One
```sql
-- One user has one profile
CREATE TABLE users (id PRIMARY KEY, name);
CREATE TABLE profiles (
    user_id PRIMARY KEY REFERENCES users(id),
    bio TEXT,
    avatar_url VARCHAR(200)
);
```

## Indexes

Speed up queries by creating indexes on frequently queried columns.

```sql
-- Create index
CREATE INDEX idx_users_email ON users(email);

-- Composite index
CREATE INDEX idx_posts_user_date ON posts(user_id, created_at);

-- Unique index
CREATE UNIQUE INDEX idx_users_email_unique ON users(email);
```

**Trade-offs**:
- ✅ Faster reads
- ❌ Slower writes
- ❌ More storage space

## Transactions

Ensure data consistency with ACID properties.

```sql
BEGIN TRANSACTION;

UPDATE accounts SET balance = balance - 100 WHERE id = 1;
UPDATE accounts SET balance = balance + 100 WHERE id = 2;

COMMIT;  -- Or ROLLBACK if error
```

### ACID Properties
- **Atomicity**: All or nothing
- **Consistency**: Valid state always
- **Isolation**: Concurrent transactions don't interfere
- **Durability**: Committed data persists

## ORMs (Object-Relational Mapping)

### SQLAlchemy (Python)
```python
from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.orm import declarative_base, Session

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100))
    email = Column(String(100), unique=True)

# Usage
engine = create_engine('postgresql://localhost/mydb')
with Session(engine) as session:
    user = User(name="Alice", email="alice@example.com")
    session.add(user)
    session.commit()
```

## Best Practices

1. **Use indexes wisely**: On frequently queried columns
2. **Normalize appropriately**: Balance normalization vs performance
3. **Use transactions**: For related operations
4. **Validate data**: At application and database level
5. **Backup regularly**: Automate database backups
6. **Monitor performance**: Query execution time, slow query log
7. **Use connection pooling**: Reuse database connections
8. **Sanitize inputs**: Prevent SQL injection

## Common Pitfalls

❌ **N+1 Query Problem**
```python
# Bad - N+1 queries
users = session.query(User).all()
for user in users:
    posts = session.query(Post).filter_by(user_id=user.id).all()  # N queries!
```

✅ **Solution: Eager Loading**
```python
# Good - 1 query with join
users = session.query(User).options(joinedload(User.posts)).all()
```

## Related Concepts
- [[SQL Fundamentals]]
- [[Database Design]]
- [[Database Optimization]]
- [[NoSQL Databases]]
- [[Data Modeling]]

*Databases are the foundation of most applications - invest time in understanding them well.*
''',
        },
    ],
    "docker-containers": [
        {
            "title": "Docker Fundamentals",
            "folder": "development/tools",
            "content": r'''# Docker Fundamentals

Docker packages applications with their dependencies into containers for consistent deployment.

## Why Docker?

### The Problem
"It works on my machine!" - Different environments cause deployment issues.

### The Solution
Package application + dependencies + environment into a container that runs identically everywhere.

## Core Concepts

### Image
A blueprint for containers - read-only template with application and dependencies.

### Container
A running instance of an image - isolated, lightweight, and portable.

### Dockerfile
Instructions for building an image.

### Registry
Storage for Docker images (Docker Hub, GitHub Container Registry).

## Basic Commands

### Images
```bash
# Pull image from registry
docker pull python:3.12

# List images
docker images

# Build image from Dockerfile
docker build -t myapp:1.0 .

# Remove image
docker rmi myapp:1.0
```

### Containers
```bash
# Run container
docker run -d -p 8000:8000 --name myapp myapp:1.0

# List running containers
docker ps

# List all containers
docker ps -a

# Stop container
docker stop myapp

# Start stopped container
docker start myapp

# Remove container
docker rm myapp

# View logs
docker logs myapp
docker logs -f myapp  # Follow logs
```

## Dockerfile

### Basic Structure
```dockerfile
# Base image
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Copy requirements
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 8000

# Run application
CMD ["python", "app.py"]
```

### Multi-Stage Build (Smaller Images)
```dockerfile
# Build stage
FROM python:3.12 AS builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --user -r requirements.txt

# Runtime stage
FROM python:3.12-slim
WORKDIR /app
COPY --from=builder /root/.local /root/.local
COPY . .
ENV PATH=/root/.local/bin:$PATH
CMD ["python", "app.py"]
```

## Docker Compose

Manage multi-container applications.

### docker-compose.yml
```yaml
version: '3.8'

services:
  web:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://db:5432/myapp
    depends_on:
      - db
  
  db:
    image: postgres:15
    environment:
      - POSTGRES_PASSWORD=secret
      - POSTGRES_DB=myapp
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

### Commands
```bash
# Start all services
docker-compose up

# Start in background
docker-compose up -d

# Stop all services
docker-compose down

# View logs
docker-compose logs -f

# Rebuild images
docker-compose build

# Run command in service
docker-compose exec web python manage.py migrate
```

## Volumes

Persist data outside containers.

### Named Volumes
```bash
# Create volume
docker volume create mydata

# Use in container
docker run -v mydata:/app/data myapp

# List volumes
docker volume ls

# Remove volume
docker volume rm mydata
```

### Bind Mounts
```bash
# Mount local directory
docker run -v /path/on/host:/path/in/container myapp

# Development with live reload
docker run -v $(pwd):/app myapp
```

## Networking

### Container Communication
```bash
# Create network
docker network create mynetwork

# Run containers on network
docker run --network mynetwork --name web myapp
docker run --network mynetwork --name db postgres

# Containers can reach each other by name
# web can connect to: postgresql://db:5432
```

## Best Practices

1. **Use Official Images**: Start with official base images
2. **Minimize Layers**: Combine RUN commands
3. **Use .dockerignore**: Exclude unnecessary files
4. **Don't Run as Root**: Create non-root user
5. **Use Multi-Stage Builds**: Smaller final images
6. **Tag Images Properly**: Use semantic versioning
7. **Health Checks**: Monitor container health
8. **Environment Variables**: Configure via env vars

### Example .dockerignore
```
.git
.venv
__pycache__
*.pyc
.pytest_cache
.coverage
*.log
```

## Security

### Best Practices
```dockerfile
# Use specific versions, not 'latest'
FROM python:3.12-slim  # ✅ Specific

# Create non-root user
RUN useradd -m appuser
USER appuser  # ✅ Don't run as root

# Scan for vulnerabilities
# docker scan myapp:1.0
```

## Common Workflows

### Development
```bash
# Build and run locally
docker build -t myapp:dev .
docker run -p 8000:8000 -v $(pwd):/app myapp:dev

# Or with docker-compose
docker-compose up
```

### Production
```bash
# Build production image
docker build -t myapp:1.0 .

# Push to registry
docker tag myapp:1.0 registry.example.com/myapp:1.0
docker push registry.example.com/myapp:1.0

# Deploy
docker pull registry.example.com/myapp:1.0
docker run -d -p 80:8000 registry.example.com/myapp:1.0
```

## Troubleshooting

### Container Won't Start
```bash
# Check logs
docker logs container-name

# Run interactively
docker run -it myapp /bin/bash
```

### Permission Issues
```bash
# Run as specific user
docker run --user $(id -u):$(id -g) myapp
```

### Cleanup
```bash
# Remove stopped containers
docker container prune

# Remove unused images
docker image prune

# Remove everything unused
docker system prune -a
```

## Related Concepts
- [[Containerization]]
- [[Kubernetes Basics]]
- [[CI/CD Pipelines]]
- [[Microservices Architecture]]
- [[DevOps Practices]]

*Docker makes "it works on my machine" a thing of the past.*
''',
        },
    ],
    "clean-code": [
        {
            "title": "Clean Code Principles",
            "folder": "development/concepts",
            "content": r'''# Clean Code Principles

Clean code is code that is easy to read, understand, and maintain.

## Core Principles

### 1. Meaningful Names

**Variables**:
```python
# ❌ Bad
d = 86400  # What is d?
t = time.time()

# ✅ Good
seconds_per_day = 86400
current_timestamp = time.time()
```

**Functions**:
```python
# ❌ Bad
def proc(data):
    ...

# ✅ Good
def process_user_registration(user_data):
    ...
```

**Classes**:
```python
# ❌ Bad
class DM:  # Data Manager? Document Model?
    ...

# ✅ Good
class UserRepository:
    ...
```

### 2. Functions Should Do One Thing

```python
# ❌ Bad - Does too much
def process_order(order):
    validate_order(order)
    calculate_total(order)
    charge_payment(order)
    send_confirmation_email(order)
    update_inventory(order)

# ✅ Good - Orchestrates single-purpose functions
def process_order(order):
    if not is_valid_order(order):
        raise ValidationError()
    
    total = calculate_total(order)
    payment = charge_payment(order, total)
    send_confirmation(order, payment)
    update_inventory(order)
```

### 3. Small Functions

**Guideline**: Functions should be 5-15 lines, rarely more than 20.

```python
# ✅ Good - Small, focused
def calculate_discount(price: float, customer_type: str) -> float:
    if customer_type == "premium":
        return price * 0.2
    elif customer_type == "regular":
        return price * 0.1
    return 0.0
```

### 4. Don't Repeat Yourself (DRY)

```python
# ❌ Bad - Repetition
def format_user(user):
    return f"{user.first_name} {user.last_name} ({user.email})"

def format_admin(admin):
    return f"{admin.first_name} {admin.last_name} ({admin.email})"

# ✅ Good - Single implementation
def format_person(person):
    return f"{person.first_name} {person.last_name} ({person.email})"
```

### 5. Comments Explain Why, Not What

```python
# ❌ Bad - States the obvious
# Increment counter by 1
counter += 1

# ✅ Good - Explains reasoning
# Skip first row because it contains headers
data = rows[1:]

# ✅ Good - Explains non-obvious behavior
# Use exponential backoff to avoid overwhelming the API
time.sleep(2 ** retry_count)
```

## Code Organization

### File Structure
```
project/
├── src/
│   └── myapp/
│       ├── __init__.py
│       ├── models/      # Data structures
│       ├── services/    # Business logic
│       ├── repositories/  # Data access
│       ├── api/         # API endpoints
│       └── utils/       # Utilities
├── tests/
└── docs/
```

### Module Organization
```python
# ✅ Good - Logical grouping
# user_service.py
from .models import User
from .repositories import UserRepository
from .validators import validate_email

class UserService:
    def __init__(self, repo: UserRepository):
        self.repo = repo
    
    def create_user(self, email: str, name: str) -> User:
        if not validate_email(email):
            raise ValueError("Invalid email")
        return self.repo.create(email=email, name=name)
```

## Error Handling

### Be Specific
```python
# ❌ Bad - Catches everything
try:
    process_data()
except:
    pass

# ✅ Good - Specific exceptions
try:
    user = get_user(user_id)
except UserNotFoundError:
    return None
except DatabaseError as e:
    logger.error(f"Database error: {e}")
    raise
```

### Fail Fast
```python
# ✅ Good - Validate early
def process_user(user_id: int, email: str):
    if user_id <= 0:
        raise ValueError("Invalid user_id")
    if not email or "@" not in email:
        raise ValueError("Invalid email")
    
    # Now proceed with confidence
    ...
```

## Code Smells

### Long Parameter Lists
```python
# ❌ Bad
def create_user(first_name, last_name, email, phone, address, city, state, zip):
    ...

# ✅ Good - Use object
from dataclasses import dataclass

@dataclass
class UserData:
    first_name: str
    last_name: str
    email: str
    phone: str
    address: str
    city: str
    state: str
    zip_code: str

def create_user(data: UserData):
    ...
```

### Magic Numbers
```python
# ❌ Bad
if user.age > 18:
    ...

# ✅ Good
LEGAL_AGE = 18
if user.age > LEGAL_AGE:
    ...
```

### Nested Conditionals
```python
# ❌ Bad - Hard to follow
def process(user):
    if user:
        if user.is_active:
            if user.has_permission:
                if not user.is_banned:
                    return do_something()
    return None

# ✅ Good - Guard clauses
def process(user):
    if not user:
        return None
    if not user.is_active:
        return None
    if not user.has_permission:
        return None
    if user.is_banned:
        return None
    
    return do_something()
```

## Refactoring Techniques

### Extract Method
```python
# Before
def render_page(user):
    html = "<html><body>"
    html += f"<h1>Welcome {user.name}</h1>"
    html += f"<p>Email: {user.email}</p>"
    html += "</body></html>"
    return html

# After
def render_page(user):
    return (f"<html><body>"
            f"{render_header(user)}"
            f"{render_user_info(user)}"
            f"</body></html>")

def render_header(user):
    return f"<h1>Welcome {{user.name}}</h1>"

def render_user_info(user):
    return f"<p>Email: {{user.email}}</p>"
```

### Replace Conditional with Polymorphism
```python
# Before
def calculate_shipping(order_type, weight):
    if order_type == "standard":
        return weight * 0.5
    elif order_type == "express":
        return weight * 1.5
    elif order_type == "overnight":
        return weight * 3.0

# After
class ShippingMethod(ABC):
    @abstractmethod
    def calculate(self, weight): ...

class StandardShipping(ShippingMethod):
    def calculate(self, weight):
        return weight * 0.5

class ExpressShipping(ShippingMethod):
    def calculate(self, weight):
        return weight * 1.5
```

## Boy Scout Rule

> "Leave the code cleaner than you found it."

- Fix small issues when you see them
- Improve names while working nearby
- Extract duplicated code
- Add missing tests

## Related Concepts
- [[SOLID Principles]]
- [[Design Patterns]]
- [[Code Review Best Practices]]
- [[Refactoring Techniques]]
- [[Technical Debt]]

*Clean code is not about perfection - it's about clarity and maintainability.*
''',
        },
    ],
    "ci-cd": [
        {
            "title": "CI/CD Fundamentals",
            "folder": "development/devops",
            "content": r'''# CI/CD Fundamentals

Continuous Integration and Continuous Deployment automate software delivery.

## What is CI/CD?

### Continuous Integration (CI)
Automatically build and test code changes.

**Benefits**:
- Catch bugs early
- Reduce integration problems
- Faster feedback
- Improved code quality

### Continuous Deployment (CD)
Automatically deploy passing changes to production.

**Benefits**:
- Faster time to market
- Reduced deployment risk
- Consistent deployment process
- More frequent releases

## CI Pipeline Stages

### 1. Code Commit
Developer pushes code to repository.

### 2. Build
Compile code and create artifacts.

```yaml
# GitHub Actions example
- name: Build
  run: |
    uv sync --dev
    uv build
```

### 3. Test
Run automated tests.

```yaml
- name: Test
  run: |
    uv run pytest --cov=src
    uv run ruff check .
    uv run pyright
```

### 4. Security Scan
Check for vulnerabilities.

```yaml
- name: Security
  run: |
    uv run bandit -r src/
    uv run safety scan
```

### 5. Deploy
Deploy to staging or production.

```yaml
- name: Deploy
  if: github.ref == 'refs/heads/main'
  run: |
    docker build -t myapp:${{ github.sha }} .
    docker push myapp:${{ github.sha }}
```

## GitHub Actions

### Basic Workflow
```yaml
name: CI

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.12'
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
      
      - name: Run tests
        run: |
          pytest
```

### Matrix Testing
```yaml
strategy:
  matrix:
    python-version: ['3.10', '3.11', '3.12']
    os: [ubuntu-latest, windows-latest, macos-latest]

steps:
  - uses: actions/setup-python@v4
    with:
      python-version: ${{ matrix.python-version }}
```

## Best Practices

### 1. Fast Feedback
- Keep CI pipeline under 10 minutes
- Run fast tests first
- Parallelize when possible

### 2. Fail Fast
- Stop pipeline on first failure
- Don't waste resources on doomed builds

### 3. Reproducible Builds
- Use locked dependencies
- Pin tool versions
- Use containers for consistency

### 4. Comprehensive Testing
```yaml
jobs:
  lint:
    # Code quality checks
  
  test:
    # Unit and integration tests
  
  security:
    # Security scanning
  
  build:
    needs: [lint, test, security]
    # Build only if all pass
```

### 5. Automated Deployment

**Staging**: Deploy every commit to main
**Production**: Deploy on tag or manual approval

```yaml
deploy-staging:
  if: github.ref == 'refs/heads/main'
  # Auto-deploy to staging

deploy-production:
  if: startsWith(github.ref, 'refs/tags/v')
  # Deploy on version tag
```

## Deployment Strategies

### Blue-Green Deployment
- Two identical environments (blue and green)
- Deploy to inactive environment
- Switch traffic when ready
- Instant rollback if issues

### Canary Deployment
- Deploy to small subset of users first
- Monitor for issues
- Gradually increase traffic
- Rollback if problems detected

### Rolling Deployment
- Update instances gradually
- Always some instances available
- Slower but safer

## Monitoring and Rollback

### Health Checks
```python
@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "version": "1.0.0",
        "database": check_database(),
    }
```

### Automated Rollback
```yaml
- name: Deploy
  run: deploy.sh
  
- name: Health Check
  run: |
    sleep 30  # Wait for startup
    if ! curl -f http://app/health; then
      echo "Health check failed, rolling back"
      rollback.sh
      exit 1
    fi
```

## Common Tools

### CI Platforms
- **GitHub Actions**: Integrated with GitHub
- **GitLab CI**: Integrated with GitLab
- **Jenkins**: Self-hosted, highly customizable
- **CircleCI**: Cloud-based
- **Travis CI**: Popular for open source

### Deployment Tools
- **Docker**: Containerization
- **Kubernetes**: Container orchestration
- **Ansible**: Configuration management
- **Terraform**: Infrastructure as code

## Troubleshooting

### Build Failures
```bash
# Run locally first
docker build -t myapp .

# Check specific step
docker build --target builder -t myapp-builder .
```

### Test Failures
```bash
# Run tests locally
pytest -v

# Run specific test
pytest tests/test_module.py::test_function
```

### Deployment Issues
```bash
# Check logs
kubectl logs deployment/myapp

# Rollback
kubectl rollout undo deployment/myapp
```

## Related Concepts
- [[DevOps Practices]]
- [[Docker Fundamentals]]
- [[Automated Testing]]
- [[Infrastructure as Code]]
- [[Monitoring and Observability]]

*CI/CD is not about tools - it's about culture and practices that enable rapid, reliable delivery.*
''',
        },
    ],
    "debugging-performance": [
        {
            "title": "Debugging Techniques",
            "folder": "development/skills",
            "content": r'''# Debugging Techniques

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
''',
        },
        {
            "title": "Performance Optimization",
            "folder": "development/skills",
            "content": r'''# Performance Optimization

Making code faster and more efficient through systematic improvements.

## First Rule of Optimization

> "Premature optimization is the root of all evil." - Donald Knuth

**Steps**:
1. **Make it work**: Correct implementation first
2. **Make it right**: Clean, maintainable code
3. **Make it fast**: Optimize if needed

## Measurement First

### Don't Guess, Measure
```python
import time

start = time.time()
result = slow_function()
elapsed = time.time() - start
print(f"Took {elapsed:.2f} seconds")
```

### Profiling
Find actual bottlenecks.

```python
import cProfile
import pstats

# Profile code
cProfile.run('main()', 'output.prof')

# Analyze results
p = pstats.Stats('output.prof')
p.sort_stats('cumulative')
p.print_stats(10)  # Top 10 slowest functions
```

### Line Profiler
Find slow lines within functions.

```bash
pip install line_profiler

# Add @profile decorator to function
# Run: kernprof -l -v script.py
```

## Algorithmic Optimization

### Time Complexity

**O(1)** - Constant:
```python
def get_first(items):
    return items[0]  # Always same time
```

**O(n)** - Linear:
```python
def find_item(items, target):
    for item in items:  # Time grows with size
        if item == target:
            return item
```

**O(n²)** - Quadratic:
```python
def find_duplicates(items):
    for i in items:
        for j in items:  # Nested loops
            if i == j:
                ...
```

**O(log n)** - Logarithmic:
```python
def binary_search(sorted_items, target):
    # Halves search space each step
    ...
```

### Choose Right Data Structure

```python
# ❌ Slow: O(n) lookup
items = ['a', 'b', 'c', 'd', 'e']
if 'c' in items:  # Checks each item

# ✅ Fast: O(1) lookup
items = {'a', 'b', 'c', 'd', 'e'}  # Set
if 'c' in items:  # Hash lookup
```

### Use Built-in Functions
```python
# ❌ Slower
total = 0
for num in numbers:
    total += num

# ✅ Faster: Built-ins are optimized
total = sum(numbers)
```

## Python-Specific Optimizations

### List Comprehensions vs Loops
```python
# Slower
result = []
for x in range(1000):
    result.append(x * 2)

# Faster: List comprehension
result = [x * 2 for x in range(1000)]

# Fastest: Generator (if you don't need list)
result = (x * 2 for x in range(1000))
```

### Use Local Variables
```python
# Slower: Global lookup each time
def process_items(items):
    for item in items:
        result = math.sqrt(item)  # Global 'math' lookup

# Faster: Local reference
def process_items(items):
    sqrt = math.sqrt  # Cache locally
    for item in items:
        result = sqrt(item)
```

### String Concatenation
```python
# ❌ Slow: Creates new string each time
result = ""
for i in range(10000):
    result += str(i)

# ✅ Fast: Join is optimized
result = "".join(str(i) for i in range(10000))
```

## Database Optimization

### Index Key Columns
```sql
-- Create index on frequently queried columns
CREATE INDEX idx_users_email ON users(email);
```

### Avoid N+1 Queries
```python
# ❌ Slow: N+1 queries
users = session.query(User).all()
for user in users:
    posts = session.query(Post).filter_by(user_id=user.id).all()

# ✅ Fast: Single query with join
users = session.query(User).options(joinedload(User.posts)).all()
```

### Use Pagination
```python
# ❌ Slow: Loads everything
all_users = session.query(User).all()

# ✅ Fast: Load in chunks
page = session.query(User).limit(100).offset(0).all()
```

## Caching

### Function Results
```python
from functools import lru_cache

@lru_cache(maxsize=128)
def expensive_calculation(n):
    # Complex computation
    return result

# First call: computed
result1 = expensive_calculation(10)

# Second call: cached!
result2 = expensive_calculation(10)
```

### Database Queries
```python
# Use Redis for caching
import redis

cache = redis.Redis()

def get_user(user_id):
    # Try cache first
    cached = cache.get(f"user:{user_id}")
    if cached:
        return json.loads(cached)
    
    # Cache miss - query database
    user = db.query(User).get(user_id)
    cache.setex(f"user:{user_id}", 3600, json.dumps(user))
    return user
```

## Memory Optimization

### Use Generators
```python
# ❌ High memory: Loads everything
def read_large_file(path):
    return [line for line in open(path)]  # All in memory!

# ✅ Low memory: Yields one at a time
def read_large_file(path):
    with open(path) as f:
        for line in f:
            yield line.strip()

# Use with iteration
for line in read_large_file('huge.txt'):
    process(line)  # Only one line in memory at a time
```

### Use __slots__
```python
# Regular class
class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y
# Uses dynamic dict for attributes

# With __slots__
class Point:
    __slots__ = ['x', 'y']
    def __init__(self, x, y):
        self.x = x
        self.y = y
# Uses fixed structure - 40-50% less memory!
```

## Async for I/O Performance

### Concurrent Requests
```python
# ❌ Slow: Sequential
def fetch_all():
    results = []
    for url in urls:
        results.append(requests.get(url))  # Wait for each
    return results
# Time: sum of all requests

# ✅ Fast: Concurrent
async def fetch_all():
    async with aiohttp.ClientSession() as session:
        tasks = [session.get(url) for url in urls]
        return await asyncio.gather(*tasks)
# Time: longest single request
```

## Optimization Checklist

### Before Optimizing
- [ ] Profile to find bottleneck
- [ ] Measure current performance
- [ ] Set performance target
- [ ] Verify correctness first

### During Optimization
- [ ] Change one thing at a time
- [ ] Measure after each change
- [ ] Keep original code for comparison
- [ ] Document why optimized

### After Optimizing
- [ ] Verify still correct
- [ ] Check all tests pass
- [ ] Measure improvement
- [ ] Document trade-offs

## Common Optimizations

### Use Appropriate Data Structure
```python
# Finding items
items_list = [1, 2, 3, ..., 1000]  # O(n) lookup
items_set = {1, 2, 3, ..., 1000}   # O(1) lookup

# Counting occurrences
from collections import Counter
counts = Counter(items)  # Optimized counting
```

### Batch Operations
```python
# ❌ Slow: One at a time
for item in items:
    db.insert(item)  # 1000 database calls

# ✅ Fast: Bulk insert
db.bulk_insert(items)  # 1 database call
```

### Lazy Evaluation
```python
# Compute only when needed
class LazyProperty:
    def __init__(self, function):
        self.function = function
        self.name = function.__name__
    
    def __get__(self, obj, type=None):
        if obj is None:
            return self
        value = self.function(obj)
        setattr(obj, self.name, value)  # Cache result
        return value

class DataProcessor:
    @LazyProperty
    def expensive_calc(self):
        # Only computed when accessed
        return complex_computation()
```

## When NOT to Optimize

### Micro-Optimizations
```python
# Not worth it:
result = x * 2  # vs result = x << 1

# Focus on:
- Algorithm choice (O(n²) → O(n log n))
- I/O optimization
- Caching
- Database queries
```

### Readable Code > Slightly Faster Code
```python
# ❌ Faster but obscure
r = [i for i in range(1000) if i % 2 == 0 and i % 3 == 0 and i % 5 == 0]

# ✅ Slower but clear
def is_divisible_by_all(n, divisors):
    return all(n % d == 0 for d in divisors)

result = [i for i in range(1000) if is_divisible_by_all(i, [2, 3, 5])]
```

## Profiling Tools

### cProfile (Built-in)
```bash
python -m cProfile -o output.prof script.py
```

### memory_profiler
```bash
pip install memory_profiler
python -m memory_profiler script.py
```

### py-spy
```bash
pip install py-spy
py-spy record -o profile.svg -- python script.py
```

## Performance Testing

### Benchmark
```python
import timeit

# Compare implementations
time1 = timeit.timeit('sum(range(100))', number=10000)
time2 = timeit.timeit('[x for x in range(100)]', number=10000)

print(f"sum(): {time1:.4f}s")
print(f"list comp: {time2:.4f}s")
```

### Load Testing
```bash
# Apache Bench
ab -n 1000 -c 10 http://localhost:8000/

# Locust
locust -f locustfile.py
```

## Related Concepts
- [[Debugging Techniques]]
- [[Profiling Tools]]
- [[Algorithm Complexity]]
- [[Python Best Practices]]
- [[System Performance]]

*Measure first, optimize second - never guess where the bottleneck is.*
''',
        },
        {
            "title": "Code Review Best Practices",
            "folder": "development/skills",
            "content": r'''# Code Review Best Practices

Code review improves quality, shares knowledge, and catches issues before production.

## Why Code Review?

### Benefits
1. **Catch Bugs**: Fresh eyes find issues
2. **Share Knowledge**: Learn from each other
3. **Maintain Standards**: Consistent code quality
4. **Better Design**: Discuss architectural decisions
5. **Team Communication**: Async collaboration

## For Reviewers

### What to Look For

#### 1. Correctness
- Does code do what it claims?
- Are edge cases handled?
- Could this cause bugs?

#### 2. Design
- Is approach sound?
- Could this be simpler?
- Does it fit existing architecture?

#### 3. Complexity
- Is code unnecessarily complex?
- Could logic be clearer?
- Are abstractions appropriate?

#### 4. Tests
- Are there sufficient tests?
- Do tests cover edge cases?
- Are tests clear and maintainable?

#### 5. Naming
- Are names clear and descriptive?
- Is naming consistent with codebase?
- Could names be improved?

#### 6. Documentation
- Are complex parts explained?
- Is public API documented?
- Are assumptions stated?

### How to Give Feedback

#### Be Kind and Constructive
```
❌ "This code is terrible."
✅ "Consider extracting this into a separate function for clarity."

❌ "You don't know what you're doing."
✅ "This approach might have issues with X. What about trying Y?"
```

#### Be Specific
```
❌ "This could be better."
✅ "This function is doing 3 things. Consider splitting into:
    - validate_input()
    - process_data()
    - format_output()"
```

#### Explain Why
```
❌ "Use list comprehension."
✅ "List comprehension would be clearer and faster here:
    result = [x * 2 for x in items]"
```

#### Distinguish Must-Fix vs Nice-to-Have
```
🔴 "Blocking: This will cause data loss if user_id is None"
🟡 "Nit: Consider more descriptive variable name"
🟢 "Optional: Could extract this for reusability"
```

#### Praise Good Code
```
✅ "Great use of type hints here!"
✅ "Nice test coverage!"
✅ "This is much clearer than the previous approach."
```

### Review Checklist

- [ ] Read description/ticket
- [ ] Understand what code should do
- [ ] Review tests first (shows intended behavior)
- [ ] Review main code
- [ ] Check for security issues
- [ ] Verify documentation
- [ ] Run code locally if complex
- [ ] Approve or request changes

## For Authors

### Before Requesting Review

#### 1. Self-Review
- Read your own code like a reviewer
- Run linters and type checkers
- Ensure all tests pass
- Check diff for accidental changes

#### 2. Keep Changes Focused
```
❌ Bad PR: "Update user system, refactor database, add tests, fix bug"
✅ Good PR: "Add email validation to user registration"
```

#### 3. Write Clear Description
```markdown
## What
Add email validation to user registration

## Why
Prevent invalid emails from creating accounts

## How
- Added validate_email() function
- Updated UserService.create_user()
- Added tests for edge cases

## Testing
- All existing tests pass
- Added 5 new tests for validation
```

#### 4. Add Comments
Explain non-obvious code.

```python
# Use exponential backoff to avoid overwhelming API
# Starts at 1s, max 32s: 1, 2, 4, 8, 16, 32
delay = min(2 ** retry_count, 32)
time.sleep(delay)
```

### Responding to Feedback

#### Be Receptive
- Assume good intentions
- Ask clarifying questions
- Explain reasoning if you disagree
- Thank reviewers

#### Address All Comments
```
✅ "Fixed in commit abc123"
✅ "Good point! Changed to..."
✅ "I kept X because... Does this make sense?"
❌ Ignoring comments
```

#### Don't Take Personally
Code review is about code, not you.

## Review Etiquette

### Timing
- **Small changes**: Review within 1 day
- **Medium changes**: Within 2 days
- **Large changes**: Break into smaller PRs

### Communication
- Be respectful and professional
- Assume competence
- Focus on code, not person
- Explain reasoning

### Disagreements
1. Discuss the trade-offs
2. Consider both perspectives
3. Defer to team standards
4. Escalate if needed

## Types of Reviews

### Quick Review (<100 lines)
- 15-30 minutes
- Focus on correctness and obvious issues

### Standard Review (100-500 lines)
- 1-2 hours
- Thorough examination
- Test locally

### Large Review (500+ lines)
- Break into smaller reviews if possible
- Review in multiple sessions
- May need design discussion first

## Automated Checks

Let automation catch mechanical issues.

```yaml
# GitHub Actions
- name: Lint
  run: ruff check .

- name: Type Check
  run: pyright

- name: Tests
  run: pytest

- name: Security
  run: bandit -r src/
```

**Reviewers** can then focus on:
- Design decisions
- Business logic
- Architecture
- User experience

## Review Tools

### Features to Look For
- Side-by-side diff view
- Inline comments
- Approval workflow
- CI integration
- Conversation threading

### Popular Platforms
- **GitHub**: Pull Requests
- **GitLab**: Merge Requests
- **Bitbucket**: Pull Requests
- **Gerrit**: Change review
- **Phabricator**: Differential

## Metrics

### Useful Metrics
- Review turnaround time
- Comments per review
- Approval rate
- Post-review bug rate

### Avoid
- Lines of code reviewed (incentivizes superficial review)
- Number of comments (incentivizes nitpicking)

## Common Review Patterns

### Bike-Shedding
Spending time on trivial issues while missing important ones.

**Solution**: Focus on high-impact issues first, skip trivial style issues covered by linters.

### Approval Without Review
Rubber-stamping without actually reading.

**Solution**: Set expectations, require meaningful engagement.

### Blocking on Subjective Preferences
```
❌ "I don't like this variable name" (blocking)
✅ "Consider renaming for clarity" (suggestion)
```

## Related Concepts
- [[Pull Request Workflow]]
- [[Git Best Practices]]
- [[Clean Code Principles]]
- [[Team Communication]]
- [[Software Quality]]

*Good code review is collaborative, not adversarial - we're all trying to build better software.*
''',
        },
    ],
}


