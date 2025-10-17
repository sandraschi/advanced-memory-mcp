# Docker Fundamentals

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
