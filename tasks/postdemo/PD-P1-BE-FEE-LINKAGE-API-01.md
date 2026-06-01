# PD-P1-BE-FEE-LINKAGE-API-01 — Fee linkage and official-template checklist API

## Exact Closure Slice

Add backend API behavior that exposes P1 fee linkage status for filing/OA packages: fee draft references, pay-list boundary, fee-reduction interpretation note, official Excel-template compatibility checklist, and customer-confirmation blockers.

## Explicit Non-Closure

No official payment execution. No automatic amount override. No generated official Excel unless customer-provided template is confirmed in a separate task. No frontend implementation.

## Remaining Follow-Up Task IDs

- `PD-P1-FE-FEE-LINKAGE-01`
- `PD-P1-QA-FULLSCOPE-E2E-01`

## Allowed Files

- `backend/app/modules/official_workflows/api.py`
- `backend/app/modules/official_workflows/schemas.py`
- `backend/app/modules/official_workflows/service.py`
- `backend/app/modules/fees/schemas.py`
- `backend/app/modules/annuity/schemas.py`
- `backend/tests/test_pd_p1_fee_linkage_api.py`
- `tasks/postdemo/PD-P1-BE-FEE-LINKAGE-API-01.md`
- `artifacts/PD-P1-BE-FEE-LINKAGE-API-01/**`

## Verification Commands

- `ruff check --fix backend/app/modules/official_workflows backend/app/modules/fees/schemas.py backend/app/modules/annuity/schemas.py backend/tests/test_pd_p1_fee_linkage_api.py`
- `ruff format backend/app/modules/official_workflows backend/app/modules/fees/schemas.py backend/app/modules/annuity/schemas.py backend/tests/test_pd_p1_fee_linkage_api.py`
- `ruff check backend/app/modules/official_workflows backend/app/modules/fees/schemas.py backend/app/modules/annuity/schemas.py backend/tests/test_pd_p1_fee_linkage_api.py`
- `cd backend && pytest -q tests/test_pd_p1_fee_linkage_api.py`
- `./scripts/task_validate.sh PD-P1-BE-FEE-LINKAGE-API-01`

## Evidence Path

- `artifacts/PD-P1-BE-FEE-LINKAGE-API-01/`

## Acceptance

- API distinguishes internal fee draft, official pay-list, official upload-template readiness, and manual payment status.
- Fee-rate list image evidence remains a blocker until customer provides readable source data.
