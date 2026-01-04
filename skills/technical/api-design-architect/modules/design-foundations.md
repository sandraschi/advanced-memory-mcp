# Design Foundations

**Confidence**: 🟡 Medium
**Last validated**: 2025-11-08
**Primary sources**: Microsoft REST API Guidelines (2024), GraphQL Spec (June 2024), gRPC Best Practices (Google, 2024), AsyncAPI 3.0.0 (2025 RC), CNCF API Landscape (2025-03)

---

## 1. RESTful APIs (HTTP/JSON)

### 1.1 Resource Modelling
- Model nouns, not verbs. Prefer `/orders/{id}` over `/getOrder`.
- Use collection + element pattern; expose sub-resources only when ownership is clear (e.g. `/orders/{id}/items`).
- Apply sparse fieldsets (`?fields=id,name,status`) to keep payloads small; default fields should satisfy 80% of use cases.
- Document canonical URIs; discourage guessable expansion via `Link` headers and documentation.

### 1.2 HTTP Semantics
- Strictly align verbs: `GET` (safe, idempotent), `POST` (non-idempotent create/actions), `PUT/PATCH` (idempotent updates).
- Return the most specific status code (422 > 400 for validation errors, 409 for concurrency conflicts).
- Use standard error shape (RFC 7807 Problem Details) with machine parseable `type` URIs.

### 1.3 Payload Conventions
- Adopt JSON:API or Microsoft guideline naming: lower_snake_case for fields, plural collection names.
- Support ETag semantics for concurrency control; require `If-Match` on destructive operations.
- Provide pagination metadata and HATEOAS links (`next`, `prev`, `self`). Offset pagination is fine for <10k records; switch to cursor-based for large datasets.

### 1.4 Versioning
- Default to URI prefix (`/v1/`) for major versions; use newsletters + deprecation headers for sunsetting.
- Avoid query-string versions; prefer minor changes guarded via feature negotiation headers.
- For internal APIs, permit header-based schema negotiation if experience in SDKs is mature.

---

## 2. GraphQL APIs

### 2.1 Schema Design
- Break schema into domain modules with federation or schema stitching; each service owns its subgraph.
- Keep field names descriptive; avoid abbreviations.
- Compose pagination through Relay spec connections to standardise tooling.
- Expose enums for finite state machines; attach `@deprecated` directives with explanations.

### 2.2 Performance Controls
- Prevent N+1 query explosions with DataLoader (or resolvers that batch by primary key).
- Enforce query cost limits: depth (max 8), complexity scoring, and query whitelists for public APIs.
- Enable Automatic Persisted Queries (APQ) in production to reduce attack surface.

### 2.3 Mutation Patterns
- Use input types with IDs and nested payloads; return domain objects plus `userErrors` arrays.
- Implement optimistic concurrency with version fields or global mutation IDs.
- Provide subscriptions/webhooks for event-based updates when latency requirements dictate.

### 2.4 Security
- Validate queries before execution; apply field-level auth in resolver layer.
- Sanitize user-supplied directives/aliases; disable introspection in prod unless behind auth.
- Monitor GraphQL-specific vulnerabilities (GraphQL CWE Top 10).

---

## 3. gRPC APIs

### 3.1 Contract-First Workflow
- Store protobuf definitions in a central repo; review via buf.build/Spectral.
- Use explicit packages and versioning (`package payments.v1;`).
- Generate language-specific clients via CI to ensure parity.

### 3.2 Design Considerations
- Prefer unary calls for request/response; adopt streaming for telemetry or large datasets.
- Keep messages granular; avoid huge nested structures that cause head-of-line blocking.
- Document error mapping (gRPC status codes ↔ domain errors).

### 3.3 Interoperability
- Provide JSON transcoding for web clients when HTTP/JSON needs exist.
- Ensure load balancing (pick-first vs round-robin) is tuned for your infrastructure.
- Use deadlines and retry policies; expose defaults via client configuration docs.

---

## 4. Event-Driven / AsyncAPI

### 4.1 Channel Design
- Model events around business facts (`order.created`), not infrastructure triggers.
- Maintain versioned schemas; publish change logs; adopt schema registry with compatibility modes.
- Provide consumer groups guidance (Kafka partitions, NATS JetStream, etc.).

### 4.2 Reliability
- Document delivery semantics (at-least-once vs exactly-once) and idempotency tokens.
- Include replay and dead-letter queue strategies; specify TTLs for unprocessed events.

### 4.3 Documentation
- Use AsyncAPI to describe channels, bindings, examples.
- Offer event catalog browse experience; link to downstream processors.

---

## 5. Cross-Cutting Concerns

### 5.1 Consistency Rules
- Align naming, error formats, and auth flows across protocols.
- Provide platform-level guidelines (e.g., standard HTTP headers, trace propagation).

### 5.2 Tooling Stack
- Linting: Spectral (REST), graphql-schema-linter, buf, AsyncAPI CLI.
- Mocking: Prism, WireMock, MockLab, Mirage.
- Testing: Contract tests (PACT, Dredd), integration harnesses, load testing (k6, Gatling).

### 5.3 Documentation
- Automate doc generation (Redocly, Stoplight, GraphQL Voyager, Buf Studio).
- Maintain “Getting Started” quickstart + SDK samples.

---

### Quick Reference
- REST quickstart: Create OpenAPI spec → run Spectral lint → generate Postman collection → publish docs with Redocly.
- GraphQL quickstart: Model schema modules → configure Apollo Gateway with federation → enforce query limits in server config.
- gRPC quickstart: Define proto → run buf lint/build → generate stubs → document with buf registry or Connect docs.
- Async quickstart: Draft AsyncAPI spec → publish to event catalog → create consumer onboarding checklist.

Review this module whenever you adopt a new protocol or when major spec revisions ship. Update `metadata.sources` with any new guidance you incorporate.*** End Patch
