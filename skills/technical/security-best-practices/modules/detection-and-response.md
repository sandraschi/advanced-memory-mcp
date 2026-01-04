# Detection & Response

**Confidence**: 🟢 High
**Last validated**: 2025-11-11
**Primary sources**: MITRE ATT&CK v14 (Oct 2025), MITRE D3FEND, Google Cloud IR Playbook (2025-03), AWS Security Incident Response Guide (2025-07), Microsoft Defender “Threat Intelligence” digest Q3 2025, FIRST CSIRT Services Framework v2.1

---

## 1. Telemetry & Observability

- **Log coverage**: Capture auth events, privilege escalations, IAM changes, network flows, endpoint telemetry, container/Kubernetes audit logs, SaaS admin actions.
- **Normalization**: Use structured logging (JSON) and consistent field taxonomy (Elastic ECS, Splunk CIM) to enable correlation.
- **Tracing**: Instrument OpenTelemetry spans with security attributes (user ID, device ID, request risk score) to trace attack paths.
- **Retention**: Align with regulatory requirements—baseline 180 days hot/log searchable, 365+ days cold storage; ensure immutability (S3 Object Lock, WORM).
- **Integrity**: Hash/sign logs or forward via secure channels to prevent tampering.

---

## 2. Detection Engineering & Alerting

- Map detections to MITRE ATT&CK tactics/techniques; maintain coverage matrix.
- Use managed analytics (AWS GuardDuty, Azure Sentinel, Chronicle) plus custom rules (Sigma, KQL, Splunk SPL).
- Build behavior-based detections (suspicious OAuth grants, service account privilege escalation, unusual data egress) in addition to IOC-based alerts.
- Apply machine learning / UEBA judiciously—tune to reduce false positives.
- Document triage playbooks in SOAR platform (Chronicle SOAR, Cortex XSOAR, Tines) with automation for containment (isolate host, revoke credentials).

---

## 3. Incident Response Lifecycle

1. **Preparation**: IR plan approved by leadership, roles defined (incident commander, comms, legal, privacy). Ensure secured comms channel and war-room tooling.
2. **Detection & analysis**: Triage alerts, determine scope, classify severity (SEV0–SEV3). Use forensic tooling (Velociraptor, AWS IR, Azure Rapid Response).
3. **Containment**: Short-term (isolate resources, revoke tokens), long-term (patch, apply segmentation). Coordinate with change management to avoid business disruption.
4. **Eradication & recovery**: Clean systems, redeploy from trusted images, monitor for re-entry.
5. **Post-incident**: Conduct blameless postmortem within 5 business days, capture lessons, update controls and training.

Maintain runbooks for high-likelihood scenarios (credential theft, ransomware, supply-chain compromise, misconfiguration).

---

## 4. Threat Intelligence Program

- Consume threat intel: CISA KEV, vendor advisories, ISAC sharing groups, commercial feeds (Recorded Future, CrowdStrike, Mandiant).
- Automate enrichment: integrate STIX/TAXII feeds into SIEM/SOAR, auto-block high-confidence IOC via firewall/EDR.
- Align intelligence with ATT&CK mapping to identify detection gaps.
- Share sanitized intel back through ISAC/ISAO when beneficial; follow legal/compliance guidelines.

---

## 5. Metrics, Assurance & Continuous Improvement

- **Key metrics**: MTTA, MTTR, detection coverage %, false positive rate, number of exercises performed, % playbooks with automation.
- **Exercises**: Conduct quarterly tabletop exercises and annual live-fire / purple team engagements (Atomic Red Team, SCYTHE).
- **Control validation**: Use breach and attack simulation (Prelude Operator, SafeBreach) to validate detections continuously.
- **Feedback loop**: Post-incident action items tracked to completion; update detections, runbooks, and training.
- **Executive reporting**: Provide quarterly summaries with risk trends and improvement roadmap to leadership/board.

---

### Response Readiness Checklist
- [ ] Comprehensive telemetry centralized, retained, and integrity protected.
- [ ] Detection rules aligned to ATT&CK with SOAR-backed response playbooks.
- [ ] Incident response plan rehearsed; on-call rotation staffed and trained.
- [ ] Threat intelligence operationalized (ingestion, enrichment, sharing).
- [ ] Metrics reviewed with leadership; continuous validation (BAS/purple team) scheduled.

Robust detection and response ensures rapid containment and recovery when preventive controls are bypassed.***
