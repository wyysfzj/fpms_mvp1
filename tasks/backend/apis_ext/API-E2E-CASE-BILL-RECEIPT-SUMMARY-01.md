# API-E2E-CASE-BILL-RECEIPT-SUMMARY-01

## Story Shape Classification

- shared_file_density: medium
- prereq_dependency_density: medium
- be_fe_coupling: high
- evidence_cost: medium
- chosen_runbook: P0-prereq-heavy-story

## Exact Closure Slice

`GET /api/v1/cases/{case_id}/receipts` returns a case billing/receipt summary with linked bill rows even when no manual `CaseReceipt` row exists yet.

## Explicit Non-Closure

- Do not create receipts automatically in this endpoint.
- Do not change bill creation semantics.
- Do not change payment/offset behavior in this task.
- Do not modify Skeleton Pack assets.

## Allowed Files

- `backend/app/modules/billing/api.py`
- `backend/app/modules/billing/schemas.py`
- `backend/tests/test_case_receipt_summary_bill_visibility.py`
- `tasks/backend/apis_ext/API-E2E-CASE-BILL-RECEIPT-SUMMARY-01.md`
- `artifacts/API-E2E-CASE-BILL-RECEIPT-SUMMARY-01/**`

## Verification Commands

```bash
./scripts/evidence_run.sh API-E2E-CASE-BILL-RECEIPT-SUMMARY-01 test /bin/zsh -lc 'cd backend && pytest -q tests/test_case_receipt_summary_bill_visibility.py'
```

```bash
./scripts/evidence_run.sh API-E2E-CASE-BILL-RECEIPT-SUMMARY-01 lint /bin/zsh -lc 'cd backend && ruff check --fix app/modules/billing/api.py app/modules/billing/schemas.py tests/test_case_receipt_summary_bill_visibility.py && ruff format app/modules/billing/api.py app/modules/billing/schemas.py tests/test_case_receipt_summary_bill_visibility.py && ruff check app/modules/billing/api.py app/modules/billing/schemas.py tests/test_case_receipt_summary_bill_visibility.py'
```

```bash
./scripts/evidence_run.sh API-E2E-CASE-BILL-RECEIPT-SUMMARY-01 task_gate ./scripts/task_validate.sh API-E2E-CASE-BILL-RECEIPT-SUMMARY-01
```

## Evidence Path

- `artifacts/API-E2E-CASE-BILL-RECEIPT-SUMMARY-01/results.jsonl`
- `artifacts/API-E2E-CASE-BILL-RECEIPT-SUMMARY-01/summary.md`
- `artifacts/API-E2E-CASE-BILL-RECEIPT-SUMMARY-01/git/diff.patch`

## Remaining Follow-Up Task IDs

- `FE-E2E-CASE-BILL-RECEIPT-SUMMARY-01`

