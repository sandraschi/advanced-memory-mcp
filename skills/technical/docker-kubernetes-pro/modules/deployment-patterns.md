# Deployment Patterns

**Confidence**: 🟡 Medium  
**Last validated**: 2025-11-08  
**Primary sources**: Kubernetes 1.30 Workload API, Argo CD Best Practices (2025), Flux GitOps Guide (2025), CNCF Progressive Delivery Working Group (2024)

---

## 1. Workload Types

- Use Deployments for stateless apps; StatefulSets for stateful workloads requiring stable identity; DaemonSets for node-level agents; Jobs/CronJobs for batch.  
- Prefer operators/CRDs for complex systems (Databases, Kafka) but evaluate maturity/support.  
- Keep manifests declarative and parameterized via Helm/Kustomize.

---

## 2. GitOps Flow

- Store manifests/Helm charts in Git; use Argo CD or Flux for reconciliation.  
- Enforce code review on manifest changes; integrate policy checks (OPA/Gatekeeper).  
- Maintain environment overlays (dev/staging/prod) with clear promotion strategy.  
- Use image automation (Flux Image Update, Argo Image Updater) with approvals for production.

---

## 3. Rollout Strategies

- **Rolling updates**: default for stateless apps; tune `maxSurge`/`maxUnavailable`.  
- **Blue/Green**: leverage dual services/router rules; use Argo Rollouts or Flagger.  
- **Canary**: gradually shift traffic; automate analysis with metrics (Prometheus, Datadog).  
- **A/B testing**: integrate with service mesh for request routing and telemetry.

Document rollback procedures for each strategy.

---

## 4. Multi-Cluster & Multi-Region

- Use Cluster API, Anthos, Azure Arc, or Fleet to manage fleets.  
- Implement topology-aware routing (Global load balancers, service mesh multicluster).  
- Sync configuration via GitOps; ensure secret distribution is secure.  
- Define disaster recovery plan (backup/restore, failover) per region.

---

## 5. Tool Integrations

- Build pipelines: Tekton, GitHub Actions, GitLab CI using `kubectl`/`helm`/`kustomize`.  
- Manage secrets via External Secrets, Sealed Secrets, HashiCorp Vault.  
- Use admission controllers (Kyverno, Gatekeeper) to enforce policy at deploy time.

---

### Checklist
- [ ] Manifests templated and version-controlled with promotion workflow.  
- [ ] GitOps or CI/CD pipeline enforces policy and approvals.  
- [ ] Rollout strategy documented with automated health checks.  
- [ ] Multi-cluster requirements assessed and tooling selected.  
- [ ] Rollback and disaster recovery procedures rehearsed.

Consistent deployment patterns reduce drift and accelerate safe delivery across environments.*** End Patch

