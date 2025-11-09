# Core Guidance

**Confidence**: 🟡 MEDIUM  
**Last validated**: 2025-11-08

> Use this module to align on platform goals, constraints, and readiness before implementing container/Kubernetes solutions.

---

## 1. Intake Checklist

| Question | Why it matters |
| --- | --- |
| What workloads are targeted (stateful, stateless, batch, ML)? | Influences storage strategy, controllers, autoscaling. |
| Target environments (dev/staging/prod, multi-cloud, edge)? | Determines cluster topology and networking. |
| Compliance/security requirements? | Drives policy-as-code, image scanning, RBAC. |
| Delivery model (CI/CD, GitOps, platform team vs product team)? | Sets expectations for tooling and automation modules. |
| SLOs (availability, latency, recovery)? | Guides scaling, observability, incident runbooks. |

Document answers in an architecture brief before design work.

---

## 2. Platform Fit Assessment

- Evaluate whether managed Kubernetes (EKS/GKE/AKS), self-hosted, or alternative (Nomad, ECS, Cloud Run) is appropriate.  
- Consider build vs buy: do teams have ops capability to run clusters 24/7?  
- Assess data services: externalize databases/message queues unless strong reason to run in-cluster.  
- Identify ecosystem integrations (service mesh, ingress, secrets, logging).

---

## 3. Maturity Ladder

| Level | Characteristics | Next Steps |
| --- | --- | --- |
| **Foundation** | Containerized apps, basic manifests, manual deployments | Set up registries, implement CI builds, define namespaces. |
| **Intermediate** | CI/CD pipelines, Helm/Kustomize, monitoring in place | Introduce GitOps, policy enforcement, autoscaling. |
| **Advanced** | Multi-cluster, service mesh, progressive delivery, SLOs | Add chaos engineering, cost optimization, platform APIs. |

Use the ladder to set roadmap targets with stakeholders.

---

## 4. Stakeholder Alignment

- **App teams**: define onboarding process, responsibilities for manifests vs platform modules.  
- **Security**: agree on scanning, RBAC, secrets, network policies.  
- **Ops/SRE**: establish observability, incident response, capacity planning.  
- **Finance**: track cost per cluster/workload, implement governance.

---

## 5. Escalation Triggers

- Frequent pod evictions or crash loops without clear root cause.  
- Security scan failures blocking releases with no remediation plan.  
- Cluster capacity < 20% headroom or frequent scaling failures.  
- Network policy misconfigurations causing outages.  
- Governance/gating inconsistencies between environments.

Escalate to platform steering group; document incidents and action items.

---

### Module Map
- Foundations → [modules/platform-foundations.md](modules/platform-foundations.md)  
- Deployment patterns → [modules/deployment-patterns.md](modules/deployment-patterns.md)  
- Security & compliance → [modules/security-and-compliance.md](modules/security-and-compliance.md)  
- Operations → [modules/observability-and-operations.md](modules/observability-and-operations.md)  
- Follow-ups → [modules/known-gaps.md](modules/known-gaps.md)

Review this guidance quarterly to stay aligned with evolving platform strategy.*** End Patch
# Core Guidance (Legacy Template)

**Confidence**: 🔴 LOW  
**Last captured**: 2025-11-08

> This module preserves the original skill instructions prior to modular conversion. Treat every section as unverified until you complete the research checklist and add dated sources.

---

# Docker and Kubernetes Pro

You are an expert in this domain with comprehensive knowledge and practical experience.

## When to Use This Skill

Activate when the user asks about:
    - Dockerfile optimization
    - Kubernetes deployments
    - container networking
    - helm charts
    - microservices

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
