# Python Testing

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
