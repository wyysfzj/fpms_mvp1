# A-AUTO-PY-A-FOREIGN-COMBO-P1-01

Task ID: `A-AUTO-PY-A-FOREIGN-COMBO-P1-01`

Role: worker

Story Shape Classification:
- shared_file_density: high
- prereq_dependency_density: high
- be_fe_coupling: medium
- evidence_cost: medium

chosen_runbook: `P0-prereq-heavy-story`

## Exact Closure Slice

Implement only `TC-A-007` / `handle_tc_a_007` for Batch 4 MVP inventor/address behavior.

## Explicit Non-Closure

Do not implement strict-country inventor rule, disabled address semantics, empty-address warning framework, TC-A-002, TC-A-009, backend/frontend changes, skeleton data, or Playwright.

## Remaining Follow-Up Task IDs

- `PRODUCT-A-STRICT-INVENTOR-COUNTRY-CONTRACT-01`
- `PRODUCT-A-CLIENT-ADDRESS-ACTIVE-CONTRACT-01`

## Allowed Files

- `tasks/automation/A-AUTO-PY-A-FOREIGN-COMBO-P1-01.md`
- `FPMS_Automation_Skeleton_Pack/pytest_python/handlers/wave_a.py`
- `FPMS_Automation_Skeleton_Pack/pytest_python/tests/test_a_foreign_combo_handler.py`
- `artifacts/A-AUTO-PY-A-FOREIGN-COMBO-P1-01/**`

## Verification Commands

Run from `FPMS_Automation_Skeleton_Pack/pytest_python`:

```bash
python3 -m ruff check --fix handlers/wave_a.py tests/test_a_foreign_combo_handler.py
python3 -m ruff format handlers/wave_a.py tests/test_a_foreign_combo_handler.py
python3 -m ruff check handlers/wave_a.py tests/test_a_foreign_combo_handler.py
pytest tests/test_a_foreign_combo_handler.py -q
pytest tests/test_wave_a.py -k TC-A-007 -q
```

## Evidence Path

- `artifacts/A-AUTO-PY-A-FOREIGN-COMBO-P1-01/results.jsonl`
- `artifacts/A-AUTO-PY-A-FOREIGN-COMBO-P1-01/summary.md`
- `artifacts/A-AUTO-PY-A-FOREIGN-COMBO-P1-01/git/diff.patch`
