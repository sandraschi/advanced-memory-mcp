# Cloud & Infrastructure

**Confidence**: 🟢 High  
**Last validated**: 2025-11-11  
**Primary sources**: CIS Controls v8.1, CIS Benchmarks (AWS 1.5.0, Azure 2.1.0, GCP 2.0.0), AWS Well-Architected Security Pillar (2025-09), Google Cloud security foundations blueprint (2025-06), Azure Security Benchmark v3, CNCF Cloud Native Security Whitepaper v2.1, NSA Kubernetes Hardening Guide v1.2

---

## 1. Identity, Access & Entitlements

| Control | Implementation Tips |
| --- | --- |
| Least privilege IAM | Model roles with job functions, use AWS IAM Access Analyzer / Azure PIM / GCP IAM Recommender to prune unused permissions. |
| Short-lived credentials | Prefer workload identity (AWS STS, Azure Managed Identities, GCP Workload Identity Federation). Block long-lived access keys; rotate automatically. |
| MFA & conditional access | Mandatory MFA for console/admin accounts; apply conditional policies (device health, network location). |
| Privileged access management | Session recording, just-in-time access, approvals via security operations. Store break-glass accounts offline with tested procedures. |
| Entitlement review | Quarterly review of IAM roles, service accounts, Kubernetes RBAC, database accounts; integrate with Identity Governance tooling. |

---

## 2. Network & Zero Trust Architecture

- **Segmentation**: Private subnets by environment tier (prod/stage/dev), use security groups/network policies with explicit allow lists.  
- **Perimeter**: Managed WAF/CDN (AWS WAF, Cloud Armor, Azure Front Door) and DDoS protection (Shield Advanced, Cloud Armor Edge).  
- **Service-to-service**: Enforce mTLS via service mesh (Istio, Linkerd) or mutual TLS termination at API gateways. Adopt zero trust principles (BeyondCorp Enterprise, Zscaler).  
- **DNS & edge controls**: Enable DNSSEC, DNS logging, and egress filtering; adopt private service connect/PrivateLink to limit internet egress.  
- **Remote access**: Replace VPNs with zero-trust access brokers when feasible; enforce device posture checks.

---

## 3. Infrastructure as Code & Platform Engineering

- **Scanning & policy enforcement**: Integrate Checkov, tfsec, terrascan, Kics in CI. Enforce policy-as-code (OPA, Sentinel, Azure Policy, AWS Config) with mandatory passes before merge/deploy.  
- **Module governance**: Maintain approved module registry (Terraform Cloud private registry, Git submodules) with code reviews, semantic versioning, signed releases.  
- **Workload hardening**: Apply CIS hardened AMIs/base images, limit container privileges (rootless where possible), enable SELinux/AppArmor.  
- **Kubernetes security**: Enable PodSecurityAdmission / Kyverno policies, restrict host networking, disable legacy admission controllers, rotate kubelet certificates, enable audit logging.  
- **Change management**: Use GitOps/ArgoCD/Flux for auditable deployments; require security champ review for high-risk infra changes.

---

## 4. Secrets & Key Management

- Centralize secrets in vaults (HashiCorp Vault, AWS Secrets Manager, Azure Key Vault, GCP Secret Manager) with automatic rotation.  
- Use envelope encryption and KMS-backed sealed secrets for Kubernetes.  
- Audit access (CloudTrail, Key Vault logs) and alert on anomalous secret retrieval.  
- Enforce developer workflows that never expose plaintext secrets (CLI wrappers, SSM sessions).  
- Implement hardware-backed roots of trust where possible (CloudHSM, AWS NitroTPM, Azure Confidential Compute).

---

## 5. Monitoring, Posture & Runtime Protection

- **Logging**: Enable CloudTrail / Audit Logs / Activity Logs in all regions, aggregate to SIEM with immutable storage (S3 Glacier, Log Archive).  
- **Posture management**: Use AWS Security Hub, Azure Defender for Cloud, GCP Security Command Center Premium; tune controls to reduce noise.  
- **Drift detection**: Detect configuration drift via Terraform Cloud, AWS Config Conformance Packs, Lacework, or Wiz. Remediate automatically where safe.  
- **Runtime protection**: Deploy workload protection (Falco, Aqua, Datadog CWS, Prisma Cloud) to monitor syscall anomalies, container escapes, kernel exploits.  
- **Patch & vuln management**: Automate AMI/base image patching (EC2 Image Builder, Packer pipelines), track container image CVEs, ensure live patching or rolling restarts.

---

### Operational Checklist
- [ ] IAM roles audited quarterly; break-glass accounts tested; MFA enforced.  
- [ ] Network architecture adheres to zero trust principles with segmented VPC/VNet design and mTLS.  
- [ ] IaC scanning + policy-as-code gates block insecure configurations; Kubernetes admission controls active.  
- [ ] Secrets managed via centralized vault with rotation + audit logging; no plaintext secrets in repos or pipelines.  
- [ ] CSPM/siem alerts monitored; drift detection + runtime protection covering all critical workloads.

Strengthening cloud and infrastructure controls delivers a resilient, zero-trust foundation that limits blast radius and simplifies compliance.***

