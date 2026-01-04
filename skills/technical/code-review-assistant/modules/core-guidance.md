# Core Guidance

**Confidence**: 🟡 MEDIUM
**Last validated**: 2025-11-08

> Start here to align on review objectives, depth, and communication style before diving into detailed heuristics.

---

## 1. Review Intake Checklist

| Question | Why it matters |
| --- | --- |
| What problem does this change solve? | Aligns reviewers with the business context and prevents goal drift. |
| What is the risk profile (size, critical path, security impact)? | Determines scrutiny level, reviewer mix, and testing expectations. |
| What validation evidence accompanies the change? | Guides focus on missing tests or docs. |
| Are there cross-team/architectural implications? | Signals need for specialist reviewers or design review. |
| What is the expected turnaround time? | Sets expectations and keeps flow-of-work smooth. |

Authors should answer these in the PR template; reviewers confirm before examining code.

---

## 2. Review Goals (Priority Order)

1. **Correctness & Safety** – logical correctness, data integrity, security pitfalls.
2. **Reliability** – error handling, resilience, observability hooks.
3. **Maintainability** – readability, modularity, tests, documentation.
4. **Performance & Cost** – complexity, resource usage, scalability.
5. **Style** – rely on automated formatters/linters; human attention only when automation cannot enforce.

Communicate which goals you evaluated to help authors follow up.

---

## 3. Sizing & Turnaround Guidance

| Diff Size | Target SLA | Guidance |
| --- | --- | --- |
| < 200 LOC | 4 business hours | Focus on correctness & maintainability. |
| 200–400 LOC | 1 business day | Consider synchronous walkthrough for complex areas. |
| > 400 LOC | Request split or schedule review meeting | Encourage smaller PRs; pair review recommended. |
| Hotfix | Immediate | Verify tests & rollback plan; follow-up cleanup review later. |

Avoid exceeding work-in-progress limits; maintain reviewer load fairness.

---

## 4. Communication Patterns

- Lead with high-level summary (`Overall:`) before inline comments.
- Distinguish blocking vs non-blocking comments (e.g., `blocker:`, `suggestion:`).
- Provide rationale and, where possible, alternative snippets or references.
- Celebrate good decisions to reinforce positive patterns.
- Encourage authors to respond with reasoning when diverging from suggestions.

---

## 5. Escalation Triggers

- Repeated disagreements unresolved after two comment rounds.
- Architectural or security concerns beyond reviewer expertise.
- High-risk release deadlines; schedule synchronous review/pre-merge huddle.
- Evidence of systemic issues (technical debt, inconsistent tests) needing tech debt tracking.

When escalation triggers, document outcomes in the PR and relevant ADR or ticket.

---

### Module Map
- Detailed heuristics & checklists → [modules/review-techniques.md](modules/review-techniques.md)
- Automation & bots → [modules/automation-and-tooling.md](modules/automation-and-tooling.md)
- Team norms & feedback loops → [modules/team-practices.md](modules/team-practices.md)
- Outstanding research → [modules/known-gaps.md](modules/known-gaps.md)

Review this module quarterly to ensure alignment with evolving team policies.*** End Patch
