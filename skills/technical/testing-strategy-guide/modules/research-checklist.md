# Research Checklist

Review every 6 months or when major testing frameworks/patterns evolve.

## 1. Source Refresh
- [ ] Google Testing Blog & Accelerate updates.  
- [ ] ThoughtWorks Technology Radar, Testing Dojos.  
- [ ] Framework release notes (pytest, Playwright, Cypress, k6).  
- [ ] Industry case studies (Netflix, Shopify, Microsoft).

## 2. Tooling Audit
- [ ] Validate CI pipelines and shared libraries for compatibility.  
- [ ] Review test flake dashboard; track resolution rate.  
- [ ] Confirm license/support plans for testing tools.  
- [ ] Update devcontainers/local tooling for parity.

## 3. Metrics & Outcomes
- [ ] Recalculate coverage and mutation scores; adjust targets.  
- [ ] Analyze escaped defect trends.  
- [ ] Assess pipeline duration and resource costs.

## 4. Documentation & Training
- [ ] Update testing handbook, templates, examples.  
- [ ] Refresh training sessions for new hires.  
- [ ] Archive outdated frameworks/tests.

## 5. Source Log
| Date | Source | Notes |
| --- | --- | --- |
| 2025-11-08 | Google Testing Blog | Test flake mitigation strategies |
| 2025-11-08 | ThoughtWorks Radar 2025 | Emerging testing practices |
| 2025-11-08 | pytest 8.1 Docs | New fixtures, plugin ecosystem |
| 2025-11-08 | Playwright 1.50 Release | Web automation improvements |

> Tip: Start with `adn_skills("distill_from_wikipedia", topic="Software testing")` for context, then track upstream changes via `adn_skills("import_from_github", repository="pytest-dev/pytest", path="doc/en")` to keep documentation current.***
