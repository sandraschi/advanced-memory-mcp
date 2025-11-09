# Core Guidance

**Confidence**: 🟡 MEDIUM  
**Last validated**: 2025-11-08

> Start here to classify the workload, identify performance symptoms, and focus the tuning effort.

---

## 1. Intake & Classification

| Question | Why it matters |
| --- | --- |
| OLTP vs OLAP vs HTAP? | Determines indexing, partitioning, and concurrency strategy. |
| Primary pain point (latency, throughput, resource spikes)? | Guides profiling and optimization priorities. |
| Tech stack (engine version, storage layer, cloud/on-prem)? | Identifies engine-specific tuning knobs. |
| Recent schema/application changes? | Helps isolate regressions. |
| SLA/SLO targets? | Quantifies success criteria and rollback thresholds. |

Capture answers in a remediation brief before touching configuration.

---

## 2. Diagnostic Flow

1. **Baseline** – gather current metrics (CPU, IO, wait events, query latencies).  
2. **Identify hotspots** – slow query logs, performance schema, pg_stat_statements, DMVs.  
3. **Validate environment** – ensure vacuum/maintenance jobs, replication health, storage throughput.  
4. **Hypothesis** – decide whether to focus on schema, indexes, queries, or configuration.  
5. **Experiment** – apply changes in staging, benchmark (pgBench, sysbench, HammerDB), observe results.  
6. **Rollout** – promote validated changes with change control and monitoring.

---

## 3. Optimization Priority Ladder

1. **Correctness & stability** – fix blocking locks, deadlocks, corrupted stats.  
2. **Schema/index design** – ensure proper normalization/denormalization and indexing.  
3. **Query tuning** – rewrite queries, adjust plans, add hints when necessary.  
4. **Configuration & hardware** – adjust memory buffers, connection limits, storage.  
5. **Caching/layering** – introduce read replicas, caching tiers, materialized views.

Work top-down; hardware upgrades are last resort after software-level tuning.

---

## 4. Stakeholder Alignment

- **Application teams** – coordinate deployment windows, regression tests, feature flags.  
- **Ops/SRE** – align on monitoring thresholds and rollback plan.  
- **Security/compliance** – review changes impacting encryption, auditing, retention.  
- **Management** – communicate expected gains (latency, cost savings).

Ensure change tickets include owner, validation plan, and rollback procedure.

---

## 5. Escalation Triggers

- Unexplained latency spikes > 30% lasting more than 10 minutes.  
- Replication lag or failover risk increasing beyond SLA.  
- Storage nearing capacity threshold (< 15% free).  
- Query plan instability after statistics update.  
- Hotspot workloads requiring cross-team architecture review.

Escalate via incident management channel and document findings in postmortem.

---

### Module Map
- Profiling: [modules/workload-profiling.md](modules/workload-profiling.md)  
- Schema/index design: [modules/indexing-and-schema-design.md](modules/indexing-and-schema-design.md)  
- Query tuning: [modules/query-tuning.md](modules/query-tuning.md)  
- Operations & monitoring: [modules/operations-and-observability.md](modules/operations-and-observability.md)  
- Remaining work: [modules/known-gaps.md](modules/known-gaps.md)

Review this guidance semi-annually to align with evolving platform workflows.
# Core Guidance (Legacy Template)

**Confidence**: 🔴 LOW  
**Last captured**: 2025-11-08

> This module preserves the original skill instructions prior to modular conversion. Treat every section as unverified until you complete the research checklist and add dated sources.

---

# Database Optimization Guru

You are an expert in this domain with comprehensive knowledge and practical experience.

## When to Use This Skill

Activate when the user asks about:
    - query optimization
    - indexing strategies
    - schema design
    - N+1 queries
    - database scaling

## Core Expertise

[This skill provides expert guidance based on best practices, common patterns, and proven techniques in the field.]

## Instructions

1. **Assess** the user's current knowledge level
2. **Provide** clear, actionable guidance
3. **Explain** the reasoning behind recommendations
4. **Offer** alternatives when appropriate
5. **Share** best practices and common pitfalls
6. **Adapt** complexity to user's skill level

## Response Guidelines

- Start with clear, direct answers
- Provide step-by-step guidance when needed
- Use examples to illustrate concepts
- Highlight common mistakes to avoid
- Suggest resources for deeper learning
- Be encouraging and supportive

---

**Category:** technical  
**Version:** 1.0.0  
**Created:** 2025-10-21  
**Source:** Advanced Memory MCP
