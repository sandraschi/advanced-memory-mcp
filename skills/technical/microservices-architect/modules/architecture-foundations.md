# Architecture Foundations

**Confidence**: 🟡 Medium  
**Last validated**: 2025-11-08  
**Primary sources**: Domain-Driven Design Quickly (2025 update), Team Topologies (2024 rev), Microservices Patterns 2e draft (2025), CNCF Reference Model (2024)

---

## 1. Service Boundary Design

- Anchor services on **domain capabilities** (DDD bounded contexts).  
- Avoid splitting on technical layers (e.g., “logging service”) unless clear ownership.  
- Validate independence via use cases: can the service change/deploy without cross-team coordination?  
- Use context mapping to document upstream/downstream relationships and data ownership.

---

## 2. Team Topology Alignment

- Apply Stream-aligned teams for core services; enablement teams for shared platforms.  
- Limit cognitive load per team (< 2 critical services).  
- Use “interface teams” or platform APIs for shared components to avoid coordination overhead.

---

## 3. Deployment Topologies

- Choose between **service per container**, **sidecar patterns**, or **modular monolith** depending on maturity.  
- Evaluate infrastructure: Kubernetes, serverless, service fabric; ensure runtime supports language/runtime diversity needs.  
- Standardize baseline infrastructure (logging, metrics, tracing libraries) across services.

---

## 4. Communication Styles

- Default to synchronous REST/gRPC for request-response; ensure retries/backoff and circuit breakers.  
- Adopt event-driven architectures for decoupling (Kafka, NATS, Pulsar); define event versioning policy.  
- Use service mesh or API gateway for cross-cutting concerns (auth, rate limiting, routing).  
- Document SLAs/SLOs per interface.

---

## 5. Architectural Decision Records

- Maintain ADRs per service for technology choices, protocols, data ownership.  
- Establish review cadence (quarterly).  
- Link ADRs to service catalog and developer portal.

---

### Checklist
- [ ] Bounded contexts identified with service ownership mapped to teams.  
- [ ] Communication styles chosen with resilience patterns documented.  
- [ ] Deployment topology and platform stack agreed and documented.  
- [ ] ADR process active with historical decisions accessible.  
- [ ] Service catalog up-to-date (capabilities, contacts, SLOs).

Solid foundations prevent the architecture from devolving into distributed monoliths.*** End Patch

