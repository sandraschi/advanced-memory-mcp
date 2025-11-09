# Automation & Tooling

**Confidence**: 🟡 Medium  
**Last validated**: 2025-11-08  
**Primary sources**: GitHub Code Review Metrics (2024), GitLab Duo Auto Review (2025 preview), JetBrains Space Review Analytics (2025), Google Code Search Tips (2024)

---

## 1. Static & Dynamic Automation

- **Pre-submit gates**: auto-formatters (Prettier, Black), lint (ESLint, Ruff, golangci-lint), type checking (mypy, tsc).  
- **Security**: CodeQL, Semgrep, Bandit; integrate with PR annotations.  
- **Dependency bots**: Dependabot/Renovate with auto-merge for low-risk updates.  
- **Test status**: require CI success; display coverage diffs (Codecov, Sonar).

Ensure automation posts clear annotations to reduce reviewer toil.

---

## 2. AI Assistants

- Use AI (GitHub Copilot, GitLab Duo, Code Whisperer) for summarising changes and suggesting improvements.  
- Treat AI suggestions as starting points; reviewers remain accountable.  
- Maintain guardrails: avoid exposing secrets, ensure licenses allow usage, log AI usage for audit.

---

## 3. Review Metrics & Analytics

Track and share:
- *Review turnaround*: time from assignment to first response.  
- *Rework ratio*: number of follow-up commits per review.  
- *Reviewer load*: open reviews per engineer; balance to avoid burnout.  
- *Approval-to-merge latency*: highlight bottlenecks.

Use GitHub Insights, LinearB, Swarmia, or custom dashboards.

---

## 4. Review Workflows & Bots

- **Auto-assign** reviewers using CODEOWNERS and rotation bots.  
- **Checklists**: embed review checklists via PR templates or GitHub apps.  
- **Reminder bots**: Slack reminders for stale reviews; escalate after SLA breach.  
- **Label automation**: label `needs-tests`, `docs-missing`, `breaking-change` automatically based on diff heuristics.

Automate low-value tasks so humans focus on architecture and quality.

---

## 5. Tooling Hygiene

- Periodically audit bots/Apps for permissions and necessity.  
- Keep CODEOWNERS and reviewer groups updated as teams evolve.  
- Version tool configurations (lint rules, formatters) with the codebase.  
- Provide onboarding docs with tool usage patterns and failure handling.

---

### Quick Actions
- [ ] Ensure all repositories have CODEOWNERS, PR templates, and CI gates configured.  
- [ ] Set up analytics dashboard with turnaround and rework metrics.  
- [ ] Review AI assistant policy and document acceptable use.  
- [ ] Automate reminders for reviews older than SLA.

Automation amplifies reviewer effectiveness—iterate regularly to remove friction.*** End Patch

