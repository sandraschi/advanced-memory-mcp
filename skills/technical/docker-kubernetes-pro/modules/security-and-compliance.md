# Security & Compliance

**Confidence**: 🟡 Medium
**Last validated**: 2025-11-08
**Primary sources**: CNCF Security Whitepaper v2 (2025), NIST SP 800-190 Container Security (2024 revision), Kubernetes Pod Security Standards (2025), SLSA v1.0

---

## 1. Supply Chain Security

- Enforce image scanning (Trivy, Aqua, Twistlock) in CI; fail builds on high severity vulnerabilities.
- Sign images (Cosign) and verify using admission controllers (Kyverno, Gatekeeper).
- Apply SLSA principles: reproducible builds, provenance attestations, trusted builders.
- Restrict base images to approved allowlist; monitor for updates.

---

## 2. Policy-as-Code & Admission Control

- Implement Pod Security Standards (baseline, restricted) or Pod Security Admission.
- Use Kyverno/Gatekeeper to enforce policies: no privileged pods, approved registries, resource limits, liveness/readiness probes.
- Integrate with CI to test policies pre-merge (conftest, kyverno CLI).
- Provide exception workflows with time-bound approvals.

---

## 3. Runtime Hardening

- Run workloads as non-root; drop unnecessary capabilities.
- Enable seccomp profiles, AppArmor/SELinux, read-only root filesystem where possible.
- Deploy runtime protections (Falco, Aqua, Sysdig Secure) for anomaly detection.
- Use network policies to restrict traffic; service mesh mTLS for east-west encryption.

---

## 4. Secrets & Identity

- Manage secrets via External Secrets Operator, Vault, AWS/GCP/Azure secret stores.
- Rotate credentials automatically; monitor for secret drift.
- Use workload identity (IRSA/GCP Workload Identity/Azure Managed Identity) instead of long-lived secrets.
- Enforce RBAC least privilege; audit clusterrolebindings regularly.

---

## 5. Compliance & Audit

- Maintain evidence packages: scan reports, policy logs, access reviews.
- Enable audit logging on API server; ship to SIEM.
- Implement CIS Benchmarks/Kube-bench in CI and scheduled scans.
- Document data residency, backup encryption, and retention policies.

---

### Checklist
- [ ] Image scanning, signing, and provenance enforced in build + deploy.
- [ ] Admission policies active with monitoring for violations.
- [ ] Runtime security tools deployed with alerting.
- [ ] Secrets/workload identity strategy documented and validated.
- [ ] Compliance evidence retained with regular audits.

Security must be continuous—review controls with each platform upgrade or regulatory change.*** End Patch
