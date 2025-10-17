# Docker Fundamentals

Docker is a platform for developing, shipping, and running applications in containers.

## What is a Container?

A container is a standardized unit of software that packages code and all its dependencies so the application runs quickly and reliably across computing environments.

- [definition] Container: Lightweight, standalone executable package with everything needed to run software
- [benefit] Consistency across development, testing, and production environments
- [principle] "Build once, run anywhere" philosophy

## Core Concepts

### Images vs Containers
```dockerfile
# Image: Blueprint/template (immutable)
# Container: Running instance of an image (ephemeral)

# Build an image
docker build -t myapp:1.0 .

# Run a container from image
docker run -d -p 8080:80 myapp:1.0
```

- [concept] Image: Read-only template with application and dependencies
- [concept] Container: Runtime instance with writable layer

### Dockerfile Structure
```dockerfile
# Base image
FROM python:3.12-slim

# Working directory
WORKDIR /app

# Copy dependencies
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Expose port
EXPOSE 8000

# Run command
CMD ["python", "app.py"]
```

- [best-practice] Use specific base image tags, not `latest`
- [best-practice] Minimize layers by combining RUN commands
- [best-practice] Use .dockerignore to exclude unnecessary files

## Essential Commands

```bash
# Build image
docker build -t app-name:tag .

# Run container
docker run -d -p host:container app-name:tag

# List containers
docker ps -a

# View logs
docker logs container-id

# Stop container
docker stop container-id

# Remove container
docker rm container-id

# Remove image
docker rmi image-id
```

## Multi-Stage Builds

```dockerfile
# Build stage
FROM node:18 AS builder
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

# Production stage
FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

- [optimization] Multi-stage builds reduce final image size
- [benefit] Separate build dependencies from runtime dependencies

## Relations
- enables [[Docker Compose]]
- enables [[Container Orchestration]]
- related_to [[Kubernetes Basics]]
- builds_on [[Linux Fundamentals]]

## Best Practices

1. **Image Size Optimization**
   - Use Alpine Linux base images
   - Multi-stage builds
   - Minimize layers

2. **Security**
   - Don't run as root
   - Scan images for vulnerabilities
   - Use trusted base images

3. **Efficiency**
   - Leverage build cache
   - Order Dockerfile instructions wisely
   - Use .dockerignore

*Docker revolutionized software deployment - master it to ship faster and more reliably.*
