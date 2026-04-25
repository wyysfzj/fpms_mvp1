# BE-A-PAYMENT-OFFSET-CASE-RECEIPT-READINESS-01

## Story Shape Classification

- shared_file_density: high
- prereq_dependency_density: high
- be_fe_coupling: medium
- evidence_cost: medium
- chosen_runbook: P0-prereq-heavy-story

## Task

- Task ID: BE-A-PAYMENT-OFFSET-CASE-RECEIPT-READINESS-01
- Role: worker
- Runbook: P0-prereq-heavy-story

## Exact Closure Slice

Verify or minimally fix payment, offset, bill balance/status, and CaseReceipt behavior required by `TC-A-021`.

This task closes only:

1. Create payment and payment line.
2. Create offset against bill.
3. Bill balance is reduced correctly.
4. Bill status becomes `PARTIALLY_SETTLED` or `SETTLED`.
5. CaseReceipt records receivable / received / arrears semantics.
6. Existing payment and offset query paths can see the result.

## Explicit Non-Closure

This task does not:

- implement over-offset unhappy path
- implement commission
- implement pytest automation handlers
- modify frontend or skeleton data

## Remaining Follow-Up Task IDs

- BE-A-COMMISSION-RULE-SEED-READINESS-01

## Allowed Files

- tasks/backend/business_logic/BE-A-PAYMENT-OFFSET-CASE-RECEIPT-READINESS-01.md
- backend/app/modules/billing/service.py
- backend/app/modules/billing/api.py
- backend/app/modules/billing/schemas.py
- backend/tests/test_payment_offset_case_receipt_readiness.py
- artifacts/BE-A-PAYMENT-OFFSET-CASE-RECEIPT-READINESS-01/**

## Verification Commands

Run from `backend/`:

```bash
python3 -m ruff check --fix app/modules/billing/service.py app/modules/billing/api.py app/modules/billing/schemas.py tests/test_payment_offset_case_receipt_readiness.py
python3 -m ruff format app/modules/billing/service.py app/modules/billing/api.py app/modules/billing/schemas.py tests/test_payment_offset_case_receipt_readiness.py
python3 -m ruff check app/modules/billing/service.py app/modules/billing/api.py app/modules/billing/schemas.py tests/test_payment_offset_case_receipt_readiness.py
pytest tests/test_payment_offset_case_receipt_readiness.py -q
```

Task gate:

```bash
./scripts/task_validate.sh BE-A-PAYMENT-OFFSET-CASE-RECEIPT-READINESS-01
```

## Evidence Path

- artifacts/BE-A-PAYMENT-OFFSET-CASE-RECEIPT-READINESS-01/results.jsonl
- artifacts/BE-A-PAYMENT-OFFSET-CASE-RECEIPT-READINESS-01/summary.md
- artifacts/BE-A-PAYMENT-OFFSET-CASE-RECEIPT-READINESS-01/git/diff.patch
