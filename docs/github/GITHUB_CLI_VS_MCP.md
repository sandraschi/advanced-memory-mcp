# GitHub CLI vs GitHub MCP - Why CLI is Better for AI

**TL;DR**: Use `gh` CLI instead of GitHub MCP. Less token waste, better results.

---

## The Problem with GitHub MCP

When AI (Claude, GPT, etc.) uses the GitHub Model Context Protocol server:

**❌ Issues**:
1. **High token consumption** - Each MCP call uses tokens for:
   - Tool invocation overhead
   - Response formatting
   - Error handling wrappers
   - Multiple round-trips for complex operations

2. **First attempt produces crap**:
   - AI doesn't know exact MCP tool signatures
   - Guesses at parameters
   - Gets errors, retries
   - Wastes tokens on trial-and-error

3. **Limited introspection**:
   - MCP tools have fixed interfaces
   - Can't easily explore all options
   - AI must memorize tool capabilities

---

## The Solution: GitHub CLI (`gh`)

**✅ Why `gh` CLI is superior**:

### 1. Self-Documenting

**First interaction**:
```
AI: gh --help
```

**Result**: Complete command reference in one shot
- All commands listed
- All flags documented
- Examples included
- No guessing needed

**From then on: smooth sailing**

---

### 2. Token Efficiency

**GitHub MCP approach** (wasteful):
```
1. Call github_mcp("list_repos") → Error (wrong params)
2. Check MCP schema
3. Call github_mcp("list_repos", owner="user") → Success
Total: 3+ round-trips
```

**GitHub CLI approach** (efficient):
```
1. gh repo list --help  (get all options once)
2. gh repo list --limit 50
Total: 2 commands, all info upfront
```

**Token savings**: 50-70% reduction in typical workflows

---

### 3. Composability

**CLI = Unix philosophy**:
```bash
# Chain commands with pipes
gh repo list | grep "mcp" | wc -l

# Combine with other tools
gh pr list --json title,url | jq '.[] | select(.title | contains("fix"))'

# Redirect output
gh issue list > issues.txt
```

**MCP = Isolated tools**:
- Each tool is separate
- No piping between tools
- Limited composition

---

### 4. Full Feature Access

**GitHub CLI**:
- ✅ All GitHub features available
- ✅ New features added quickly
- ✅ Extensions ecosystem
- ✅ Direct API access when needed

**GitHub MCP**:
- ⚠️ Limited to exposed tools
- ⚠️ Lags behind GitHub API updates
- ⚠️ No extension support
- ⚠️ Workarounds needed for edge cases

---

## The Workflow Pattern

### Initial Learning (One-Time Cost)

**Step 1**: AI asks for help
```
AI: gh --help
```

**Output** (cached/learned):
```
Core commands:
  auth:        Authenticate gh and git
  browse:      Open the repository in the browser
  codespace:   Connect to and manage codespaces
  gist:        Manage gists
  issue:       Manage issues
  pr:          Manage pull requests
  release:     Manage releases
  repo:        Manage repositories
  
Additional commands:
  alias:       Create command shortcuts
  api:         Make an authenticated GitHub API request
  ...
```

**Step 2**: AI drills down
```
AI: gh pr --help
```

**Output**:
```
Create, view, and check out pull requests.

USAGE
  gh pr [command]

CORE COMMANDS
  checkout:    Check out a pull request in git
  create:      Create a pull request
  list:        List pull requests
  status:      Show status of relevant pull requests
  view:        View a pull request
  ...
```

**Step 3**: AI gets specific
```
AI: gh pr create --help
```

**Output**: Every flag, every option, examples.

---

### Ongoing Use (Efficient)

**After initial learning**:

```bash
# AI knows exactly what to do
gh pr create --title "Fix bug" --body "Details here" --base main

# No trial-and-error
gh issue create --title "Feature request" --label enhancement

# Confident usage
gh repo create my-new-repo --public --clone
```

**No wasted tokens. No retries. Just works.**

---

## Comparison Table

| Aspect | GitHub CLI (`gh`) | GitHub MCP |
|--------|------------------|------------|
| **Token Efficiency** | ✅ High (self-documenting) | ❌ Low (trial-and-error) |
| **First Use** | ✅ `--help` explains everything | ❌ Guessing game |
| **Learning Curve** | ✅ AI learns once, uses forever | ⚠️ AI must memorize schemas |
| **Feature Coverage** | ✅ 100% GitHub features | ⚠️ Limited to exposed tools |
| **Composability** | ✅ Unix pipes, chaining | ❌ Isolated tool calls |
| **Error Messages** | ✅ Clear, actionable | ⚠️ Wrapped in MCP overhead |
| **Performance** | ✅ Direct execution | ⚠️ MCP layer overhead |
| **Maintenance** | ✅ GitHub maintains | ⚠️ Community MCP updates lag |

---

## Real-World Example

### Task: Create PR with 5 commits

**GitHub MCP approach** (10+ tool calls):
1. `github_mcp("auth")` - Authenticate
2. `github_mcp("get_branches")` - List branches
3. `github_mcp("get_commits", branch="feature")` - Get commits
4. `github_mcp("create_pr", ...)` - Wrong params, error
5. Check MCP schema
6. `github_mcp("create_pr", ...)` - Try again, error (missing body)
7. `github_mcp("create_pr", ...)` - Success!
8. `github_mcp("add_labels", ...)` - Add labels
9. `github_mcp("request_review", ...)` - Request review

**Estimated tokens**: 5,000-8,000

---

**GitHub CLI approach** (3 commands):
```bash
# 1. Get help (first time only)
gh pr create --help

# 2. Create PR
gh pr create \
  --title "Add new feature" \
  --body "Implements X, Y, Z" \
  --base main \
  --head feature/new-feature \
  --label enhancement \
  --reviewer username

# 3. Done!
```

**Estimated tokens**: 1,000-1,500 (70% reduction)

---

## When to Use Each

### Use GitHub CLI (`gh`)

**✅ Default choice for**:
- AI-driven workflows
- Complex GitHub operations
- Token efficiency matters
- Full feature access needed
- Composable workflows
- Local development

**Example use cases**:
- Automated PR creation
- Issue management
- Release workflows
- Repository management
- Code review automation

---

### Use GitHub MCP

**⚠️ Only when**:
- Already committed to MCP-only stack
- Simple, one-off operations
- Claude Desktop UI integration needed
- Client doesn't have CLI installed

**Example use cases**:
- Quick status checks in Claude Desktop
- Simple issue creation from chat
- One-off repository queries

---

## Setup Guide

### Install GitHub CLI

**macOS**:
```bash
brew install gh
```

**Windows**:
```bash
# Scoop
scoop install gh

# Chocolatey
choco install gh

# Or download: https://cli.github.com/
```

**Linux**:
```bash
# Debian/Ubuntu
sudo apt install gh

# Fedora
sudo dnf install gh

# Arch
sudo pacman -S github-cli
```

---

### Configure for AI Use

**1. Authenticate**:
```bash
gh auth login
```

**2. Set preferences**:
```bash
# Default editor (for AI-generated content)
gh config set editor "nano"

# Default browser (optional)
gh config set browser "firefox"
```

**3. Test**:
```bash
gh repo list
gh pr list
gh issue list
```

---

### AI Workflow Template

**Teach your AI this pattern**:

```markdown
When working with GitHub:

1. First time using a command:
   ```
   gh <command> --help
   ```
   Read all options, flags, examples.

2. Subsequent uses:
   Directly execute with full confidence:
   ```
   gh <command> --option value
   ```

3. Complex operations:
   Chain commands:
   ```
   gh <command1> | jq '.[]' | gh <command2>
   ```

4. Error handling:
   Read error message, adjust, retry.
   (Errors are clear, not wrapped)
```

---

## Migration from GitHub MCP

**If you're currently using GitHub MCP**:

### Step 1: Install CLI
```bash
brew install gh  # or your package manager
gh auth login
```

### Step 2: Replace MCP Calls

**Before** (GitHub MCP):
```python
github_mcp("create_pr", {
    "title": "Fix bug",
    "body": "Details here",
    "base": "main",
    "head": "feature/fix"
})
```

**After** (GitHub CLI):
```bash
gh pr create \
  --title "Fix bug" \
  --body "Details here" \
  --base main \
  --head feature/fix
```

### Step 3: Update Documentation

Update your AI prompts/instructions to use `gh` instead of MCP tools.

---

## Advanced Tips

### 1. Use JSON Output for Parsing

```bash
# Get structured data
gh pr list --json number,title,state,url

# Pipe to jq for filtering
gh pr list --json number,title | jq '.[] | select(.title | contains("bug"))'
```

---

### 2. Create Aliases for Common Tasks

```bash
# Create PR from current branch
gh alias set prc 'pr create --fill'

# Usage
gh prc
```

---

### 3. Use Templates

```bash
# Create issue with template
gh issue create --template bug_report.md

# Create PR with template
gh pr create --template pull_request_template.md
```

---

### 4. Combine with Git

```bash
# Create branch and PR in one go
git checkout -b feature/new-thing
git commit -am "Add feature"
git push -u origin feature/new-thing
gh pr create --fill
```

---

## Token Consumption Analysis

**Typical AI GitHub Workflow** (50 operations):

| Approach | Total Tokens | Operations | Avg per Op |
|----------|-------------|------------|------------|
| GitHub MCP | ~250,000 | 50 | ~5,000 |
| GitHub CLI (first time) | ~100,000 | 50 | ~2,000 |
| GitHub CLI (after learning) | ~50,000 | 50 | ~1,000 |

**ROI**: After ~10 operations, CLI has paid for initial learning cost.

---

## Common Workflows

### 1. Create Feature Branch + PR

```bash
# CLI (efficient)
git checkout -b feature/new
git commit -am "Add feature"
git push -u origin feature/new
gh pr create --title "Add feature" --body "Details" --draft

# vs MCP (10+ tool calls, 5x tokens)
```

---

### 2. Review and Merge PR

```bash
# CLI
gh pr view 123
gh pr checks 123  # See CI status
gh pr merge 123 --squash --delete-branch

# vs MCP (multiple calls, verbose responses)
```

---

### 3. Issue Management

```bash
# CLI
gh issue list --label bug --state open
gh issue create --title "Bug" --body "Description" --label bug
gh issue close 456 --comment "Fixed in #123"

# vs MCP (separate tools for each action)
```

---

### 4. Release Workflow

```bash
# CLI (one command)
gh release create v1.0.0 \
  --title "Version 1.0.0" \
  --notes "Release notes here" \
  dist/*.whl

# vs MCP (5+ tool calls)
```

---

## Conclusion

**Use GitHub CLI for AI workflows. Period.**

**Benefits**:
- ✅ 50-70% token reduction
- ✅ Self-documenting (`--help`)
- ✅ Smooth sailing after initial learning
- ✅ Full GitHub feature access
- ✅ Composable with other tools

**The pattern**:
1. **First use**: `gh <command> --help` (learn once)
2. **All subsequent uses**: Direct execution (no trial-and-error)
3. **Result**: Efficient, confident GitHub automation

**Token efficiency matters**. Use `gh`.

---

## References

- GitHub CLI Docs: https://cli.github.com/manual/
- GitHub CLI Repo: https://github.com/cli/cli
- All Commands: `gh --help`
- Command Specific: `gh <command> --help`

---

*Written after discovering MCP wastes tokens, CLI is smooth sailing*  
*October 2025*

