# BE-A-PAYMENT-OFFSET-UNHAPPY-01

## Story Shape Classification

- shared_file_density: high
- prereq_dependency_density: high
- be_fe_coupling: medium
- evidence_cost: medium
- chosen_runbook: P0-prereq-heavy-story

## Exact Closure Slice

Add stable payment unhappy validation needed by TC-A-022:

1. Reject duplicate `client_id + pay_no`.
2. Reject payment dates in the future.
3. Preserve existing offset validation and case receipt behavior.

## Explicit Non-Closure

Do not implement pytest automation handlers, commission logic, frontend changes, skeleton data changes, migrations, or broader billing refactors.

## Remaining Follow-Up Task IDs

- A-AUTO-PY-A-PAYMENT-OFFSET-VALIDATION-P1-01

## Allowed Files

- tasks/backend/business_logic/BE-A-PAYMENT-OFFSET-UNHAPPY-01.md
- backend/app/modules/billing/service.py
- backend/app/modules/billing/api.py
- backend/app/modules/billing/schemas.py
- backend/tests/test_payment_offset_unhappy.py
- artifacts/BE-A-PAYMENT-OFFSET-UNHAPPY-01/**

## Verification Commands

```bash
cd backend
python3 -m ruff check --fix app/modules/billing/service.py app/modules/billing/api.py app/modules/billing/schemas.py tests/test_payment_offset_unhappy.py
python3 -m ruff format app/modules/billing/service.py app/modules/billing/api.py app/modules/billing/schemas.py tests/test_payment_offset_unhappy.py
python3 -m ruff check app/modules/billing/service.py app/modules/billing/api.py app/modules/billing/schemas.py tests/test_payment_offset_unhappy.py
pytest tests/test_payment_offset_unhappy.py -q
pytest tests/test_payment_offset_case_receipt_readiness.py -q
```

## Evidence Path

- artifacts/BE-A-PAYMENT-OFFSET-UNHAPPY-01/results.jsonl
- artifacts/BE-A-PAYMENT-OFFSET-UNHAPPY-01/summary.md
- artifacts/BE-A-PAYMENT-OFFSET-UNHAPPY-01/git/diff.patch
