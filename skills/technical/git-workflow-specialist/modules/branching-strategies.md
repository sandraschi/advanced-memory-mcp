# Branching Strategies

**Confidence**: 🟡 Medium
**Last validated**: 2025-11-08
**Primary sources**: Trunk-Based Development Book (2024 Edition), Git 2.46 Features, Atlassian GitFlow Guide (2025), GitHub Merge Queue Documentation (2025)

---

## 1. Trunk-Based Development (TBD)

- Short-lived feature branches (< 48 hours); merge via pull request with automated checks.
- Feature flags/dynamic configuration for incomplete work.
- Requires fast CI, merge queue, and strong test automation.
- Benefits: minimal merge conflicts, quick feedback, easier continuous delivery.

### When to use
- High release frequency, microservices/feature flag culture, teams comfortable with continuous integration.

---

## 2. Release Branching / GitFlow

- Long-lived `main` + `develop`, with release and hotfix branches.
- Use when multiple release versions supported simultaneously or compliance demands staging environment.
- Ensure strict policies to avoid drift (cherry-pick fixes forward).
- Automate merging back to `main`/`develop` to reduce human error.

### When to use
- Regulated environments, enterprise products with scheduled releases.

---

## 3. Trunk + Release Branch Hybrids

- Teams work on trunk; create short-lived release branches for stabilization.
- Tag releases from release branch; merge stabilization changes back to trunk.
- Align with GitHub flow (main branch deployable).
- Works well with merge queues and selective backports.

---

## 4. Monorepo Considerations

- Split repo into logical ownership areas with CODEOWNERS.
- Use selective builds (Bazel, Nx, Pants) to minimize CI impact.
- Merge queue or batching (GitHub Merge Queue, Gerrit) to maintain stability.
- Consider virtual sub-repos (git sparse-checkout, worktrees) for developer ergonomics.

---

## 5. Change Promotion & Backporting

- Implement automated cherry-pick bots (GitHub `gh` CLI, GitLab cherry-pick) with templates.
- Track backport obligations in issue tracker; label PRs with target releases.
- For LTS maintenance, maintain dedicated branches with restricted access.

---

### Decision Aids

| Question | TBD | Release Branch | Hybrid |
| --- | --- | --- | --- |
| Need multiple parallel production versions? | 🚫 | ✅ | ✅ |
| Desire rapid continuous delivery? | ✅ | 🚫 | ✅ |
| Strong CI discipline available? | ✅ | ⚠️ | ✅ |
| Heavy compliance checks? | ⚠️ (needs automation) | ✅ | ✅ |

---

### Checklist
- [ ] Selected workflow documented with rationale.
- [ ] Branch protection and automation align with chosen strategy.
- [ ] Feature flag policy defined (if using TBD).
- [ ] Release/backport SOP documented.
- [ ] Training delivered to team on updated workflow.

Choose the simplest workflow that meets business needs; iterate as team maturity grows.*** End Patch
