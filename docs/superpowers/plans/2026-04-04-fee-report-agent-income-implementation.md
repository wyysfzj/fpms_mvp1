# FEERPT-INCOME-01 Plan

## Story Shape Classification

- `shared_file_density`: `medium`
- `prereq_dependency_density`: `low`
- `be_fe_coupling`: `shared FE/BE residual implementation`
- `evidence_cost`: `medium`

## chosen_runbook

- `P0-frontend-heavy-story`

## Batch Manifest

### Wave 1

- task: `tasks/postenhancement/backend/FEERPT-INCOME-BE-01.md`
- owner: `main thread`
- allowlist:
  - `backend/app/modules/fees/service.py`
  - `backend/app/modules/fees/schemas.py`
  - `backend/tests/test_fee_report.py`
  - `docs/superpowers/specs/2026-04-04-fee-report-agent-income-implementation-design.md`
  - `docs/superpowers/plans/2026-04-04-fee-report-agent-income-implementation.md`
  - `tasks/postenhancement/backend/FEERPT-INCOME-BE-01.md`
- verification:
  - `python3 -m ruff format backend/app/modules/fees/schemas.py backend/app/modules/fees/service.py backend/tests/test_fee_report.py`
  - `python3 -m ruff check backend/app/modules/fees/api.py backend/app/modules/fees/service.py backend/app/modules/fees/schemas.py backend/tests/test_fee_report.py`
  - `cd backend && pytest -q tests/test_fee_report.py`

### Wave 2

- task: `tasks/postenhancement/frontend/FEERPT-INCOME-FE-01.md`
- owner: `main thread`
- allowlist:
  - `frontend/src/api/fees.ts`
  - `frontend/src/api/fees.types.ts`
  - `frontend/src/modules/fees/pages/FeeDraftList.vue`
  - `docs/superpowers/specs/2026-04-04-fee-report-agent-income-implementation-design.md`
  - `docs/superpowers/plans/2026-04-04-fee-report-agent-income-implementation.md`
  - `tasks/postenhancement/frontend/FEERPT-INCOME-FE-01.md`
- verification:
  - `cd frontend && npm run lint -- src/api/fees.ts src/api/fees.types.ts src/modules/fees/pages/FeeDraftList.vue`
  - `cd frontend && npm run typecheck`

### Wave 3

- task: `tasks/postenhancement/backend/FEERPT-INCOME-QA-01.md`
- owner: `main thread`
- allowlist:
  - `docs/superpowers/specs/2026-04-04-fee-report-agent-income-implementation-design.md`
  - `docs/superpowers/plans/2026-04-04-fee-report-agent-income-implementation.md`
  - `tasks/postenhancement/backend/FEERPT-INCOME-QA-01.md`
- verification:
  - `./scripts/task_validate.sh FEERPT-INCOME-BE-01`
  - `./scripts/task_validate.sh FEERPT-INCOME-FE-01`
  - `./scripts/task_validate.sh FEERPT-INCOME-QA-01`
