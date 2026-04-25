# PRODUCT-A-CASE-SPEC-FEE-DISCOUNT-CONTRACT-01

Task ID: `PRODUCT-A-CASE-SPEC-FEE-DISCOUNT-CONTRACT-01`

Role: product / rule contract

Story Shape Classification:
- shared_file_density: low
- prereq_dependency_density: high
- be_fe_coupling: medium
- evidence_cost: medium

chosen_runbook: `P0-prereq-heavy-story`

## Exact Closure Slice

Freeze the MVP assertion surface for `TC-A-009` / spec, fee reduction, and discount boundaries.

## Explicit Non-Closure

No backend, frontend, pytest handler, skeleton data, migration, or Playwright changes.

## Remaining Follow-Up Task IDs

- `BE-A-CASE-SPEC-FEE-DISCOUNT-RULE-01`
- `A-AUTO-PY-A-SPEC-FEE-DISCOUNT-P1-01`
- `PRODUCT-A-FEE-REDUCTION-RATIO-CONTRACT-01`

## Allowed Files

- `tasks/product/PRODUCT-A-CASE-SPEC-FEE-DISCOUNT-CONTRACT-01.md`
- `docs/product/PRODUCT-A-CASE-SPEC-FEE-DISCOUNT-CONTRACT-01.md`
- `artifacts/PRODUCT-A-CASE-SPEC-FEE-DISCOUNT-CONTRACT-01/**`

## Verification Commands

```bash
test -f tasks/product/PRODUCT-A-CASE-SPEC-FEE-DISCOUNT-CONTRACT-01.md
test -f docs/product/PRODUCT-A-CASE-SPEC-FEE-DISCOUNT-CONTRACT-01.md
rg -n "TC-A-009|spec_pages|discount_rate|fee_reduction|product_decision_required|422" docs/product/PRODUCT-A-CASE-SPEC-FEE-DISCOUNT-CONTRACT-01.md
./scripts/task_validate.sh PRODUCT-A-CASE-SPEC-FEE-DISCOUNT-CONTRACT-01
```

## Evidence Path

- `artifacts/PRODUCT-A-CASE-SPEC-FEE-DISCOUNT-CONTRACT-01/results.jsonl`
- `artifacts/PRODUCT-A-CASE-SPEC-FEE-DISCOUNT-CONTRACT-01/summary.md`
- `artifacts/PRODUCT-A-CASE-SPEC-FEE-DISCOUNT-CONTRACT-01/git/diff.patch`
