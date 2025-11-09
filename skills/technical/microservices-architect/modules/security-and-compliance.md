# Security & Compliance

**Confidence**: 🟡 Medium  
**Last validated**: 2025-11-08  
**Primary sources**: CNCF Microservices Security Whitepaper (2025), NIST Zero Trust Architecture SP 800-207A (2024), OWASP Microservices Security Cheat Sheet (2025), PCI DSS 4.0 Guidance (2024)

---

## 1. Identity & Access

- Adopt zero-trust: mutual TLS between services (service mesh, SPIFFE/SPIRE).  
- Use centralized identity provider for service-to-service auth (JWT, OAuth2 client credentials).  
- Enforce fine-grained authorization (OPA, Cedar, AWS Verified Permissions).  
- Rotate secrets automatically; use vaults and workload identity.

---

## 2. Policy Enforcement

- Implement policy-as-code for Kubernetes/Cloud (OPA/Gatekeeper, Kyverno).  
- Require SBOMs and signed artifacts (SLSA, Sigstore).  
- Automate compliance checks in CI/CD (static analysis, dependency scanning, IaC scanning).  
- Track exceptions with expiry and review cycles.

---

## 3. Data Protection & Privacy

- Classify data sensitivity per service; enforce encryption in transit and at rest.  
- Apply tokenization/redaction for PII before sharing events.  
- Document data residency requirements and retention schedules.  
- Implement right-to-be-forgotten workflows across services.

---

## 4. Monitoring & Incident Response

- Enable security observability: audit logs, abnormal traffic detection, WAF.  
- Integrate SIEM with service telemetry; correlate across services.  
- Prepare incident response runbooks for credential compromise, data leak, supply chain attacks.  
- Conduct tabletop exercises with engineering + security teams.

---

## 5. Compliance Alignment

- Map controls to frameworks (SOC2, ISO 27001, PCI DSS).  
- Provide evidence from CI/CD, release approvals, access logs.  
- Automate change records linking commits to tickets.  
- Ensure third-party services meet compliance requirements.

---

### Checklist
- [ ] Zero-trust identity and policy enforcement active across services.  
- [ ] Supply chain security (scanning, signing, SBOM) integrated.  
- [ ] Data protection and privacy workflows documented.  
- [ ] Security monitoring and incident response rehearsed.  
- [ ] Compliance evidence automated and reviewed on schedule.

Security must be layered into every service to keep distributed systems trustworthy and audit-ready.*** End Patch

