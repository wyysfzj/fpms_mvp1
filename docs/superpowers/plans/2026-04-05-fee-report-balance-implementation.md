# FEERPT-BALANCE-01 Plan

## Story Shape Classification

- `shared_file_density`: `medium`
- `prereq_dependency_density`: `medium`
- `be_fe_coupling`: `shared FE/BE balance-summary implementation after semantics freeze`
- `evidence_cost`: `medium`

## chosen_runbook

- `P0-frontend-heavy-story`

## Batch Manifest

| Task ID | Owner | Allowlist | Dependency Notes | Exact Closure Slice | Explicit Non-closure |
|---|---|---|---|---|---|
| `FEERPT-BALANCE-BE-01` | main thread | `backend/app/modules/fees/service.py`, `backend/app/modules/fees/schemas.py`, `backend/tests/test_fee_report.py`, `docs/superpowers/specs/2026-04-05-fee-report-balance-implementation-design.md`, `docs/superpowers/plans/2026-04-05-fee-report-balance-implementation.md`, `tasks/postenhancement/backend/FEERPT-BALANCE-BE-01.md` | Depends on `FEERPT-BALANCE-SPEC-01`; owns fee summary backend contract and test coverage | Add `billed_amount`, `received_amount`, `unpaid_balance_amount`, `partially_received_bill_count` to fee report summary with correct bill-lineage semantics | No FE rendering, no trend/export, no hand-made bill lineage support |
| `FEERPT-BALANCE-FE-01` | main thread | `frontend/src/api/fees.ts`, `frontend/src/api/fees.types.ts`, `frontend/src/modules/fees/pages/FeeDraftList.vue`, `docs/superpowers/specs/2026-04-05-fee-report-balance-implementation-design.md`, `docs/superpowers/plans/2026-04-05-fee-report-balance-implementation.md`, `tasks/postenhancement/frontend/FEERPT-BALANCE-FE-01.md` | Runs after backend contract is in place | Render billed / received / unpaid summary block and wire FE contract | No new page, no chart/export, no trend reporting |
| `FEERPT-BALANCE-QA-01` | main thread | `artifacts/FEERPT-BALANCE-BE-01/**`, `artifacts/FEERPT-BALANCE-FE-01/**`, `artifacts/FEERPT-BALANCE-QA-01/**`, `tasks/postenhancement/backend/FEERPT-BALANCE-QA-01.md` | Runs after BE and FE tasks pass | Audit evidence, gates, and exact closure for the balance summary slice | No product-code changes |

## Serialized Shared-file Decisions

- `backend/app/modules/fees/service.py`
- `backend/app/modules/fees/schemas.py`
- `backend/tests/test_fee_report.py`

must be owned only by `FEERPT-BALANCE-BE-01`.

- `frontend/src/api/fees.ts`
- `frontend/src/api/fees.types.ts`
- `frontend/src/modules/fees/pages/FeeDraftList.vue`

must be owned only by `FEERPT-BALANCE-FE-01`.

## Verification

### Backend

- `python3 -m ruff format backend/app/modules/fees/schemas.py backend/app/modules/fees/service.py backend/tests/test_fee_report.py`
- `python3 -m ruff check backend/app/modules/fees/api.py backend/app/modules/fees/service.py backend/app/modules/fees/schemas.py backend/tests/test_fee_report.py`
- `cd backend && pytest -q tests/test_fee_report.py`
- `./scripts/task_validate.sh FEERPT-BALANCE-BE-01`

### Frontend

- `cd frontend && npm run lint -- src/api/fees.ts src/api/fees.types.ts src/modules/fees/pages/FeeDraftList.vue`
- `cd frontend && npm run typecheck`
- `./scripts/task_validate.sh FEERPT-BALANCE-FE-01`

### QA

- `./scripts/task_validate.sh FEERPT-BALANCE-QA-01`

## Done Definition

- Fee report summary exposes the four new balance metrics
- FE renders the new summary block in Simplified Chinese
- Hand-made bill items without `draft_id` lineage are excluded
- Required evidence exists and all three task gates pass
