# Research Checklist

Use this flow each quarter or when significant tooling/AI changes land.

## 1. Source Refresh
- [ ] Review Google “Engineering Practices” updates (https://google.github.io/eng-practices/).
- [ ] Check Microsoft, GitHub, and Atlassian code review guidance posts for new recommendations.
- [ ] Track ThoughtWorks Technology Radar entries relevant to review tooling.

## 2. Metrics & Analytics
- [ ] Export review turnaround, rework rate, defect escape rate; compare against targets.
- [ ] Survey developers for review satisfaction; log sentiments.
- [ ] Inspect random merged PRs for calibration (quality audit).

## 3. Tooling Validation
- [ ] Audit lint/check configurations; ensure automation covers style issues.
- [ ] Review AI assistant policy; test latest capabilities and guardrails.
- [ ] Confirm CODEOWNERS and reviewer rotation scripts reflect team changes.
- [ ] Ensure reminder bots and dashboards still operate correctly.

## 4. Policy & Documentation
- [ ] Update Definition of Review Done and reviewer onboarding docs.
- [ ] Record new examples of exemplary reviews for knowledge base.
- [ ] Refresh inline comment templates/examples.

## 5. Source Log
| Date | Source | Notes |
| --- | --- | --- |
| 2025-11-08 | Google Engineering Practices (2024-10) | Verified review goals, communication patterns |
| 2025-11-08 | Microsoft Code Review Playbook (2025-05) | Added AI assistant cautions |
| 2025-11-08 | GitHub Code Review Metrics (2024) | Benchmarked turnaround, approval rates |
| 2025-11-08 | ThoughtWorks Tech Radar (2025-04) | Highlighted evolving review tooling |

> Tip: Kick off refreshes with `adn_skills("distill_from_wikipedia", topic="Code review")`, then fetch updated guidance via `adn_skills("import_from_github", repository="google/eng-practices")` before confirming with official docs.*** End Patch
