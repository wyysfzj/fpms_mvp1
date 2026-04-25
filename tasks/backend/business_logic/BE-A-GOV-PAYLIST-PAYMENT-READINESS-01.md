# BE-A-GOV-PAYLIST-PAYMENT-READINESS-01

## Story Shape Classification

- shared_file_density: high
- prereq_dependency_density: high
- be_fe_coupling: medium
- evidence_cost: medium
- chosen_runbook: P0-prereq-heavy-story

## Task

- Task ID: BE-A-GOV-PAYLIST-PAYMENT-READINESS-01
- Role: worker
- Runbook: P0-prereq-heavy-story

## Exact Closure Slice

Verify the existing pay-list and official-payment flow for APPLY_FEE GOV FeeItems required by `TC-A-017`.

This task closes only:

1. Create pay list from APPLY_FEE GOV FeeItems.
2. Planned pay date is supported.
3. Pay list list/detail path remains stable.
4. Register official payments.
5. PayList status becomes `PAID`.
6. Paid amounts default from planned fee item amount.
7. Paid records are visible through existing query paths.

## Explicit Non-Closure

This task does not:

- implement APPLY_FEE draft generation
- implement bill, payment offset, or commission behavior
- implement pytest automation handlers
- modify frontend or skeleton data

## Remaining Follow-Up Task IDs

- BE-A-APPLY-BILL-READINESS-01

## Allowed Files

- tasks/backend/business_logic/BE-A-GOV-PAYLIST-PAYMENT-READINESS-01.md
- backend/app/modules/annuity/service.py
- backend/app/modules/annuity/api.py
- backend/app/modules/annuity/schemas.py
- backend/tests/test_apply_gov_paylist_readiness.py
- artifacts/BE-A-GOV-PAYLIST-PAYMENT-READINESS-01/**

## Verification Commands

Run from `backend/`:

```bash
python3 -m ruff check --fix app/modules/annuity/service.py app/modules/annuity/api.py app/modules/annuity/schemas.py tests/test_apply_gov_paylist_readiness.py
python3 -m ruff format app/modules/annuity/service.py app/modules/annuity/api.py app/modules/annuity/schemas.py tests/test_apply_gov_paylist_readiness.py
python3 -m ruff check app/modules/annuity/service.py app/modules/annuity/api.py app/modules/annuity/schemas.py tests/test_apply_gov_paylist_readiness.py
pytest tests/test_apply_gov_paylist_readiness.py -q
```

Task gate:

```bash
./scripts/task_validate.sh BE-A-GOV-PAYLIST-PAYMENT-READINESS-01
```

## Evidence Path

- artifacts/BE-A-GOV-PAYLIST-PAYMENT-READINESS-01/results.jsonl
- artifacts/BE-A-GOV-PAYLIST-PAYMENT-READINESS-01/summary.md
- artifacts/BE-A-GOV-PAYLIST-PAYMENT-READINESS-01/git/diff.patch
