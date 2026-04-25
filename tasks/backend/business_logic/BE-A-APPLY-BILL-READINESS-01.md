# BE-A-APPLY-BILL-READINESS-01

## Story Shape Classification

- shared_file_density: high
- prereq_dependency_density: high
- be_fe_coupling: medium
- evidence_cost: medium
- chosen_runbook: P0-prereq-heavy-story

## Task

- Task ID: BE-A-APPLY-BILL-READINESS-01
- Role: worker
- Runbook: P0-prereq-heavy-story

## Exact Closure Slice

Verify or minimally fix bill generation from APPLY_FEE drafts required by `TC-A-019`.

This task closes only:

1. Generate one AR bill from one APPLY_FEE draft under one client.
2. BillItem rows bind to the source FeeDraft and FeeItem rows.
3. TotalGov / TotalService / TotalMisc / Amount / Balance are stable.
4. Bill status is `UNSETTLED`.
5. Existing bill-from-drafts behavior is preserved.

## Explicit Non-Closure

This task does not:

- implement payment offset
- implement commission
- implement pytest automation handlers
- implement cross-client or mixed-currency unhappy cases
- modify frontend or skeleton data

## Remaining Follow-Up Task IDs

- BE-A-PAYMENT-OFFSET-CASE-RECEIPT-READINESS-01
- BE-A-COMMISSION-RULE-SEED-READINESS-01

## Allowed Files

- tasks/backend/business_logic/BE-A-APPLY-BILL-READINESS-01.md
- backend/app/modules/billing/service.py
- backend/app/modules/billing/api.py
- backend/app/modules/billing/schemas.py
- backend/tests/test_apply_bill_readiness.py
- artifacts/BE-A-APPLY-BILL-READINESS-01/**

## Verification Commands

Run from `backend/`:

```bash
python3 -m ruff check --fix app/modules/billing/service.py app/modules/billing/api.py app/modules/billing/schemas.py tests/test_apply_bill_readiness.py
python3 -m ruff format app/modules/billing/service.py app/modules/billing/api.py app/modules/billing/schemas.py tests/test_apply_bill_readiness.py
python3 -m ruff check app/modules/billing/service.py app/modules/billing/api.py app/modules/billing/schemas.py tests/test_apply_bill_readiness.py
pytest tests/test_apply_bill_readiness.py -q
```

Task gate:

```bash
./scripts/task_validate.sh BE-A-APPLY-BILL-READINESS-01
```

## Evidence Path

- artifacts/BE-A-APPLY-BILL-READINESS-01/results.jsonl
- artifacts/BE-A-APPLY-BILL-READINESS-01/summary.md
- artifacts/BE-A-APPLY-BILL-READINESS-01/git/diff.patch
