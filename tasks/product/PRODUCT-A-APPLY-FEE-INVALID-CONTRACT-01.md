# PRODUCT-A-APPLY-FEE-INVALID-CONTRACT-01

## Story Shape Classification

- shared_file_density: low
- prereq_dependency_density: high
- be_fe_coupling: medium
- evidence_cost: medium
- chosen_runbook: P0-prereq-heavy-story

## Exact Closure Slice

Freeze the TC-A-016 product/backend contract for APPLY_FEE draft and item invalid-data validation.

## Explicit Non-Closure

Do not modify backend, frontend, pytest automation, skeleton data, migrations, or Playwright assets.

## Remaining Follow-Up Task IDs

- BE-A-APPLY-FEE-ITEM-VALIDATION-01
- A-AUTO-PY-A-APPLY-FEE-INVALID-P1-01

## Allowed Files

- tasks/product/PRODUCT-A-APPLY-FEE-INVALID-CONTRACT-01.md
- docs/product/PRODUCT-A-APPLY-FEE-INVALID-CONTRACT-01.md
- artifacts/PRODUCT-A-APPLY-FEE-INVALID-CONTRACT-01/**

## Verification Commands

```bash
test -f tasks/product/PRODUCT-A-APPLY-FEE-INVALID-CONTRACT-01.md
test -f docs/product/PRODUCT-A-APPLY-FEE-INVALID-CONTRACT-01.md
rg -n "TC-A-016|FEE_DRAFT|FEE_ITEM|product_decision_required" docs/product/PRODUCT-A-APPLY-FEE-INVALID-CONTRACT-01.md
./scripts/task_validate.sh PRODUCT-A-APPLY-FEE-INVALID-CONTRACT-01
```

## Evidence Path

- artifacts/PRODUCT-A-APPLY-FEE-INVALID-CONTRACT-01/results.jsonl
- artifacts/PRODUCT-A-APPLY-FEE-INVALID-CONTRACT-01/summary.md
- artifacts/PRODUCT-A-APPLY-FEE-INVALID-CONTRACT-01/git/diff.patch
