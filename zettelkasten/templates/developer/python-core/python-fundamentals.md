# Python Fundamentals

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
multiline = """\1
\2"""
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
