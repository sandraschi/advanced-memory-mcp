# Data & Transaction Strategy

**Confidence**: 🟡 Medium  
**Last validated**: 2025-11-08  
**Primary sources**: Designing Data-Intensive Applications 2e (2025 draft), CNCF Data on Kubernetes (2024), Martin Fowler Saga Pattern Updates (2025), Outbox/Inbox Pattern Guide (2024)

---

## 1. Data Ownership

- Assign a single service as system of record for each business aggregate.  
- Publish change events for downstream consumers; avoid shared database writes.  
- Maintain data catalog with ownership, retention, and residency requirements.

---

## 2. Consistency Models

- Classify operations needing strong vs eventual consistency.  
- Use sagas (orchestration, choreography) for multi-service transactions; document compensation logic.  
- For read models, adopt CQRS with materialized views or caching layers.  
- Evaluate transactional outbox pattern to ensure atomic event publishing.

---

## 3. Data Integration

- Implement CDC (Debezium, Maxwell) when legacy shared databases must coexist.  
- Use schema registry (Confluent, Redpanda) to manage evolution; enforce compatibility modes.  
- For analytics, build data pipeline (e.g., Kafka → Snowflake/BigQuery) with governance.

---

## 4. Storage Technology Choices

- Match storage engine to service needs (relational, document, time-series, graph).  
- Standardize on a small set of managed offerings to reduce cognitive load.  
- Document backup/restore, DR, and cost considerations per store.

---

## 5. Testing & Observability

- Create integration tests for sagas and compensation flows.  
- Monitor outbox/inbox queues, event lag, and replication health.  
- Implement data quality checks and anomaly detection (Great Expectations, dbt tests).

---

### Checklist
- [ ] Data ownership map documented with system-of-record per aggregate.  
- [ ] Consistency requirements captured with saga/outbox strategies defined.  
- [ ] Schema evolution and CDC processes in place.  
- [ ] Storage technology standard, backup/DR documented.  
- [ ] Data observability metrics and tests running in CI/production.

Clear data strategy prevents the distributed monolith trap and supports reliable business operations.*** End Patch

