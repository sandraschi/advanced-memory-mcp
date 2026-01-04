# Maintenance & Governance

**Confidence**: 🟡 Medium
**Last validated**: 2025-11-08
**Primary sources**: Git Large Repository Maintenance Guide (2024), Git Security Best Practices (2025), CISA Secure Software Development Attestation (2025), Compliance frameworks (SOX/ISO)

---

## 1. Repository Hygiene

- Periodically prune stale branches; automate reminders after inactivity threshold.
- Archive or delete deprecated repositories; document migration paths.
- Monitor repository size; use Git LFS or artifact stores for large binaries.
- Run `git fsck` / `git gc` on self-hosted repos or schedule maintenance windows.

---

## 2. Incident Response

- Document rollback procedures for bad releases (revert vs cherry-pick).
- Define process for compromised credentials or malicious commits (rotate tokens, sign-off).
- Maintain audit logs and enable push protection / secret scanning.
- Run incident drills (simulate force push, history rewrite).

---

## 3. Compliance & Audit

- Ensure required sign-offs (CODEOWNERS, approvals) captured in PR metadata.
- Enable branch protection (no force push, require status checks).
- Store release artifacts/checksums; link commits to tickets for traceability.
- Retain logs per compliance policy (30/90/365 days).

---

## 4. Documentation & Training

- Keep CONTRIBUTING.md, README, and workflow docs current.
- Provide onboarding checklists and video walkthroughs.
- Capture retrospectives and lessons learned in runbooks.
- Maintain glossary of Git commands/workflows for new hires.

---

## 5. Metrics & Continuous Improvement

- Track KPIs: lead time for changes, review turnaround, change failure rate, merge conflict frequency.
- Review metrics monthly; identify automation or process improvements.
- Conduct workflow retros after major incidents or releases.
- Rotate workflow stewards to sustain engagement.

---

### Checklist
- [ ] Branch/archive policy automated and visible to team.
- [ ] Incident playbooks tested annually.
- [ ] Compliance controls (approvals, signing) monitored.
- [ ] Documentation refreshed at least quarterly.
- [ ] Metrics reviewed with actionable follow-ups.

Strong governance keeps Git workflows sustainable and audit-ready over time.*** End Patch
