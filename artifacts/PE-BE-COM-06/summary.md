# PE-BE-COM-06 Evidence Summary

## Task
- ID: `PE-BE-COM-06`
- Runbook: `tasks/postenhancement/backend/PE-BE-COM-06.md`

## Scope Compliance
- Product-code edits are within allowlist:
  - `backend/app/modules/commission/service.py`
  - `backend/app/modules/billing/service.py`

## Implemented
- Added commission settleable recompute service:
  - `recompute_commission_settleable(db, case_ids, as_of_date=None, strict=True)`
- Deterministic settleable decision logic implemented:
  1. `force_settle=True` -> `is_settleable=True`
  2. `force_settle=False and wait_pay=True` -> settleable only when `paid_ratio >= 1.0`
  3. otherwise (`wait_pay=False`) -> settleable by default (`True`)
- Payment progress source:
  - aggregates `t_case_receipt` in service-fee scope (`fee_type='SERVICE'`) per case
  - `paid_ratio = received / receivable`, denominator `<=0` -> `0`, clamped to `[0,1]`
- Deterministic field updates:
  - updates only `is_settleable` and `settleable_date`
  - transition behavior:
    - false -> true: set `settleable_date=as_of_date`
    - true -> true: keep existing `settleable_date`
    - true -> false: clear `settleable_date`
  - does not touch settlement progress flags (`s1_done`, `s2_done`)
  - skips terminal commission statuses (`SETTLED/CANCELLED/VOID/CLOSED`) to avoid regression
- Billing hook integration:
  - wired recompute invocation in `create_offset(...)` and `reverse_offset(...)`
  - affected case set comes from bill items with non-null `case_id` and `fee_type='SERVICE'`
  - hook runs after offset/reverse commit+refresh
  - uses `strict=False` and structured logging, so billing return contracts remain unchanged

## Verification
- Wrapper lint:
  - `./scripts/evidence_run.sh PE-BE-COM-06 lint bash -lc 'cd backend && ruff check app/modules/billing/service.py app/modules/commission/service.py && ruff format --check app/modules/billing/service.py app/modules/commission/service.py'`
  - Result: PASS (`rc=0`)
- Wrapper test:
  - `./scripts/evidence_run.sh PE-BE-COM-06 test bash -lc 'cd backend && pytest -q'`
  - Result: PASS (`141 passed, 3 warnings in 30.71s`)

## Evidence Files
- `artifacts/PE-BE-COM-06/results.jsonl`
- `artifacts/PE-BE-COM-06/summary.md`
- `artifacts/PE-BE-COM-06/git/diff.patch`
