# PD-P1-DEMO-V5-OA-SIGNATURE-SEED-FIX-20260705-01

## Design References

- `AGENTS.md`
- `docs/postdemo/postdemo_p1_lifecycle_demo_script_20260704.md`
- `FPMS_Automation_Skeleton_Pack/playwright_ts/src/support/pdP1LiveSeed.py`
- `artifacts/PD-P1-DEMO-V5-UI-E2E-RUN-20260705-01/**`

## Story Shape Classification

- `shared_file_density`: low
- `prereq_dependency_density`: low
- `be_fe_coupling`: low
- `evidence_cost`: medium
- `chosen_runbook`: `P0-single-lane-story`

## Exact Closure Slice

Fix V5 demo seed so OA reply package `SIGNATURE_CONFIRMED` starts as confirmed, matching V4 and allowing receipt archive gate completion, while filing package signature confirmation remains pending.

## Explicit Non-Closure

Do not change product logic, backend APIs, UI behavior, database schema, CPC/OA direct submit, RPA, automatic signature, automatic payment, or Longxia email automation.

## Allowed Files

- `tasks/postdemo/PD-P1-DEMO-V5-OA-SIGNATURE-SEED-FIX-20260705-01.md`
- `FPMS_Automation_Skeleton_Pack/playwright_ts/src/support/pdP1LiveSeed.py`
- `artifacts/PD-P1-DEMO-V5-OA-SIGNATURE-SEED-FIX-20260705-01/**`

## Verification Commands

- Red DB check: V5 OA `SIGNATURE_CONFIRMED` is not `DONE`.
- `cd FPMS_Automation_Skeleton_Pack/playwright_ts && npm run demo:p1:v5:seed`
- Green DB check: V5 OA `SIGNATURE_CONFIRMED` is `DONE`, and V5 filing `SIGNATURE_CONFIRMED` remains `PENDING`.
- `cd backend && .venv/bin/ruff check ../FPMS_Automation_Skeleton_Pack/playwright_ts/src/support/pdP1LiveSeed.py`
- `git diff --check -- FPMS_Automation_Skeleton_Pack/playwright_ts/src/support/pdP1LiveSeed.py tasks/postdemo/PD-P1-DEMO-V5-OA-SIGNATURE-SEED-FIX-20260705-01.md`
- `./scripts/task_validate.sh PD-P1-DEMO-V5-OA-SIGNATURE-SEED-FIX-20260705-01`

## Done Definition

- V5 OA package archive gate is not blocked by seed-created signature checklist state.
- V5 filing package still reflects pending manual signature responsibility.
- Required evidence exists under `artifacts/PD-P1-DEMO-V5-OA-SIGNATURE-SEED-FIX-20260705-01/**`.

## Remaining Follow-Up Task IDs

None.
