# Core Guidance

**Confidence**: 🟡 MEDIUM
**Last validated**: 2025-11-08

> Launch every refactoring effort with a clear why, measurable goals, and stakeholder alignment.

---

## 1. Refactoring Charter

| Element | Description |
| --- | --- |
| Business driver | e.g., faster feature delivery, reduce production bugs, regulatory requirement |
| Scope | Modules/packages affected, boundaries, exclusions |
| Success metrics | Lead time, defect rate, cycle time, code health score |
| Timebox/Budget | Sprint allocation, dedicated team, guardrails |
| Risks | Potential regressions, schedule impact, coordination with other teams |

Document charter in shared workspace; review with stakeholders.

---

## 2. Intake & Discovery

- Gather pain points from engineers, QA, support.
- Run codebase diagnostics (lint, static analysis, complexity metrics).
- Evaluate test coverage and automation maturity.
- Decide between opportunistic vs planned refactoring.

---

## 3. Prioritization Principles

- Tackle high-impact, high-risk areas with clear value.
- Favor refactoring in conjunction with feature work (“scout rule”).
- Avoid large big-bang rewrites unless supported by strong business case.
- Maintain incremental delivery with continuous integration.

---

## 4. Safety Guidelines

- Establish minimum test coverage or create characterization tests.
- Use feature flags or toggles for risky transformations.
- Ensure CI/CD pipeline is green before/after each slice.
- Plan rollback strategy for each milestone.

---

## 5. Communication Cadence

- Kick-off meeting with engineering + product + QA + stakeholders.
- Weekly updates on progress, risks, metrics.
- Retrospective post-completion capturing lessons learned.

---

### Module Map
- Assessment/prioritization → [modules/assessment-and-prioritization.md](modules/assessment-and-prioritization.md)
- Tactical patterns → [modules/refactoring-patterns.md](modules/refactoring-patterns.md)
- Safety nets → [modules/safety-net-and-testing.md](modules/safety-net-and-testing.md)
- Architecture modernization → [modules/architecture-modernization.md](modules/architecture-modernization.md)
- Stakeholder management → [modules/change-management-and-communication.md](modules/change-management-and-communication.md)

Review charter quarterly to ensure refactoring remains aligned with strategic goals.***
# Core Guidance (Legacy Template)

**Confidence**: 🔴 LOW
**Last captured**: 2025-11-08

> This module preserves the original skill instructions prior to modular conversion. Treat every section as unverified until you complete the research checklist and add dated sources.

---

# Refactoring Specialist

You are an expert in this domain with comprehensive knowledge and practical experience.

## When to Use This Skill

Activate when the user asks about:
    - refactoring patterns
    - technical debt
    - code smells
    - safe refactoring
    - legacy code

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
