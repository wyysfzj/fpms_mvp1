# PD-P1-DEMO-SEED-SAFETY-GUARDS-20260704-01

## Story Shape Classification

- shared_file_density: low
- prereq_dependency_density: low
- be_fe_coupling: none
- evidence_cost: medium

## chosen_runbook

`P0-single-lane-story`

## Closure Slice

Add safety guards to the P1 demo seed cleanup: block execution outside local/dev/demo/test environments, and prevent deleting a dynamic pay-list if it contains non-P1-demo GovPayment rows.

## Non-Closure

No product UI changes, no API behavior changes, no schema changes, no broad smoke cleanup, and no change to P1 demo fixture identity.

## Allowlist

- `FPMS_Automation_Skeleton_Pack/playwright_ts/src/support/pdP1LiveSeed.py`
- `tasks/postdemo/PD-P1-DEMO-SEED-SAFETY-GUARDS-20260704-01.md`
- `artifacts/PD-P1-DEMO-SEED-SAFETY-GUARDS-20260704-01/**`

## Verification

- Red: `FPMS_ENV=prod ... pdP1LiveSeed.py` should be rejected but currently runs.
- Green: `FPMS_ENV=prod ... pdP1LiveSeed.py` exits non-zero with a safety message.
- Green: seed cleanup rejects a mixed pay-list that contains a non-demo GovPayment row.
- Green: normal `npm run demo:p1:seed` succeeds.
- `backend/.venv/bin/python -m py_compile FPMS_Automation_Skeleton_Pack/playwright_ts/src/support/pdP1LiveSeed.py`
- `./scripts/task_validate.sh PD-P1-DEMO-SEED-SAFETY-GUARDS-20260704-01`

## Done Definition

- The seed script cannot run when `FPMS_ENV` is production-like.
- Dynamic pay-list deletion only proceeds when every GovPayment on that pay-list belongs to `CASE-PD-P1-LIVE` or its demo fee items.
- Normal local demo seed remains repeatable.

## Remaining Follow-Up Task IDs

None.
