# Research Checklist

Review quarterly or after major framework/security advisories.

## 1. Source Refresh
- [ ] OWASP updates (Top 10, ASVS, API Security Top 10).
- [ ] NIST publications (SSDF, CSF, SP 800 series).
- [ ] CIS Benchmarks updates for cloud providers.
- [ ] CNCF Security SIG releases and threat reports.

## 2. Control Review
- [ ] Audit SAST/DAST/secret scanning coverage.
- [ ] Verify SBOM/signing pipeline remains operational.
- [ ] Review vulnerability backlog and SLA compliance.
- [ ] Validate incident response drills executed and documented.

## 3. Compliance
- [ ] Check regulatory changes (e.g., PCI DSS, GDPR guidance).
- [ ] Update policy library and control matrix accordingly.
- [ ] Ensure audit evidence retained and accessible.

## 4. Training & Awareness
- [ ] Refresh security champion program curricula.
- [ ] Review phishing simulation metrics; adjust training.
- [ ] Communicate new threats to engineering teams.

## 5. Source Log
| Date | Source | Notes |
| --- | --- | --- |
| 2025-11-11 | OWASP Top 10 2021 + 2024 addendum, OWASP API Top 10 2023 | Re-mapped mitigations and runtime controls |
| 2025-11-11 | NIST SSDF Rev.1 draft + CSF 2.0 roadmap | Updated SDLC and governance alignment |
| 2025-11-11 | CIS Controls v8.1 & cloud benchmarks | Refreshed cloud/IaC guidance and metrics |
| 2025-11-11 | CNCF Security Whitepaper v2.1, Google Threat Horizons Q3 2025 | Informed detection, response, and runtime protection |

> Tip: Use `adn_skills("distill_from_wikipedia", topic="Secure software development")` for quick refreshers, then pull latest policies with `adn_skills("import_from_github", repository="owasp/www-project-top-ten")` to diff changes and summarize updates in metadata sources.***
