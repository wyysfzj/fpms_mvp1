# GF-BILL-VIS-01 Plan

## Story Shape Classification
- shared_file_density: medium
- prereq_dependency_density: medium
- be_fe_coupling: medium
- evidence_cost: medium
- chosen_runbook: P0-frontend-heavy-story

## Batch Manifest
1. `GF-BILL-VIS-BE-01`
   - closure: project bill visibility fields from existing grant-fee draft and bill lineage
   - non-closure: no state-machine or billing write-path changes
2. `GF-BILL-VIS-FE-01`
   - closure: render billed indicator and bill link on grant-fee worklist
   - non-closure: no new action buttons or bill creation path
3. `GF-BILL-VIS-QA-01`
   - closure: validate exact slice and evidence
   - non-closure: no product-code changes

## Verification
- `python3 -m ruff format backend/app/modules/grant_fees/schemas.py backend/app/modules/grant_fees/service.py backend/tests/test_grant_fee_worklist_api.py`
- `python3 -m ruff check backend/app/modules/grant_fees/api.py backend/app/modules/grant_fees/schemas.py backend/app/modules/grant_fees/service.py backend/tests/test_grant_fee_worklist_api.py`
- `cd backend && pytest -q tests/test_grant_fee_worklist_api.py`
- `cd frontend && npm run lint -- src/api/grantFees.ts src/api/grantFees.types.ts src/modules/grantFees/pages/GrantFeeTaskList.vue`
- `cd frontend && npm run typecheck`
- `./scripts/task_validate.sh GF-BILL-VIS-BE-01`
- `./scripts/task_validate.sh GF-BILL-VIS-FE-01`
- `./scripts/task_validate.sh GF-BILL-VIS-QA-01`

