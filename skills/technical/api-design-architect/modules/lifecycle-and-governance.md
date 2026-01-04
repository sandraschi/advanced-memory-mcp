# Lifecycle & Governance

**Confidence**: 🟡 Medium
**Last validated**: 2025-11-08
**Primary sources**: Stripe API Change Management (2024), Google Cloud API Lifecycle (2024), Stoplight Governance Playbook (2025), OWASP API Security Checklist (2023)

---

## 1. Governance Operating Model

- **Design authority**: Form an API review board with platform, security, SRE, DX, and product representation. Meet weekly for design reviews.
- **Design doc template**: Include capability map, consumer personas, error strategy, versioning plan, threat model summary, and rollout strategy.
- **Approval gates**: Require sign-off for security, backwards-compatibility, and documentation completeness before implementation begins.

### RACI Snapshot
| Task | Responsible | Accountable | Consulted | Informed |
| --- | --- | --- | --- | --- |
| API design doc | Product/API architect | Platform lead | Security, SRE, DX | Consumer teams |
| Contract linting | Platform tooling | API architect | Dev teams | Review board |
| Breaking change approval | API review board | Platform leadership | Support, Customer Success | All consumers |

---

## 2. Versioning & Change Management

1. **Semantic versioning** – Use `MAJOR.MINOR.PATCH`. Breaking changes bump MAJOR and must provide a deprecation plan.
2. **Deprecation protocol** – Minimum 90-day notice for external consumers; send email + developer portal announcements + `Sunset` headers.
3. **Change log** – Maintain human-readable release notes and machine-readable change feed (Atom/JSON).
4. **Compatibility tests** – Adopt consumer-driven contracts (CDC) or regression suites to detect breaking changes before deploy.
5. **Feature flags** – Wrap new endpoints/fields in opt-in flags to test with limited audiences.

### Breaking Change Guardrails
- Require ADR documenting rationale and mitigation.
- Provide migration guides and sample SDK patches.
- Monitor error rates for old vs new versions during overlap period.
- Automatically sunset deprecated versions when traffic falls below KPI threshold.

---

## 3. Documentation & Developer Experience

- **Single source of truth** – Store OpenAPI/GraphQL SDL/Proto in version control; generate docs automatically (Redocly, GraphQL Docs, Buf Registry).
- **Quickstarts** – Provide sample requests, Postman collections, and cURL examples.
- **SDK strategy** – Support at least two major languages for public APIs. Generate from contract; include semantic versioning and changelog.
- **Feedback loop** – Implement doc feedback widget; triage weekly. Track docs satisfaction NPS or doc effectiveness score.

---

## 4. Testing Strategy

| Layer | Purpose | Tooling |
| --- | --- | --- |
| Contract linting | Enforce naming, description, schema rules | Spectral, Stoplight, buf lint |
| Unit/Integration | Verify business logic | Jest, pytest, Go test, Postman/newman |
| Contract tests | Ensure backwards compatibility | PACT, Dredd, Schemathesis |
| Load tests | Validate SLO adherence | k6, Gatling |
| Chaos/resilience | Validate timeouts, retries, circuit breakers | Chaos Mesh, Gremlin |

Automate tests in CI; block merges when contract linting or CDC fails. Store test artefacts for compliance.

---

## 5. Rollout & Communication

1. **Launch checklist**
   - ✅ API contract approved
   - ✅ Threat model signed off
   - ✅ Monitoring dashboards live
   - ✅ Documentation published
   - ✅ Support runbook ready
2. **Beta → GA**
   - Beta consumers in feature flag → collect feedback → iterate
   - Publish GA timeline with migration plan
   - Provide office hours and sample code to unblock adoption
3. **Incident response**
   - Integrate API errors with on-call systems (PagerDuty).
   - Provide public status page with component-level reporting.
   - Run post-incident review; update docs & runbooks.

---

## 6. Metrics & KPIs

- **Adoption**: active apps, API call volume by version, time-to-first-call.
- **Quality**: error budgets, latency percentiles, schema linting pass rate.
- **DX health**: doc satisfaction, support ticket resolution time.
- **Governance**: % of APIs passing review on first submission, number of unapproved breaking changes detected.

Feed metrics into exec dashboards; tie to OKRs (e.g., “Reduce breaking change incidents by 80% QoQ”).

---

### Checklist Snapshot
- [ ] Design doc approved by review board.
- [ ] Contract linted and published.
- [ ] Versioning plan and deprecation policy documented.
- [ ] AuthN/Z and rate limits agreed with security.
- [ ] Observability dashboards live with error budgets.
- [ ] Change log entry drafted.
- [ ] SDKs and docs generated and peer reviewed.

Use this module whenever you move from design to launch or prepare quarterly governance reviews.*** End Patch
