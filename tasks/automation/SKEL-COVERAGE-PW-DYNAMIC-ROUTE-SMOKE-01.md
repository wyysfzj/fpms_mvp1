# SKEL-COVERAGE-PW-DYNAMIC-ROUTE-SMOKE-01

## Story Shape Classification

- shared_file_density: low
- prereq_dependency_density: low
- be_fe_coupling: medium
- evidence_cost: medium
- chosen_runbook: P0-frontend-heavy-story

## Exact Closure Slice

Add one Playwright Skeleton Pack smoke test for the currently uncovered dynamic frontend routes only:

- `clients/:id/edit`
- `documents/:id/envelope`
- `documents/:id/edit`
- `collections/dunning/:id`

The smoke must authenticate, create the minimal required real API data, navigate each resolved dynamic route, and assert the app renders without browser page errors.

## Explicit Non-Closure

This task does not add business-flow assertions, does not update product frontend or backend code, does not modify route definitions, does not add API endpoints, and does not cover remaining pytest real-handler gaps.

## Allowed Files

- `FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/current-dynamic-route-smoke.spec.ts`
- `tasks/automation/SKEL-COVERAGE-PW-DYNAMIC-ROUTE-SMOKE-01.md`
- `artifacts/SKEL-COVERAGE-PW-DYNAMIC-ROUTE-SMOKE-01/**`

## Verification

- `cd FPMS_Automation_Skeleton_Pack/playwright_ts && npx tsc --noEmit`
- `cd FPMS_Automation_Skeleton_Pack/playwright_ts && npx playwright test src/tests/current-dynamic-route-smoke.spec.ts --list`
- `python3 FPMS_Automation_Skeleton_Pack/scripts/audit_current_coverage.py`
- `./scripts/task_validate.sh SKEL-COVERAGE-PW-DYNAMIC-ROUTE-SMOKE-01`

## Remaining Follow-up Task IDs

- `SKEL-COVERAGE-PY-X-TASK-SPECIAL-SEARCH-01`
- `SKEL-COVERAGE-PY-X-TASK-LOGS-01`
- Additional per-case real-handler coverage tasks for the remaining audit gaps.

## Done Definition

- The new Playwright smoke includes all four currently uncovered dynamic frontend routes.
- The smoke uses real API setup rather than mocked frontend data.
- TypeScript validation and Playwright test listing pass.
- Coverage audit reports `rough_frontend_uncovered_route_count: 0`.
- Required evidence and task gate pass.
