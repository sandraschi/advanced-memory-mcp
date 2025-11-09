# Known Gaps & Validation Tasks

## Open Items
- ⏳ Deep dive on distributed SQL (CockroachDB, YugabyteDB) tuning patterns for inclusion.  
- ⏳ Compare adaptive indexing/tuning features (SQL Server Automatic Tuning, Aurora Auto Optimize) and document guardrails.  
- ⏳ Gather case studies on columnar stores (Snowflake/BigQuery) to expand beyond row stores.

## TODOs
1. Create reusable benchmarking harness with Terraform + Ansible for multi-engine testing.  
2. Publish standard operating procedure for hot index rebuild with zero downtime.  
3. Validate plan regression detection using Query Store/pg_stat_statements automation.

## Notes
- Increase confidence to **high** after distributed SQL research and automation SOPs completed.  
- Track major engine release notes (PostgreSQL 17, MySQL 9) to update modules promptly.*** End Patch
