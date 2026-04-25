# BE-A-GOV-PAYLIST-VALIDATION-MVP-01

## Story Shape Classification

- shared_file_density: medium
- prereq_dependency_density: high
- be_fe_coupling: medium
- evidence_cost: medium
- chosen_runbook: P0-prereq-heavy-story

## Exact Closure Slice

Allow TC-A-018 narrowed MVP official-payment validation to reach service-layer business semantics through the public API.

This task closes only:

1. `POST /api/v1/gov-payments` with `paid_amount <= 0` returns stable business error `GOV_PAYMENT_INVALID`.
2. Existing successful government payment registration remains unchanged.

## Explicit Non-Closure

Do not implement stale planned-pay-date warnings, paid official-payment edit/audit, frontend UI, pytest automation handlers, or skeleton data changes.

## Remaining Follow-Up Task IDs

- PRODUCT-A-GOV-PAYLIST-PAID-EDIT-AUDIT-CONTRACT-01
- BE-A-GOV-PAYMENT-PAID-EDIT-AUDIT-01

## Allowed Files

- tasks/backend/business_logic/BE-A-GOV-PAYLIST-VALIDATION-MVP-01.md
- backend/app/modules/annuity/api.py
- backend/tests/test_gov_paylist_validation_mvp.py
- artifacts/BE-A-GOV-PAYLIST-VALIDATION-MVP-01/**

## Verification Commands

Run from `backend/`:

```bash
python3 -m ruff check --fix app/modules/annuity/api.py tests/test_gov_paylist_validation_mvp.py
python3 -m ruff format app/modules/annuity/api.py tests/test_gov_paylist_validation_mvp.py
python3 -m ruff check app/modules/annuity/api.py tests/test_gov_paylist_validation_mvp.py
pytest tests/test_gov_paylist_validation_mvp.py tests/test_apply_gov_paylist_readiness.py -q
```

## Evidence Path

- artifacts/BE-A-GOV-PAYLIST-VALIDATION-MVP-01/results.jsonl
- artifacts/BE-A-GOV-PAYLIST-VALIDATION-MVP-01/summary.md
- artifacts/BE-A-GOV-PAYLIST-VALIDATION-MVP-01/git/diff.patch
