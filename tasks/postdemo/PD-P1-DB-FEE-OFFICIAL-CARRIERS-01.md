# PD-P1-DB-FEE-OFFICIAL-CARRIERS-01 — Official fee linkage carriers

## Exact Closure Slice

Add data carriers for P1 official-fee workflow readiness: official fee checklist rows, cponline template compatibility metadata, fee-reduction interpretation note, and pay-list boundary metadata.

## Explicit Non-Closure

No fee calculation overhaul. No automatic payment. No claim that current `PayList`/`GovPayment` exports match the official upload Excel. No frontend changes.

## Remaining Follow-Up Task IDs

- `PD-P1-BE-FEE-LINKAGE-API-01`
- `PD-P1-FE-FEE-LINKAGE-01`

## Allowed Files

- `backend/app/modules/fees/models.py`
- `backend/app/modules/fees/schemas.py`
- `backend/app/modules/annuity/models.py`
- `backend/app/modules/annuity/schemas.py`
- `backend/alembic/versions/pd_p1_db_04_official_fee_carriers.py`
- `backend/tests/test_pd_p1_official_fee_carriers.py`
- `tasks/postdemo/PD-P1-DB-FEE-OFFICIAL-CARRIERS-01.md`
- `artifacts/PD-P1-DB-FEE-OFFICIAL-CARRIERS-01/**`

## Verification Commands

- `ruff check --fix backend/app/modules/fees/models.py backend/app/modules/fees/schemas.py backend/app/modules/annuity/models.py backend/app/modules/annuity/schemas.py backend/alembic/versions/pd_p1_db_04_official_fee_carriers.py backend/tests/test_pd_p1_official_fee_carriers.py`
- `ruff format backend/app/modules/fees/models.py backend/app/modules/fees/schemas.py backend/app/modules/annuity/models.py backend/app/modules/annuity/schemas.py backend/alembic/versions/pd_p1_db_04_official_fee_carriers.py backend/tests/test_pd_p1_official_fee_carriers.py`
- `ruff check backend/app/modules/fees/models.py backend/app/modules/fees/schemas.py backend/app/modules/annuity/models.py backend/app/modules/annuity/schemas.py backend/alembic/versions/pd_p1_db_04_official_fee_carriers.py backend/tests/test_pd_p1_official_fee_carriers.py`
- `cd backend && pytest -q tests/test_pd_p1_official_fee_carriers.py`
- `./scripts/task_validate.sh PD-P1-DB-FEE-OFFICIAL-CARRIERS-01`

## Evidence Path

- `artifacts/PD-P1-DB-FEE-OFFICIAL-CARRIERS-01/**`

## Acceptance

- Official fee checklist state is representable without altering payment execution.
- Fields clearly separate internal fee drafts/pay-lists from official Excel-upload compatibility data.
