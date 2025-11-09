# Research Checklist

Run this review every 6 months or when major architectural guidance changes.

## 1. Source Refresh
- [ ] Review CNCF microservices whitepapers, SIG App Delivery updates.  
- [ ] Track major cloud provider architecture guides (AWS Builders Library, Google CRE blog, Azure Architecture Center).  
- [ ] Check service mesh roadmaps (Istio Ambient, Linkerd, Cilium).  
- [ ] Monitor Team Topologies and DDD community articles for organizational patterns.

## 2. Architecture Health Audit
- [ ] Update service catalog and ownership map; ensure no orphaned services.  
- [ ] Audit SLO compliance and incident trends per service.  
- [ ] Evaluate coupling (shared databases, duplicated logic) and plan remediation.  
- [ ] Assess platform capability gaps (observability, CI/CD, governance).

## 3. Documentation & Training
- [ ] Refresh ADR index and highlight deprecated decisions.  
- [ ] Update onboarding materials for new teams/services.  
- [ ] Capture lessons from recent migrations or outages.

## 4. Compliance & Security
- [ ] Review zero-trust controls, policy-as-code rules, and threat models.  
- [ ] Confirm data residency/privacy policies remain accurate.  
- [ ] Audit supply chain security posture (SBOM, signing) across services.

## 5. Source Log
| Date | Source | Notes |
| --- | --- | --- |
| 2025-11-08 | Team Topologies 2024 Update | Team/service alignment guidance |
| 2025-11-08 | CNCF Microservices Security WP 2025 | Zero-trust patterns |
| 2025-11-08 | Google CRE Microservices Lessons | Ops and reliability practices |
| 2025-11-08 | Uber ADR Collection 2024 | Case studies on service decomposition |

> Tip: Kick off reviews with `adn_skills("distill_from_wikipedia", topic="Microservices")`, then pull CNCF primary sources via `adn_skills("import_from_github", repository="cncf/toc", path="whitepapers/microservices")` and capture outcomes in `metadata.sources`.***
