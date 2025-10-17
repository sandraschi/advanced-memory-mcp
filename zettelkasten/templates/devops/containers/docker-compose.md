# Docker Compose

Docker Compose is a tool for defining and running multi-container Docker applications using YAML configuration.

## Why Docker Compose?

- [problem] Running multiple containers manually is tedious
- [solution] Define entire stack in one YAML file
- [benefit] Reproducible development environments

## Basic Structure

```yaml
version: '3.8'

services:
  web:
    build: ./web
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://db:5432/myapp
    depends_on:
      - db
    volumes:
      - ./web:/app

  db:
    image: postgres:15-alpine
    environment:
      - POSTGRES_DB=myapp
      - POSTGRES_PASSWORD=secret
    volumes:
      - postgres-data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

volumes:
  postgres-data:
```

## Essential Commands

```bash
# Start services
docker-compose up -d

# View logs
docker-compose logs -f service-name

# Stop services
docker-compose down

# Rebuild services
docker-compose up -d --build

# Scale services
docker-compose up -d --scale web=3

# Execute command in service
docker-compose exec web python manage.py migrate
```

## Common Patterns

### Web Application Stack
```yaml
services:
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
    depends_on:
      - web

  web:
    build: .
    environment:
      - REDIS_URL=redis://redis:6379
    depends_on:
      - db
      - redis

  db:
    image: postgres:15-alpine

  redis:
    image: redis:7-alpine
```

### Development vs Production

```yaml
# docker-compose.yml (base)
services:
  web:
    build: .
    environment:
      - NODE_ENV=development

# docker-compose.prod.yml (override)
services:
  web:
    environment:
      - NODE_ENV=production
    restart: always
```

```bash
# Development
docker-compose up

# Production
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

## Relations
- builds_on [[Docker Fundamentals]]
- enables [[Microservices Development]]
- related_to [[Kubernetes Basics]]
- used_for [[Local Development Environment]]

## Best Practices

1. **Use environment variables** for configuration
2. **Named volumes** for persistence
3. **Health checks** for service readiness
4. **Depends_on** for service ordering
5. **Resource limits** to prevent runaway containers

```yaml
services:
  web:
    deploy:
      resources:
        limits:
          cpus: '0.5'
          memory: 512M
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
```

*Docker Compose makes multi-container applications simple and reproducible.*
