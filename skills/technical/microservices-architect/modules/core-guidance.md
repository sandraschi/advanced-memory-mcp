# Core Guidance

**Confidence**: 🟡 MEDIUM  
**Last validated**: 2025-11-08

> Use this module to understand whether microservices solve the right problem, clarify scope, and align stakeholders before designing service boundaries.

---

## 1. Discovery Checklist

| Question | Why it matters |
| --- | --- |
| What pain are we solving (deployment cadence, team autonomy, scalability)? | Avoid microservices “for fashion”; focus on measurable outcomes. |
| Current architecture maturity (monolith, modular monolith, service-based)? | Determines migration path and interim patterns. |
| Team topology and ownership model? | Team boundaries should map to service boundaries (Team Topologies). |
| Platform readiness (CI/CD, observability, runtime platform)? | Microservices amplify operational complexity; verify platform support. |
| Compliance/security constraints? | Plan for zero-trust networking, audit trails, data residency. |

Record answers in an architecture decision record (ADR).

---

## 2. Success Metrics

- Lead time for change, deployment frequency, change failure rate, MTTR.  
- Team autonomy indicators: MTTR for independent teams, backlog throughput.  
- Operational metrics: p95 latency, error budgets, cost per request.  
- Set baseline and target values to evaluate microservices adoption.

---

## 3. Migration Strategy

1. **Strangle**: carve out features via strangler fig pattern; maintain contract compatibility.  
2. **Modular Monolith**: ensure boundaries exist before extraction.  
3. **Service Sizing**: start larger (“macroservices”), iterate when deployment pain requires finer granularity.  
4. **Platform Hardening**: CI/CD, observability, service discovery in place before large-scale split.

---

## 4. Anti-pattern Radar

- “Nanoservices” with tightly coupled functionality.  
- Shared databases without ownership boundaries.  
- No centralized contract governance leading to drift.  
- Overreliance on synchronous REST without resilience.  
- Teams reorganizing without aligning service ownership.

Escalate when anti-patterns arise; schedule architecture review.

---

## 5. Stakeholder Alignment

- **Engineering**: service ownership, deployment responsibilities, on-call rotation.  
- **Product**: release cadence, dependency management across teams.  
- **Security**: policies for authn/z, secret rotation, compliance.  
- **Platform/SRE**: infrastructure cost, observability stack, incident management.

Hold kick-off workshop; document agreements in playbook.

---

### Module Map
- Service decomposition → [modules/architecture-foundations.md](modules/architecture-foundations.md)  
- Contract & integration patterns → [modules/service-contracts-and-integration.md](modules/service-contracts-and-integration.md)  
- Data strategy → [modules/data-and-transaction-strategy.md](modules/data-and-transaction-strategy.md)  
- Operational excellence → [modules/platform-operations.md](modules/platform-operations.md)  
- Governance & compliance → [modules/security-and-compliance.md](modules/security-and-compliance.md)  
- Follow-ups → [modules/known-gaps.md](modules/known-gaps.md)

Review this intake guide semi-annually to keep criteria aligned with organizational goals.***
# Core Guidance (Legacy Template)

**Confidence**: 🔴 LOW  
**Last captured**: 2025-11-08

> This module preserves the original skill instructions prior to modular conversion. Treat every section as unverified until you complete the research checklist and add dated sources.

---

# Microservices Architect

You are an expert in this domain with comprehensive knowledge and practical experience.

## When to Use This Skill

Activate when the user asks about:
    - service boundaries
    - API gateways
    - service mesh
    - event-driven architecture
    - distributed tracing

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
