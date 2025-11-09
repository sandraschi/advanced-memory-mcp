# Indexing & Schema Design

**Confidence**: 🟡 Medium  
**Last validated**: 2025-11-08  
**Primary sources**: PostgreSQL Physical Design Guide (2025), MySQL 8.3 InnoDB Indexing (2024), SQL Server Index Tuning (2025), Google Cloud Spanner Schema Best Practices (2025)

---

## 1. Schema Strategy

- **Normalization vs Denormalization**: keep OLTP systems 3NF or BCNF where possible; denormalize for hot joins but document data consistency mechanism.  
- **Partitioning/Sharding**: leverage range/hash partitioning for large tables; align partition key with query predicates.  
- **Data types**: choose smallest fitting types; avoid oversized `VARCHAR`; use UUID v7/time-based for sequential writes if required.  
- **Temporal tables**: consider time-series partitioning, retention policies, and materialized views.

---

## 2. Index Design Principles

1. **Workload-driven** – derive indexing strategy from top queries (WHERE, JOIN, ORDER BY).  
2. **Composite indexes** – order columns by equality predicates first, then range, then ordering.  
3. **Covering indexes** – include select list columns to avoid lookups when beneficial.  
4. **Partial/filtered indexes** – index subsets (e.g., `WHERE status='ACTIVE'`).  
5. **Functional indexes** – index expressions used in predicates (e.g., `LOWER(email)`).

Keep index count balanced; each index impacts write cost.

---

## 3. Engine-Specific Tips

- **PostgreSQL**:  
  - Use `btree` by default; `GIN`/`GiST` for JSONB/full-text/geospatial.  
  - Monitor bloat (pgstattuple) and autovacuum.  
  - Consider BRIN for large append-only tables.

- **MySQL (InnoDB)**:  
  - Primary key clustered; keep it narrow.  
  - Secondary indexes store primary key pointer; mind composite order.  
  - Use invisible indexes to test removal impact.

- **SQL Server**:  
  - Include columns for covering indexes; use filtered indexes for selective queries.  
  - Analyze with Database Engine Tuning Advisor but validate suggestions manually.

- **Cloud Spanner**:  
  - Interleave tables for hierarchical data to co-locate storage.  
  - Avoid hotspots by sharding keys (hash prefix).

---

## 4. Index Maintenance

- Regularly review unused indexes (`pg_stat_user_indexes`, `sys.dm_db_index_usage_stats`).  
- Drop redundant/unused indexes to reduce write overhead.  
- Schedule reindex or `OPTIMIZE TABLE` for fragmentation when necessary.  
- Update statistics frequently (ANALYZE, `AUTO_UPDATE_STATISTICS`) to keep optimizer accurate.

---

## 5. Migration Workflow

1. Create indexes concurrently / online to avoid downtime.  
2. Validate in staging with representative load.  
3. Deploy using expansion → verify → cleanup pattern (add new index, run dual writes, remove old).  
4. Monitor impact (CPU, latency, size).

---

### Checklist
- [ ] Schema review with workload classification completed.  
- [ ] Indexes mapped to specific queries with justification.  
- [ ] Redundant/unused indexes identified for removal.  
- [ ] Maintenance plan documented (vacuum/reindex/statistics).  
- [ ] Change rollout plan with monitoring/rollback ready.

Use this module to ensure physical design supports current workloads while keeping write overhead manageable.*** End Patch

