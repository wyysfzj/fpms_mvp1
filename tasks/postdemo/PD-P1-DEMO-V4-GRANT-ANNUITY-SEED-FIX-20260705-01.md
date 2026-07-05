# PD-P1-DEMO-V4-GRANT-ANNUITY-SEED-FIX-20260705-01

## Story Shape Classification

- shared_file_density: medium
- prereq_dependency_density: medium
- be_fe_coupling: low
- evidence_cost: medium
- chosen_runbook: P0-frontend-heavy-story

## Closure

Make the P1 live demo seed prepare stable grant-fee and annuity task fixtures for case `P1E2E-LIVE`, so the V4 UI demo can show the authorization fee node and annuity monitoring node without depending on manual date-picker input or incidental existing demo data.

## Non-Closure

Do not change product status-machine logic, database schema, backend product APIs, frontend product UI, CPC/OA direct submit, RPA, QR/signature automation, automatic official payment, or Longxia email automation.

## Allowlist

- `tasks/postdemo/PD-P1-DEMO-V4-GRANT-ANNUITY-SEED-FIX-20260705-01.md`
- `FPMS_Automation_Skeleton_Pack/playwright_ts/src/support/pdP1LiveSeed.py`
- `FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/pd-p1.live-backend.spec.ts`
- `artifacts/PD-P1-DEMO-V4-GRANT-ANNUITY-SEED-FIX-20260705-01/**`

## Runbook

1. Add a targeted failing Playwright live-backend assertion proving the seed exposes grant-fee and annuity rows for `P1E2E-LIVE`.
2. Minimally update `pdP1LiveSeed.py` to seed only demo fixture rows for grant fee and annuity tasks.
3. Re-run the targeted test.
4. Capture evidence and run the task gate.

## Verification

- `cd FPMS_Automation_Skeleton_Pack/playwright_ts && npx playwright test src/tests/pd-p1.live-backend.spec.ts --grep "@P1-live-demo 授权费和年费"`
- `cd FPMS_Automation_Skeleton_Pack/playwright_ts && npm run demo:p1:seed`
- `./scripts/task_validate.sh PD-P1-DEMO-V4-GRANT-ANNUITY-SEED-FIX-20260705-01`

## Done Definition

- The targeted test fails before the seed fix and passes after the seed fix.
- `demo:p1:seed` remains idempotent and only clears/recreates fixed demo fixture data.
- Grant-fee and annuity task pages can be filtered by `P1E2E-LIVE`.
- Evidence exists under `artifacts/PD-P1-DEMO-V4-GRANT-ANNUITY-SEED-FIX-20260705-01/**`.

## Follow-Up Task IDs

None.
