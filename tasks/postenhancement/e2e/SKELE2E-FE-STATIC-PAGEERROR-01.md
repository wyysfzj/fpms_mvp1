# SKELE2E-FE-STATIC-PAGEERROR-01 — Document dispatch static route page error

Task ID: `SKELE2E-FE-STATIC-PAGEERROR-01`

## Exact Closure Slice

Fix only the frontend static route smoke page error emitted by `/documents/dispatch` when the page loads reference data.

This task closes only:

1. `/documents/dispatch` no longer calls `/doc-templates` with a backend-invalid `page_size`.
2. `FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/current-static-route-smoke.spec.ts` no longer records the `/documents/dispatch` `"Object"` page error.
3. The existing document dispatch page layout and user-facing text remain unchanged.

## Explicit Non-Closure

No backend changes. No schema or migration changes. No route additions. No document dispatch workflow behavior changes beyond making initial reference-data loading use backend-valid pagination.

## Remaining Follow-Up Task IDs

- `SKELE2E-BROWSERUSE-RUNTIME-01`

## Story Shape Classification

| Field | Value |
|---|---|
| shared_file_density | Low. One frontend page and one task file are in scope. |
| prereq_dependency_density | Low. The backend API contract is already proven by the failing smoke and direct API probe. |
| be_fe_coupling | Medium. The fix aligns the FE page with the backend query validation limit without changing backend behavior. |
| evidence_cost | Medium. Requires RED static route smoke, focused rerun, and task gate evidence. |

chosen_runbook: `P0-frontend-heavy-story`

## Allowed Files

- `tasks/postenhancement/e2e/SKELE2E-FE-STATIC-PAGEERROR-01.md`
- `frontend/src/modules/documents/pages/DocumentDispatch.vue`
- `artifacts/SKELE2E-FE-STATIC-PAGEERROR-01/**`

## Verification Commands

- `python3 /Users/cfcc/.codex/skills/atomic-evidence-gates/scripts/evidence_gate.py check-task tasks/postenhancement/e2e/SKELE2E-FE-STATIC-PAGEERROR-01.md`
- `cd FPMS_Automation_Skeleton_Pack/playwright_ts && env FPMS_BASE_URL=http://127.0.0.1:5173 FPMS_API_URL=http://127.0.0.1:8002/api/v1 FPMS_RUN_ID=FESTATIC0510 npm run test -- src/tests/current-static-route-smoke.spec.ts --project=chromium`
- `npm --prefix frontend run typecheck`
- `npm --prefix frontend run lint`
- `python3 /Users/cfcc/.codex/skills/atomic-evidence-gates/scripts/evidence_gate.py validate SKELE2E-FE-STATIC-PAGEERROR-01`
- `./scripts/task_validate.sh SKELE2E-FE-STATIC-PAGEERROR-01`

## Evidence Path

- `artifacts/SKELE2E-FE-STATIC-PAGEERROR-01/`

## Done Definition

- RED evidence shows the static route smoke page error originates at `/documents/dispatch`.
- The page uses backend-valid doc-template list pagination during initial reference-data loading.
- Static route smoke passes without page errors.
- Frontend lint and typecheck pass.
- Required task evidence and task gate pass.
