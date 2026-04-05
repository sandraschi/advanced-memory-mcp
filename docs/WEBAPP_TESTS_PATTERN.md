# Webapp "Tests" Page Pattern

This repo implements a **Tests page** in the webapp: users can run the project test suite from the UI and see stdout/stderr and pass/fail. This doc describes the pattern so it can be reused across other MCP/webapp repos.

**See also:**

- **Canonical pattern (all webapps):** [mcp-central-docs/patterns/WEBAPP_TESTS_PAGE_PATTERN.md](https://github.com/sandraschi/mcp-central-docs/blob/main/patterns/WEBAPP_TESTS_PAGE_PATTERN.md)
- **MemOps note (knowledge-graph entity):** [docs/notes/webapp-tests-page-pattern.md](notes/webapp-tests-page-pattern.md) — frontmatter, observations, relations for ADN/MemOps.

## Could we use this in all webapps?

Yes. The pattern is generic:

- **Backend:** One endpoint (e.g. `POST /tests/run`) that runs the project test runner in a subprocess (pytest, `npm test`, etc.), with a **feature flag** so it is disabled by default.
- **Frontend:** A "Tests" page with a Run button, optional target/args, and a results area (exit code, duration, stdout/stderr).

Any webapp with a backend can expose the endpoint; any with a frontend can add the page.

## Should we?

**Use it when:**

- The repo has a test suite (pytest, jest, vitest, etc.) and you want to run it from the browser during local dev or demos.
- You want a consistent "run tests and see results" experience across several webapps.
- The app is dev/local-first and you are comfortable guarding the endpoint with an env flag.

**Skip or defer when:**

- The webapp has no tests or only E2E in CI (nothing meaningful to run from the UI).
- The app is strictly production-facing and you do not want to add a test-runner endpoint at all.
- You prefer to keep test execution only in the terminal/CI and not in the webapp.

**Recommendation:** Treat it as an **optional, recommended pattern** for SOTA/local-first webapps. Document it once (e.g. in mcp-central-docs or this doc) and let each repo decide whether to add it. Do not make it mandatory for every webapp.

## Implementation checklist (reuse in another webapp)

1. **Backend**
   - Add a route, e.g. `POST /tests/run`.
   - Require an env guard (e.g. `ENABLE_WEBAPP_TESTS=1`); return 403 if not set.
   - Resolve repo/project root (from `__file__` or env).
   - Run the test command in a subprocess (e.g. `python -m pytest` or `npm run test`) with timeout.
   - Return JSON: `{ success, exit_code, stdout, stderr, duration_seconds }`.

2. **Frontend**
   - Add `runTests(options?)` in the API client.
   - Add a "Tests" page: Run button, optional target/args input, then display result summary and raw stdout/stderr (e.g. in `<pre>`).
   - Add a nav entry (e.g. "Tests" with a flask/beaker icon).

3. **Docs**
   - In the webapp README, note that the Tests page exists and that the backend must be started with the feature flag (e.g. `ENABLE_WEBAPP_TESTS=1`).

## Variations

- **Node/Express backend:** Same idea: `POST /tests/run` runs `npm run test` or `npx jest` in the repo root.
- **Frontend-only webapp:** No backend endpoint; you could run tests only via CI or a separate script, or add a small Node server just for this endpoint.
- **Structured results:** Use a reporter (e.g. pytest-json-report, jest --jsonOutputFile) and return structured pass/fail per test for a richer UI later.

## Security

- Never enable the test runner in production. Rely on the env flag and document that it must not be set in prod.
- Optional: restrict by IP or auth if the webapp is ever exposed beyond localhost.

## Reference in this repo

- Backend: `src/advanced_memory/api/routers/tests_router.py`
- Frontend: `webapp/frontend/src/pages/tests/Tests.tsx`, `api.runTests()`
- Webapp README: "Tests page" and "API endpoints" sections
- MemOps note: `docs/notes/webapp-tests-page-pattern.md` (entity-style note for knowledge graph)

To adopt this in another webapp, copy the router and page logic and adapt the test command and repo-root resolution to that project. The canonical pattern doc lives in **mcp-central-docs** so all webapps share one source of truth.
