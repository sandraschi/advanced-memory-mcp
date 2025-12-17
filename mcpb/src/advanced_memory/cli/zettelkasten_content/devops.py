"""DevOps Engineer Zettelkasten Templates - Comprehensive infrastructure and automation notes."""

DEVOPS_TEMPLATES = {
    "containers": [
        {
            "title": "Docker Fundamentals",
            "folder": "devops/containers",
            "content": r"""# Docker Fundamentals

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
""",
        },
        {
            "title": "Docker Compose",
            "folder": "devops/containers",
            "content": r"""# Docker Compose

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
""",
        },
        {
            "title": "Kubernetes Basics",
            "folder": "devops/kubernetes",
            "content": r"""# Kubernetes Basics

Kubernetes (K8s) is an open-source container orchestration platform for automating deployment, scaling, and management of containerized applications.

## Core Concepts

### Cluster Architecture

```mermaid
graph TB
    Master[Control Plane]
    Master --> API[API Server]
    Master --> Sched[Scheduler]
    Master --> CM[Controller Manager]
    Master --> etcd[etcd]

    Worker1[Worker Node 1]
    Worker2[Worker Node 2]

    Worker1 --> Kubelet1[Kubelet]
    Worker1 --> Proxy1[Kube-proxy]
    Worker1 --> Pod1[Pods]

    Worker2 --> Kubelet2[Kubelet]
    Worker2 --> Proxy2[Kube-proxy]
    Worker2 --> Pod2[Pods]
```

- [definition] Control Plane: Manages the Kubernetes cluster
- [definition] Worker Nodes: Run containerized applications
- [component] API Server: Frontend for K8s control plane
- [component] Scheduler: Assigns pods to nodes
- [component] etcd: Distributed key-value store for cluster data

### Pods

Smallest deployable unit in Kubernetes - one or more containers that share network and storage.

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: nginx-pod
  labels:
    app: nginx
spec:
  containers:
  - name: nginx
    image: nginx:1.25
    ports:
    - containerPort: 80
```

- [definition] Pod: Wrapper around one or more containers
- [characteristic] Pods are ephemeral and replaceable
- [pattern] Usually one container per pod (sidecar pattern for multiple)

### Deployments

Manage replica sets and provide declarative updates for Pods.

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nginx-deployment
spec:
  replicas: 3
  selector:
    matchLabels:
      app: nginx
  template:
    metadata:
      labels:
        app: nginx
    spec:
      containers:
      - name: nginx
        image: nginx:1.25
        ports:
        - containerPort: 80
```

- [benefit] Automatic scaling and self-healing
- [feature] Rolling updates with zero downtime
- [feature] Rollback capabilities

### Services

Expose applications running in Pods to network traffic.

```yaml
apiVersion: v1
kind: Service
metadata:
  name: nginx-service
spec:
  type: LoadBalancer
  selector:
    app: nginx
  ports:
  - port: 80
    targetPort: 80
```

Service Types:
- **ClusterIP**: Internal cluster access only (default)
- **NodePort**: Exposes on each Node's IP at a static port
- **LoadBalancer**: Cloud load balancer
- **ExternalName**: Maps service to DNS name

## Essential kubectl Commands

```bash
# Get resources
kubectl get pods
kubectl get deployments
kubectl get services

# Describe resource
kubectl describe pod pod-name

# View logs
kubectl logs pod-name

# Execute command in pod
kubectl exec -it pod-name -- /bin/bash

# Apply configuration
kubectl apply -f deployment.yaml

# Delete resources
kubectl delete -f deployment.yaml

# Port forwarding
kubectl port-forward pod-name 8080:80
```

## Relations
- builds_on [[Docker Fundamentals]]
- enables [[Container Orchestration]]
- related_to [[Helm Package Manager]]
- used_with [[CI/CD Pipelines]]

## Key Benefits

1. **Self-healing**: Automatically restarts failed containers
2. **Horizontal scaling**: Scale up/down based on demand
3. **Load balancing**: Distribute traffic across pods
4. **Rolling updates**: Deploy without downtime
5. **Service discovery**: Automatic DNS for services

*Kubernetes is complex but essential for modern cloud-native applications.*
""",
        },
    ],
    "cicd": [
        {
            "title": "CI/CD Fundamentals",
            "folder": "devops/cicd",
            "content": r"""# CI/CD Fundamentals

Continuous Integration and Continuous Delivery/Deployment automate software delivery pipelines.

## Definitions

- [definition] **Continuous Integration (CI)**: Automatically build and test code changes
- [definition] **Continuous Delivery (CD)**: Automatically deploy to staging/pre-production
- [definition] **Continuous Deployment (CD)**: Automatically deploy to production

## CI/CD Pipeline Stages

```mermaid
graph LR
    A[Code Commit] --> B[Build]
    B --> C[Test]
    C --> D[Security Scan]
    D --> E[Deploy Staging]
    E --> F{Manual Approval}
    F -->|Approved| G[Deploy Production]
    F -->|Rejected| H[Rollback]
```

### 1. Build Stage
- Compile code
- Create artifacts
- Build Docker images

### 2. Test Stage
- Unit tests
- Integration tests
- End-to-end tests
- Code quality checks (linting, formatting)

### 3. Security Stage
- Dependency scanning
- Container image scanning
- SAST (Static Application Security Testing)
- License compliance

### 4. Deploy Stage
- Deploy to environments (dev, staging, production)
- Database migrations
- Configuration management

## Popular CI/CD Tools

### GitHub Actions
```yaml
name: CI/CD Pipeline

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  build-and-test:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v4

    - name: Set up Python
      uses: actions/setup-python@v5
      with:
        python-version: '3.12'

    - name: Install dependencies
      run: |
        pip install -r requirements.txt

    - name: Run tests
      run: |
        pytest

    - name: Build Docker image
      run: |
        docker build -t myapp:${{ github.sha }} .

    - name: Deploy
      if: github.ref == 'refs/heads/main'
      run: |
        # Deploy to production
        kubectl apply -f k8s/
```

### GitLab CI
```yaml
stages:
  - build
  - test
  - deploy

build:
  stage: build
  script:
    - docker build -t $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA .
    - docker push $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA

test:
  stage: test
  script:
    - pytest

deploy:
  stage: deploy
  script:
    - kubectl apply -f k8s/
  only:
    - main
```

## Best Practices

### 1. Fast Feedback
- Keep builds under 10 minutes
- Run fast tests first
- Parallelize test execution

### 2. Build Once, Deploy Many
- Build artifacts once, deploy to all environments
- Use same Docker image across environments
- Environment-specific configuration via env vars

### 3. Security in Pipeline
- Scan dependencies for vulnerabilities
- Scan Docker images
- Enforce code signing
- No secrets in code

### 4. Immutable Artifacts
- Tag builds with version/commit SHA
- Store artifacts in registry
- Never modify artifacts after build

### 5. Automated Testing
- Unit tests: Fast, isolated
- Integration tests: Multiple components
- E2E tests: Full user workflows
- Minimum 80% code coverage

## Deployment Strategies

### Blue-Green Deployment
- [strategy] Run two identical production environments
- [benefit] Zero downtime, instant rollback
- [process] Switch traffic from blue to green

### Canary Deployment
- [strategy] Gradually roll out to subset of users
- [benefit] Test in production with limited risk
- [process] Monitor metrics, increase traffic if healthy

### Rolling Deployment
- [strategy] Gradually replace old version with new
- [benefit] No downtime, controlled rollout
- [process] Update pods one at a time

## Relations
- enables [[Continuous Integration]]
- enables [[Continuous Deployment]]
- uses [[Docker Fundamentals]]
- uses [[Kubernetes Basics]]
- related_to [[DevOps Culture]]

## Metrics to Track

- **Build Success Rate**: % of builds that pass
- **Build Duration**: Time from commit to deployable artifact
- **Deployment Frequency**: How often deploying to production
- **Lead Time**: Time from commit to production
- **MTTR**: Mean time to recovery from failures
- **Change Failure Rate**: % of deployments causing incidents

*CI/CD is the backbone of modern software delivery - automate everything!*
""",
        },
    ],
    "infrastructure": [
        {
            "title": "Infrastructure as Code",
            "folder": "devops/infrastructure",
            "content": r"""# Infrastructure as Code (IaC)

Infrastructure as Code manages and provisions infrastructure through machine-readable definition files rather than manual configuration.

## Core Principles

- [definition] IaC: Managing infrastructure using code and version control
- [principle] **Declarative over Imperative**: Describe what you want, not how to create it
- [principle] **Idempotent**: Running multiple times produces same result
- [principle] **Version Controlled**: Infrastructure changes tracked in Git

## Benefits

1. **Reproducibility**: Create identical environments reliably
2. **Speed**: Provision infrastructure in minutes
3. **Documentation**: Code is self-documenting
4. **Collaboration**: Team can review infrastructure changes
5. **Disaster Recovery**: Rebuild infrastructure from code

## Popular IaC Tools

### Terraform

```hcl
# Configure provider
provider "aws" {
  region = "us-west-2"
}

# Define resources
resource "aws_instance" "web" {
  ami           = "ami-0c55b159cbfafe1f0"
  instance_type = "t3.micro"

  tags = {
    Name = "WebServer"
    Environment = "Production"
  }
}

resource "aws_s3_bucket" "data" {
  bucket = "my-app-data-bucket"

  versioning {
    enabled = true
  }
}

# Output values
output "instance_ip" {
  value = aws_instance.web.public_ip
}
```

- [tool] Terraform: Cloud-agnostic IaC tool
- [benefit] Works with AWS, Azure, GCP, and 100+ providers
- [feature] Plan before apply to preview changes

### Terraform Workflow
```bash
# Initialize
terraform init

# Preview changes
terraform plan

# Apply changes
terraform apply

# Destroy resources
terraform destroy
```

### CloudFormation (AWS)

```yaml
Resources:
  WebServer:
    Type: AWS::EC2::Instance
    Properties:
      ImageId: ami-0c55b159cbfafe1f0
      InstanceType: t3.micro
      Tags:
        - Key: Name
          Value: WebServer

  DataBucket:
    Type: AWS::S3::Bucket
    Properties:
      BucketName: my-app-data-bucket
      VersioningConfiguration:
        Status: Enabled

Outputs:
  InstanceIP:
    Value: !GetAtt WebServer.PublicIp
```

- [tool] CloudFormation: AWS-specific IaC service
- [benefit] Deep AWS integration
- [feature] Automatic rollback on errors

## State Management

### Terraform State
- [concept] State file tracks real infrastructure
- [best-practice] Store state remotely (S3, Terraform Cloud)
- [warning] Never manually edit state file
- [security] Encrypt state (may contain secrets)

```hcl
# Remote state configuration
terraform {
  backend "s3" {
    bucket = "my-terraform-state"
    key    = "prod/terraform.tfstate"
    region = "us-west-2"
    encrypt = true
  }
}
```

## Modules and Reusability

```hcl
# Module definition (modules/web-server/main.tf)
variable "instance_type" {
  type    = string
  default = "t3.micro"
}

resource "aws_instance" "server" {
  ami           = var.ami_id
  instance_type = var.instance_type
}

# Using module
module "web_server" {
  source        = "./modules/web-server"
  instance_type = "t3.small"
}
```

- [best-practice] Create reusable modules for common patterns
- [benefit] DRY (Don't Repeat Yourself) principle
- [organization] Separate modules for different components

## Relations
- builds_on [[DevOps Culture]]
- uses [[Terraform]]
- uses [[CloudFormation]]
- enables [[Immutable Infrastructure]]
- related_to [[Configuration Management]]

## Best Practices

1. **Version Control Everything**
   - All IaC code in Git
   - Review infrastructure changes via PRs
   - Tag releases

2. **Separate Environments**
   - Different state files per environment
   - Use workspaces or separate configurations
   - Never share state between environments

3. **Security**
   - Encrypt state files
   - Use secrets management (AWS Secrets Manager, Vault)
   - Least privilege IAM policies
   - Scan for security issues

4. **Testing**
   - Validate syntax before apply
   - Test in dev environment first
   - Use terraform plan extensively
   - Automated compliance checks

5. **Documentation**
   - README for each module
   - Variable descriptions
   - Output documentation
   - Architecture diagrams

*Treat infrastructure like code - version it, test it, review it.*
""",
        },
    ],
    "monitoring": [
        {
            "title": "Monitoring and Observability",
            "folder": "devops/monitoring",
            "content": r"""# Monitoring and Observability

Monitoring and observability help you understand system behavior and quickly identify issues.

## Three Pillars of Observability

### 1. Metrics
Numerical measurements over time.

```yaml
# Prometheus metrics example
http_requests_total{method="GET", status="200"} 1234
response_time_seconds{endpoint="/api/users"} 0.145
cpu_usage_percent{instance="web-1"} 65.2
```

- [definition] Metrics: Time-series numerical data
- [example] CPU usage, request rate, error rate, response time
- [tool] Prometheus: Industry-standard metrics collection

### 2. Logs
Discrete events with timestamps and details.

```json
{
  "timestamp": "2025-10-16T10:30:00Z",
  "level": "ERROR",
  "service": "api",
  "message": "Database connection failed",
  "error": "connection timeout",
  "request_id": "abc123"
}
```

- [definition] Logs: Timestamped event records
- [benefit] Detailed context for debugging
- [tool] ELK Stack (Elasticsearch, Logstash, Kibana)

### 3. Traces
End-to-end request flows through distributed systems.

```
Request ID: abc123
├─ API Gateway (10ms)
├─ Auth Service (50ms)
├─ User Service (120ms)
│  ├─ Database Query (80ms)
│  └─ Cache Hit (2ms)
└─ Response (5ms)
Total: 185ms
```

- [definition] Tracing: Request path through microservices
- [benefit] Identify bottlenecks in distributed systems
- [tool] Jaeger, Zipkin for distributed tracing

## Monitoring Stack

### Prometheus + Grafana

```yaml
# Prometheus config
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'api-service'
    static_configs:
      - targets: ['api:8080']
```

```python
# Instrument Python application
from prometheus_client import Counter, Histogram, start_http_server

# Define metrics
requests_total = Counter('requests_total', 'Total HTTP requests')
request_duration = Histogram('request_duration_seconds', 'Request duration')

# Use in application
@app.route('/api/endpoint')
def endpoint():
    requests_total.inc()
    with request_duration.time():
        # Handle request
        return {"status": "ok"}
```

## Key Metrics to Monitor

### Application Metrics
- **Request Rate**: Requests per second
- **Error Rate**: Errors per second or percentage
- **Response Time**: P50, P95, P99 latencies
- **Saturation**: Resource utilization (CPU, memory, disk)

### Infrastructure Metrics
- **CPU Usage**: Per container/node
- **Memory Usage**: Current and trends
- **Disk I/O**: Read/write rates
- **Network Traffic**: In/out bandwidth

### Business Metrics
- **Active Users**: Current concurrent users
- **Conversion Rate**: Feature usage metrics
- **Revenue**: Per service/feature

## Alerting Best Practices

```yaml
# Prometheus alert rule
groups:
  - name: api-alerts
    rules:
      - alert: HighErrorRate
        expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.05
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "High error rate on {{ $labels.instance }}"
```

- [principle] **Alert on Symptoms, Not Causes**: Alert on user impact
- [best-practice] Avoid alert fatigue - only critical alerts
- [pattern] On-call rotation for alert handling

## SLIs, SLOs, and SLAs

- **SLI (Service Level Indicator)**: Quantitative measure (e.g., 99.9% uptime)
- **SLO (Service Level Objective)**: Target value for SLI
- **SLA (Service Level Agreement)**: Contract with consequences

Example:
- SLI: Request success rate
- SLO: 99.95% of requests succeed
- SLA: Credits if below 99.9%

## Relations
- builds_on [[DevOps Culture]]
- uses [[Prometheus]]
- uses [[Grafana]]
- related_to [[Incident Management]]
- enables [[Site Reliability Engineering]]

## Observability vs Monitoring

- [monitoring] **Known Unknowns**: Alert on expected failures
- [observability] **Unknown Unknowns**: Explore and understand novel failures

*You can't improve what you don't measure - monitor everything!*
""",
        },
    ],
}
