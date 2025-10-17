# Performance Optimization

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
