# RESTful API Design

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
