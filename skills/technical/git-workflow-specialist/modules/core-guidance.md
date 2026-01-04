# Core Guidance

**Confidence**: 🟡 MEDIUM
**Last validated**: 2025-11-08

> Start here to understand team context, repository health, and workflow constraints before prescribing branching or tooling changes.

---

## 1. Intake Questions

| Topic | Key Questions |
| --- | --- |
| Team cadence | Release frequency? Number of concurrent initiatives? Distributed time zones? |
| Repository shape | Monorepo vs multi-repo? Size (>5GB)? Submodules? |
| Compliance | Auditing, segregation of duties, change control requirements? |
| Tooling | Hosting (GitHub, GitLab, Azure DevOps), CI/CD stack, code review tools? |
| Pain points | Merge conflicts, long-lived branches, flaky releases, review bottlenecks? |

Capture answers to inform branching strategy and automation priorities.

---

## 2. Workflow Readiness Checklist

- Enforced branch protection (status checks, reviews, signed commits if required).
- CI pipeline turnaround < 10 minutes for trunk builds.
- Release automation or manual steps documented.
- Clear Definition of Done (tests, docs, approvals).
- Backlog/ticket system integrated with commits/PRs.

If prerequisites missing, address them before adopting advanced workflows.

---

## 3. Decision Matrix (Workflow Selection)

| Scenario | Recommended Workflow | Notes |
| --- | --- | --- |
| Rapid delivery, feature flags, small teams | Trunk-Based Development | Requires strong CI and feature flag discipline. |
| Regulated environments, multiple release trains | GitFlow / Release Branching | Ensure hotfix paths well-documented. |
| SaaS with weekly releases, many squads | Trunk w/ Release Branches | Combine trunk for daily merges with short-lived release branches. |
| Monorepo with large platform team | Trunk + codeowners + merge queue | Automate gating and selective builds. |

Document chosen workflow in team handbook.

---

## 4. Stakeholder Alignment

- **Engineering**: expectations for branch lifespan, review SLA, conflict resolution.
- **Product**: release cadence, feature flag rollout strategy.
- **Security/Compliance**: sign-off requirements, audit logging, change control.
- **Platform/DevOps**: CI resources, merge queues, tooling ownership.

Conduct kickoff workshops when changing workflows; provide training.

---

## 5. Escalation Triggers

- Unmerged branches older than agreed SLA (e.g., >5 days).
- Frequent release rollback due to merge issues.
- Review queue backlog exceeding team limit.
- Compliance violations (missing approvals, unsigned commits) detected.
- Merge queue or CI instability affecting throughput.

Escalate to workflow steering group; capture action items in retro.

---

### Module Map
- Branching decisions → [modules/branching-strategies.md](modules/branching-strategies.md)
- Collaboration & reviews → [modules/collaboration-and-reviews.md](modules/collaboration-and-reviews.md)
- Automation → [modules/automation-and-tooling.md](modules/automation-and-tooling.md)
- Governance → [modules/maintenance-and-governance.md](modules/maintenance-and-governance.md)
- Outstanding work → [modules/known-gaps.md](modules/known-gaps.md)

Revisit this guidance semi-annually to ensure workflow choices still fit team maturity.*** End Patch
# Core Guidance (Legacy Template)

**Confidence**: 🔴 LOW
**Last captured**: 2025-11-08

> This module preserves the original skill instructions prior to modular conversion. Treat every section as unverified until you complete the research checklist and add dated sources.

---

# Git Workflow Specialist

You are an expert in this domain with comprehensive knowledge and practical experience.

## When to Use This Skill

Activate when the user asks about:
    - Git branching
    - merge conflicts
    - rebase vs merge
    - Git workflows
    - collaboration patterns

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
