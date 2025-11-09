# Core Guidance

**Confidence**: 🟡 MEDIUM  
**Last validated**: 2025-11-08

> Establish context, risks, and goals before investing in new tests or automation frameworks.

---

## 1. Intake Assessment

| Question | Why it matters |
| --- | --- |
| Product risk profile | Safety-critical? Financial? Consumer app? Impacts test rigor. |
| Release cadence | Continuous delivery vs quarterly releases shapes automation needs. |
| Current pain points | Flaky tests, long pipelines, low coverage, regression escapes. |
| Team capabilities | In-house QA, developer testing culture, tooling expertise. |
| Compliance | Regulatory requirements (SOX, HIPAA, ISO) influence documentation. |

Document findings in test strategy charter.

---

## 2. Goals & Metrics

- Define SMART goals (e.g., reduce escaped defects by 40%, cut pipeline time by 30%).  
- Set target coverage types (unit, integration, E2E) and quality KPIs (MTTR, change failure rate).  
- Align with engineering/product leadership to secure buy-in.

---

## 3. Risk Matrix

- Map features/services to risk levels (critical, high, medium, low).  
- Allocate testing intensity based on risk (more integration/e2e for critical paths).  
- Reassess after major releases or incidents.

---

## 4. Governance

- Identify test strategy owner, QA leads, developer champions.  
- Schedule reviews (quarterly) to adjust plan.  
- Communicate expectations via engineering handbook and onboarding.

---

## 5. Escalation

- Define process for blocker bugs or test infrastructure failures.  
- Maintain incident channel for flaky tests and pipeline outages.  
- Track debt items in backlog with prioritization.

---

### Module Map
- Test portfolio planning → [modules/test-pyramid-and-planning.md](modules/test-pyramid-and-planning.md)  
- Automation architecture → [modules/automation-frameworks.md](modules/automation-frameworks.md)  
- Non-functional → [modules/non-functional-testing.md](modules/non-functional-testing.md)  
- CI & observability → [modules/ci-integration-and-observability.md](modules/ci-integration-and-observability.md)  
- Metrics → [modules/quality-metrics-and-governance.md](modules/quality-metrics-and-governance.md)

Review intake semi-annually to remain aligned with evolving product needs.***
# Core Guidance (Legacy Template)

**Confidence**: 🔴 LOW  
**Last captured**: 2025-11-08

> This module preserves the original skill instructions prior to modular conversion. Treat every section as unverified until you complete the research checklist and add dated sources.

---

# Testing Strategy Guide

You are an expert in this domain with comprehensive knowledge and practical experience.

## When to Use This Skill

Activate when the user asks about:
    - unit testing
    - integration tests
    - TDD/BDD
    - mocking
    - test coverage

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
