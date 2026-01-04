# Review Techniques

**Confidence**: 🟡 Medium
**Last validated**: 2025-11-08
**Primary sources**: Google Engineering Practices (2024), Microsoft Dev Blogs Code Review Playbook (2025), ThoughtWorks Technology Radar (2025-04)

---

## 1. Review Workflow

1. **Preparation** – read PR summary + design docs; pull code locally if complex.
2. **Top-down pass** – scan files list, architecture diagrams, test coverage to understand scope.
3. **Focused passes** – evaluate correctness, security, maintainability in separate sweeps.
4. **Comment craft** – provide actionable feedback with rationale; link to standards or docs.
5. **Summarise** – leave final comment summarising key findings and remaining blockers.

---

## 2. Heuristic Checklist

| Category | Questions |
| --- | --- |
| Correctness | Does the change cover edge cases? Are invariants preserved? |
| Security | Any new input surface? Are secret handling, auth, authz secure? |
| Observability | Are logs/metrics/traces added or updated for new paths? |
| Testing | Are unit/integration tests present? Do tests fail without the code change? |
| Maintainability | Is the change scoped? Is documentation updated? Any duplication introduced? |
| Performance | Any unbounded loops, N+1 queries, large data transfers? |

Use checklists per language/framework (link to team-specific guides).

---

## 3. Language/Framework Tips

- **Python**: watch for mutable default args, iterator exhaustion, async vs sync mix-ups, typing coverage.
- **JavaScript/TypeScript**: ensure strict null checks, dependency injection vs global state, bundler impacts.
- **Go**: verify error handling, context propagation, interface usage.
- **SQL**: check for SQL injection, index usage, transaction boundaries.

Maintain cheat sheets in team wiki; update quarterly.

---

## 4. Anti-patterns to Watch

- “Drive-by” large refactors in feature PRs.
- Excessive duplication or copy/paste of config.
- Lack of rollback plan for migrations.
- Feature toggle debt (flags with no removal plan).
- Lazy error handling (`catch {}`) or swallowing exceptions.

Call out anti-patterns with remediation suggestions.

---

## 5. Approvals & Follow-ups

- Use explicit labels/checks for `blocker`, `major`, `minor`.
- Require tests to pass before final approval.
- For unresolved debates, schedule synchronous discussion and document outcome.
- Ensure follow-up tasks (tech debt, docs) are captured in backlog with owner and due date.

---

### Quick Reference Templates
- **Blocking comment**:
  ```
  blocker: This path bypasses auth middleware. Please route through SecurityGuard or explain why public access is safe.
  ```
- **Suggestion**:
  ```
  suggestion: Consider extracting validation into validateOrder() to keep handler focused on orchestration.
  ```
- **Praise**:
  ```
  love: Great job adding contract tests—this will prevent future regressions.
  ```

Reviewing with empathy and clarity accelerates delivery while protecting quality.*** End Patch
