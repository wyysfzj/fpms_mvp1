# FPMS-DEMO-FIRST-LOAD-NETWORK-RELIABILITY-20260823-01

Status: ACTIVE
Risk-Class: PROTECTED
Dependency: customer V5 candidate `9abb17b5e298d7080abe47d27072f8c25b91cbaa`
and the customer instruction on 2026-08-23 to eliminate first-load `Network Error` from the
case-detail and payment pages before the live demo resumes.

## Observable Outcome

The local V5 demo serves browser API traffic through the frontend origin at `/api/v1`. A clean
browser context can log in and open the exact case-detail and payment pages on the first attempt,
without reload, without an API CORS preflight, without a failed browser API request, and without a
visible `Network Error`. The behavior remains true across repeated clean browser contexts and two
independent fresh local-demo runs.

## Exact Root-Cause Boundary

The captured failure occurred at the unnecessary local cross-origin boundary: the browser sent a
successful `OPTIONS` request to port 8000 but did not dispatch the corresponding GET; Axios therefore
had no HTTP response and displayed `Network Error`. Backend case/list reads, the same lifecycle GET
after reload, and manual CORS response headers were all correct. The browser-internal reason for
abandoning the post-preflight GET remains external and is not guessed. A fresh restart also proved a
second local-runner race: Vite accepted `/api/v1` while Uvicorn was not yet listening, and the proxy
reported `ECONNREFUSED 127.0.0.1:8000`. This story removes the preflight dependency and makes backend
health a prerequisite for starting the frontend, instead of adding page-specific reloads or retries.

## Explicit Non-Closure

No lifecycle, legal-status, deadline, fee, billing, payment, offset, evidence, auth, permission,
schema, migration, seed, API envelope, or production deployment semantics change. Do not add generic
HTTP retries, hide genuine API errors, swallow deterministic 4xx/5xx responses, change backend CORS,
change the production Docker/nginx topology, or refactor unrelated frontend networking. The separate
case fee-reduction display label is not absorbed by this story.

## Allowed Files

- `tasks/postdemo/FPMS-DEMO-FIRST-LOAD-NETWORK-RELIABILITY-20260823-01.md`
- `frontend/vite.config.ts`
- `backend/scripts/run_local_demo_abc.py`
- `backend/tests/test_demo_abc_local_runner.py`
- `FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/demo-first-load-network.live-backend.spec.ts`
- `artifacts/FPMS-DEMO-FIRST-LOAD-NETWORK-RELIABILITY-20260823-01/**`

## Verification Commands

- RED then GREEN: focused pytest for the local runner frontend API-base contract.
- RED then GREEN: focused pytest proves the frontend process is not launched until `/healthz` has
  returned success and that a backend early exit fails closed.
- RED then GREEN: the focused live Playwright contract must observe the old cross-origin URL/preflight
  before the change and, after the change, verify same-origin `/api/v1`, zero API `OPTIONS`, zero
  `requestfailed`, zero visible `Network Error`, and successful first-load case-detail lifecycle and
  payment empty state without reload.
- GREEN: scoped Ruff for the changed Python files, frontend typecheck, Playwright discovery, and
  `git diff --check`.
- Final reliability proof: two fresh local-demo process runs; each runs the browser contract across
  at least three clean browser contexts and retains request/response evidence and cleanup checks.
- Independent High review of the exact committed candidate with `P0/P1/P2 = 0/0/0`.

## Evidence Path

- `artifacts/FPMS-DEMO-FIRST-LOAD-NETWORK-RELIABILITY-20260823-01/**`

## Risk and Rollback

PROTECTED because the affected pages expose lifecycle and customer-finance facts, although this
story changes only the local browser transport topology. Rollback is the single exact story commit;
database and business state are unchanged.

## Remaining Follow-Up Task IDs

- `FPMS-DEMO-CASE-FEE-REDUCTION-DISPLAY-20260823-01`
