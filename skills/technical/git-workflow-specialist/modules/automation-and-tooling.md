# Automation & Tooling

**Confidence**: 🟡 Medium
**Last validated**: 2025-11-08
**Primary sources**: GitHub Actions Workflow Features (2025), GitLab 17 Pipeline Enhancements (2025), pre-commit 3.7 Docs (2024), Release Please / semantic-release Guides (2025)

---

## 1. Local Automation

- Configure `pre-commit` hooks (lint, format, security scans).
- Provide `gitconfig` snippets for aliases, rerere, credential helpers.
- Document use of worktrees, sparse-checkout for large repos.
- Encourage `git commit --signoff` and gpg/sigstore signing if required.

---

## 2. CI/CD Integration

- Enforce status checks: lint/test/build, security (SAST, secret scanning), license compliance.
- Use merge queues (GitHub, GitLab) to serialize merges with rebase + retest.
- Automate release notes and tagging (Release Please, semantic-release).
- Integrate code coverage, static analysis results into PR checks.

---

## 3. Bot Ecosystem

- Dependabot/Renovate for dependency updates with grouping rules.
- danger.js or Reviewdog for automated PR comments (docs reminders, changelog).
- Auto-assign bots for reviewers; Slack bots for stale PR reminders.
- Cherry-pick/backport bots for LTS branches.

---

## 4. Governance & Auditing

- Centralize CODEOWNERS, branch protection, and repository settings via APIs or Terraform (e.g., GitHub Provider).
- Audit logs for force pushes, branch deletion, permission changes.
- Implement policy-as-code for repo standards (Scorecards, Allstar, GitHub configuration-as-code).

---

## 5. Developer Experience

- Provide CLI tooling (`gh`, `glab`, `git-town`, `git-extras`) with company presets.
- Offer templates for new services/modules (cookiecutter, plop).
- Maintain documentation portal with examples of common tasks (bisect, revert, cherry-pick).

---

### Checklist
- [ ] Pre-commit and local tooling documented and enforced.
- [ ] CI/CD checks mapped to Definition of Done.
- [ ] Bots configured for dependencies, reviews, and backports.
- [ ] Repository governance automated and audited.
- [ ] Developer experience tooling maintained with onboarding guide.

Automation reduces toil and ensures workflows remain consistent across teams.*** End Patch
