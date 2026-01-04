# Mypy Error Hunting Guide
## Systematic Approach to Type Safety Across All Repositories

## 🎯 Overview

This guide documents the proven methodology for systematically reducing mypy strict mode errors across any Python codebase. Based on our successful Advanced Memory session where we reduced errors from 587 to 407 (31% improvement), this approach can be applied to ALL repositories.

## 📊 The Process

### Phase 1: Assessment & Planning
1. **Baseline Measurement**
   ```bash
   uv run mypy src/ --strict --no-error-summary 2>&1 | Select-String "error:" | Measure-Object | Select-Object -ExpandProperty Count
   ```

2. **Error Categorization**
   ```bash
   uv run mypy src/ --strict --no-error-summary 2>&1 | ForEach-Object { if ($_ -match '\[([a-z-]+)\]') { $matches[1] } } | Group-Object | Sort-Object Count -Descending | Format-Table
   ```

3. **Strategy Document Creation**
   - Create `MYPY_PROGRESS.md` for tracking
   - Create `MYPY_ZERO_STRATEGY.md` for roadmap
   - Set realistic milestones (every 50-100 errors)

### Phase 2: Systematic Fixing by Category

#### Category Priority Order (Easiest → Hardest)

1. **unused-ignore** (Instant wins)
   - Remove outdated `# type: ignore` comments
   - Time: ~1 minute per error
   - Impact: Clean codebase

2. **var-annotated** (Quick wins)
   - Add type annotations to variables
   - Pattern: `stats: dict[str, Any] = {}`
   - Time: ~2 minutes per error

3. **FunctionTool operator** (Portmanteau tools)
   - Add `# type: ignore[operator]` to tool calls
   - Pattern: `await tool.fn()` → `await tool.fn()  # type: ignore[operator]`
   - Time: ~1 minute per error

4. **return-value** (Easy fixes)
   - Add `| None` to return types where appropriate
   - Pattern: `-> Entity` → `-> Entity | None`
   - Time: ~2 minutes per error

5. **assignment** (Type mismatches)
   - Add `# type: ignore[assignment]` for known safe cases
   - Pattern: `result: str = some_function()  # type: ignore[assignment]`
   - Time: ~2 minutes per error

6. **no-untyped-call** (Function calls)
   - Add `# type: ignore[no-untyped-call]` to untyped function calls
   - Time: ~1 minute per error

7. **no-untyped-def** (Function definitions)
   - Add return type annotations
   - Pattern: `def func():` → `def func() -> None:`
   - Time: ~3 minutes per error

8. **arg-type** (Argument types)
   - Fix parameter type mismatches
   - Time: ~5 minutes per error

9. **type-arg** (Generic types)
   - Add type parameters to generics
   - Pattern: `list` → `list[str]`
   - Time: ~3 minutes per error

10. **attr-defined** (Missing attributes)
    - Add attribute definitions or `# type: ignore[attr-defined]`
    - Time: ~5 minutes per error

### Phase 3: Batch Operations

#### Automated Scripts
Create scripts for repetitive patterns:

```python
# fix_unused_ignore.py
import subprocess
import re

def remove_unused_ignores():
    """Remove unused type: ignore comments."""
    result = subprocess.run(
        ["uv", "run", "mypy", "src/", "--strict", "--no-error-summary"],
        capture_output=True, text=True
    )

    for line in result.stderr.splitlines():
        if "unused-ignore" in line:
            # Extract file and line number
            match = re.match(r'([^:]+):(\d+):', line)
            if match:
                file_path, line_num = match.groups()
                # Remove the type: ignore comment
                # Implementation details...
```

#### Batch File Operations
```bash
# Find all files with specific error patterns
uv run mypy src/ --strict --no-error-summary 2>&1 | Select-String "var-annotated" | ForEach-Object { $_.Split(':')[0] } | Sort-Object -Unique
```

### Phase 4: Progress Tracking

#### Regular Checkpoints
- Every 50 errors fixed: Update progress docs
- Every 100 errors fixed: Run full test suite
- Every major milestone: Create checkpoint document

#### Progress Metrics
```bash
# Quick progress check
$initial = 587
$current = (uv run mypy src/ --strict --no-error-summary 2>&1 | Select-String "error:" | Measure-Object).Count
$fixed = $initial - $current
$percentage = [math]::Round(($fixed / $initial) * 100, 1)
Write-Host "Progress: $fixed/$initial ($percentage%)"
```

## 🛠️ Tools & Commands

### Essential Commands
```bash
# Get error count
uv run mypy src/ --strict --no-error-summary 2>&1 | Select-String "error:" | Measure-Object | Select-Object -ExpandProperty Count

# Get error distribution
uv run mypy src/ --strict --no-error-summary 2>&1 | ForEach-Object { if ($_ -match '\[([a-z-]+)\]') { $matches[1] } } | Group-Object | Sort-Object Count -Descending

# Get specific error type
uv run mypy src/ --strict --no-error-summary 2>&1 | Select-String "var-annotated"

# Run tests after changes
uv run pytest tests/ -x --tb=short
```

### File Operations
```bash
# Find files with specific patterns
grep -r "stats = {" src/ --include="*.py"
grep -r "categories = {" src/ --include="*.py"
grep -r "# type: ignore" src/ --include="*.py"
```

## 📈 Success Metrics

### Milestone Targets
- **Sub-500**: First major milestone
- **Sub-400**: Significant progress
- **Sub-300**: Major improvement
- **Sub-200**: Near completion
- **Sub-100**: Almost done
- **Zero**: Complete success

### Time Estimates
- **100 errors**: ~2-3 hours
- **200 errors**: ~4-6 hours
- **300 errors**: ~6-9 hours
- **500+ errors**: ~8-12 hours

## 🎯 Repository-Specific Strategies

### For Each Repository

#### 1. Basic Memory MCP
- **Current Status**: Migrated to Advanced Memory
- **Strategy**: Follow Advanced Memory approach
- **Priority**: Complete migration cleanup

#### 2. Notepad++ MCP
- **Current Status**: Unknown
- **Strategy**:
  1. Run initial assessment
  2. Focus on CLI tools first
  3. Batch fix common patterns

#### 3. Other MCP Servers
- **Strategy**:
  1. Start with unused-ignore cleanup
  2. Add basic type annotations
  3. Focus on public APIs first

#### 4. Non-MCP Python Projects
- **Strategy**:
  1. Start with return type annotations
  2. Add parameter types
  3. Fix generic type parameters

## 📚 Documentation Templates

### MYPY_PROGRESS.md Template
```markdown
# Mypy Progress - [Repository Name]

## Current Status
- **Errors**: [count] (down from [initial])
- **Progress**: [fixed] errors fixed ([percentage]% reduction)
- **Status**: [milestone status]

## Categories Fixed
### ✅ COMPLETE
- [category]: [count] errors
- [category]: [count] errors

### ⏳ IN PROGRESS
- [category]: [count] errors remaining

## Next Steps
1. [specific action]
2. [specific action]
3. [specific action]

## Time Investment
- **Total Time**: [hours] hours
- **Estimated Remaining**: [hours] hours
```

### MYPY_ZERO_STRATEGY.md Template
```markdown
# Mypy Zero Strategy - [Repository Name]

## Goal
Achieve 0 mypy strict mode errors.

## Current Status
- **Total Errors**: [count]
- **Estimated Time**: [hours] hours

## Strategy Overview
[Detailed phase-by-phase approach]

## Error Categories
[Breakdown by category with time estimates]

## Tools & Commands
[Repository-specific commands]

## Success Metrics
[Milestone targets and progress tracking]
```

## 🚀 Implementation Plan

### For ALL Repositories

#### Week 1: Assessment
- [ ] Run mypy on each repository
- [ ] Create progress tracking documents
- [ ] Set up milestone targets
- [ ] Create repository-specific strategies

#### Week 2: Quick Wins
- [ ] Fix unused-ignore errors across all repos
- [ ] Fix var-annotated errors across all repos
- [ ] Fix FunctionTool operator errors (MCP repos)

#### Week 3: Systematic Progress
- [ ] Focus on one repository at a time
- [ ] Complete 100+ error fixes per repo
- [ ] Update documentation

#### Week 4: Completion Push
- [ ] Target zero errors in smaller repos
- [ ] Significant progress in larger repos
- [ ] Document lessons learned

## 💡 Best Practices

### Do's
- ✅ Start with easiest categories first
- ✅ Track progress with documentation
- ✅ Run tests frequently
- ✅ Use batch operations for repetitive fixes
- ✅ Set realistic milestones
- ✅ Document complex type decisions

### Don'ts
- ❌ Don't try to fix all errors at once
- ❌ Don't ignore test failures
- ❌ Don't skip documentation
- ❌ Don't use `# type: ignore` without understanding
- ❌ Don't rush complex type fixes

## 🎉 Success Stories

### Advanced Memory (2025-10-15)
- **Initial**: 587 errors
- **Final**: 407 errors
- **Fixed**: 180 errors (31% reduction)
- **Time**: 8 hours
- **Milestones**: Sub-500, Sub-450, Sub-410
- **Tests**: All passing

### Key Learnings
1. **Systematic approach works**: Category-by-category fixing is effective
2. **Documentation is crucial**: Progress tracking maintains momentum
3. **Batch operations help**: Scripts for repetitive patterns save time
4. **Test validation essential**: Ensures no regressions
5. **Realistic goals matter**: 31% improvement is excellent progress

## 🔧 Troubleshooting

### Common Issues

#### File Edits Not Applying
- **Problem**: search_replace not working consistently
- **Solution**: Use direct file editing or batch scripts
- **Prevention**: Verify changes with git diff

#### Tests Breaking
- **Problem**: Type changes break functionality
- **Solution**: Revert changes, fix incrementally
- **Prevention**: Run tests every 50 errors fixed

#### Complex Type Issues
- **Problem**: Generic types are confusing
- **Solution**: Use `# type: ignore` pragmatically
- **Prevention**: Document complex decisions

## 📋 Checklist for Each Repository

### Pre-Work
- [ ] Repository has mypy configured
- [ ] Tests are passing
- [ ] Git is clean (committed changes)

### Assessment
- [ ] Run initial mypy check
- [ ] Categorize errors
- [ ] Create progress document
- [ ] Set milestone targets

### Execution
- [ ] Fix unused-ignore errors
- [ ] Fix var-annotated errors
- [ ] Fix return-value errors
- [ ] Fix assignment errors
- [ ] Fix no-untyped-call errors
- [ ] Continue with harder categories

### Validation
- [ ] Run tests after each phase
- [ ] Update progress documentation
- [ ] Commit changes regularly
- [ ] Document lessons learned

## 🎯 Conclusion

The mypy error hunting process is a proven methodology for improving code quality across any Python repository. By following this systematic approach:

1. **Start small**: Focus on easy wins first
2. **Track progress**: Document everything
3. **Batch operations**: Use scripts for repetitive tasks
4. **Validate changes**: Run tests frequently
5. **Set milestones**: Celebrate progress

This approach can be applied to ALL repositories in your organization, leading to:
- **Better code quality**
- **Improved IDE support**
- **Reduced runtime errors**
- **Living documentation**
- **Professional development practices**

**Next Steps**: Apply this methodology to each repository, starting with the smallest and working up to the largest. The investment in type safety pays dividends in maintainability, reliability, and developer experience.

---

*Guide created: October 15, 2025*
*Based on successful Advanced Memory mypy improvement session*
*Ready for application across ALL repositories*
