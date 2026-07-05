# PD-FEE-SCENARIO-GRANT-ANNUITY-DEADLINE-PREVIEW-20260705-01

Story Shape Classification
- shared_file_density: medium
- prereq_dependency_density: medium
- be_fe_coupling: medium
- evidence_cost: medium
- chosen_runbook: P0-prereq-heavy-story

## Exact Closure Slice
- Extend existing grant fee task and annuity task outputs with Chinese deadline preview fields for demo explanation.
- Expose trigger source, deadline rule, calculation basis, and fee node explanation without changing task state machines or fee amount algorithms.
- Render those explanation fields in the existing grant fee and annuity frontend lists.

## Explicit Non-Closure
- No annual fee due-date recalculation or overwrite.
- No new fee type, automatic payment, CPC/OA direct submit, RPA, signing, or official system integration.
- No PCT/Hague/IC_LAYOUT automatic trigger enablement.
- No schema migration or new persistence model.

## Remaining Follow-Up Task IDs
- `PD-FEE-SCENARIO-FOLLOWUP-TRIGGER-FINAL-REGRESSION-20260705-01`

## Allowed Files
- tasks/postdemo/PD-FEE-SCENARIO-GRANT-ANNUITY-DEADLINE-PREVIEW-20260705-01.md
- backend/app/modules/grant_fees/schemas.py
- backend/app/modules/grant_fees/service.py
- backend/tests/test_grant_fee_notice_task_creation.py
- backend/tests/test_grant_fee_draft_linkage_api.py
- backend/app/modules/annuity/api.py
- backend/app/modules/annuity/schemas.py
- backend/tests/test_annuity_generate.py
- frontend/src/api/grantFees.types.ts
- frontend/src/api/grantFees.ts
- frontend/src/modules/grantFees/pages/GrantFeeTaskList.vue
- frontend/src/api/annuity.types.ts
- frontend/src/api/annuity.ts
- frontend/src/modules/annuity/pages/AnnuityTaskList.vue
- artifacts/PD-FEE-SCENARIO-GRANT-ANNUITY-DEADLINE-PREVIEW-20260705-01/**

## Verification Commands
- `python3 /Users/cfcc/.codex/skills/atomic-evidence-gates/scripts/evidence_gate.py check-task tasks/postdemo/PD-FEE-SCENARIO-GRANT-ANNUITY-DEADLINE-PREVIEW-20260705-01.md`
- `cd backend && PYTHONPATH=. pytest tests/test_grant_fee_notice_task_creation.py tests/test_grant_fee_draft_linkage_api.py tests/test_annuity_generate.py -q`
- `cd backend && python -m ruff check --fix app/modules/grant_fees/schemas.py app/modules/grant_fees/service.py tests/test_grant_fee_notice_task_creation.py tests/test_grant_fee_draft_linkage_api.py app/modules/annuity/api.py app/modules/annuity/schemas.py tests/test_annuity_generate.py`
- `cd backend && python -m ruff format app/modules/grant_fees/schemas.py app/modules/grant_fees/service.py tests/test_grant_fee_notice_task_creation.py tests/test_grant_fee_draft_linkage_api.py app/modules/annuity/api.py app/modules/annuity/schemas.py tests/test_annuity_generate.py`
- `cd backend && python -m ruff check app/modules/grant_fees/schemas.py app/modules/grant_fees/service.py tests/test_grant_fee_notice_task_creation.py tests/test_grant_fee_draft_linkage_api.py app/modules/annuity/api.py app/modules/annuity/schemas.py tests/test_annuity_generate.py`
- `cd frontend && npm run typecheck`
- `cd frontend && npm run build`
- `./scripts/task_validate.sh PD-FEE-SCENARIO-GRANT-ANNUITY-DEADLINE-PREVIEW-20260705-01`

## Evidence Path
- artifacts/PD-FEE-SCENARIO-GRANT-ANNUITY-DEADLINE-PREVIEW-20260705-01/**

## Done Definition
- Grant fee task list/state responses include Chinese `trigger_rule`, `deadline_rule`, `fee_basis`, and `fee_node_explanation`.
- Annuity task list responses include Chinese `trigger_rule`, `deadline_rule`, `fee_basis`, and `fee_node_explanation`.
- Existing due dates and fee amounts are not recalculated by this task.
- Frontend grant fee and annuity lists render the explanation fields with Simplified Chinese labels.
- Required evidence files and task gate exist.
