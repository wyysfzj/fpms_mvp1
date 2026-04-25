# BE-A-APPLY-FEE-ITEM-VALIDATION-01

## Story Shape Classification

- shared_file_density: high
- prereq_dependency_density: high
- be_fe_coupling: medium
- evidence_cost: medium
- chosen_runbook: P0-prereq-heavy-story

## Exact Closure Slice

Implement the confirmed TC-A-016 MVP backend validation for the rate-driven fee item model:

1. Reject blank draft currency.
2. Reject negative fee item quantity or unit price.
3. Reject deletion that would leave a draft with no fee items.
4. Preserve existing rate-driven `FeeRate` error semantics.

## Explicit Non-Closure

Do not add manual fee item API fields for fee code/name or fee type override. Do not implement pay list, bill, payment, commission, frontend, skeleton data, or pytest automation handler changes.

## Remaining Follow-Up Task IDs

- A-AUTO-PY-A-APPLY-FEE-INVALID-P1-01

## Allowed Files

- tasks/backend/business_logic/BE-A-APPLY-FEE-ITEM-VALIDATION-01.md
- backend/app/modules/fees/service.py
- backend/app/modules/fees/api.py
- backend/app/modules/fees/schemas.py
- backend/tests/test_apply_fee_item_validation.py
- artifacts/BE-A-APPLY-FEE-ITEM-VALIDATION-01/**

## Verification Commands

```bash
cd backend
python3 -m ruff check --fix app/modules/fees/service.py app/modules/fees/api.py app/modules/fees/schemas.py tests/test_apply_fee_item_validation.py
python3 -m ruff format app/modules/fees/service.py app/modules/fees/api.py app/modules/fees/schemas.py tests/test_apply_fee_item_validation.py
python3 -m ruff check app/modules/fees/service.py app/modules/fees/api.py app/modules/fees/schemas.py tests/test_apply_fee_item_validation.py
pytest tests/test_apply_fee_item_validation.py -q
pytest tests/test_apply_fee_draft_rule.py -q
```

## Evidence Path

- artifacts/BE-A-APPLY-FEE-ITEM-VALIDATION-01/results.jsonl
- artifacts/BE-A-APPLY-FEE-ITEM-VALIDATION-01/summary.md
- artifacts/BE-A-APPLY-FEE-ITEM-VALIDATION-01/git/diff.patch
