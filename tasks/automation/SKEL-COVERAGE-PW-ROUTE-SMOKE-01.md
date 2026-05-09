# SKEL-COVERAGE-PW-ROUTE-SMOKE-01

## Story Shape Classification

- shared_file_density: medium
- prereq_dependency_density: low
- be_fe_coupling: medium
- evidence_cost: medium
- chosen_runbook: P0-frontend-heavy-story

## Exact Closure Slice

Add a Playwright current-implementation static-route smoke that discovers static frontend routes from the real Vue router, authenticates against the real backend, navigates each static route without API mocking, and asserts the app shell renders without page errors. Update the current coverage audit so this dynamic static-route smoke is counted as covering static frontend routes.

## Explicit Non-Closure

This task does not create test data for dynamic `:id` routes, does not mock backend APIs, does not implement missing canonical case handlers, and does not change frontend product behavior.

## Allowed Files

- `FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/current-static-route-smoke.spec.ts`
- `FPMS_Automation_Skeleton_Pack/scripts/audit_current_coverage.py`
- `tasks/automation/SKEL-COVERAGE-PW-ROUTE-SMOKE-01.md`
- `artifacts/SKEL-COVERAGE-PW-ROUTE-SMOKE-01/**`

## Verification

- `cd FPMS_Automation_Skeleton_Pack/playwright_ts && npx tsc --noEmit`
- `cd FPMS_Automation_Skeleton_Pack/playwright_ts && npm test -- --list --grep "current static frontend routes"`
- `python3 FPMS_Automation_Skeleton_Pack/scripts/audit_current_coverage.py`
- `./scripts/task_validate.sh SKEL-COVERAGE-PW-ROUTE-SMOKE-01`

## Remaining Follow-up Task IDs

- `SKEL-COVERAGE-PW-DYNAMIC-ROUTE-SMOKE-01`
- `SKEL-COVERAGE-PY-REMAINING-HANDLERS-01`
- `SKEL-COVERAGE-BE-ROUTE-GAP-01`

## Done Definition

- Static frontend routes are discovered from the current router at Playwright runtime.
- The smoke uses real login and does not intercept or mock API data.
- The audit reports reduced rough frontend route gap count after static-route coverage is recognized.
- Required evidence and task gate pass.
