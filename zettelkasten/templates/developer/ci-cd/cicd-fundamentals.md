# CI/CD Fundamentals

Continuous Integration and Continuous Deployment automate software delivery.

## What is CI/CD?

### Continuous Integration (CI)
Automatically build and test code changes.

**Benefits**:
- Catch bugs early
- Reduce integration problems
- Faster feedback
- Improved code quality

### Continuous Deployment (CD)
Automatically deploy passing changes to production.

**Benefits**:
- Faster time to market
- Reduced deployment risk
- Consistent deployment process
- More frequent releases

## CI Pipeline Stages

### 1. Code Commit
Developer pushes code to repository.

### 2. Build
Compile code and create artifacts.

```yaml
# GitHub Actions example
- name: Build
  run: |
    uv sync --dev
    uv build
```

### 3. Test
Run automated tests.

```yaml
- name: Test
  run: |
    uv run pytest --cov=src
    uv run ruff check .
    uv run pyright
```

### 4. Security Scan
Check for vulnerabilities.

```yaml
- name: Security
  run: |
    uv run bandit -r src/
    uv run safety scan
```

### 5. Deploy
Deploy to staging or production.

```yaml
- name: Deploy
  if: github.ref == 'refs/heads/main'
  run: |
    docker build -t myapp:${{ github.sha }} .
    docker push myapp:${{ github.sha }}
```

## GitHub Actions

### Basic Workflow
```yaml
name: CI

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.12'

      - name: Install dependencies
        run: |
          pip install -r requirements.txt

      - name: Run tests
        run: |
          pytest
```

### Matrix Testing
```yaml
strategy:
  matrix:
    python-version: ['3.10', '3.11', '3.12']
    os: [ubuntu-latest, windows-latest, macos-latest]

steps:
  - uses: actions/setup-python@v4
    with:
      python-version: ${{ matrix.python-version }}
```

## Best Practices

### 1. Fast Feedback
- Keep CI pipeline under 10 minutes
- Run fast tests first
- Parallelize when possible

### 2. Fail Fast
- Stop pipeline on first failure
- Don't waste resources on doomed builds

### 3. Reproducible Builds
- Use locked dependencies
- Pin tool versions
- Use containers for consistency

### 4. Comprehensive Testing
```yaml
jobs:
  lint:
    # Code quality checks

  test:
    # Unit and integration tests

  security:
    # Security scanning

  build:
    needs: [lint, test, security]
    # Build only if all pass
```

### 5. Automated Deployment

**Staging**: Deploy every commit to main
**Production**: Deploy on tag or manual approval

```yaml
deploy-staging:
  if: github.ref == 'refs/heads/main'
  # Auto-deploy to staging

deploy-production:
  if: startsWith(github.ref, 'refs/tags/v')
  # Deploy on version tag
```

## Deployment Strategies

### Blue-Green Deployment
- Two identical environments (blue and green)
- Deploy to inactive environment
- Switch traffic when ready
- Instant rollback if issues

### Canary Deployment
- Deploy to small subset of users first
- Monitor for issues
- Gradually increase traffic
- Rollback if problems detected

### Rolling Deployment
- Update instances gradually
- Always some instances available
- Slower but safer

## Monitoring and Rollback

### Health Checks
```python
@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "version": "1.0.0",
        "database": check_database(),
    }
```

### Automated Rollback
```yaml
- name: Deploy
  run: deploy.sh

- name: Health Check
  run: |
    sleep 30  # Wait for startup
    if ! curl -f http://app/health; then
      echo "Health check failed, rolling back"
      rollback.sh
      exit 1
    fi
```

## Common Tools

### CI Platforms
- **GitHub Actions**: Integrated with GitHub
- **GitLab CI**: Integrated with GitLab
- **Jenkins**: Self-hosted, highly customizable
- **CircleCI**: Cloud-based
- **Travis CI**: Popular for open source

### Deployment Tools
- **Docker**: Containerization
- **Kubernetes**: Container orchestration
- **Ansible**: Configuration management
- **Terraform**: Infrastructure as code

## Troubleshooting

### Build Failures
```bash
# Run locally first
docker build -t myapp .

# Check specific step
docker build --target builder -t myapp-builder .
```

### Test Failures
```bash
# Run tests locally
pytest -v

# Run specific test
pytest tests/test_module.py::test_function
```

### Deployment Issues
```bash
# Check logs
kubectl logs deployment/myapp

# Rollback
kubectl rollout undo deployment/myapp
```

## Related Concepts
- [[DevOps Practices]]
- [[Docker Fundamentals]]
- [[Automated Testing]]
- [[Infrastructure as Code]]
- [[Monitoring and Observability]]

*CI/CD is not about tools - it's about culture and practices that enable rapid, reliable delivery.*
