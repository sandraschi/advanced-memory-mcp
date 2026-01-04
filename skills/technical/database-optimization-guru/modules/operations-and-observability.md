# Operations & Observability

**Confidence**: 🟡 Medium
**Last validated**: 2025-11-08
**Primary sources**: AWS RDS/Aurora Operations Guide (2025), Google Cloud SQL Operations (2025), Azure SQL Managed Instance Best Practices (2024), Percona Monitoring and Management (PMM) Playbook (2025)

---

## 1. Capacity & Scaling

- Track resource headroom (CPU, memory, storage, IOPS). Alert when utilization exceeds 70% sustained.
- For cloud databases, evaluate vertical vs horizontal scaling, read replicas, or sharding.
- Implement connection pooling (PgBouncer, ProxySQL, SQL Server connection pooling) to stabilize workloads.
- Schedule maintenance windows for vacuuming, statistics updates, and index maintenance.

---

## 2. Caching & Replication

- Use application-level caches (Redis, Memcached) for hot reads; implement invalidation strategy.
- Configure read replicas for reporting/analytics; ensure lag monitoring and failover readiness.
- Consider materialized views or result caches for recurring heavy aggregations.
- Employ write-ahead logging shipping or CDC for downstream systems; monitor lag/backlog.

---

## 3. Monitoring Stack

- **Metrics**: Collect via Prometheus exporters, CloudWatch metrics, Azure Monitor. Key metrics: latency, throughput, replication lag, checkpoint duration, cache hit ratio, deadlocks.
- **Logs**: Enable slow query log, error log rotation, audit logs where required. Forward to centralized logging (ELK, Cloud Logging).
- **Tracing**: Instrument database spans in distributed tracing (OpenTelemetry) to correlate with app performance.
- Build dashboards & alerts (Grafana/Datadog) with runbook links.

---

## 4. Incident Response

- Maintain runbooks for common issues: locking, runaway queries, disk saturation, failover.
- Implement automatic query killers for long-running queries exceeding thresholds (pg_terminate_backend, ProxySQL).
- Test backup/restore regularly; document RPO/RTO.
- Perform chaos drills (replica failure, storage outage) to validate processes.

---

## 5. Cost Optimization

- Rightsize instances/storage; use storage auto-scaling where supported.
- Evaluate reserved instances or committed use discounts.
- Archive cold data to cheaper storage (external tables, BigQuery, S3).
- Purge obsolete indexes/materialized views to reduce storage and maintenance cost.

---

### Checklist
- [ ] Dashboards with key metrics/alerts linked to runbooks.
- [ ] Backups and restore tests validated within last quarter.
- [ ] Replication/caching strategies documented with owners.
- [ ] Maintenance plan scheduled (vacuum, index rebuild, stats).
- [ ] Cost monitoring in place with monthly review.

Operational excellence keeps optimized databases healthy and reliable after tuning changes.*** End Patch
