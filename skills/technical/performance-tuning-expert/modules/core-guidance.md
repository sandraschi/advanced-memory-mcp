# Core Guidance

**Confidence**: 🟡 MEDIUM
**Last validated**: 2025-11-08

> Start here to define success criteria, scope the investigation, and prioritize performance work for maximum impact.

---

## 1. Intake Assessment

| Question | Why it matters |
| --- | --- |
| What user-facing symptoms exist (slow pages, API latency, resource saturation)? | Focus metrics on real impact. |
| Which metrics/SLOs are breached? | Clarifies urgency and target thresholds. |
| What changed recently (deployments, infra, traffic patterns)? | Helps identify regression root cause. |
| What is the business priority? | Aligns tuning with product outcomes and resource allocation. |

Document baseline metrics before tuning.

---

## 2. Prioritization Framework

- Evaluate improvements by **value vs effort**; tackle high-impact, low-effort items first.
- Consider cost of regression to avoid premature optimization.
- Communicate trade-offs (e.g., caching increases complexity) with stakeholders.

---

## 3. Workflow Overview

1. **Instrument** – ensure metrics/traces/logs capture necessary detail.
2. **Profile** – gather data with profilers/benchmarks.
3. **Analyze** – locate hotspots, bottlenecks, architectural debt.
4. **Optimize** – apply targeted fixes; avoid shotgun changes.
5. **Validate** – re-run benchmarks, load tests; compare to baseline.
6. **Guard** – bake in regression tests/alerts.

---

## 4. Stakeholder Alignment

- **Product/UX** – define performance budgets and user impact.
- **Engineering** – coordinate code-level changes across teams/services.
- **Ops/SRE** – plan infrastructure adjustments, scaling, incident response.
- **Finance** – understand cost implications of hardware upgrades or caching layers.

---

## 5. Anti-patterns to Watch

- Optimizing without baselines or clear metrics.
- Relying solely on synthetic benchmarks without real traffic validation.
- Over-indexing on micro-optimizations while architectural bottlenecks persist.
- Neglecting regression testing leading to performance whiplash.

Escalate when anti-patterns surface to redirect efforts.

---

### Module Map
- Instrumentation → [modules/profiling-and-metrics.md](modules/profiling-and-metrics.md)
- Backend tuning → [modules/backend-optimization.md](modules/backend-optimization.md)
- Client optimization → [modules/frontend-and-client.md](modules/frontend-and-client.md)
- Runtime/infrastructure → [modules/infrastructure-and-runtime.md](modules/infrastructure-and-runtime.md)
- Regression protection → [modules/regression-testing-and-guardrails.md](modules/regression-testing-and-guardrails.md)

Review this guidance semi-annually to ensure prioritization aligns with evolving product KPIs.***
# Core Guidance (Legacy Template)

**Confidence**: 🔴 LOW
**Last captured**: 2025-11-08

> This module preserves the original skill instructions prior to modular conversion. Treat every section as unverified until you complete the research checklist and add dated sources.

---

# Performance Tuning Expert

You are an expert in this domain with comprehensive knowledge and practical experience.

## When to Use This Skill

Activate when the user asks about:
    - profiling tools
    - caching strategies
    - algorithm optimization
    - database tuning
    - CDN usage

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
