# Quality Gates & Observability

**Confidence**: 🟡 Medium  
**Last validated**: 2025-11-08  
**Primary sources**: DORA Accelerate 2024, Google SRE Workbook (2024), LaunchDarkly Progressive Delivery Guide (2025), GitHub Actions Environments (2025), GitLab 16.11 Deployment Analytics

---

## 1. Test Strategy Matrix

| Stage | Purpose | Typical Tools | Gate Type |
| --- | --- | --- | --- |
| Lint & static analysis | Fast syntax/style/security feedback | ESLint, Ruff, SonarQube, Trivy | Mandatory |
| Unit tests | Logic correctness | pytest, jest, go test | Mandatory (fail pipeline) |
| Integration tests | Service interaction | pytest + docker-compose, Postman, Pact | Mandatory |
| End-to-end / UI | User journeys | Playwright, Cypress, Selenium Grid | Conditional (run nightly / before prod) |
| Performance | SLO validation | k6, Gatling, Locust | Conditional (per release or threshold) |
| Chaos / resilience | Fault tolerance | Chaos Mesh, Gremlin | Optional (quarterly) |

Document expected runtime budgets per stage and keep < 10 minutes for CI feedback.

---

## 2. Automated Quality Gates

- **Branch protection**: require status checks, code review approval, signed commits if mandated.  
- **Coverage**: set thresholds (e.g., ≥ 80% for critical services) and enforce via coverage reports.  
- **Vulnerability scanning**: integrate SAST/DAST/SCA; fail builds on HIGH severity vulnerabilities.  
- **Policy-as-code**: use Open Policy Agent (OPA)/Conftest to enforce infra/security policies.  
- **Release approvals**: for production, require automated evidence bundle + manual approval by on-call or product owner if compliance demands.

---

## 3. Progressive Delivery

1. **Feature flags** – wrap risky changes; maintain flag lifecycle (creation, rollout, removal).  
2. **Canary analysis** – compare metrics between baseline and canary; use automated judgement (Kayenta, Argo Rollouts Analysis).  
3. **Shadow deployments** – route mirrored traffic to new version; monitor results before full rollout.  
4. **Automated rollback** – trigger on error budget burn, latency spikes, or feature flag kill switch.

---

## 4. Observability Integration

- Emit deployment events to tracing/logging systems (OpenTelemetry, Honeycomb, Datadog).  
- Track DORA metrics automatically: lead time, deployment frequency, change failure rate, MTTR.  
- Build dashboards per service showing latest deployment, responsible squad, feature flag states.  
- Configure alerts for pipeline health (queue time, failure rate) and release SLO violations.

### Example Metrics Bundle
- `deployment.frequency` (per day)  
- `deployment.success_rate` with failure reasons  
- `build.duration_p95` per repo  
- `queue.wait_time_avg`  
- `rollback.count` per month

---

## 5. Documentation & Evidence

- Generate release notes automatically from git history + issues.  
- Store test reports, security scans, and deployment approvals with retention (e.g., S3 bucket + immutability).  
- Provide “release health” summary for stakeholders after each deployment (Slack/Teams integration).

---

## 6. Continuous Improvement

- Run monthly deployment retros using DORA metrics.  
- Track flaky tests; auto-quarantine but report root cause timeframe < 7 days.  
- Introduce experimentation (A/B) and continuous verification loops for critical services.

---

### Checklist
- [ ] Status checks blocking merges configured.  
- [ ] Automated evidence bundle generated per release (tests, scans, approvals).  
- [ ] Deployment dashboard displays current version & SLOs.  
- [ ] Alerting on pipeline failures and release regressions.  
- [ ] Feature flag removal backlog reviewed weekly.

Use this module to maintain high confidence in every release while keeping feedback cycles fast.*** End Patch

