# Clean Code Principles

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
