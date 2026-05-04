# CASEDOCK-QA-REALAPI-E2E-01 — Case document gate real API QA close audit

## Exact Closure Slice

Add or update the smallest FPMS Automation Skeleton Pack real API verification needed for Case Document Gate Minimal UI Mock fullstack completion, run final backend/frontend checks, and write a close audit mapping prompt requirements to implementation files, APIs, tests, and evidence.

## Explicit Non-Closure

No product feature changes unless a harness-only fix is required to run real API evidence. No static network interception as completion evidence. No new dependencies. No database schema or migration changes. No unrelated automation framework refactor.

## Remaining Follow-Up Task IDs

None

## Story Shape Classification

| Field | Value |
|---|---|
| shared_file_density | Medium. QA may add one skeleton pytest test and write close audit evidence; product files are not owned by this task. |
| prereq_dependency_density | High. Depends on all backend and frontend implementation tasks passing independently. |
| be_fe_coupling | High. Final evidence must cover real backend API data used by the frontend surfaces and batch submit hard-block enforcement. |
| evidence_cost | High. Requires skeleton real API verification, backend targeted tests, frontend lint/typecheck/build, all task gates, and close audit. |

chosen_runbook: `P0-prereq-heavy-story`

## Allowed Files

- `tasks/postenhancement/qa/CASEDOCK-QA-REALAPI-E2E-01.md`
- `FPMS_Automation_Skeleton_Pack/pytest_python/**`
- `FPMS_Automation_Skeleton_Pack/playwright_ts/**`
- `artifacts/CASEDOCK-QA-REALAPI-E2E-01/**`
- `artifacts/CASEDOCK-FULLSTACK-CLOSE-AUDIT-01/**`

## Verification Commands

- `FPMS_API_URL=<real API URL> pytest -q FPMS_Automation_Skeleton_Pack/pytest_python/tests/test_casedock_real_api.py`
- backend targeted pytest list from Case Document Gate backend tasks
- `npm --prefix frontend run lint`
- `npm --prefix frontend run typecheck`
- `npm --prefix frontend run build`
- all newly added/updated task gates for this batch
- `python3 /Users/cfcc/.codex/skills/atomic-evidence-gates/scripts/evidence_gate.py check-task tasks/postenhancement/qa/CASEDOCK-QA-REALAPI-E2E-01.md`
- `python3 /Users/cfcc/.codex/skills/atomic-evidence-gates/scripts/evidence_gate.py validate CASEDOCK-QA-REALAPI-E2E-01`
- `./scripts/task_validate.sh CASEDOCK-QA-REALAPI-E2E-01`

## Evidence Path

- `artifacts/CASEDOCK-QA-REALAPI-E2E-01/`
- `artifacts/CASEDOCK-FULLSTACK-CLOSE-AUDIT-01/`

## Done Definition

- Skeleton Pack verification covers real API behavior for intake gate, case detail gate, document impact preview, batch candidate final gate, and batch submit hard-block rejection.
- Final backend targeted tests pass.
- Frontend lint, typecheck, and build pass.
- Every implementation task gate in this fullstack batch passes.
- Close audit maps every prompt requirement to files/APIs/tests/evidence and records "Prettier not applicable" if no Prettier script/config/dependency exists.
