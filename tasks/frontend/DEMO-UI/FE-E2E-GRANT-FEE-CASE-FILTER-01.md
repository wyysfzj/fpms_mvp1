# FE-E2E-GRANT-FEE-CASE-FILTER-01

## Story Shape Classification

- shared_file_density: medium
- prereq_dependency_density: medium
- be_fe_coupling: high
- evidence_cost: medium
- chosen_runbook: P0-frontend-heavy-story

## Exact Closure Slice

Make `/grant-fee/tasks` visibly searchable by case number and display case number in task rows, so filtering `RUI202605100035` can find the target task after GRANT_NOTICE.

## Explicit Non-Closure

- Do not create grant-fee tasks in frontend code.
- Do not implement annuity, billing, payment, or commission behavior here.
- Do not modify Skeleton Pack assets.

## Allowed Files

- `backend/app/modules/grant_fees/api.py`
- `backend/app/modules/grant_fees/schemas.py`
- `backend/app/modules/grant_fees/service.py`
- `backend/tests/test_grant_fee_worklist_api.py`
- `frontend/src/api/grantFees.ts`
- `frontend/src/api/grantFees.types.ts`
- `frontend/src/modules/grantFees/pages/GrantFeeTaskList.vue`
- `tasks/frontend/DEMO-UI/FE-E2E-GRANT-FEE-CASE-FILTER-01.md`
- `artifacts/FE-E2E-GRANT-FEE-CASE-FILTER-01/**`

## Verification Commands

```bash
./scripts/evidence_run.sh FE-E2E-GRANT-FEE-CASE-FILTER-01 test /bin/zsh -lc 'cd backend && pytest -q tests/test_grant_fee_worklist_api.py && cd ../frontend && npm run typecheck'
```

```bash
./scripts/evidence_run.sh FE-E2E-GRANT-FEE-CASE-FILTER-01 lint /bin/zsh -lc 'cd backend && ruff check --fix app/modules/grant_fees/api.py app/modules/grant_fees/schemas.py app/modules/grant_fees/service.py tests/test_grant_fee_worklist_api.py && ruff format app/modules/grant_fees/api.py app/modules/grant_fees/schemas.py app/modules/grant_fees/service.py tests/test_grant_fee_worklist_api.py && ruff check app/modules/grant_fees/api.py app/modules/grant_fees/schemas.py app/modules/grant_fees/service.py tests/test_grant_fee_worklist_api.py && cd ../frontend && npm run lint -- src/api/grantFees.ts src/api/grantFees.types.ts src/modules/grantFees/pages/GrantFeeTaskList.vue'
```

```bash
./scripts/evidence_run.sh FE-E2E-GRANT-FEE-CASE-FILTER-01 task_gate ./scripts/task_validate.sh FE-E2E-GRANT-FEE-CASE-FILTER-01
```

## Evidence Path

- `artifacts/FE-E2E-GRANT-FEE-CASE-FILTER-01/results.jsonl`
- `artifacts/FE-E2E-GRANT-FEE-CASE-FILTER-01/summary.md`
- `artifacts/FE-E2E-GRANT-FEE-CASE-FILTER-01/git/diff.patch`

## Remaining Follow-Up Task IDs

- None

