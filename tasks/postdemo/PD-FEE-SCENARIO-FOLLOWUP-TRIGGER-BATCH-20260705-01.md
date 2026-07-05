# PD-FEE-SCENARIO-FOLLOWUP-TRIGGER-BATCH-20260705-01

Story Shape Classification
- shared_file_density: medium
- prereq_dependency_density: medium
- be_fe_coupling: medium
- evidence_cost: medium
- chosen_runbook: P0-prereq-heavy-story

## Batch Closure Slice
- Coordinate the P1.5 domestic follow-up fee trigger implementation from `docs/postdemo/postdemo_fee_followup_trigger_design_20260705.md`.
- Complete reexamination fee trigger preview first, then grant/annuity deadline preview.
- Confirm PCT/Hague/IC_LAYOUT remain parameterized and design-frozen, with no automatic trigger enabled.

## Explicit Non-Closure
- No CPC/OA direct submit, RPA, signing, automatic payment, PCT/Hague/IC_LAYOUT automatic trigger implementation, schema migration, or broad fee-state-machine rewrite.

## Execution Waves

### Wave 1
- Task: `tasks/postdemo/PD-FEE-SCENARIO-REEXAM-TRIGGER-PREVIEW-20260705-01.md`
- Owner: main thread
- Serialized files: `backend/app/modules/fees/service.py`, `backend/app/modules/fees/schemas.py`, `frontend/src/api/fees.types.ts`

### Wave 2
- Task: `tasks/postdemo/PD-FEE-SCENARIO-GRANT-ANNUITY-DEADLINE-PREVIEW-20260705-01.md`
- Owner: main thread
- Dependency: Wave 1 evidence complete
- Serialized files: grant fee, annuity, and related frontend list/type files

### Wave 3
- Task: `tasks/postdemo/PD-FEE-SCENARIO-FOLLOWUP-TRIGGER-FINAL-REGRESSION-20260705-01.md`
- Owner: main thread
- Dependency: Wave 1 and Wave 2 PASS
- Closure: evidence ledger and final regression only

## Batch Done Definition
- Both implementation tasks are PASS with required evidence and task gates.
- Final regression ledger maps design items to task evidence.
- The final summary explicitly states that PCT/Hague/IC_LAYOUT automatic triggers remain disabled/non-implemented.
