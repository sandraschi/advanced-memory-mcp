# Research Checklist

Run this verification every 6 months or after major engine releases.

## 1. Source Refresh
- [ ] PostgreSQL release notes & performance docs (https://www.postgresql.org/docs/current/).  
- [ ] MySQL/Percona performance schema updates (https://dev.mysql.com/doc/).  
- [ ] Cloud provider tuning guides (AWS RDS/Aurora, GCP Cloud SQL/Spanner, Azure SQL).  
- [ ] Vendor blog posts on new optimizer features or index types.

## 2. Benchmark & Metrics Review
- [ ] Re-run baseline benchmarks on staging with production-like data.  
- [ ] Compare latency/throughput against historical baselines.  
- [ ] Audit wait event and slow query reports for new hotspots.  
- [ ] Validate replication lag and backup restore times.

## 3. Configuration & Maintenance Audit
- [ ] Confirm autovacuum/analyze jobs meeting targets.  
- [ ] Review index bloat and maintenance schedule.  
- [ ] Verify statistics update cadence; adjust thresholds if workload shifted.  
- [ ] Ensure connection pooling and caching configs align with traffic patterns.

## 4. Documentation
- [ ] Update runbooks and tuning playbooks with new findings.  
- [ ] Append new sources with title/URL/date to metadata and table below.  
- [ ] Share summary with application teams and capture feedback.

## 5. Source Log
| Date | Source | Notes |
| --- | --- | --- |
| 2025-11-08 | PostgreSQL 16 Performance Docs | Buffer tuning, parallel query updates |
| 2025-11-08 | MySQL 8.3 Reference Manual | Performance Schema enhancements |
| 2025-11-08 | AWS Aurora Best Practices | Autopilot features and cluster scaling |
| 2025-11-08 | Google Spanner Tuning Guide | Recommendations on interleaving & splitting |

> Tip: Use `adn_skills("distill_from_wikipedia", topic="Database tuning")` for quick refreshers before pulling upstream docs via `adn_skills("import_from_github", repository="postgres/postgres", path="doc/src/sgml/performance.sgml")` and validating against official manuals.*** End Patch
