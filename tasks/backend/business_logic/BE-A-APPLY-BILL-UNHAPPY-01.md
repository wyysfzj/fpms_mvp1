# BE-A-APPLY-BILL-UNHAPPY-01

## Story Shape Classification

- shared_file_density: high
- prereq_dependency_density: high
- be_fe_coupling: medium
- evidence_cost: medium
- chosen_runbook: P0-prereq-heavy-story

## Exact Closure Slice

Verify and minimally fix TC-A-020 bill invalid combinations:

1. Mixed clients rejected with `BILL_SINGLE_CLIENT_REQUIRED`.
2. Mixed currencies rejected with `BILL_CURRENCY_MISMATCH`.
3. Empty draft / no billable items rejected with stable bill item error.
4. Negative manual AR bill rejected with `BILL_MANUAL_TOTAL_INVALID`.
5. Preserve happy bill readiness behavior.

## Explicit Non-Closure

Do not implement payment offset, commission, frontend, skeleton data, or pytest automation handlers.

## Remaining Follow-Up Task IDs

- A-AUTO-PY-A-BILL-INVALID-COMBOS-P1-01

## Allowed Files

- tasks/backend/business_logic/BE-A-APPLY-BILL-UNHAPPY-01.md
- backend/app/modules/billing/service.py
- backend/app/modules/billing/api.py
- backend/app/modules/billing/schemas.py
- backend/tests/test_apply_bill_unhappy.py
- artifacts/BE-A-APPLY-BILL-UNHAPPY-01/**

## Verification Commands

```bash
cd backend
python3 -m ruff check --fix app/modules/billing/service.py app/modules/billing/api.py app/modules/billing/schemas.py tests/test_apply_bill_unhappy.py
python3 -m ruff format app/modules/billing/service.py app/modules/billing/api.py app/modules/billing/schemas.py tests/test_apply_bill_unhappy.py
python3 -m ruff check app/modules/billing/service.py app/modules/billing/api.py app/modules/billing/schemas.py tests/test_apply_bill_unhappy.py
pytest tests/test_apply_bill_unhappy.py -q
pytest tests/test_apply_bill_readiness.py -q
```

## Evidence Path

- artifacts/BE-A-APPLY-BILL-UNHAPPY-01/results.jsonl
- artifacts/BE-A-APPLY-BILL-UNHAPPY-01/summary.md
- artifacts/BE-A-APPLY-BILL-UNHAPPY-01/git/diff.patch
