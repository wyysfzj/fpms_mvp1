# API-E2E-PAYMENT-OFFSET-LINKAGE-01

## Story Shape Classification

- shared_file_density: high
- prereq_dependency_density: medium
- be_fe_coupling: high
- evidence_cost: medium
- chosen_runbook: P0-prereq-heavy-story

## Exact Closure Slice

Allow a payment created from a selected bill to retain bill/case linkage sufficient for payment list visibility, payment line selection, and offset creation against that bill.

## Explicit Non-Closure

- Do not change database schema.
- Do not change bad-debt or dunning flows.
- Do not change frontend payment UI in this task.
- Do not modify Skeleton Pack assets.

## Allowed Files

- `backend/app/modules/billing/api.py`
- `backend/app/modules/billing/schemas.py`
- `backend/app/modules/billing/service.py`
- `backend/tests/test_payment_bill_linkage_api.py`
- `tasks/backend/apis_ext/API-E2E-PAYMENT-OFFSET-LINKAGE-01.md`
- `artifacts/API-E2E-PAYMENT-OFFSET-LINKAGE-01/**`

## Verification Commands

```bash
./scripts/evidence_run.sh API-E2E-PAYMENT-OFFSET-LINKAGE-01 test /bin/zsh -lc 'cd backend && pytest -q tests/test_payment_bill_linkage_api.py'
```

```bash
./scripts/evidence_run.sh API-E2E-PAYMENT-OFFSET-LINKAGE-01 lint /bin/zsh -lc 'cd backend && ruff check --fix app/modules/billing/api.py app/modules/billing/schemas.py app/modules/billing/service.py tests/test_payment_bill_linkage_api.py && ruff format app/modules/billing/api.py app/modules/billing/schemas.py app/modules/billing/service.py tests/test_payment_bill_linkage_api.py && ruff check app/modules/billing/api.py app/modules/billing/schemas.py app/modules/billing/service.py tests/test_payment_bill_linkage_api.py'
```

```bash
./scripts/evidence_run.sh API-E2E-PAYMENT-OFFSET-LINKAGE-01 task_gate ./scripts/task_validate.sh API-E2E-PAYMENT-OFFSET-LINKAGE-01
```

## Evidence Path

- `artifacts/API-E2E-PAYMENT-OFFSET-LINKAGE-01/results.jsonl`
- `artifacts/API-E2E-PAYMENT-OFFSET-LINKAGE-01/summary.md`
- `artifacts/API-E2E-PAYMENT-OFFSET-LINKAGE-01/git/diff.patch`

## Remaining Follow-Up Task IDs

- `FE-E2E-PAYMENT-OFFSET-VISIBILITY-01`

