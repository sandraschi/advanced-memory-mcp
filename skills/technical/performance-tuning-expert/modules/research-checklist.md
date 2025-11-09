# Research Checklist

Run this review every 6 months or after major runtime/framework releases.

## 1. Source Refresh
- [ ] Review performance engineering blogs (Google, Netflix, AWS, Microsoft) for new techniques.  
- [ ] Track runtime release notes (JVM, Node.js, Python, Go, Rust).  
- [ ] Monitor browser performance updates (Chrome, Firefox, Safari).  
- [ ] Follow CNCF/FinOps reports for cost-performance trends.

## 2. Benchmark Health
- [ ] Re-run benchmarks under controlled environment; update baselines.  
- [ ] Validate CI performance tests and adjust guardrails.  
- [ ] Evaluate new profiling tools (eBPF, Parca, Pixie).  
- [ ] Inspect production metrics for anomalies/regressions.

## 3. Documentation
- [ ] Update runbooks and playbooks with latest techniques.  
- [ ] Refresh onboarding material for profiling tools.  
- [ ] Capture lessons learned from recent performance incidents.

## 4. Stakeholder Review
- [ ] Meet with product/UX to confirm performance budgets remain relevant.  
- [ ] Align with FinOps on cost/performance trade-offs.  
- [ ] Share report summarizing wins, regressions, and roadmap.

## 5. Source Log
| Date | Source | Notes |
| --- | --- | --- |
| 2025-11-08 | Google Web Vitals 2025 | Updated INP guidance |
| 2025-11-08 | AWS Builders Library | Performance engineering case studies |
| 2025-11-08 | Netflix Tech Blog | Auto-tuning and cost optimization insights |
| 2025-11-08 | Mechanical Sympathy Notes | Low-level JVM/OS tuning updates |

> Tip: Use `adn_skills("distill_from_wikipedia", topic="Performance engineering")` for quick refreshers, then mine case studies via `adn_skills("import_from_github", repository="Netflix/performance-best-practices")` (hypothetical) before citing findings.***
