# Service Contracts & Integration

**Confidence**: 🟡 Medium  
**Last validated**: 2025-11-08  
**Primary sources**: AsyncAPI 3.0 RC (2025), OpenAPI 3.1 Best Practices (2024), gRPC Design Guide (2025), NATS JetStream Patterns (2025)

---

## 1. Contract Standards

- REST/HTTP: OpenAPI 3.1 + JSON Schema; enforce linting (Spectral).  
- gRPC: Proto3 with buf build/lint; generate multi-language stubs.  
- Messaging: AsyncAPI for events; include schema versioning and delivery semantics.  
- Document backward compatibility expectations and deprecation policy.

---

## 2. Contract Governance

- Maintain centralized contract repository with automated linting and breaking change detection (e.g., Optic, Buf breaking).  
- Introduce contract review board with representatives from producer/consumer teams.  
- Automate publishing to developer portal with examples and SDKs.  
- Require consumer-driven contract tests (PACT, Pactflow, Hoverfly) for critical integrations.

---

## 3. Integration Patterns

- **Synchronous**: apply retries with exponential backoff, idempotency keys, circuit breakers (Resilience4j, Envoy).  
- **Asynchronous**: choose between pub/sub, event sourcing, CQRS; document ordering and idempotency guarantees.  
- **Batch/data pipelines**: use change data capture (Debezium) or scheduled extracts with schema evolution plan.

---

## 4. Versioning Strategy

- Backwards compatible changes should be default; communicate through semantic versioning or header negotiation.  
- For breaking changes, support side-by-side versions with migration window.  
- Provide release notes and migration guides for consumers; monitor adoption.

---

## 5. Testing & Observability

- Implement contract tests in CI for producers and consumers.  
- Emit integration metrics (success/failure rates, latency) per interface.  
- Trace requests end-to-end (W3C trace-context) to debug integration issues.  
- Log correlation IDs across services.

---

### Checklist
- [ ] Contracts stored, linted, and versioned with automation.  
- [ ] Integration patterns documented with resilience requirements.  
- [ ] Contract testing and monitoring integrated into CI/CD.  
- [ ] Deprecation and migration processes defined.  
- [ ] Developer portal or catalog exposes up-to-date contracts.

Reliable contracts are the backbone of sustainable microservices ecosystems.*** End Patch

