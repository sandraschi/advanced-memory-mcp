# Query Tuning

**Confidence**: 🟡 Medium  
**Last validated**: 2025-11-08  
**Primary sources**: PostgreSQL Planner Guide (2025), MySQL Optimizer Hints (2024), SQL Server Query Store (2025), Oracle SQL Performance Tuning (2024)

---

## 1. Execution Plan Analysis

- Generate plans with actual runtime stats (`EXPLAIN ANALYZE`, `EXPLAIN FORMAT=JSON`, SQL Server `SET STATISTICS IO/TIME`).  
- Look for red flags: sequential scans on large tables, nested loop over large result sets, implicit conversions, missing join predicates.  
- Compare estimated vs actual rows; large discrepancies indicate outdated stats or poor predicates.

---

## 2. Query Rewrite Patterns

| Issue | Fix |
| --- | --- |
| N+1 queries | Use JOINs, window functions, or prefetch strategies. |
| Scalar subqueries | Convert to JOIN or CTE where appropriate. |
| Wildcard leading `%` search | Introduce trigram/full-text indexes or search service. |
| Complex OR predicates | Break into UNION ALL with selective indexes or use partial indexes. |
| Unbounded pagination | Use keyset pagination or cursors. |

Document rewrites and add regression tests to lock improvements.

---

## 3. Optimizer Guidance

- Update statistics (`ANALYZE`, `UPDATE STATISTICS`) before tuning.  
- For tricky cases, consider hints (PostgreSQL `ENABLE_NESTLOOP=off`, MySQL `STRAIGHT_JOIN`, SQL Server `OPTION(RECOMPILE)`). Use sparingly and document rationale.  
- Evaluate parameter sniffing impact; use `OPTIMIZE FOR`, plan guides, or `sp_recompile` as last resort.

---

## 4. Caching & Materialization

- Introduce materialized views or summary tables for heavy analytics queries; schedule refresh.  
- Utilize result cache (Oracle) or query cache (Memcached/Redis) where consistent.  
- For read replicas, ensure queries direct to appropriate replica via connection routing.

---

## 5. Testing & Validation

- Create regression tests comparing old vs new execution time.  
- Benchmark with realistic data/parameters.  
- Monitor query performance post-deploy via Query Store, pg_stat_statements, or APM dashboards.  
- Capture plan fingerprints to detect regressions after stats/hardware changes.

---

### Checklist
- [ ] Execution plan captured and analyzed.  
- [ ] Root cause identified (missing index, rewrite, stats).  
- [ ] Query rewritten or hint applied with documentation.  
- [ ] Tests/benchmarks confirm improvement.  
- [ ] Post-deploy monitoring set up for regression detection.

Use this module iteratively: diagnose → adjust → measure until SLA goals are met.*** End Patch

