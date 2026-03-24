# PE-BE-DB-05 Evidence Summary

## Task
- ID: PE-BE-DB-05
- Runbook: `tasks/postenhancement/backend/PE-BE-DB-05.md`

## Scope Compliance
- Changes restricted to allowlist:
  - `backend/alembic/versions/pe_be_db_05_create_t_dunning.py`
  - `backend/app/modules/collections/models.py`

## Migration
- Revision ID: `pe_be_db_05_dunning_01`
- Down revision: `pe_be_db_04_annuity_task_01`
- New tables:
  - `t_dunning` (supports multi-round dunning via `round_no`)
  - `t_dunning_line` (bill snapshot lines)
- Snapshot support fields include:
  - `bill_no_snapshot`
  - `due_date_snapshot`
  - `bill_status_snapshot`
  - `outstanding_amount`
  - `currency_snapshot`
- SQLite compatibility:
  - integer autoincrement PKs
  - `CURRENT_TIMESTAMP` defaults
  - no dialect-specific SQL

## Model
- Added `Dunning` and `DunningLine` models in `backend/app/modules/collections/models.py`.
- Included unique constraint mirror for `(dunning_id, line_no)`.

## Verification
- `cd backend && alembic upgrade head` -> PASS
