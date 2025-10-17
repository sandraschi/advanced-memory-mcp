# Python Virtual Environments

Virtual environments isolate project dependencies, preventing conflicts between projects.

## Why Virtual Environments?

### The Problem
```bash
# Project A needs requests 2.25.0
pip install requests==2.25.0

# Project B needs requests 2.31.0
pip install requests==2.31.0  # ❌ Breaks Project A!
```

### The Solution
Each project gets its own isolated environment with its own dependencies.

## Creating Virtual Environments

### Using venv (Built-in)
```bash
# Create environment
python -m venv .venv

# Activate (Windows)
.venv\\Scripts\\activate

# Activate (Unix/Mac)
source .venv/bin/activate

# Deactivate
deactivate
```

### Using UV (Modern, Fast)
```bash
# Create and sync dependencies
uv sync

# Activate
source .venv/bin/activate  # Unix/Mac
.venv\\Scripts\\activate  # Windows

# Run command in venv without activating
uv run python script.py
```

### Using Poetry
```bash
# Create environment and install deps
poetry install

# Run in environment
poetry run python script.py

# Activate shell
poetry shell
```

## Managing Dependencies

### requirements.txt
```bash
# Generate
pip freeze > requirements.txt

# Install
pip install -r requirements.txt
```

### pyproject.toml (Modern)
```toml
[project]
dependencies = [
    "requests>=2.31.0",
    "pandas>=2.0.0",
]

[tool.uv]
dev-dependencies = [
    "pytest>=8.0.0",
    "ruff>=0.1.0",
]
```

```bash
# Install with uv
uv sync
uv sync --dev  # Include dev dependencies
```

## Best Practices

1. **One venv per project**
   ```
   project/
   ├── .venv/          # Virtual environment
   ├── src/            # Source code
   ├── tests/          # Tests
   └── pyproject.toml  # Dependencies
   ```

2. **Add .venv to .gitignore**
   ```gitignore
   .venv/
   venv/
   *.pyc
   __pycache__/
   ```

3. **Document Python version**
   ```toml
   [project]
   requires-python = ">=3.11"
   ```

4. **Lock dependencies**
   ```bash
   # UV automatically creates uv.lock
   uv lock

   # Poetry creates poetry.lock
   poetry lock
   ```

5. **Use consistent tool across team**
   - Choose: venv, UV, Poetry, or conda
   - Document in README
   - Stick with it

## Common Workflows

### Starting New Project
```bash
# With UV (recommended)
mkdir myproject && cd myproject
uv init
uv add requests pandas
uv sync

# With venv
mkdir myproject && cd myproject
python -m venv .venv
source .venv/bin/activate
pip install requests pandas
pip freeze > requirements.txt
```

### Joining Existing Project
```bash
# With UV
git clone repo
cd repo
uv sync --dev

# With venv
git clone repo
cd repo
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Updating Dependencies
```bash
# With UV
uv lock --upgrade
uv sync

# With pip
pip install --upgrade package-name
pip freeze > requirements.txt
```

## Troubleshooting

### "Command not found" after install
```bash
# Ensure venv is activated
which python  # Should show .venv/bin/python

# Or use uv run
uv run python script.py
```

### Conflicting dependencies
```bash
# Check what's installed
pip list

# Create fresh environment
rm -rf .venv
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Different Python versions
```bash
# Specify Python version
python3.11 -m venv .venv

# Or with UV
uv python install 3.11
uv python pin 3.11
```

## Related Concepts
- [[Python Fundamentals]]
- [[Package Management]]
- [[Dependency Management]]
- [[Python Project Structure]]
- [[Reproducible Builds]]

*Virtual environments are not optional - they're essential for professional Python development.*
