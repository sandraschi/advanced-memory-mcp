# Application Security

**Confidence**: 🟢 High  
**Last validated**: 2025-11-11  
**Primary sources**: OWASP Top 10:2021 + 2024 addendum, OWASP API Security Top 10:2023, OWASP ASVS v4.0.3, NIST SP 800-63-3, SLSA v1.0, Google “Architecting Secure Applications” (2025), Microsoft Secure Development Lifecycle (2024 refresh)

---

## 1. Foundational Controls (Map to ASVS L2/L3)

| Area | Must-haves | Reference |
| --- | --- | --- |
| **Validation & encoding** | Use allow-list validation for inputs, centralized sanitizer libraries; HTML encode before output. | ASVS V5, V6 |
| **Authentication** | Enforce MFA, rate-limit login attempts, store salted BCrypt/Argon2 hashes, adopt OAuth2/OIDC for third-party clients. | NIST 800-63-3, ASVS V2 |
| **Authorization** | Implement coarse-grained (RBAC/ABAC) and fine-grained checks; use policy engines (Cedar, OPA); deny by default. | ASVS V4 |
| **Session management** | Regenerate session IDs post-auth, set `Secure`, `HttpOnly`, `SameSite` cookies, monitor session anomalies. | ASVS V3 |
| **Cryptography** | Use TLS 1.2+ (prefer 1.3), AES-256-GCM, SHA-256/512, rotate keys with KMS/HSM, maintain crypto inventory. | ASVS V7 |
| **Logging & monitoring** | Centralize logs (ELK, Cloud Logging), redact sensitive data, enable tamper detection, integrate SIEM alerts. | ASVS V9 |

---

## 2. OWASP Top 10 & API Top 10 Mitigation Matrix

| Risk | Mitigations |
| --- | --- |
| Broken Access Control / Excessive Data Exposure | Use centralized authorization service, enforce object-level checks, apply GraphQL schema allow-lists, run access unit tests. |
| Cryptographic Failures | TLS everywhere, HSTS, secure cookie flags, certificate pinning for mobile clients, automatic key rotation. |
| Injection (SQL/NoSQL/LDAP/Command) | ORM prepared statements, parameterized queries, input validation, escaping libraries, static analysis for tainted flows. |
| Insecure Design | Conduct misuse/abuse case reviews, enforce security design patterns (e.g., envelope encryption, tokenization). |
| Security Misconfiguration | Immutable infrastructure, baseline templates, automated config scanning (ScoutSuite, Steampipe). |
| Vulnerable Components / Software Integrity | SBOM, dependency scanning, signed packages, restrict direct internet downloads, enforce reproducible builds. |
| Identification & Authentication Failures | Strict session lifecycle, adaptive authentication, ReCAPTCHA/bot detection, device fingerprinting as needed. |
| Software & Data Integrity Failures / Supply Chain | Signed commits, branch protection, verified CI/CD steps, SLSA attestations, verified dependencies. |
| Logging & Monitoring Failures | Structured logs with request IDs, anomaly detection, alerting thresholds, test incident response to log tampering. |
| SSRF / API9 Improper Asset Management | Metadata service protections (IMDSv2, firewall rules), network segmentation, canonical service inventory, API gateway allowlists. |

Treat OWASP Top 10 as baseline and augment with domain-specific checklists (e.g., OWASP Mobile Top 10, MASVS, OWASP ML Security Top 10).

---

## 3. Secure Coding & Review Playbook

1. **Standardize guidance**: Maintain language/framework-specific secure coding guides (e.g., Python, Go, Node, Java). Reference CERT secure coding rules.  
2. **Pre-commit & CI hooks**: Bandit, Gosec, ESLint security, spotbugs. Fail builds on critical findings.  
3. **Secure code review**: Use checklist template covering auth, data exposure, crypto, secrets, error handling, logging. Require a security champion review on high-risk changes.  
4. **AI-assisted coding guardrails**: If using Copilot/Cline, enforce secrets checking, diff scanning, and code provenance review to prevent prompt injection or random library inclusion.

---

## 4. Dependency & Supply Chain Security

- **Source control hygiene**: Enforce signed commits and verified GitHub/GitLab workflows; track third-party contributors.  
- **Package policy**: Maintain allow/block lists, monitor typosquatting via Artifact Hub/Phylum, require checksums (`pip --require-hashes`, `npm audit signatures`, `cargo vet`).  
- **SBOM pipeline**: Generate SBOM at build time (Syft, CycloneDX) and store in registry; compare against VEX advisories.  
- **Runtime attestation**: Validate containers/binaries before deployment (Cosign, AWS Signer).  
- **Third-party SaaS review**: Use vendor questionnaires (SIG Lite), require SOC 2 + pen test summary for integrated services.

---

## 5. Runtime & Client Protections

- **Edge defense**: Configure WAF/CDN (AWS WAF, Cloud Armor, Azure Front Door) with managed rules + custom rules for business logic.  
- **API security**: Use API gateways with schema validation, JWT validation, mTLS, rate limiting, and quota enforcement; log to API inventory service.  
- **Browser controls**: Strict CSP, X-Frame-Options, Referrer-Policy, Permissions-Policy, Subresource Integrity, downscope CORS.  
- **Feature flags**: Deploy security fixes behind flags, maintain rollback strategies, integrate with incident automation.  
- **Telemetry**: Instrument RASP/EDR signals, collect user behavior analytics to detect anomalies.

---

### Validation Checklist
- [ ] ASVS L2 controls satisfied (L3 for payment/auth systems).  
- [ ] OWASP Top 10 + API Top 10 mapped to concrete mitigations with owners.  
- [ ] Secure coding standards enforced via linting, reviews, and champion sign-off.  
- [ ] SBOM + package policies implemented; supply-chain risks monitored.  
- [ ] Runtime protections (WAF, rate limiting, CSP, API gateway) active and tested quarterly.

Robust application security combines preventive design, continuous verification, and runtime defenses to stay ahead of evolving attack surfaces.***

