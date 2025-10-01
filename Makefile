.PHONY: help install dev-install test test-cov lint format type-check security clean build release docker-build docker-run docs pre-commit

# Default target
help:
	@echo "Available commands:"
	@echo "  install      - Install the package in development mode"
	@echo "  dev-install  - Install with all development dependencies"
	@echo "  test         - Run tests"
	@echo "  test-cov     - Run tests with coverage"
	@echo "  lint         - Run linting (ruff)"
	@echo "  format       - Format code (ruff)"
	@echo "  type-check   - Run type checking (mypy)"
	@echo "  security     - Run security checks (bandit, safety)"
	@echo "  clean        - Clean build artifacts"
	@echo "  build        - Build the package"
	@echo "  release      - Create a new release (patch/minor/major)"
	@echo "  docker-build - Build Docker image"
	@echo "  docker-run   - Run Docker container"
	@echo "  docs         - Build documentation"
	@echo "  pre-commit   - Run pre-commit hooks"

# Installation
install:
	uv pip install -e .

dev-install:
	uv sync --dev

# Testing
test:
	uv run pytest tests/

test-cov:
	uv run pytest --cov=src --cov-report=term-missing --cov-report=html tests/

# Code Quality
lint:
	uv run ruff check .

lint-fix:
	uv run ruff check --fix .

format:
	uv run ruff format .

format-check:
	uv run ruff format --check .

type-check:
	uv run mypy src/

# Security
security:
	@echo "Running security checks..."
	uv run bandit -r src/ -f json -o bandit-report.json
	uv run safety check --json --output safety-report.json
	@echo "Security reports generated: bandit-report.json, safety-report.json"

# Cleaning
clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .coverage
	rm -rf htmlcov/
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	find . -type d -name __pycache__ -delete
	find . -type f -name "*.pyc" -delete

# Building
build:
	uv build

# Release Management
release-patch:
	uv run python scripts/release.py patch

release-minor:
	uv run python scripts/release.py minor

release-major:
	uv run python scripts/release.py major

release-dry-run:
	uv run python scripts/release.py patch --dry-run

# Docker
docker-build:
	docker build -t advanced-memory:latest .

docker-run:
	docker run -it --rm -p 8000:8000 \
		-v $(shell pwd)/data:/app/data \
		advanced-memory:latest

# Documentation
docs:
	@echo "Documentation build placeholder"
	@echo "Would build docs here..."

# Pre-commit
pre-commit:
	uv run pre-commit run --all-files
