# BE-B-OA-BILL-PAYMENT-READINESS-01

Task ID: `BE-B-OA-BILL-PAYMENT-READINESS-01`

Story Shape Classification:
- shared_file_density: high
- prereq_dependency_density: high
- be_fe_coupling: medium
- evidence_cost: medium

chosen_runbook: `P0-prereq-heavy-story`

## Exact Closure Slice

Verify or minimally fix OA fee draft to pay-list, official payment, AR bill, customer payment, offset, and CaseReceipt readiness for `TC-B-010` and `TC-B-011`.

This task closes only:

1. OA `GOV` fee items can feed pay-list creation and official payment.
2. OA `SERVICE` and `GOV` items can generate an AR bill from drafts.
3. Customer payment and offset reduce bill balance and update CaseReceipt visibility.
4. Existing A-wave bill/payment behavior remains intact.

## Explicit Non-Closure

Do not implement pytest automation handlers.
Do not implement commission behavior.
Do not modify OA fee item schema.
Do not modify frontend or skeleton data.

## Remaining Follow-Up Task IDs

- `BE-B-OA-COMMISSION-READINESS-01`
- `B-AUTO-PY-B-OA-BILL-PAYMENT-P0-01`

## Allowed Files

- `tasks/backend/business_logic/BE-B-OA-BILL-PAYMENT-READINESS-01.md`
- `backend/app/modules/billing/service.py`
- `backend/app/modules/billing/api.py`
- `backend/app/modules/billing/schemas.py`
- `backend/tests/test_b_oa_bill_payment_readiness.py`
- `artifacts/BE-B-OA-BILL-PAYMENT-READINESS-01/**`

If behavior is already supported, this may be a test/readiness-only task.

## Verification Commands

Run from `backend/`:

```bash
python3 -m ruff check --fix app/modules/billing/service.py app/modules/billing/api.py app/modules/billing/schemas.py tests/test_b_oa_bill_payment_readiness.py
python3 -m ruff format app/modules/billing/service.py app/modules/billing/api.py app/modules/billing/schemas.py tests/test_b_oa_bill_payment_readiness.py
python3 -m ruff check app/modules/billing/service.py app/modules/billing/api.py app/modules/billing/schemas.py tests/test_b_oa_bill_payment_readiness.py
pytest tests/test_b_oa_bill_payment_readiness.py -q
pytest tests/test_apply_bill_readiness.py tests/test_payment_offset_case_receipt_readiness.py -q
```

Task gate:

```bash
./scripts/task_validate.sh BE-B-OA-BILL-PAYMENT-READINESS-01
```

## Evidence Path

- `artifacts/BE-B-OA-BILL-PAYMENT-READINESS-01/results.jsonl`
- `artifacts/BE-B-OA-BILL-PAYMENT-READINESS-01/summary.md`
- `artifacts/BE-B-OA-BILL-PAYMENT-READINESS-01/git/diff.patch`
