# Research Checklist

Run this checklist monthly or when major CI/CD platform releases drop.

## 1. Source Refresh
- [ ] DORA Accelerate research updates (https://dora.dev/research/).
- [ ] SLSA specification changes (https://slsa.dev/spec/).
- [ ] GitHub Actions, GitLab, Jenkins release notes for pipeline features.
- [ ] Progressive delivery tooling updates (LaunchDarkly, Harness, Argo Rollouts).

## 2. Platform Validation
- [ ] Smoke-test reusable workflow templates; confirm OIDC auth still succeeds.
- [ ] Validate autoscaling runners capacity; ensure build queue time < 2 minutes.
- [ ] Re-run reference pipeline across dev/staging/prod environments; confirm parity.
- [ ] Audit artifact retention policies and storage costs.

## 3. Security & Compliance
- [ ] Review OWASP CI/CD Security Top 10 for new recommendations.
- [ ] Regenerate SBOM + provenance for reference service; verify signatures.
- [ ] Audit secrets inventory, rotate stale tokens, and confirm vault policies.
- [ ] Run SAST/SCA/DAST on sample service and attach reports.

## 4. Documentation & Metrics
- [ ] Update pipeline runbooks, architecture diagrams, and escalation contacts.
- [ ] Export DORA metrics and compare against OKRs.
- [ ] Refresh screenshots/snippets embedded in developer portal docs.

## 5. Source Log
| Date | Source | Notes |
| --- | --- | --- |
| 2025-11-08 | DORA Accelerate 2024 | Deployment & reliability benchmarks |
| 2025-11-08 | SLSA v1.0 | Provenance + supply-chain requirements |
| 2025-11-08 | GitHub Actions Runner v4 Docs | Ephemeral runners, OIDC guidance |
| 2025-11-08 | GitLab CI/CD 16.11 | Merge queue & deployment analytics updates |

> Tip: Use `adn_skills("distill_from_wikipedia", topic="Continuous delivery")` for quick refreshers, then bootstrap workflow examples with `adn_skills("import_from_github", repository="org/repo", ...)` before validating against vendor docs.*** End Patch
