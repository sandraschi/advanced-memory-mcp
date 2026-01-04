# Security & Observability

**Confidence**: 🟡 Medium
**Last validated**: 2025-11-08
**Primary sources**: OWASP API Security Top 10 (2023), NIST SP 800-204D (2024), CNCF Observability Whitepaper (2025), Google SRE Workbook (2024)

---

## 1. Secure-by-Default Principles

1. **Authentication**
   - External APIs: OAuth 2.1 client credentials or authorization code flow with PKCE.
   - Internal service-to-service: mTLS + SPIFFE/SPIRE or workload identity.
   - GraphQL/gRPC: enforce auth at gateway and resolver/method level.

2. **Authorization**
   - Centralised policy engine (OPA/Styra, AWS Verified Permissions) or fine-grained RBAC/ABAC.
   - Enforce least privilege scopes; document required claims.
   - For GraphQL, use field-level guards; for REST, check resource ownership in handlers.

3. **Input Validation**
   - Server-side validation using JSON Schema / zod / Joi / protobuf validation libraries.
   - Reject requests failing linting before hitting business logic.
   - Escape outputs; sanitize GraphQL query aliases to prevent injection.

4. **Rate Limiting & Throttling**
   - Implement global + per-consumer rate limits.
   - Communicate quotas via headers (`X-RateLimit-Limit`, `X-RateLimit-Remaining`).
   - Provide burst allowances for partner integrations and document escalation path.

5. **Data Protection**
   - Enforce TLS 1.3 externally; TLS 1.2+ internally.
   - Encrypt sensitive fields at rest; tokenise PII where possible.
   - Redact secrets in logs and traces.

---

## 2. Threat Modelling Checklist

- Use STRIDE or LINDDUN for each endpoint; document mitigations.
- Identify BOLA (Broken Object Level Authorization) risks, injection vectors, and mass assignment possibilities.
- Ensure error responses avoid leaking implementation detail.
- For GraphQL, test for introspection abuse, insecure batching, and alias-based DoS.
- Validate third-party dependencies (libraries, gateways) with SBOM and vulnerability scans.

---

## 3. Testing & Automation

- Security unit tests: verify auth checks, scope validation, and e2e token flows.
- Dynamic API security testing (DAST) using OWASP ZAP, StackHawk, or 42Crunch.
- Contract-level fuzzing: Schemathesis, InSpectre for OpenAPI; GraphQL Conformance for GraphQL.
- Integrate security tests in CI; block if high severity issues > 0.

---

## 4. Observability Baseline

### 4.1 Telemetry
- **Tracing**: adopt OpenTelemetry; propagate `traceparent` headers across services.
- **Metrics**: collect RED metrics (Rate, Errors, Duration) per endpoint + business KPIs.
- **Logs**: structured JSON logs with correlation IDs and request context; set retention by compliance needs.

### 4.2 SLOs
- Define P50/P90/P99 latency targets and error budgets for each API surface.
- Create burn-rate alerts (2h, 6h windows).
- Track saturation metrics: CPU, memory, queue depth, DB connections.

### 4.3 Dashboards
- Build Grafana/Datadog dashboards: overall health, top endpoints, consumer breakdown, version adoption.
- Add anomaly detection for suspicious usage (spikes, geo anomalies).
- Link runbooks and playbooks in dashboard annotations.

---

## 5. Runtime Guardrails

- Circuit breakers with fallback responses; configure retries with exponential backoff (max 3).
- Global API gateway to enforce WAF rules, JWT validation, schema validation, bot detection.
- Shadow traffic testing before major releases; compare telemetry between shadow and control.

---

## 6. Compliance & Audit

- Maintain audit logs of access tokens, admin actions, and schema changes.
- Keep evidence of threat models, pentest reports, SOC2 controls.
- Document data residency and retention policies; provide DSAR process if handling personal data.

---

### Quick Actions
- **Security review**: run OWASP ASVS Level 2 checklist, update threat model, confirm log redaction.
- **Pre-launch**: verify rate limits work, mTLS certificates rotate automatically, and fail-open scenarios are mitigated.
- **Post-incident**: capture timeline, update playbooks, adjust metrics thresholds, run learning review.

Update this module whenever OWASP or relevant standards publish revisions, or when observability tooling changes materially.*** End Patch
