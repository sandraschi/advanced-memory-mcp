# Git Fundamentals

Git is a distributed version control system for tracking changes in source code during software development.

## Core Concepts

### Repository (Repo)
A directory tracked by Git containing your project's history.

### Commit
A snapshot of your project at a specific point in time.

### Branch
An independent line of development.

### Remote
A version of your repository hosted on a server (e.g., GitHub).

## Basic Workflow

### Initialize Repository
```bash
# Create new repo
git init

# Clone existing repo
git clone https://github.com/user/repo.git
```

### Stage and Commit
```bash
# Check status
git status

# Stage files
git add file.py
git add .  # Stage all changes

# Commit
git commit -m "Add new feature"

# Stage and commit in one step
git commit -am "Update existing files"
```

### View History
```bash
# Show commits
git log
git log --oneline  # Compact view
git log --graph --oneline --all  # Visual branch history

# Show changes
git diff  # Unstaged changes
git diff --staged  # Staged changes
git show commit-hash  # Specific commit
```

## Branching

### Create and Switch Branches
```bash
# Create new branch
git branch feature-name

# Switch to branch
git checkout feature-name

# Create and switch in one command
git checkout -b feature-name

# Modern syntax (Git 2.23+)
git switch feature-name
git switch -c feature-name  # Create and switch
```

### Merge Branches
```bash
# Switch to target branch
git checkout main

# Merge feature branch
git merge feature-name

# Delete merged branch
git branch -d feature-name
```

## Working with Remotes

### Basic Remote Operations
```bash
# Add remote
git remote add origin https://github.com/user/repo.git

# View remotes
git remote -v

# Fetch changes
git fetch origin

# Pull changes (fetch + merge)
git pull origin main

# Push changes
git push origin main
git push -u origin feature-name  # Set upstream
```

## Undoing Changes

### Before Commit
```bash
# Discard unstaged changes
git checkout -- file.py
git restore file.py  # Modern syntax

# Unstage files
git reset HEAD file.py
git restore --staged file.py  # Modern syntax
```

### After Commit
```bash
# Amend last commit
git commit --amend -m "New message"

# Reset to previous commit (keep changes)
git reset --soft HEAD~1

# Reset to previous commit (discard changes)
git reset --hard HEAD~1  # ⚠️ Destructive!

# Revert commit (create new commit)
git revert commit-hash  # ✅ Safe for shared branches
```

## Best Practices

1. **Commit Often**: Small, focused commits
2. **Write Good Messages**: Clear, descriptive commit messages
3. **Use Branches**: Feature branches for new work
4. **Pull Before Push**: Avoid conflicts
5. **Don't Commit Secrets**: Use .gitignore
6. **Review Before Commit**: `git diff --staged`

## Commit Message Convention
```
type(scope): subject

body (optional)

footer (optional)
```

**Types**: feat, fix, docs, style, refactor, test, chore

**Example**:
```
feat(auth): add user login functionality

Implement JWT-based authentication with refresh tokens.
Includes login, logout, and token refresh endpoints.

Closes #123
```

## Common .gitignore Patterns
```gitignore
# Python
__pycache__/
*.pyc
.venv/
*.egg-info/

# IDEs
.vscode/
.idea/
*.swp

# OS
.DS_Store
Thumbs.db

# Project-specific
config.local.py
*.log
.env
```

## Related Concepts
- [[Git Branching Strategies]]
- [[Git Workflows]]
- [[GitHub Pull Requests]]
- [[Code Review Best Practices]]
- [[Version Control Philosophy]]

*Git is not just a tool - it's a time machine for your code.*
