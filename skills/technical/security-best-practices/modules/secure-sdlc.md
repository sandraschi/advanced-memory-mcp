# Secure SDLC

**Confidence**: 🟢 High
**Last validated**: 2025-11-11
**Primary sources**: NIST SP 800-218 Rev.1 (SSDF), OWASP SAMM 2.1, Microsoft SDL 2024, GitHub Advanced Security (Oct 2025), BSIMM14, Google Threat Horizons Q3 2025

---

## 1. Plan & Design

| Activity | Guidance | Tooling / Evidence |
| --- | --- | --- |
| Security requirements | Translate regulatory + business intake into explicit acceptance criteria (e.g., “All APIs must enforce OAuth2 client credentials”). | Requirements traceability matrix in Jira/ADO |
| Threat modeling | Run STRIDE/PASTA or LINDDUN sessions for new epics; capture mitigations and residual risk. | IriusRisk, ThreatPlaybook, Miro template |
| Architecture review | Perform security architecture review for high-risk changes (payments, auth, data residency). | Design doc checklists, ADRs with security section |
| Security backlog | Seed backlog with high-level initiatives (zero trust milestone, PKI upgrade, SBOM coverage). | Shared Kanban board linked to product OKRs |

**Deliverables**: Threat model wiki pages, updated architecture diagrams, accepted risk register entries.

---

## 2. Build & Integrate

| Control | Recommended Practice | References |
| --- | --- | --- |
| Secure coding | Enforce language-specific coding standards (CERT, PSR-12, Effective Python); use IDE linting extensions. | OWASP ASVS v4.0.3 |
| Static analysis | Run SAST for every PR (CodeQL, Semgrep, SonarQube). Gate on critical issues. Track false positive suppression policy. | NIST SSDF PO.3 / PW.5 |
| Dependency hygiene | Use Renovate or Dependabot with security updates auto-merged; enforce `npm audit`/`pip-audit`; maintain allowlist for licenses. | OpenSSF Scorecard |
| Secrets management | Block commits containing secrets (GitHub secret scanning, Gitleaks) and rotate compromised credentials automatically. | Microsoft SDL |
| Developer enablement | Run secure coding workshops + phishing simulations; maintain “secure patterns” snippets repo. | BSIMM14 SFD2 |

**Tip**: Tag repos with “security-critical” to apply stricter branch protections and mandatory reviews from security champions.

---

## 3. Verify & Test

- **Dynamic testing**: Automate DAST scans (OWASP ZAP baseline, StackHawk) for staging environments; include GraphQL/API scanning.
- **Fuzzing & property-based tests**: Apply libFuzzer, Jazzer, AFL++ where parsing/untrusted data occurs.
- **Interactive testing**: Leverage IAST (Contrast, Seeker) for critical Java/.NET services to catch runtime issues.
- **Infrastructure & container scanning**: Trivy, Grype, or Aqua to scan container images; check base images weekly.
- **Manual pen testing / red teaming**: Schedule at least annually, or after major architectural change; feed findings into backlog with SLAs (see Maintenance).

Map each activity back to NIST SSDF PW.7/PS.3 and OWASP SAMM Verification domains.

---

## 4. Release & Deploy

1. **SBOM & attestations**: Generate SBOM (Syft, CycloneDX) for every build. Store in artifact repository along with provenance attestations (in-toto, SLSA Build Level 2+).
2. **Artifact signing**: Use Sigstore Cosign or GPG for container images and binaries; enforce signature verification in CI/CD pipeline.
3. **Policy-as-code gates**: Integrate OPA/Gatekeeper, Conftest, or Terraform Sentinel to block drift from CIS benchmarks or internal baselines.
4. **Change management**: Embed security impact check in change templates; ensure emergency changes are post-reviewed within 24 hours.
5. **Configuration baselines**: Maintain golden AMIs/base images; run drift detection (Terraform Cloud, AWS Config, Azure Policy).

---

## 5. Operate & Improve

- **Vulnerability management**: Track findings in a centralized queue. Recommended SLAs: SEV0 24h, SEV1 7d, SEV2 30d, SEV3 90d. Escalate overdue items weekly.
- **Runtime observability**: Feed security events into SIEM/SOAR (Splunk, Chronicle, Azure Sentinel). Instrument runtime application self-protection (RASP) where high-risk.
- **Feedback loop**: Conduct quarterly security retros, review incident postmortems, update threat models accordingly.
- **Feature flags**: Roll out security patches behind flags for safe canarying; maintain kill switches.
- **Metrics**: Track mean time to remediate, % of repos with automated scanning, threat model coverage, SBOM completeness.

---

### Implementation Checklist
- [ ] Threat models completed for all new high/critical epics (recorded with mitigations).
- [ ] SAST + dependency + secret scanning enforced on every PR; failures gate merge.
- [ ] DAST/IAST + fuzzing executed for critical services prior to release.
- [ ] SBOMs generated, signed, and stored; artifact provenance verified in pipeline.
- [ ] Vulnerability SLA dashboard live with weekly reviews; training plan executed quarterly.

Secure SDLC turns security into a continuous delivery practice, aligning with NIST SSDF, OWASP SAMM, and BSIMM maturity expectations.***
