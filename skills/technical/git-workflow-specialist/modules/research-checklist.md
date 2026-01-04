# Research Checklist

Run this validation every 6 months or after major Git platform announcements.

## 1. Source Refresh
- [ ] Review latest Git release notes (https://github.com/git/git/tree/master/Documentation/RelNotes).
- [ ] Check hosting provider updates (GitHub, GitLab, Azure DevOps) for workflow features.
- [ ] Monitor trunk-based development and GitFlow community articles for emerging practices.
- [ ] Track compliance/security guidelines (CISA, NIST) affecting commit signing or approvals.

## 2. Workflow Health Audit
- [ ] Pull metrics on merge frequency, review turnaround, change failure rate.
- [ ] Inspect backlog of long-lived branches; verify SLA adherence.
- [ ] Validate merge queue / CI stability; note flakiness trends.
- [ ] Review dependency update cadence and automation effectiveness.

## 3. Documentation & Tooling
- [ ] Ensure CONTRIBUTING.md, workflow docs, and PR templates reflect current process.
- [ ] Verify automation scripts/bots still functioning (pre-commit, release bots).
- [ ] Update training materials and record any new walkthroughs.

## 4. Compliance & Governance
- [ ] Audit branch protection and required reviews; adjust if org policy changed.
- [ ] Review signing policies and credential rotation logs.
- [ ] Confirm audit trail accessibility for recent releases/incidents.

## 5. Source Log
| Date | Source | Notes |
| --- | --- | --- |
| 2025-11-08 | Git 2.46 Release Notes | Merge queue enhancements, sparse checkout improvements |
| 2025-11-08 | GitHub Flow Guide 2025 | Updated PR best practices, merge queue docs |
| 2025-11-08 | Trunk-Based Dev Playbook | Reinforced small batch, feature flag guidance |
| 2025-11-08 | Atlassian Git Tutorials | Workflow comparison charts & compliance notes |

> Tip: Start with `adn_skills("distill_from_wikipedia", topic="Git")` for high-level refresh, then dive into primary sources via `adn_skills("import_from_github", repository="git/git", path="Documentation")` before cross-checking official release posts.*** End Patch
