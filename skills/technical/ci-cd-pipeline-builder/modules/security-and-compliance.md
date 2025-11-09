# Security & Compliance

**Confidence**: 🟡 Medium  
**Last validated**: 2025-11-08  
**Primary sources**: SLSA v1.0 (2024), NIST SSDF SP 800-218 (2023), OWASP CICD Security Top 10 (2024), GitHub Actions OIDC (2025), Sigstore/cosign Docs (2025)

---

## 1. Supply Chain Integrity

1. **Provenance** – adopt SLSA v1.0 Level 3 where practical:  
   - Use trusted builders (GitHub hosted runners, hardened self-hosted with attestations).  
   - Generate signed provenance (in-toto, cosign) for each artifact.  
   - Store provenance in artifact registry; verify before deploy.

2. **SBOM** – produce Software Bill of Materials (CycloneDX/SPDX) for applications and containers; attach to release.  
3. **Dependency Management** – lock dependencies (poetry.lock, package-lock.json, go.sum); run SCA (Dependabot, Renovate, Snyk).  
4. **Signature Verification** – verify third-party tools and base images; enforce cosign/rekor signatures.

---

## 2. Secret & Credential Hygiene

- Replace long-lived secrets with OIDC federated tokens (GitHub → AWS/Azure/GCP, GitLab Workload Identity).  
- Store remaining secrets in Vault/Secrets Manager with rotation policies; never commit to repo.  
- Scan repos and artifacts for secret leakage (gitleaks, TruffleHog).  
- Limit runner permissions; use ephemeral runners for privileged jobs.

---

## 3. Compliance Automation

- Map controls to frameworks (SOC2, ISO 27001, PCI DSS).  
- Capture audit evidence automatically: test reports, approvals, release logs, SBOM, provenance.  
- Maintain segregation of duties (SoD): enforce reviewer vs deployer separation using environment protection rules.  
- Implement policy-as-code (OPA, HashiCorp Sentinel) to gate infrastructure changes.  
- Provide compliance dashboards summarizing control coverage and outstanding actions.

---

## 4. Security Testing Integration

- **SAST**: run on every push (CodeQL, SonarQube).  
- **SCA**: daily or per dependency change (Dependabot, Renovate).  
- **DAST**: scheduled or pre-prod (OWASP ZAP, StackHawk).  
- **Container scanning**: Trivy, Grype integrated before publishing images.  
- **IaC scanning**: Checkov, tfsec, cfn-nag on infrastructure definitions.

Fail pipeline on HIGH severity issues; auto-create tickets with SLA to remediate.

---

## 5. Access Controls & Audit

- Enforce principle of least privilege on pipeline service accounts.  
- Require MFA for Git hosting and pipeline platforms.  
- Log all administrative actions; forward to SIEM (Splunk, Datadog, Chronicle).  
- Periodically audit access lists; remove stale credentials.

---

## 6. Incident Response Preparedness

- Maintain runbooks for compromised pipeline, credential leak, or malicious artifact.  
- Implement automated revocation and rebuild process (rotate tokens, rebuild images, invalidate caches).  
- Conduct annual tabletop exercises focusing on supply-chain attacks.  
- Capture post-incident improvement items and feed into backlog.

---

### Checklist
- [ ] Provenance generated & verified for every artifact.  
- [ ] SBOM published with each release and retained per compliance requirements.  
- [ ] Secrets managed through OIDC or vault with enforced rotation.  
- [ ] Security scans integrated and blocking on high severity issues.  
- [ ] Audit evidence automatically archived (approvals, test results, deploy logs).  
- [ ] Incident response playbooks reviewed and tested within last 12 months.

Use this module to keep pipelines resilient against supply-chain threats while satisfying audit obligations.*** End Patch

