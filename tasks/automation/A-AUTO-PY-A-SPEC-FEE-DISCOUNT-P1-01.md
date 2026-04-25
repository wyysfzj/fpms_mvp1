# A-AUTO-PY-A-SPEC-FEE-DISCOUNT-P1-01

Task ID: `A-AUTO-PY-A-SPEC-FEE-DISCOUNT-P1-01`

Role: worker

Story Shape Classification:
- shared_file_density: high
- prereq_dependency_density: high
- be_fe_coupling: medium
- evidence_cost: medium

chosen_runbook: `P0-prereq-heavy-story`

## Exact Closure Slice

Implement only `TC-A-009` / `handle_tc_a_009` for Batch 4 MVP spec and discount boundaries.

## Explicit Non-Closure

Do not implement fee-reduction ratio validation, fee-policy warning, TC-A-002, TC-A-007, backend/frontend changes, skeleton data, or Playwright.

## Remaining Follow-Up Task IDs

- `PRODUCT-A-FEE-REDUCTION-RATIO-CONTRACT-01`

## Allowed Files

- `tasks/automation/A-AUTO-PY-A-SPEC-FEE-DISCOUNT-P1-01.md`
- `FPMS_Automation_Skeleton_Pack/pytest_python/handlers/wave_a.py`
- `FPMS_Automation_Skeleton_Pack/pytest_python/tests/test_a_spec_fee_discount_handler.py`
- `artifacts/A-AUTO-PY-A-SPEC-FEE-DISCOUNT-P1-01/**`

## Verification Commands

Run from `FPMS_Automation_Skeleton_Pack/pytest_python`:

```bash
python3 -m ruff check --fix handlers/wave_a.py tests/test_a_spec_fee_discount_handler.py
python3 -m ruff format handlers/wave_a.py tests/test_a_spec_fee_discount_handler.py
python3 -m ruff check handlers/wave_a.py tests/test_a_spec_fee_discount_handler.py
pytest tests/test_a_spec_fee_discount_handler.py -q
pytest tests/test_wave_a.py -k TC-A-009 -q
```

## Evidence Path

- `artifacts/A-AUTO-PY-A-SPEC-FEE-DISCOUNT-P1-01/results.jsonl`
- `artifacts/A-AUTO-PY-A-SPEC-FEE-DISCOUNT-P1-01/summary.md`
- `artifacts/A-AUTO-PY-A-SPEC-FEE-DISCOUNT-P1-01/git/diff.patch`
