# Research Checklist

Run this refresh every quarter or after major Kubernetes/Docker releases.

## 1. Source Refresh
- [ ] Review Kubernetes release notes (https://kubernetes.io/releases/).  
- [ ] Check Docker/BuildKit updates and OCI spec changes.  
- [ ] Track CNCF security/governance whitepapers and SIG announcements.  
- [ ] Monitor managed Kubernetes provider updates (EKS, GKE, AKS, OpenShift).

## 2. Platform Validation
- [ ] Audit cluster versions, upgrade plans, and deprecations.  
- [ ] Re-run conformance tests (Sonobuoy) on staging.  
- [ ] Validate GitOps pipelines (sync status, drift alerts).  
- [ ] Confirm admission policies and runtime security controls functioning.

## 3. Observability & Cost
- [ ] Review SLO dashboards; adjust thresholds if workloads changed.  
- [ ] Analyze cost reports (Kubecost) and document actions.  
- [ ] Confirm autoscaling policies meet demand; run load test if necessary.  
- [ ] Update incident runbooks with recent lessons learned.

## 4. Documentation
- [ ] Update platform architecture diagrams and onboarding guides.  
- [ ] Append new sources to `metadata.sources` and table below.  
- [ ] Share quarterly platform health report with stakeholders.

## 5. Source Log
| Date | Source | Notes |
| --- | --- | --- |
| 2025-11-08 | Kubernetes 1.30 Docs | API removals, autoscaling improvements |
| 2025-11-08 | CNCF Security Whitepaper v2 | Supply chain & policy guidance |
| 2025-11-08 | Docker Best Practices 2025 | BuildKit optimizations, SBOM requirements |
| 2025-11-08 | Managed K8s Ops Guides | Provider-specific operational recommendations |

> Tip: Start with `adn_skills("distill_from_wikipedia", topic="Kubernetes")` for context, then grab upstream docs via `adn_skills("import_from_github", repository="kubernetes/website", path="content/en/docs")` and cross-check before updating modules.*** End Patch
