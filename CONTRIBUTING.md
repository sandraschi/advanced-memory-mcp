# Contributing to Advanced Memory MCP

Thank you for your interest in contributing to Advanced Memory MCP! 🎉

## 📋 Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Contributing Guidelines](#contributing-guidelines)
- [Pull Request Process](#pull-request-process)
- [Issue Reporting](#issue-reporting)
- [Development Workflow](#development-workflow)
- [Testing](#testing)
- [Documentation](#documentation)
- [Release Process](#release-process)

## 🤝 Code of Conduct

This project and everyone participating in it is governed by our [Code of Conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code.

## 🚀 Getting Started

### Prerequisites

- Python 3.11+ (3.12+ recommended)
- [uv](https://docs.astral.sh/uv/) for dependency management
- Git
- Node.js 18+ (for MCPB package development)

### Quick Setup

1. **Fork the repository**
   ```bash
   git clone https://github.com/sandraschi/advanced-memory-mcp.git
   cd advanced-memory-mcp
   ```

2. **Install dependencies**
   ```bash
   uv sync --dev
   ```

3. **Run tests**
   ```bash
   uv run pytest
   ```

4. **Install pre-commit hooks**
   ```bash
   uv run pre-commit install
   ```

## 🛠️ Development Setup

### Project Structure

```
advanced-memory-mcp/
├── src/advanced_memory/          # Main source code
│   ├── mcp/                      # MCP server implementation
│   │   ├── tools/                # MCP tools (individual + portmanteau)
│   │   └── server.py             # FastMCP server setup
│   ├── api/                      # FastAPI endpoints
│   ├── services/                 # Business logic
│   └── models/                   # Database models
├── tests/                        # Test suite
├── prompts/                      # Prompt templates
├── server/                       # MCPB package server files
├── docs/                         # Documentation
└── .github/                      # GitHub workflows and templates
```

### Environment Variables

Create a `.env` file in the project root:

```bash
# Development settings
DEBUG=true
LOG_LEVEL=DEBUG

# Database (for testing)
DATABASE_URL=sqlite:///./test.db

# Project settings
DEFAULT_PROJECT_PATH=./test-projects
```

## 📝 Contributing Guidelines

### Types of Contributions

We welcome several types of contributions:

- 🐛 **Bug fixes**
- ✨ **New features**
- 📚 **Documentation improvements**
- 🧪 **Test coverage**
- 🔧 **Performance optimizations**
- 🎨 **UI/UX improvements**

### Code Style

We follow these coding standards:

- **Python**: Follow PEP 8, use type hints, format with `ruff`
- **Line length**: 100 characters maximum
- **Imports**: Group imports (standard, third-party, local)
- **Naming**: `snake_case` for functions/variables, `PascalCase` for classes
- **Documentation**: Docstrings for all public functions

### Commit Messages

We use [Conventional Commits](https://www.conventionalcommits.org/):

```
type(scope): description

feat(content): add new portmanteau tool for content management
fix(export): resolve issue with PDF export on Windows
docs: update installation guide
test: add unit tests for portmanteau tools
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

## 🔄 Pull Request Process

### Before Submitting

1. **Check existing issues and PRs**
2. **Create an issue** if you're proposing a major change
3. **Fork the repository** and create a feature branch
4. **Make your changes** following our coding standards
5. **Add tests** for new functionality
6. **Update documentation** as needed
6. **Run the test suite** and ensure all tests pass

### PR Requirements

- [ ] **Title follows conventional commits format**
- [ ] **Description includes all required sections**
- [ ] **Tests pass** (unit, integration, linting)
- [ ] **Code coverage** maintained or improved
- [ ] **Documentation updated** (if applicable)
- [ ] **Breaking changes** documented
- [ ] **Self-review** completed

### PR Template

We provide a comprehensive PR template. Please fill out all sections:

- **Description**: What does this PR do?
- **Related Issues**: Link to relevant issues
- **Type of Change**: Bug fix, feature, etc.
- **Testing**: How was this tested?
- **Checklist**: All items completed

## 🐛 Issue Reporting

### Before Creating an Issue

1. **Search existing issues** to avoid duplicates
2. **Check documentation** and troubleshooting guides
3. **Try the latest version** to ensure it's not already fixed

### Issue Templates

We provide several issue templates:

- **Bug Report**: For reporting bugs
- **Feature Request**: For suggesting new features
- **Question**: For asking questions
- **Installation Issue**: For setup problems
- **Performance Issue**: For performance problems
- **Compatibility Issue**: For compatibility problems

### Issue Guidelines

- **Use descriptive titles**
- **Provide detailed information**
- **Include reproduction steps**
- **Share system information**
- **Add screenshots** when helpful

## 🔄 Development Workflow

### Branch Strategy

- `main`: Production-ready code
- `develop`: Integration branch for features
- `feature/*`: Feature branches
- `fix/*`: Bug fix branches
- `docs/*`: Documentation branches

### Development Process

1. **Create feature branch** from `develop`
2. **Make changes** with frequent commits
3. **Write tests** for new functionality
4. **Update documentation**
5. **Create pull request** to `develop`
6. **Address review feedback**
7. **Merge to develop** after approval

### Code Review Process

- **Automated checks** must pass (CI/CD pipeline)
- **At least one review** required for core changes
- **Maintainer approval** for breaking changes
- **Documentation review** for user-facing changes

## 🧪 Testing

### Test Structure

```
tests/
├── unit/                    # Unit tests
├── integration/             # Integration tests
├── mcp/                     # MCP tool tests
├── api/                     # API tests
└── fixtures/                # Test fixtures
```

### Running Tests

```bash
# Run all tests
uv run pytest

# Run specific test categories
uv run pytest tests/unit/
uv run pytest tests/integration/
uv run pytest tests/mcp/

# Run with coverage
uv run pytest --cov=src/advanced_memory --cov-report=html

# Run specific test
uv run pytest tests/mcp/test_portmanteau_tools.py::test_adn_content
```

### Test Guidelines

- **Write tests first** (TDD approach)
- **Test edge cases** and error conditions
- **Mock external dependencies**
- **Maintain high coverage** (90%+ target)
- **Use descriptive test names**

### Test Types

- **Unit Tests**: Test individual functions/methods
- **Integration Tests**: Test component interactions
- **API Tests**: Test HTTP endpoints
- **MCP Tests**: Test MCP tool functionality
- **End-to-End Tests**: Test complete workflows

## 📚 Documentation

### Documentation Types

- **README.md**: Project overview and quick start
- **Prompt Templates**: User guides and examples
- **API Documentation**: Code documentation
- **Contributing Guide**: This document
- **Security Policy**: Security guidelines

### Documentation Guidelines

- **Keep it up-to-date** with code changes
- **Use clear, concise language**
- **Include examples** and code snippets
- **Test all examples** before committing
- **Follow markdown best practices**

### Updating Documentation

- **Update relevant docs** with code changes
- **Test all examples** in documentation
- **Check links** and references
- **Review for clarity** and completeness

## 🚀 Release Process

### Release Types

- **Major**: Breaking changes (v1.0.0 → v2.0.0)
- **Minor**: New features (v1.0.0 → v1.1.0)
- **Patch**: Bug fixes (v1.0.0 → v1.0.1)
- **Pre-release**: Alpha/beta/RC versions

### Release Checklist

- [ ] **All tests pass**
- [ ] **Documentation updated**
- [ ] **Changelog updated**
- [ ] **Version bumped**
- [ ] **Security scan completed**
- [ ] **Performance tests passed**
- [ ] **Breaking changes documented**

### Automated Release

Our CI/CD pipeline handles:
- **Version bumping**
- **Package building** (Python + MCPB)
- **Testing and validation**
- **GitHub release creation**
- **PyPI publishing** (for stable releases)

## 🏷️ Labels and Milestones

### Issue Labels

- **Priority**: `critical`, `high`, `medium`, `low`
- **Type**: `bug`, `feature`, `documentation`, `performance`
- **Status**: `needs-triage`, `in-progress`, `blocked`
- **Area**: `mcp-tools`, `api`, `documentation`, `ci-cd`

### Milestones

- **Version milestones**: Track progress toward releases
- **Feature milestones**: Group related issues
- **Bug fix milestones**: Track critical fixes

## 🤝 Getting Help

### Community

- **GitHub Discussions**: General questions and ideas
- **GitHub Issues**: Bug reports and feature requests
- **Code Review**: Learn from PR reviews

### Maintainers

- **@sandraschi**: Project maintainer
- **Response time**: Usually within 48 hours
- **Availability**: Monday-Friday, CET timezone

## 📄 License

By contributing to Advanced Memory MCP, you agree that your contributions will be licensed under the same license as the project (see [LICENSE](LICENSE) file).

## 🙏 Recognition

Contributors will be recognized in:
- **README.md**: Contributor list
- **Release notes**: Feature contributors
- **GitHub**: Contributor statistics

Thank you for contributing to Advanced Memory MCP! 🎉

---

*Last updated: October 2024*