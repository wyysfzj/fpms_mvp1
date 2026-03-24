# PE-BE-DB-06 Evidence Summary

## Task
- ID: PE-BE-DB-06
- Runbook: `tasks/postenhancement/backend/PE-BE-DB-06.md`

## Scope Compliance
- Changes restricted to allowlist:
  - `backend/alembic/versions/pe_be_db_06_create_t_commission_rule.py`
  - `backend/app/modules/commission/models.py`

## Migration
- Revision ID: `pe_be_db_06_comm_rule_01`
- Down revision: `pe_be_db_05_dunning_01`
- New table: `t_commission_rule`
- Required support fields covered:
  - CaseType/FeeType: `case_type`, `fee_type`
  - S1/S2: `s1_rate`, `s2_rate`, `s1_fixed_amount`, `s2_fixed_amount`
  - WaitPay/ForceSettle: `wait_pay`, `force_settle`
- SQLite compatibility:
  - integer autoincrement PK
  - `CURRENT_TIMESTAMP` defaults
  - no dialect-specific SQL

## Model
- Added `CommissionRule` model in `backend/app/modules/commission/models.py` aligned to migration fields.

## Verification
- `cd backend && alembic upgrade head` -> PASS
