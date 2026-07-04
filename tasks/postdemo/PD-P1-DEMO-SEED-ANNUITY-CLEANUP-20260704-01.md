# PD-P1-DEMO-SEED-ANNUITY-CLEANUP-20260704-01

## Story Shape Classification

- shared_file_density: low
- prereq_dependency_density: low
- be_fe_coupling: none
- evidence_cost: medium

## chosen_runbook

`P0-single-lane-story`

## Closure Slice

Fix the P1 demo seed cleanup so `demo:p1:seed` can safely reset data after a full lifecycle demo that generated annuity tasks, annuity fee drafts, GovPayment rows, and dynamic pay-list records for `CASE-PD-P1-LIVE`.

## Non-Closure

No product UI changes, no API behavior changes, no schema changes, no broad smoke cleanup, and no deletion outside explicit P1 demo fixture ownership.

## Allowlist

- `FPMS_Automation_Skeleton_Pack/playwright_ts/src/support/pdP1LiveSeed.py`
- `artifacts/PD-P1-DEMO-SEED-ANNUITY-CLEANUP-20260704-01/**`

## Verification

- Red: `cd FPMS_Automation_Skeleton_Pack/playwright_ts && NO_PROXY=127.0.0.1,localhost no_proxy=127.0.0.1,localhost FPMS_API_URL=http://127.0.0.1:8000/api/v1 FPMS_BASE_URL=http://127.0.0.1:5173 npm run test:pd-p1` fails during fixture cleanup with SQLite FK error.
- Green: `cd FPMS_Automation_Skeleton_Pack/playwright_ts && npm run demo:p1:seed`
- Green: same `npm run test:pd-p1`
- `./scripts/task_validate.sh PD-P1-DEMO-SEED-ANNUITY-CLEANUP-20260704-01`

## Done Definition

- Dynamic annuity pay-lists derived from P1 demo fee items or `CASE-PD-P1-LIVE` GovPayment rows are deleted before fee drafts and the case row.
- Cleanup remains constrained to explicit P1 demo fixture ownership and does not use broad wildcard deletion.

## Remaining Follow-Up Task IDs

None.
