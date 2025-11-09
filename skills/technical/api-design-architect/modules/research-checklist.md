# Research Checklist

Use this lightweight cycle every quarter or when major standards change.

## 1. Source Refresh
- [ ] Check Microsoft REST API Guidelines changelog (https://github.com/microsoft/api-guidelines/releases).  
- [ ] Review OWASP API Security Top 10 updates (https://owasp.org/API-Security/) for new mitigations.  
- [ ] Validate GraphQL spec revisions (https://spec.graphql.org/) and Apollo federated roadmap.  
- [ ] Monitor CNCF API landscape reports for emerging tooling.

## 2. Protocol Drill-down
- [ ] REST: confirm error format alignment with RFC 9457 / Problem Details updates.  
- [ ] GraphQL: test new depth/complexity limit recommendations; record metrics.  
- [ ] gRPC: verify buf build pipeline and code generation outputs; watch for protobuf breaking changes.  
- [ ] AsyncAPI: assess 3.x roadmap; capture channel naming patterns from community case studies.

## 3. Security & Observability
- [ ] Run automated security scans (ZAP/StackHawk/42Crunch) on exemplar APIs; link reports.  
- [ ] Recalculate SLO baselines; ensure dashboards include new endpoints.  
- [ ] Confirm trace sampling strategy still meets cost vs fidelity needs.

## 4. Update Artefacts
- [ ] Append new sources (title + URL + access date) to the table below and to `metadata.sources`.  
- [ ] Note resulting changes in change log / release notes.  
- [ ] Revisit [modules/known-gaps.md](known-gaps.md) and close addressed items.

## 5. Source Log
| Date | Source | Notes |
| --- | --- | --- |
| 2025-11-08 | Microsoft REST API Guidelines vLatest | Confirmed naming, pagination, error semantics |
| 2025-11-08 | OWASP API Security Top 10 (2023) | Revalidated BOLA mitigations, rate-limiting recommendations |
| 2025-11-08 | GraphQL Spec June 2024 | Checked directives, deprecation behaviour, APQ guidance |
| 2025-11-08 | CNCF API Landscape 2025 | Emerging tooling and governance metrics |

> Tip: Use `adn_skills("distill_from_wikipedia", topic="Application programming interface")` or `adn_skills("distill_from_arxiv", query="API governance")` to seed research, then pull canonical guidance via `adn_skills("import_from_github", repository="microsoft/api-guidelines")` before updating core modules.*** End Patch
