# BE-A-APPLY-FEE-DRAFT-RULE-01

## Story Shape Classification

- shared_file_density: high
- prereq_dependency_density: high
- be_fe_coupling: medium
- evidence_cost: medium
- chosen_runbook: P0-prereq-heavy-story

## Task

- Task ID: BE-A-APPLY-FEE-DRAFT-RULE-01
- Role: worker
- Runbook: P0-prereq-heavy-story

## Exact Closure Slice

Implement the minimal backend rule/API path needed to generate one APPLY_FEE draft and FeeItems for `TC-A-015`, based on `PRODUCT-A-APPLY-FEE-DRAFT-CONTRACT-01`.

This task closes only:

1. Generate an OPEN APPLY_FEE draft for a legal domestic invention case.
2. Use existing FeeDraft, FeeItem, and FeeRate models.
3. Calculate base official fee, excess claim fee, official fee reduction, service fee discount, and totals.
4. Return stable response fields for automation.
5. Preserve generic fee CRUD behavior.

## Explicit Non-Closure

This task does not:

- implement pay list, bill, payment, or commission behavior
- implement pytest automation handlers
- modify frontend or skeleton data
- add schema migrations

## Remaining Follow-Up Task IDs

- BE-A-GOV-PAYLIST-PAYMENT-READINESS-01
- BE-A-APPLY-BILL-READINESS-01

## Allowed Files

- tasks/backend/business_logic/BE-A-APPLY-FEE-DRAFT-RULE-01.md
- backend/app/modules/fees/service.py
- backend/app/modules/fees/api.py
- backend/app/modules/fees/schemas.py
- backend/tests/test_apply_fee_draft_rule.py
- artifacts/BE-A-APPLY-FEE-DRAFT-RULE-01/**

## Verification Commands

Run from `backend/`:

```bash
python3 -m ruff check --fix app/modules/fees/service.py app/modules/fees/api.py app/modules/fees/schemas.py tests/test_apply_fee_draft_rule.py
python3 -m ruff format app/modules/fees/service.py app/modules/fees/api.py app/modules/fees/schemas.py tests/test_apply_fee_draft_rule.py
python3 -m ruff check app/modules/fees/service.py app/modules/fees/api.py app/modules/fees/schemas.py tests/test_apply_fee_draft_rule.py
pytest tests/test_apply_fee_draft_rule.py -q
```

Task gate:

```bash
./scripts/task_validate.sh BE-A-APPLY-FEE-DRAFT-RULE-01
```

## Evidence Path

- artifacts/BE-A-APPLY-FEE-DRAFT-RULE-01/results.jsonl
- artifacts/BE-A-APPLY-FEE-DRAFT-RULE-01/summary.md
- artifacts/BE-A-APPLY-FEE-DRAFT-RULE-01/git/diff.patch
