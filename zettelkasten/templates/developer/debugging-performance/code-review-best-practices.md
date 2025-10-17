# Code Review Best Practices

Code review improves quality, shares knowledge, and catches issues before production.

## Why Code Review?

### Benefits
1. **Catch Bugs**: Fresh eyes find issues
2. **Share Knowledge**: Learn from each other
3. **Maintain Standards**: Consistent code quality
4. **Better Design**: Discuss architectural decisions
5. **Team Communication**: Async collaboration

## For Reviewers

### What to Look For

#### 1. Correctness
- Does code do what it claims?
- Are edge cases handled?
- Could this cause bugs?

#### 2. Design
- Is approach sound?
- Could this be simpler?
- Does it fit existing architecture?

#### 3. Complexity
- Is code unnecessarily complex?
- Could logic be clearer?
- Are abstractions appropriate?

#### 4. Tests
- Are there sufficient tests?
- Do tests cover edge cases?
- Are tests clear and maintainable?

#### 5. Naming
- Are names clear and descriptive?
- Is naming consistent with codebase?
- Could names be improved?

#### 6. Documentation
- Are complex parts explained?
- Is public API documented?
- Are assumptions stated?

### How to Give Feedback

#### Be Kind and Constructive
```
❌ "This code is terrible."
✅ "Consider extracting this into a separate function for clarity."

❌ "You don't know what you're doing."
✅ "This approach might have issues with X. What about trying Y?"
```

#### Be Specific
```
❌ "This could be better."
✅ "This function is doing 3 things. Consider splitting into:
    - validate_input()
    - process_data()
    - format_output()"
```

#### Explain Why
```
❌ "Use list comprehension."
✅ "List comprehension would be clearer and faster here:
    result = [x * 2 for x in items]"
```

#### Distinguish Must-Fix vs Nice-to-Have
```
🔴 "Blocking: This will cause data loss if user_id is None"
🟡 "Nit: Consider more descriptive variable name"
🟢 "Optional: Could extract this for reusability"
```

#### Praise Good Code
```
✅ "Great use of type hints here!"
✅ "Nice test coverage!"
✅ "This is much clearer than the previous approach."
```

### Review Checklist

- [ ] Read description/ticket
- [ ] Understand what code should do
- [ ] Review tests first (shows intended behavior)
- [ ] Review main code
- [ ] Check for security issues
- [ ] Verify documentation
- [ ] Run code locally if complex
- [ ] Approve or request changes

## For Authors

### Before Requesting Review

#### 1. Self-Review
- Read your own code like a reviewer
- Run linters and type checkers
- Ensure all tests pass
- Check diff for accidental changes

#### 2. Keep Changes Focused
```
❌ Bad PR: "Update user system, refactor database, add tests, fix bug"
✅ Good PR: "Add email validation to user registration"
```

#### 3. Write Clear Description
```markdown
## What
Add email validation to user registration

## Why
Prevent invalid emails from creating accounts

## How
- Added validate_email() function
- Updated UserService.create_user()
- Added tests for edge cases

## Testing
- All existing tests pass
- Added 5 new tests for validation
```

#### 4. Add Comments
Explain non-obvious code.

```python
# Use exponential backoff to avoid overwhelming API
# Starts at 1s, max 32s: 1, 2, 4, 8, 16, 32
delay = min(2 ** retry_count, 32)
time.sleep(delay)
```

### Responding to Feedback

#### Be Receptive
- Assume good intentions
- Ask clarifying questions
- Explain reasoning if you disagree
- Thank reviewers

#### Address All Comments
```
✅ "Fixed in commit abc123"
✅ "Good point! Changed to..."
✅ "I kept X because... Does this make sense?"
❌ Ignoring comments
```

#### Don't Take Personally
Code review is about code, not you.

## Review Etiquette

### Timing
- **Small changes**: Review within 1 day
- **Medium changes**: Within 2 days
- **Large changes**: Break into smaller PRs

### Communication
- Be respectful and professional
- Assume competence
- Focus on code, not person
- Explain reasoning

### Disagreements
1. Discuss the trade-offs
2. Consider both perspectives
3. Defer to team standards
4. Escalate if needed

## Types of Reviews

### Quick Review (<100 lines)
- 15-30 minutes
- Focus on correctness and obvious issues

### Standard Review (100-500 lines)
- 1-2 hours
- Thorough examination
- Test locally

### Large Review (500+ lines)
- Break into smaller reviews if possible
- Review in multiple sessions
- May need design discussion first

## Automated Checks

Let automation catch mechanical issues.

```yaml
# GitHub Actions
- name: Lint
  run: ruff check .

- name: Type Check
  run: pyright

- name: Tests
  run: pytest

- name: Security
  run: bandit -r src/
```

**Reviewers** can then focus on:
- Design decisions
- Business logic
- Architecture
- User experience

## Review Tools

### Features to Look For
- Side-by-side diff view
- Inline comments
- Approval workflow
- CI integration
- Conversation threading

### Popular Platforms
- **GitHub**: Pull Requests
- **GitLab**: Merge Requests
- **Bitbucket**: Pull Requests
- **Gerrit**: Change review
- **Phabricator**: Differential

## Metrics

### Useful Metrics
- Review turnaround time
- Comments per review
- Approval rate
- Post-review bug rate

### Avoid
- Lines of code reviewed (incentivizes superficial review)
- Number of comments (incentivizes nitpicking)

## Common Review Patterns

### Bike-Shedding
Spending time on trivial issues while missing important ones.

**Solution**: Focus on high-impact issues first, skip trivial style issues covered by linters.

### Approval Without Review
Rubber-stamping without actually reading.

**Solution**: Set expectations, require meaningful engagement.

### Blocking on Subjective Preferences
```
❌ "I don't like this variable name" (blocking)
✅ "Consider renaming for clarity" (suggestion)
```

## Related Concepts
- [[Pull Request Workflow]]
- [[Git Best Practices]]
- [[Clean Code Principles]]
- [[Team Communication]]
- [[Software Quality]]

*Good code review is collaborative, not adversarial - we're all trying to build better software.*
