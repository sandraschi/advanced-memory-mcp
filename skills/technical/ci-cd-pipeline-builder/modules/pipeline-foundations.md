# Pipeline Foundations

**Confidence**: 🟡 Medium
**Last validated**: 2025-11-08
**Primary sources**: DORA 2024 Accelerate Report, GitHub Actions Runner v4 Docs (2025), GitLab CI/CD 16.11, Jenkins Configuration as Code (JCasC) 2025, ArgoCD 2.10 Docs

---

## 1. Architecture Blueprint

1. **Source of truth**: code + pipeline definitions in version control (`.github/workflows`, `.gitlab-ci.yml`, `Jenkinsfile`, etc.).
2. **Infrastructure as code**: Terraform/Pulumi/CloudFormation to provision build agents, artifact stores, environments.
3. **Artifact management**: store build outputs in artifact repo (GitHub Packages, Artifactory, Nexus, AWS CodeArtifact).
4. **Promotion flow**: build once → promote artifacts across environments; never rebuild downstream environments.
5. **Orchestration**: choose orchestrator (GitHub Actions, GitLab, Jenkins, Azure DevOps). Document triggers, fan-in/out patterns.

### Example Flow
```
Commit → Static checks → Unit tests → Build artifact → Security scans → Publish artifact → Deploy to staging → Integration tests → Canary → Production
```

---

## 2. Workflow Design Patterns

### 2.1 Trunk-Based Development
- Short-lived feature branches (≤ 2 days).
- Require status checks + code review + branch protection.
- Use merge queues (GitHub Merge Queue, GitLab Merge Trains) to avoid race conditions.

### 2.2 Selective Builds
- Monorepos: adopt path filters / Bazel / Nx to rebuild affected components only.
- Micro-repos: use reusable workflow templates to ensure consistency.

### 2.3 Deployment Strategies
- **Blue/Green**: maintain two identical environments; switch traffic using load balancer.
- **Canary**: progressive rollout (1% → 10% → 100%) with automated metrics checks.
- **Feature flags**: ensure fallbacks; prefer server-side toggles.

### 2.4 Rollback/Forward
- Automate rollback via previous artifact redeploy; keep change freeze windows for critical periods.
- Encourage roll-forward with hotfix branches + quick validation pipeline.

---

## 3. Environment Strategy

| Environment | Purpose | Controls |
| --- | --- | --- |
| Dev | Fast feedback, integration between services | Optional automated tests, allow snapshot DBs |
| Staging | Production-like verification | Required integration/regression tests, synthetic monitoring |
| Pre-prod / Canary | Live traffic with limited exposure | Feature flags, automated rollback |
| Production | Customer-facing | SLO monitoring, change approvals, automated rollback |

Automate environment provisioning via Terraform + Helm/ArgoCD; ensure config drift detection.

---

## 4. Tooling Recommendations

| Category | Tooling | Notes |
| --- | --- | --- |
| Workflow | GitHub Actions, GitLab CI, Jenkins (JCasC), Azure Pipelines | Select based on hosting needs, integration ecosystem |
| Artifacts | Artifactory, Nexus, GitHub Packages, AWS CodeArtifact | Support immutability, retention policies |
| Secrets | HashiCorp Vault, AWS Secrets Manager, GitHub OIDC | Prefer OIDC short-lived tokens over stored secrets |
| Infrastructure | Terraform, Pulumi, Crossplane | Integrate plan/apply into pipeline |
| Deployment | ArgoCD, Flux, Spinnaker, Harness | GitOps for Kubernetes, progressive delivery features |

Document chosen stack and maintenance responsibilities.

---

## 5. Parallelism & Performance

- Use job matrices and dynamic runners to parallelize tests; ensure total runtime < 10 minutes for CI step.
- Cache dependencies (npm, pip, Maven) with hashed keys; warm caches via scheduled jobs.
- Scale runners automatically (GitHub self-hosted autoscaling, GitLab Autoscaler, Jenkins Kubernetes plugin).
- Monitor queue times; keep < 2 minutes for fast feedback.

---

## 6. Disaster Recovery

- Back up pipeline configuration, secrets, and artifact metadata.
- Maintain secondary runners/region failover strategy.
- Run game days to rehearse pipeline outages and recovery steps.
- Document manual runbook for critical deployments if automation fails.

---

### Quick Reference
- **Bootstrap**: create repo → define reusable workflow templates → set branch protection → integrate IaC + artifact storage.
- **Migration**: audit existing jobs → convert to declarative pipelines → ensure idempotency → add policy gates.
- **Scaling**: implement autoscaling runners → adopt caching strategies → instrument queue times + DORA metrics.

Use this module as the foundation before layering quality gates and compliance controls.*** End Patch
