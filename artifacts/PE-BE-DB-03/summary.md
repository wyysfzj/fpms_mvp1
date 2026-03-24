# PE-BE-DB-03 Evidence Summary

## Task
- ID: PE-BE-DB-03
- Runbook: `tasks/postenhancement/backend/PE-BE-DB-03.md`

## Scope Compliance
- Changes restricted to allowlist:
  - `backend/alembic/versions/pe_be_db_03_create_t_gov_payment.py`
  - `backend/app/modules/annuity/models.py`

## Migration
- Revision ID: `pe_be_db_03_gov_payment_01`
- Down revision: `pe_be_db_02_pay_list_01`
- New table: `t_gov_payment`
- FK links:
  - `pay_list_id -> t_pay_list.id`
  - `case_id -> t_case.id`
  - `fee_item_id -> t_fee_item.id`
- SQLite compatibility:
  - integer autoincrement PK
  - `CURRENT_TIMESTAMP` defaults
  - no dialect-specific SQL

## Model
- Updated `backend/app/modules/annuity/models.py` with `GovPayment` model matching migration fields and FKs.

## Verification
- `cd backend && alembic upgrade head` -> PASS
