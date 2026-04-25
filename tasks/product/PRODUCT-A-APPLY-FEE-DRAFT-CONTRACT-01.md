# PRODUCT-A-APPLY-FEE-DRAFT-CONTRACT-01

## Story Shape Classification

- shared_file_density: low
- prereq_dependency_density: high
- be_fe_coupling: medium
- evidence_cost: medium
- chosen_runbook: P0-prereq-heavy-story

## Task

- Task ID: PRODUCT-A-APPLY-FEE-DRAFT-CONTRACT-01
- Role: worker
- Runbook: P0-prereq-heavy-story

## Exact Closure Slice

Freeze the product/backend contract for `TC-A-015` APPLY_FEE draft generation.

This task closes only:

1. Required case fields and fee-rate inputs for domestic invention APPLY_FEE generation.
2. FeeDraft and FeeItem output contract.
3. Calculation rules for base official fee, excess claim fee, fee reduction, service fee, and discount.
4. Stable API shape and error semantics for backend implementation.
5. Idempotency and automation assertion surface.

## Explicit Non-Closure

This task does not:

- modify backend code
- modify pytest automation handlers
- modify frontend UI
- modify skeleton data
- create migrations
- implement fee calculation

## Remaining Follow-Up Task IDs

- BE-A-APPLY-FEE-DRAFT-RULE-01

## Allowed Files

- tasks/product/PRODUCT-A-APPLY-FEE-DRAFT-CONTRACT-01.md
- docs/product/PRODUCT-A-APPLY-FEE-DRAFT-CONTRACT-01.md
- artifacts/PRODUCT-A-APPLY-FEE-DRAFT-CONTRACT-01/**

## Verification Commands

```bash
test -f tasks/product/PRODUCT-A-APPLY-FEE-DRAFT-CONTRACT-01.md
test -f docs/product/PRODUCT-A-APPLY-FEE-DRAFT-CONTRACT-01.md
rg -n "APPLY_FEE|claim|fee reduction|service fee|FeeRate|FeeDraft|FeeItem|idempot" docs/product/PRODUCT-A-APPLY-FEE-DRAFT-CONTRACT-01.md
./scripts/task_validate.sh PRODUCT-A-APPLY-FEE-DRAFT-CONTRACT-01
```

## Evidence Path

- artifacts/PRODUCT-A-APPLY-FEE-DRAFT-CONTRACT-01/results.jsonl
- artifacts/PRODUCT-A-APPLY-FEE-DRAFT-CONTRACT-01/summary.md
- artifacts/PRODUCT-A-APPLY-FEE-DRAFT-CONTRACT-01/git/diff.patch
