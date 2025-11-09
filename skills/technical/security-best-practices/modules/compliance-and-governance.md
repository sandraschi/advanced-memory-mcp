# Compliance & Governance

**Confidence**: 🟢 High  
**Last validated**: 2025-11-11  
**Primary sources**: NIST Cybersecurity Framework 2.0 (final 2024, roadmap 2025-10), ISO/IEC 27001:2022 & 27002:2022, SOC 2 Trust Services Criteria (2025), CIS Controls v8.1, DORA RTS (2025 draft), PCI DSS 4.0 FAQ (2025-07), Gartner “Cybersecurity Program Management” (2025)

---

## 1. Governance Framework & Policies

- Establish master policy hierarchy: Corporate Information Security Policy (CISP) → standards → procedures → guidelines.  
- Map policy statements to control catalogs (e.g., NIST CSF 2.0 Functions, ISO 27001 Annex A, CIS v8). Maintain traceability matrix.  
- Review policies annually or when regulatory changes occur (e.g., DORA, AI Act). Include legal, compliance, HR, security stakeholders.  
- Publish policies in accessible knowledge base; require employee attestation.

---

## 2. Control Implementation & Evidence

- Maintain control matrix capturing: control objective, implementation detail, owner, system scope, evidence source, monitoring cadence.  
- Automate evidence collection where possible (CI run logs, infrastructure state snapshots, IAM reports). Use GRC tooling (ServiceNow GRC, Drata, Vanta) or internal dashboards.  
- Define control health indicators (pass/fail, maturity score). Escalate red/yellow controls in governance forums.  
- Integrate control verification into CI/CD (policy-as-code) and change management workflows.

---

## 3. Assurance, Audits & Risk Management

- Schedule internal audits quarterly (rotating themes) and external attestations per compliance obligations (SOC 2 Type II annually, ISO surveillance audits).  
- Maintain audit-ready packet: architecture diagrams, network topology, asset inventory, IAM reports, incident response testing evidence, penetration test summaries.  
- Track issues in risk register with owners, severity, due dates; integrate with enterprise risk management.  
- Perform annual risk assessments (ISO 27005 / NIST 800-30 methodology) and update risk appetite statements approved by leadership/board.

---

## 4. Vendor & Third-Party Risk Management

- Maintain vendor inventory with data classification, connectivity, and contract SLAs.  
- Assess critical vendors using SIG/SIG Lite, CSA STAR, or custom questionnaires; request SOC 2, ISO certs, pen test summaries.  
- Implement contractual clauses: breach notification timelines, subprocessor transparency, right to audit, incident cooperation.  
- Continuous monitoring: leverage SecurityScorecard/BitSight, monitor CISA KEV for vendor CVEs, require SBOM for software suppliers.  
- Establish offboarding/termination playbook (access revocation, data return/destruction).

---

## 5. Training, Awareness & Culture

- Deliver onboarding + annual training tailored to roles (engineers, support, execs). Track completion metrics and knowledge checks.  
- Run quarterly phishing/social engineering simulations; feed results into targeted micro-training.  
- Promote security champions program, lunch-and-learn sessions, “security office hours.”  
- Include security responsibilities in job descriptions and performance reviews.

---

### Governance Checklist
- [ ] Policy library aligned with NIST CSF 2.0 / ISO 27001, reviewed in last 12 months, employee attestations captured.  
- [ ] Control matrix up to date with owners, evidence locations, and automated health indicators.  
- [ ] Internal/external audit schedule executed; remediation items tracked to closure.  
- [ ] Vendor risk management lifecycle operating with continuous monitoring and contractual safeguards.  
- [ ] Security awareness + role-based training delivered with measurable improvements.

Strong governance ensures security practices remain compliant, auditable, and integrated with enterprise risk management.***

