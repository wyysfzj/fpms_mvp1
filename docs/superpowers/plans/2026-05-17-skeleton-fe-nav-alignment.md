# Skeleton FE Navigation Alignment Plan

## Story Shape Classification

- shared_file_density: medium
- prereq_dependency_density: low
- be_fe_coupling: frontend automation only
- evidence_cost: medium
- chosen_runbook: P0-frontend-heavy-story

## Task Plan Classification

- shared_file_density: medium
- prereq_dependency_density: low
- be_fe_coupling: frontend automation only
- evidence_cost: medium
- chosen_runbook: P0-frontend-heavy-story

## Atomic Task

- `tasks/automation/SKEL-PW-FE-NAV-ALIGNMENT-01.md`

## Execution Plan

1. Create and validate the atomic task file with the exact closure slice, non-closure, allowlist, verification commands, and follow-up IDs.
2. Initialize evidence for `SKEL-PW-FE-NAV-ALIGNMENT-01`.
3. Update Playwright skeleton defaults to current local frontend/API development URLs.
4. Update login and task page objects to current Chinese labels and current routes.
5. Add a product sidebar page object and fixture.
6. Add a targeted Playwright smoke for production sidebar navigation behavior.
7. Run TypeScript, asset validation, targeted Playwright listing/smoke when services are available, task gate, and evidence validation.

## Shared Ownership Handling

All edits are serialized in this single agent. No concurrent agent owns `FPMS_Automation_Skeleton_Pack/playwright_ts/src/fixtures/fpms.fixtures.ts`, Playwright config, or page objects.

## Non-Closure Boundary

Do not change product `frontend/**`, backend `backend/**`, structured automation data assets, testcase IDs, permission maps, API response contracts, or unrelated Playwright wave handlers.
