# Core Guidance

**Confidence**: 🟡 MEDIUM
**Last validated**: 2025-11-08

> Use this module as the decision hub before diving into the deeper playbooks. It helps you triage the request, pick the right protocol, and surface the most relevant supporting module.

---

## 1. Triage Checklist (2 minutes)

1. **Interaction style** – Are consumers internal, partner, or public? Do they need synchronous request/response, streaming, or messaging?
2. **Domain stability** – How often do resource models change? High churn may point to GraphQL or event-based approaches; stable domains pair well with REST or gRPC.
3. **Contract ownership** – Who owns schema governance? Central platform teams favour contract-first specs; product squads may prefer code-first with strong linting.
4. **SLAs/SLOs** – What latency/availability targets are required? Align transport (HTTP/2, HTTP/3, gRPC) and caching strategy accordingly.
5. **Compliance surface** – Any regulatory constraints (PII, PCI, HIPAA) that demand audit trails, data residency, or schema redaction?

Record answers in the discovery section of your design doc before moving forward.

---

## 2. Protocol Selection Matrix

| Context | Recommended Style | Key Modules |
| --- | --- | --- |
| Resource-centric, broad consumer base, HTTP ecosystems | REST with JSON:API / Microsoft guidelines | `design-foundations` Sections 1–2 |
| Complex domain, schema evolution, client-driven queries | GraphQL with schema federation | `design-foundations` Section 3 |
| Low-latency, typed payloads, service-to-service | gRPC with protobuf contracts | `design-foundations` Section 4 |
| Event-driven integrations, async workflows | AsyncAPI + event sourcing patterns | `design-foundations` Section 5 |

Use the matrix to justify the protocol in your architecture decision record (ADR).

---

## 3. Deliverable Checklist

| Phase | Deliverable | Owner |
| --- | --- | --- |
| Discovery | Context diagram, capability map, consumer interviews | Product + Platform |
| Design | Contract draft (OpenAPI/GraphQL SDL/Proto/AsyncAPI), field-level glossary | API architect |
| Review | Threat model, performance budget, backwards-compatibility plan | Security + SRE |
| Launch | Documentation site, SDKs/Postman collection, rollout plan | Developer experience team |
| Operate | SLO dashboard, error budget policy, change log | Reliability engineering |

Map these to your organisation’s definition of done (DoD) and incorporate in `lifecycle-and-governance.md`.

---

## 4. Escalation Triggers

- **Consumer confusion** – If more than 20% of consumers ask how to compose endpoints, revisit resource granularity.
- **Breaking changes** – If more than two breaking changes are proposed per quarter, enable stricter API review or adopt consumer-driven contracts.
- **Latency regressions** – If P95 increases >10% after a change, run load tests and evaluate N+1 query patterns or pagination defaults.
- **Security incidents** – Any failed OWASP API Top 10 check forces a regression test run and documentation update.

Cross-reference with `security-and-observability.md` for mitigation steps.

---

## 5. Quick Responses (Prompts)

| Scenario | Response Outline |
| --- | --- |
| “How do we version our REST API?” | Point to `lifecycle-and-governance.md` → Versioning strategies (URI vs header vs content negotiation) → recommend semantic versioning with sunset headers. |
| “We need GraphQL but fear N+1 issues.” | Direct to `design-foundations.md` → GraphQL data loaders & caching → `security-and-observability.md` instrumentation guidance. |
| “Partners require SLA commitments.” | Use `lifecycle-and-governance.md` rollout guardrails + `security-and-observability.md` monitoring templates. |
| “How do we document gRPC services?” | Reference `design-foundations.md` gRPC section + `lifecycle-and-governance.md` doc tooling (buf.build, Spectral). |

Having quick outlines accelerates conversations and preserves consistency.

---

### Related Modules
- Deep design patterns → [modules/design-foundations.md](modules/design-foundations.md)
- Change governance → [modules/lifecycle-and-governance.md](modules/lifecycle-and-governance.md)
- Security & telemetry → [modules/security-and-observability.md](modules/security-and-observability.md)
- Outstanding work → [modules/known-gaps.md](modules/known-gaps.md)

Keep this module lightweight; revisit quarterly to ensure heuristics mirror production reality.
