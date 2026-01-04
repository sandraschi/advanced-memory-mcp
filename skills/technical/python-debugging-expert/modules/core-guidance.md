# Core Guidance

**Confidence**: 🟡 MEDIUM
**Last validated**: 2025-11-08

> Start here to capture context, triage severity, and create a reproducible path before diving into tooling.

---

## 1. Intake Template

| Field | Details |
| --- | --- |
| Symptom | Error message, stack trace, performance degradation, incorrect output |
| Environment | Python version, OS, container, dependencies |
| Reproduction steps | Minimal example, test case, input data |
| Recent changes | Deployments, dependency updates, config toggles |
| Impact | User-facing severity, business priority, SLA breach |

Populate template in issue tracker before debugging begins.

---

## 2. Severity & Prioritization

- **P0**: production outage, data corruption → mobilize incident response.
- **P1**: severe user impact, SLA at risk → prioritize, assign dedicated engineers.
- **P2**: minor regression or non-critical bug → schedule into sprint.
- Communicate status to stakeholders; maintain timeline of actions.

---

## 3. Debugging Workflow

1. Reproduce issue locally or in isolated environment.
2. Add logging/assertions to narrow down scope (use `logging`, `rich`, `structlog`).
3. Attach debugger or profiling tool relevant to symptom.
4. Validate hypotheses iteratively; keep notes.
5. Once fixed, add regression tests and observability guardrails.

---

## 4. Communication

- Provide updates in incident channels or issue comments with findings.
- Share reproduction steps and temporary mitigations.
- Document final root cause analysis (RCA) and fix summary.

---

## 5. Anti-patterns

- Making speculative fixes without reproduction.
- Ignoring dependency/environment differences.
- Leaving logging changes or debug code in production.
- Skipping regression tests after fix.

Escalate when reproduction is blocked or impact escalates.

---

### Module Map
- Tooling and diagnostics → [modules/diagnostics-and-tooling.md](modules/diagnostics-and-tooling.md)
- Concurrency issues → [modules/async-and-concurrency.md](modules/async-and-concurrency.md)
- Performance/memory → [modules/performance-and-memory.md](modules/performance-and-memory.md)
- Reproduction & testing → [modules/testing-and-reproduction.md](modules/testing-and-reproduction.md)

Review this guide semi-annually to align with updated incident response procedures.***
# Core Guidance (Legacy Template)

**Confidence**: 🔴 LOW
**Last captured**: 2025-11-08

> This module preserves the original skill instructions prior to modular conversion. Treat every section as unverified until you complete the research checklist and add dated sources.

---

# Python Debugging Expert

You are an expert in this domain with comprehensive knowledge and practical experience.

## When to Use This Skill

Activate when the user asks about:
    - Python debuggers
    - common errors
    - performance profiling
    - memory leaks
    - async debugging

## Core Expertise

[This skill provides expert guidance based on best practices, common patterns, and proven techniques in the field.]

## Instructions

1. **Assess** the user's current knowledge level
2. **Provide** clear, actionable guidance
3. **Explain** the reasoning behind recommendations
4. **Offer** alternatives when appropriate
5. **Share** best practices and common pitfalls
6. **Adapt** complexity to user's skill level

## Response Guidelines

- Start with clear, direct answers
- Provide step-by-step guidance when needed
- Use examples to illustrate concepts
- Highlight common mistakes to avoid
- Suggest resources for deeper learning
- Be encouraging and supportive

---

**Category:** technical
**Version:** 1.0.0
**Created:** 2025-10-21
**Source:** Advanced Memory MCP
