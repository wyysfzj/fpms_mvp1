# PRODUCT-A-GOV-PAYLIST-UNHAPPY-CONTRACT-01

## Story Shape Classification

- shared_file_density: low
- prereq_dependency_density: high
- be_fe_coupling: medium
- evidence_cost: medium
- chosen_runbook: P0-prereq-heavy-story

## Exact Closure Slice

Freeze the TC-A-018 product/backend contract for official-fee pay-list unhappy validation.

## Explicit Non-Closure

Do not modify backend, frontend, pytest automation, skeleton data, migrations, or Playwright assets.

## Remaining Follow-Up Task IDs

- BE-A-GOV-PAYLIST-UNHAPPY-01
- FE-A-GOV-PAYLIST-UNHAPPY-01
- A-AUTO-PY-A-GOV-PAYLIST-VALIDATION-P1-01

## Allowed Files

- tasks/product/PRODUCT-A-GOV-PAYLIST-UNHAPPY-CONTRACT-01.md
- docs/product/PRODUCT-A-GOV-PAYLIST-UNHAPPY-CONTRACT-01.md
- artifacts/PRODUCT-A-GOV-PAYLIST-UNHAPPY-CONTRACT-01/**

## Verification Commands

```bash
test -f tasks/product/PRODUCT-A-GOV-PAYLIST-UNHAPPY-CONTRACT-01.md
test -f docs/product/PRODUCT-A-GOV-PAYLIST-UNHAPPY-CONTRACT-01.md
rg -n "TC-A-018|planned_pay_date|GovPayment|product_decision_required" docs/product/PRODUCT-A-GOV-PAYLIST-UNHAPPY-CONTRACT-01.md
./scripts/task_validate.sh PRODUCT-A-GOV-PAYLIST-UNHAPPY-CONTRACT-01
```

## Evidence Path

- artifacts/PRODUCT-A-GOV-PAYLIST-UNHAPPY-CONTRACT-01/results.jsonl
- artifacts/PRODUCT-A-GOV-PAYLIST-UNHAPPY-CONTRACT-01/summary.md
- artifacts/PRODUCT-A-GOV-PAYLIST-UNHAPPY-CONTRACT-01/git/diff.patch
