# Collaboration & Reviews

**Confidence**: 🟡 Medium
**Last validated**: 2025-11-08
**Primary sources**: GitHub Pull Request Guide (2025), Google Engineering Practices (Code Review 2024), LinearB Engineering Benchmarks (2024), Pair Programming Research (2024 ACM)

---

## 1. Pull Request Best Practices

- Keep PRs small (< 400 LOC diff) and focused; link to tracking issues.
- Provide clear summary, testing evidence, screenshots/logs if applicable.
- Use draft PRs for early feedback; convert when ready.
- Apply labels for release notes, breaking changes, or docs updates.

---

## 2. Review Process

- Establish SLA for first response (e.g., < 4 working hours).
- Require at least one qualified reviewer via CODEOWNERS.
- Distinguish comment types (`blocker`, `nit`, `suggestion`).
- Resolve conflicts with synchronous discussion if threads exceed two rounds.
- Capture decisions in PR description or linked ADR.

---

## 3. Pair & Mob Programming

- Encourage pair sessions for complex changes; use co-author commits (`Co-authored-by:`).
- Document driver/navigator cadence; rotate to spread knowledge.
- For mob sessions, capture summary notes and action items in issue tracker.

---

## 4. Conflict Resolution

- Use `git rerere` or `git-imerge` for recurring conflicts; teach devs to rebase frequently.
- For large merges, schedule stabilization windows and allocate conflict sheriffs.
- Automate merge queues to serialize merges and reduce conflicts.

---

## 5. Knowledge Sharing

- Maintain contribution guidelines / style guides.
- Conduct regular “merge retros” to review merged PRs for improvements.
- Celebrate high-quality reviews in team channels to reinforce behaviour.
- Use PR templates with checklists (tests, docs, security).

---

### Checklist
- [ ] Review SLAs agreed and monitored.
- [ ] PR template + labels standardised.
- [ ] Pair/mob guidelines published.
- [ ] Merge conflict playbook documented.
- [ ] Feedback loop (surveys/metrics) active to monitor review satisfaction.

Healthy collaboration practices prevent bottlenecks and ensure consistent code quality.*** End Patch
