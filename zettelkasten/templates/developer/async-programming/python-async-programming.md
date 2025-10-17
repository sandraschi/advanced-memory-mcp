# Python Async Programming

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
