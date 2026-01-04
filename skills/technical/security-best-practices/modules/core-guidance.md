# Core Guidance

**Confidence**: 🟢 HIGH
**Last validated**: 2025-11-11

> Begin with context. A good intake distinguishes a high-regulated fintech rollout from an internal prototype and prevents “one-size-fits-all” controls.

---

## 1. Security Intake Blueprint

| Dimension | Key Questions | Evidence / Output |
| --- | --- | --- |
| **Business context** | What products, customer promises, and SLAs are affected? | Security charter, product OKRs |
| **Data classification** | Which datasets (PII, PCI, PHI, trade secrets) are processed? Any residency constraints? | Data inventory, privacy impact assessment |
| **Threat landscape** | What adversaries matter? (eCrime, ransomware, malicious insiders, nation-state) Recent incidents or red-team findings? | Threat model, attack tree |
| **Regulatory scope** | SOC 2, ISO 27001, PCI-DSS 4.0, HIPAA, GDPR/UK GDPR, FedRAMP, DORA, AI Act? | Compliance matrix with control owners |
| **Current controls** | Which secure SDLC steps, detection capabilities, and incident playbooks exist today? | Control catalog, policy library |
| **People & ownership** | Who is accountable? Security champions per squad? On-call rotations for incident response? | RACI, champion roster |

**Deliverable**: Intake findings captured in a security assessment ticket and a living risk register (e.g., Jira, ServiceNow, spreadsheet).

---

## 2. Risk Prioritization & Scorecarding

1. **Map risks** using an impact × likelihood matrix (align severities with corporate risk appetite).
2. **Focus on top systemic threats**: OWASP Top 10, OWASP API Top 10, MITRE ATT&CK TTPs relevant to your stack, supply-chain / SLSA considerations.
3. **Quantify** with a lightweight scorecard:
   - Critical APIs without authentication? => score 5
   - CVSS ≥ 9.0 findings unresolved >7 days? => score 4
   - SBOM coverage < 70% of services? => score 3
4. Produce an executive summary that separates **“rapid wins”** (e.g., secret detection) from **strategic programmes** (e.g., zero trust network segmentation).

---

## 3. Outcome & Metric Alignment

- Tie security improvements to **business outcomes**: e.g., “Reduce high severity MTTR from 7 days to 48 hours,” or “Achieve ISO 27001 certification Q2.”
- Track **leading indicators** (SAST coverage %, threat model completion per epic) and **lagging indicators** (critical vulnerability backlog, incident MTTA/MTTR).
- Align with engineering OKRs or value-stream KPIs; publish dashboards (Looker, Grafana, PowerBI) to reinforce accountability.

---

## 4. Operating Model & Governance

| Element | Recommendation |
| --- | --- |
| **Security steering committee** | Meets monthly; includes eng leadership, product, compliance, CISO delegate. Maintains risk register decisions. |
| **Security champions** | One per squad/service line; 10–15% time allocation; maintain “security backlog” inside sprint tracking. |
| **Working cadences** | Weekly sync: triage new findings. Monthly deep dive: top risks, preview of upcoming audits. Quarterly business review: metrics vs OKRs. |
| **Artifacts** | Security strategy doc, control matrix (owners + tooling), tabletop exercise calendar, vendor risk tracker. |

Document roles/responsibilities (RACI) and share internally (Confluence/Notion/SharePoint).

---

## 5. Escalation & Incident Readiness

- Maintain severity guidelines (SEV0 critical) with explicit impact thresholds (data exfiltration, production outage).
- Publish on-call tree (Security Ops → Duty Manager → Incident Commander) and contact channels (Slack #security-incident, hotline).
- Define decision points: when to engage legal/privacy, escalate to executives, or contact regulators/customers.
- Conduct quarterly tabletop exercises covering ransomware, supply-chain compromise, insider risk scenarios; feed outcomes into [modules/detection-and-response.md](modules/detection-and-response.md).

---

## 6. Scorecard Snapshot Template

| Category | Maturity (1–5) | Notes / Actions |
| --- | --- | --- |
| Secure SDLC | 3 | Threat modeling coverage 60%; target 90% by Q1. |
| Application security | 2 | API auth gaps identified; align with OWASP API Top 10 controls. |
| Cloud & infra | 4 | CIS benchmarks automated; secrets rotation still manual in two regions. |
| Detection & response | 3 | SIEM has coverage; need playbooks for AI/LLM abuse. |
| Compliance & governance | 4 | SOC 2 Type II complete; prepping for PCI DSS 4.0 SAQ D. |

Review and share quarterly (see research checklist).

---

### Module Map
- Secure SDLC → [modules/secure-sdlc.md](modules/secure-sdlc.md)
- Application security → [modules/application-security.md](modules/application-security.md)
- Cloud & infrastructure → [modules/cloud-and-infrastructure.md](modules/cloud-and-infrastructure.md)
- Detection & response → [modules/detection-and-response.md](modules/detection-and-response.md)
- Compliance & governance → [modules/compliance-and-governance.md](modules/compliance-and-governance.md)

Re-run intake at least quarterly or whenever business scope shifts (new regions, mergers, major feature launches).***
