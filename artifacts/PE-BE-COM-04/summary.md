# PE-BE-COM-04 Evidence Summary

## Task
- ID: `PE-BE-COM-04`
- Runbook: `tasks/postenhancement/backend/PE-BE-COM-04.md`

## Scope Compliance
- Product-code changes restricted to allowlist only:
  - `backend/app/modules/commission/service.py`

## Implemented
- Added bill-triggered commission service:
  - `apply_commission_for_bill(db, bill_id, actor_id=None, strict=True)`
- Processing scope:
  - reads bill items by `bill_id`
  - processes only items with `case_id` and service-fee context (`fee_type == "SERVICE"`)
  - aggregates service base fee by case
- Rule matching contract implemented:
  - enabled rules only
  - effective window includes reference date (`bill.bill_date` or `date.today()`)
  - dimensions with null wildcard matching: `fee_type`, `case_type`, `flow_dir`, `patent_category`
  - deterministic selection priority:
    - specificity desc (non-null dimension count)
    - `effective_from` latest (null last)
    - `id` desc
- Idempotent upsert behavior:
  - deterministic upsert key: `(case_id, agent_id, fee_type, rule_id)`
  - create when missing, update when existing
  - conflict-safe guard returns `409` when multiple rows match upsert key (`COMMISSION_UPSERT_CONFLICT`)
  - rerun for same bill does not create duplicate commission rows
- Commission field mapping:
  - create/update writes `rule_id/base_fee/s1_rate/s2_rate/s1_amount/s2_amount/wait_pay/force_settle`
  - stage amounts computed deterministically from base/rate/fixed and quantized to cents
  - update does not reset `s1_done/s2_done` and does not regress status (keeps existing status unless empty)
- Strict/non-strict behavior:
  - `strict=True` raises BusinessError semantics (`400/404/409` where applicable)
  - `strict=False` rolls back and returns non-blocking summary with `status=FAILED_NON_BLOCKING` and error payload
  - execution is all-or-none for a bill run (single commit at end; rollback on error)
- Existing API/billing hook wiring remains unchanged.

## Verification
- Wrapper lint:
  - `./scripts/evidence_run.sh PE-BE-COM-04 lint bash -lc 'cd backend && ruff check app/modules/commission/service.py && ruff format --check app/modules/commission/service.py'`
  - Result: PASS (`rc=0`)
- Wrapper test:
  - `./scripts/evidence_run.sh PE-BE-COM-04 test bash -lc 'cd backend && pytest -q'`
  - Result: PASS (`141 passed, 3 warnings in 30.21s`)

## Evidence Files
- `artifacts/PE-BE-COM-04/results.jsonl`
- `artifacts/PE-BE-COM-04/summary.md`
- `artifacts/PE-BE-COM-04/git/diff.patch`
