# GF-BATCH-INSTRUCTION-01 Plan

## Story Shape Classification

- `shared_file_density`: `high`
- `prereq_dependency_density`: `medium`
- `be_fe_coupling`: `shared FE/BE batch instruction path`
- `evidence_cost`: `medium`

## chosen_runbook

- `P0-frontend-heavy-story`

## Batch Manifest

| Task ID | Owner | Allowlist | Dependency Notes | Exact Closure Slice | Explicit Non-closure |
|---|---|---|---|---|---|
| `GF-BATCH-INSTR-BE-01` | main thread | `backend/app/modules/grant_fees/api.py`, `backend/app/modules/grant_fees/service.py`, `backend/app/modules/grant_fees/schemas.py`, `backend/tests/test_grant_fee_state_machine_api.py` | Depends on existing grant-fee state machine semantics; must not stretch beyond batch PAY / ABANDON | Add batch instruction endpoint, schema, service mutation, and targeted tests for batch PAY / ABANDON | No notice generation, no batch draft generation, no bill/document linkage |
| `GF-BATCH-INSTR-FE-01` | main thread | `frontend/src/api/grantFees.ts`, `frontend/src/api/grantFees.types.ts`, `frontend/src/modules/grantFees/pages/GrantFeeTaskList.vue` | Runs after backend contract is fixed | Add selection UI and batch PAY / ABANDON action path on grant-fee page | No document generation, no detail/edit, no bill generation |
| `GF-BATCH-INSTR-QA-01` | main thread | `artifacts/GF-BATCH-INSTR-BE-01/**`, `artifacts/GF-BATCH-INSTR-FE-01/**`, `artifacts/GF-BATCH-INSTR-QA-01/**`, `tasks/postenhancement/backend/GF-BATCH-INSTR-QA-01.md` | Runs after BE and FE closures | Audit evidence, gates, and exact closure for batch instruction slice | No product-code changes |

## Serialized Shared-file Decisions

- Backend files must be owned first:
  - `backend/app/modules/grant_fees/api.py`
  - `backend/app/modules/grant_fees/service.py`
  - `backend/app/modules/grant_fees/schemas.py`
  - `backend/tests/test_grant_fee_state_machine_api.py`
- Frontend files attach only after backend contract is frozen:
  - `frontend/src/api/grantFees.ts`
  - `frontend/src/api/grantFees.types.ts`
  - `frontend/src/modules/grantFees/pages/GrantFeeTaskList.vue`

## Verification

- `python3 -m ruff format backend/app/modules/grant_fees/api.py backend/app/modules/grant_fees/service.py backend/app/modules/grant_fees/schemas.py backend/tests/test_grant_fee_state_machine_api.py`
- `python3 -m ruff check backend/app/modules/grant_fees/api.py backend/app/modules/grant_fees/service.py backend/app/modules/grant_fees/schemas.py backend/tests/test_grant_fee_state_machine_api.py`
- `cd backend && pytest -q tests/test_grant_fee_state_machine_api.py`
- `cd frontend && npm run lint -- src/api/grantFees.ts src/api/grantFees.types.ts src/modules/grantFees/pages/GrantFeeTaskList.vue`
- `cd frontend && npm run typecheck`
- `./scripts/task_validate.sh GF-BATCH-INSTR-BE-01`
- `./scripts/task_validate.sh GF-BATCH-INSTR-FE-01`
- `./scripts/task_validate.sh GF-BATCH-INSTR-QA-01`

## Done Definition

- Batch PAY / ABANDON API exists and is permission-protected
- Grant-fee page supports multi-selection and real batch action
- Success and invalid-state paths are tested
- Required artifacts exist and all task gates pass
