# Core Guidance

**Confidence**: 🟡 MEDIUM  
**Last validated**: 2025-11-08

> Start here to understand pipeline maturity, stakeholder needs, and platform constraints before diving into detailed implementation modules.

---

## 1. Rapid Assessment

| Question | Why it matters | Notes |
| --- | --- | --- |
| What is the target lead time for changes? | Aligns with DORA metrics and influences pipeline parallelism. | Record baseline lead time & desired improvement. |
| How many deployment targets/environments exist? | Drives environment promotion strategy and infrastructure orchestration. | Map dev → staging → prod (or multi-region). |
| What compliance or audit requirements apply? | Determines evidence retention, approvals, segregation of duties. | e.g., SOX, PCI, ISO 27001. |
| Toolchain preferences/constraints? | Influences platform choice (GitHub Actions, GitLab, Jenkins, Azure DevOps). | Note managed vs self-hosted runners. |

Document answers in the pipeline design brief stored alongside the repo.

---

## 2. Pipeline Maturity Ladder

| Level | Characteristics | Next Steps |
| --- | --- | --- |
| **Bronze** | Manual approvals, basic build/test, limited environments. | Automate lint/tests, introduce artifact repository, set up trunk-based merges. |
| **Silver** | Automated testing + deployments, infra as code, canary or blue/green options. | Add observability checks, policy-as-code, progressive delivery controls. |
| **Gold** | Fully automated releases, feature flags, continuous verification, auditable controls. | Expand chaos testing, automated rollback, predictive analytics. |

Assess current stage and use modules to target upgrades.

---

## 3. Platform Decision Helpers

| Constraint | Recommended Platform | Notes |
| --- | --- | --- |
| GitOps-first, Kubernetes heavy | GitHub Actions + ArgoCD, Flux | Pair with OIDC-based secrets, ephemeral runners. |
| Self-hosted / air-gapped | Jenkins with Configuration as Code or GitLab Self-Managed | Requires hardened agents, SLSA provenance focus. |
| Multi-cloud SaaS | GitHub Actions, CircleCI, Harness | Evaluate per-minute pricing vs runner fleet costs. |
| Enterprise approvals | Azure DevOps Pipelines | Use environment approvals, branch policies, Azure AD integration. |

Document the rationale in an ADR before implementation.

---

## 4. Stakeholder Communication

- **Developers**: emphasise faster feedback, self-service pipelines, rollback safety.  
- **Security/compliance**: highlight policy-as-code, SBOM generation, audit logging.  
- **Ops/SRE**: show deployment guardrails, observability, and roll-forward vs rollback plans.  
- **Leadership**: present DORA metrics baseline and improvement targets.

Schedule quarterly demos of pipeline improvements to sustain buy-in.

---

## 5. Quick Response Templates

| Scenario | Recommended module & actions |
| --- | --- |
| “We need to add integration tests without slowing delivery.” | See `quality-gates-and-observability.md` → Test staging matrix → parallelisation patterns. |
| “How do we satisfy SLSA v1.0?” | Use `security-and-compliance.md` → Provenance generation → signing & attestations. |
| “Multi-service monorepo – how to avoid rebuild storms?” | `pipeline-foundations.md` → Selective builds via Bazel/Nx → path-based workflows. |
| “Our approvals are slowing deployment.” | `quality-gates-and-observability.md` → Automated evidence bundles + conditional approvals. |

---

### Related Modules
- Architecture and tooling → [modules/pipeline-foundations.md](modules/pipeline-foundations.md)
- Quality and metrics → [modules/quality-gates-and-observability.md](modules/quality-gates-and-observability.md)
- Security & audit → [modules/security-and-compliance.md](modules/security-and-compliance.md)
- Ongoing work → [modules/known-gaps.md](modules/known-gaps.md)

Review this core module whenever pipeline scope changes or a new platform is introduced.*** End Patch
