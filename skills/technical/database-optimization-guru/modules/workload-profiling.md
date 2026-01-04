# Workload Profiling

**Confidence**: 🟡 Medium
**Last validated**: 2025-11-08
**Primary sources**: PostgreSQL 16 Monitoring Guide (2025), MySQL Performance Schema Cookbook (2024), AWS Performance Insights (2025), Google Cloud SQL Observability (2025)

---

## 1. Baseline Metrics

| Metric | Tooling | Notes |
| --- | --- | --- |
| Query latency percentiles (P50/P95/P99) | pg_stat_statements, Performance Schema, Datadog APM | Track per endpoint/workload. |
| Throughput (QPS/TPS) | CloudWatch, Prometheus exporters | Break down read vs write. |
| Wait events / locks | pg_stat_activity, sys.dm_os_wait_stats, MySQL sys schema | Identify contention. |
| Resource usage | CPU, memory, disk IO, network | Correlate with workload spikes. |
| Cache hit ratios | pg_statio, buffer pool metrics | Low hit rate indicates missing indexes or cache sizing issues. |

Collect baselines over representative intervals (peak vs off-peak).

---

## 2. Sampling Techniques

- Enable **slow query log** (threshold ~500ms) to capture heavy hitters.
- Use **pg_stat_statements** or **performance_schema.events_statements_summary_by_digest** for normalized query stats.
- Sample **EXPLAIN (ANALYZE, BUFFERS)** or `EXPLAIN FORMAT=JSON` snapshots for top queries.
- For cloud-managed services, ingest **Performance Insights** or **Query Store** data.

Ensure sampling runs outside critical windows to avoid extra load.

---

## 3. Benchmarking

- Reproduce workload using tools: pgBench, sysbench, HammerDB, YCSB.
- Mirror production schema and data volume in staging; scrub sensitive data.
- Record baseline latency/throughput before changes; repeat after each tuning iteration.
- Use connection poolers (PgBouncer, ProxySQL) in benchmarks to mimic production architecture.

---

## 4. Diagnostics Checklist

| Symptom | Investigation |
| --- | --- |
| High CPU, low IO | Query complexity, missing indexes, CPU-bound operations. |
| High IO, low CPU | Table scans, bloated indexes, insufficient caching. |
| Lock contention | Identify blocking sessions, long-running transactions, isolation levels. |
| High replication lag | Slow queries on replica, network saturation, disk performance. |
| Spiky latency | Autovacuum/maintenance interactions, auto-scaling events, plan cache thrash. |

---

## 5. Tooling Quick Reference

- **PostgreSQL**: `pg_stat_statements`, `pg_stat_io`, `auto_explain`, `pg_top`, `pgBadger`.
- **MySQL**: Performance Schema, `sys` schema views, `pt-query-digest`, `EXPLAIN ANALYZE`.
- **SQL Server/Azure**: Query Store, Extended Events, DMVs (`sys.dm_exec_query_stats`).
- **Managed services**: AWS Performance Insights, Cloud SQL Insights, Azure SQL Intelligent Insights.

---

### Checklist
- [ ] Baseline metrics captured for peak/off-peak.
- [ ] Top N slow queries identified with frequency and total time.
- [ ] Wait event analysis documented with hypotheses.
- [ ] Benchmark environment prepared with reproducible workload.
- [ ] Findings shared with stakeholders before implementing schema/query changes.

Use this module before and after any optimization to ensure changes measurably improve performance.*** End Patch
