# Platform Foundations

**Confidence**: 🟡 Medium
**Last validated**: 2025-11-08
**Primary sources**: Kubernetes 1.30 Architecture Docs (2025), Docker Build Best Practices (2025), CNCF Platform Engineering Whitepaper (2024), OCI Image Spec 1.1 (2024)

---

## 1. Container Image Hygiene

- Use minimal base images (distroless, alpine with caution); pin versions and digest.
- Multi-stage builds to separate build/run layers; prune unnecessary artifacts.
- Embed labels (version, VCS commit, build timestamp).
- Scan images automatically (Trivy, Grype, Aqua) and fail builds on high severity CVEs.
- Sign images with Sigstore Cosign and enforce verification in admission controllers.

---

## 2. Registry & Artifact Strategy

- Use private registries (AWS ECR, GCR, ACR, Harbor); configure immutable tags and lifecycle policies.
- Mirror public images to internal registries to reduce supply-chain risk.
- Implement RBAC and network restrictions for registry access.
- Cache frequently used base images in cluster to reduce cold start time.

---

## 3. Cluster Architecture

- Choose control plane management (managed vs self-managed).
- Size node pools based on workload profiles (CPU/memory heavy, GPU, spot/preemptible).
- Use node taints/tolerations and affinity to place workloads correctly.
- Set up CNI (Cilium, Calico) and CSI drivers aligning with networking/storage needs.
- Configure namespace structure per environment/team with resource quotas and limit ranges.

---

## 4. Configuration & Secrets

- Store configuration in ConfigMaps/Secrets; mount via env or volumes.
- Use External Secrets Operator/Secrets Manager for rotation.
- Template manifests with Helm, Kustomize, or Jsonnet; maintain DRY overlays.
- Keep cluster bootstrap scripts (Terraform, Crossplane, Pulumi) in version control.

---

## 5. Service Discovery & Networking

- Standardize ingress (NGINX, ALB, Istio) and service mesh (Istio, Linkerd, Consul) where appropriate.
- Apply network policies to restrict east-west traffic.
- Use DNS or service mesh for multi-cluster connectivity; adopt Gateway API if supported.
- Plan for load balancer quotas and IP address management.

---

### Checklist
- [ ] Container build pipelines enforce scanning and signing.
- [ ] Registry policies (immutability, retention, access) defined.
- [ ] Cluster bootstrap/IaC scripts documented and versioned.
- [ ] Namespace/resource quota strategy agreed with stakeholders.
- [ ] Networking and service discovery components standardized.

Mastering these foundations ensures reliable, secure building blocks for higher-level deployment patterns.*** End Patch
