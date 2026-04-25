# BE-A-CASE-A2-FULL-FIELDS-READINESS-01

Task ID: `BE-A-CASE-A2-FULL-FIELDS-READINESS-01`

Role: worker

Story Shape Classification:
- shared_file_density: medium
- prereq_dependency_density: high
- be_fe_coupling: medium
- evidence_cost: medium

chosen_runbook: `P0-prereq-heavy-story`

## Exact Closure Slice

Verify the backend supports the `TC-A-002` MVP full-field assertion surface frozen by `PRODUCT-A-CASE-A2-FULL-FIELDS-CONTRACT-01`.

## Explicit Non-Closure

Do not add case-level `prio_date`, do not implement `GeneralPowerUsed`, do not modify pytest automation, frontend, skeleton data, migrations, or Playwright.

## Remaining Follow-Up Task IDs

- `A-AUTO-PY-A-MINIMAL-REQUIRED-P1-01`
- `PRODUCT-A-GENERAL-POWER-CONTRACT-01`

## Allowed Files

- `tasks/backend/business_logic/BE-A-CASE-A2-FULL-FIELDS-READINESS-01.md`
- `backend/tests/test_case_a2_full_fields_readiness.py`
- `artifacts/BE-A-CASE-A2-FULL-FIELDS-READINESS-01/**`

## Verification Commands

Run from `backend/`:

```bash
python3 -m ruff check --fix tests/test_case_a2_full_fields_readiness.py
python3 -m ruff format tests/test_case_a2_full_fields_readiness.py
python3 -m ruff check tests/test_case_a2_full_fields_readiness.py
pytest tests/test_case_a2_full_fields_readiness.py -q
```

## Evidence Path

- `artifacts/BE-A-CASE-A2-FULL-FIELDS-READINESS-01/results.jsonl`
- `artifacts/BE-A-CASE-A2-FULL-FIELDS-READINESS-01/summary.md`
- `artifacts/BE-A-CASE-A2-FULL-FIELDS-READINESS-01/git/diff.patch`
