# Object-Oriented Programming

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
