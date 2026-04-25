# BE-A-CASE-SPEC-FEE-DISCOUNT-RULE-01

Task ID: `BE-A-CASE-SPEC-FEE-DISCOUNT-RULE-01`

Role: worker

Story Shape Classification:
- shared_file_density: medium
- prereq_dependency_density: high
- be_fe_coupling: medium
- evidence_cost: medium

chosen_runbook: `P0-prereq-heavy-story`

## Exact Closure Slice

Verify the backend supports the `TC-A-009` MVP spec and discount boundary surface frozen by `PRODUCT-A-CASE-SPEC-FEE-DISCOUNT-CONTRACT-01`.

## Explicit Non-Closure

Do not add fee-reduction ratio validation, applicant-kind/fee-policy warning behavior, pytest automation, frontend, skeleton data, migrations, or Playwright changes.

## Remaining Follow-Up Task IDs

- `A-AUTO-PY-A-SPEC-FEE-DISCOUNT-P1-01`
- `PRODUCT-A-FEE-REDUCTION-RATIO-CONTRACT-01`

## Allowed Files

- `tasks/backend/business_logic/BE-A-CASE-SPEC-FEE-DISCOUNT-RULE-01.md`
- `backend/tests/test_case_spec_fee_discount_rule.py`
- `artifacts/BE-A-CASE-SPEC-FEE-DISCOUNT-RULE-01/**`

## Verification Commands

Run from `backend/`:

```bash
python3 -m ruff check --fix tests/test_case_spec_fee_discount_rule.py
python3 -m ruff format tests/test_case_spec_fee_discount_rule.py
python3 -m ruff check tests/test_case_spec_fee_discount_rule.py
pytest tests/test_case_spec_fee_discount_rule.py -q
```

## Evidence Path

- `artifacts/BE-A-CASE-SPEC-FEE-DISCOUNT-RULE-01/results.jsonl`
- `artifacts/BE-A-CASE-SPEC-FEE-DISCOUNT-RULE-01/summary.md`
- `artifacts/BE-A-CASE-SPEC-FEE-DISCOUNT-RULE-01/git/diff.patch`
