# PD-P1-DEMO-V5-SEED-CLEANUP-NEW-CASE-20260705-01

## Design References

- `AGENTS.md`
- `docs/postdemo/postdemo_p1_lifecycle_demo_design_20260704.md`
- `docs/postdemo/postdemo_p1_lifecycle_demo_script_20260704.md`
- `FPMS_Automation_Skeleton_Pack/playwright_ts/src/support/pdP1LiveSeed.py`
- `FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/pd-p1.live-backend.spec.ts`
- Current backend SQLite demo seed models for clients, cases, documents, official workflows, fees, grant fees, and annuity.

## Story Shape Classification

- `shared_file_density`: medium
- `prereq_dependency_density`: medium
- `be_fe_coupling`: medium
- `evidence_cost`: high
- `chosen_runbook`: `P0-prereq-heavy-story`

## Exact Closure Slice

Add a safe V5 demo cleanup/seed path that preserves one old V4 demo dataset and creates a new V5 demo customer, new case, filing package, OA package, fee draft/pay-list, letter, grant fee task, and annuity tasks from explicit fixture IDs.

## Explicit Non-Closure

Do not delete real data. Do not use wildcard cleanup. Do not change product business logic, database schema, UI behavior, CPC/OA direct submit, RPA, QR/signature automation, automatic official payment, or Longxia email automation.

## Allowed Files

- `tasks/postdemo/PD-P1-DEMO-V5-SEED-CLEANUP-NEW-CASE-20260705-01.md`
- `FPMS_Automation_Skeleton_Pack/playwright_ts/src/support/pdP1LiveSeed.py`
- `FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/pd-p1.live-backend.spec.ts`
- `FPMS_Automation_Skeleton_Pack/playwright_ts/package.json`
- `artifacts/PD-P1-DEMO-V5-SEED-CLEANUP-NEW-CASE-20260705-01/**`

## Demo Data Boundary

- Preserve old comparison data: `CLIENT-PD-P1-LIVE`, `P1E2E-LIVE`, `CASE-PD-P1-LIVE`.
- V5 seed may delete and recreate only explicit V5 fixture IDs such as `CLIENT-PD-P1-V5-LIVE`, `P1E2E-V5-LIVE`, `CASE-PD-P1-V5-LIVE`, `FILING-PD-P1-V5-LIVE`, `OA-PD-P1-V5-LIVE`, `FD-PD-P1-V5-LIVE`, `DOC-LETTER-PD-P1-V5-LIVE`, V5 grant fee task, and V5 annuity task IDs.
- No `LIKE '%P1%'`, prefix-only, or broad `SMOKE-*` cleanup is allowed.

## Verification Commands

- Red test before implementation: `cd FPMS_Automation_Skeleton_Pack/playwright_ts && npm run test:pd-p1:v5 -- --grep @P1-v5-seed`
- Green test after implementation: `cd FPMS_Automation_Skeleton_Pack/playwright_ts && npm run demo:p1:v5:seed`
- `cd FPMS_Automation_Skeleton_Pack/playwright_ts && npm run test:pd-p1:v5 -- --grep @P1-v5-seed`
- `cd FPMS_Automation_Skeleton_Pack/playwright_ts && npx tsc --noEmit`
- `git diff --check -- FPMS_Automation_Skeleton_Pack/playwright_ts/src/support/pdP1LiveSeed.py FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/pd-p1.live-backend.spec.ts FPMS_Automation_Skeleton_Pack/playwright_ts/package.json tasks/postdemo/PD-P1-DEMO-V5-SEED-CLEANUP-NEW-CASE-20260705-01.md`
- `./scripts/task_validate.sh PD-P1-DEMO-V5-SEED-CLEANUP-NEW-CASE-20260705-01`

## Done Definition

- V5 seed is idempotent.
- V5 seed refuses unsafe environments according to the existing demo seed safety rules.
- V5 seed does not delete old `P1E2E-LIVE` data.
- V5 seed creates `CLIENT-PD-P1-V5-LIVE` and `P1E2E-V5-LIVE` plus downstream P1/P1.5 demo fixtures.
- Targeted V5 seed test proves old data is preserved and new data is created.
- Required evidence exists under `artifacts/PD-P1-DEMO-V5-SEED-CLEANUP-NEW-CASE-20260705-01/**`.

## Remaining Follow-Up Task IDs

- `PD-P1-DEMO-V5-UI-E2E-RUN-20260705-01`
