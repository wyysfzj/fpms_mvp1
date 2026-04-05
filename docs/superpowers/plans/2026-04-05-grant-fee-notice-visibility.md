# GF-NOTICE-VIS-01 Plan

## Story Shape Classification

- `shared_file_density`: `medium`
- `prereq_dependency_density`: `low`
- `be_fe_coupling`: `notice carrier visibility slice`
- `evidence_cost`: `medium`

## chosen_runbook

- `P0-frontend-heavy-story`

## Batch Manifest

1. `GF-NOTICE-VIS-BE-01`
   - closure: project `notify_count` into grant-fee worklist response
   - non-closure: no new linkage or generation behavior
2. `GF-NOTICE-VIS-FE-01`
   - closure: render internal notice status and counter on the existing grant-fee worklist
   - non-closure: no real document/task creation path
3. `GF-NOTICE-VIS-QA-01`
   - closure: validate evidence, scope, and task gates
   - non-closure: no product-code changes

## Verification

- `python3 -m ruff format backend/app/modules/grant_fees/schemas.py backend/app/modules/grant_fees/service.py backend/tests/test_grant_fee_worklist_api.py`
- `python3 -m ruff check backend/app/modules/grant_fees/api.py backend/app/modules/grant_fees/schemas.py backend/app/modules/grant_fees/service.py backend/tests/test_grant_fee_worklist_api.py`
- `cd backend && pytest -q tests/test_grant_fee_worklist_api.py`
- `cd frontend && npm run lint -- src/api/grantFees.ts src/api/grantFees.types.ts src/modules/grantFees/pages/GrantFeeTaskList.vue`
- `cd frontend && npm run typecheck`
- `./scripts/task_validate.sh GF-NOTICE-VIS-BE-01`
- `./scripts/task_validate.sh GF-NOTICE-VIS-FE-01`
- `./scripts/task_validate.sh GF-NOTICE-VIS-QA-01`

