# Database Fundamentals

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
