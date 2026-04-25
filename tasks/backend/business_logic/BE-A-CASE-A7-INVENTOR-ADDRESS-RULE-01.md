# BE-A-CASE-A7-INVENTOR-ADDRESS-RULE-01

Task ID: `BE-A-CASE-A7-INVENTOR-ADDRESS-RULE-01`

Role: worker

Story Shape Classification:
- shared_file_density: medium
- prereq_dependency_density: high
- be_fe_coupling: medium
- evidence_cost: medium

chosen_runbook: `P0-prereq-heavy-story`

## Exact Closure Slice

Verify the backend supports the `TC-A-007` MVP inventor/address assertion surface frozen by `PRODUCT-A-CASE-A7-INVENTOR-ADDRESS-CONTRACT-01`.

## Explicit Non-Closure

Do not invent strict-country inventor rules, disabled-address semantics, empty-address warning framework, pytest automation, frontend, skeleton data, migrations, or Playwright changes.

## Remaining Follow-Up Task IDs

- `A-AUTO-PY-A-FOREIGN-COMBO-P1-01`
- `PRODUCT-A-STRICT-INVENTOR-COUNTRY-CONTRACT-01`
- `PRODUCT-A-CLIENT-ADDRESS-ACTIVE-CONTRACT-01`

## Allowed Files

- `tasks/backend/business_logic/BE-A-CASE-A7-INVENTOR-ADDRESS-RULE-01.md`
- `backend/tests/test_case_a7_inventor_address_rule.py`
- `artifacts/BE-A-CASE-A7-INVENTOR-ADDRESS-RULE-01/**`

## Verification Commands

Run from `backend/`:

```bash
python3 -m ruff check --fix tests/test_case_a7_inventor_address_rule.py
python3 -m ruff format tests/test_case_a7_inventor_address_rule.py
python3 -m ruff check tests/test_case_a7_inventor_address_rule.py
pytest tests/test_case_a7_inventor_address_rule.py -q
```

## Evidence Path

- `artifacts/BE-A-CASE-A7-INVENTOR-ADDRESS-RULE-01/results.jsonl`
- `artifacts/BE-A-CASE-A7-INVENTOR-ADDRESS-RULE-01/summary.md`
- `artifacts/BE-A-CASE-A7-INVENTOR-ADDRESS-RULE-01/git/diff.patch`
