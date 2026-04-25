# A-AUTO-PY-A-MINIMAL-REQUIRED-P1-01

Task ID: `A-AUTO-PY-A-MINIMAL-REQUIRED-P1-01`

Role: worker

Story Shape Classification:
- shared_file_density: high
- prereq_dependency_density: high
- be_fe_coupling: medium
- evidence_cost: medium

chosen_runbook: `P0-prereq-heavy-story`

## Exact Closure Slice

Implement only `TC-A-002` / `handle_tc_a_002` for Batch 4 MVP full-field case creation.

## Explicit Non-Closure

Do not implement `TC-A-007`, `TC-A-009`, backend/frontend changes, skeleton YAML/JSON/manifest/schema, Playwright, case-level `prio_date`, or `GeneralPowerUsed`.

## Remaining Follow-Up Task IDs

- `PRODUCT-A-GENERAL-POWER-CONTRACT-01`

## Allowed Files

- `tasks/automation/A-AUTO-PY-A-MINIMAL-REQUIRED-P1-01.md`
- `FPMS_Automation_Skeleton_Pack/pytest_python/handlers/wave_a.py`
- `FPMS_Automation_Skeleton_Pack/pytest_python/tests/test_a_minimal_required_handler.py`
- `FPMS_Automation_Skeleton_Pack/pytest_python/tests/test_a_case_create_handler.py`
- `FPMS_Automation_Skeleton_Pack/pytest_python/tests/test_a_case_duplicate_handler.py`
- `FPMS_Automation_Skeleton_Pack/pytest_python/tests/test_a_case_invalid_combo_handler.py`
- `artifacts/A-AUTO-PY-A-MINIMAL-REQUIRED-P1-01/**`

## Verification Commands

Run from `FPMS_Automation_Skeleton_Pack/pytest_python`:

```bash
python3 -m ruff check --fix handlers/wave_a.py tests/test_a_minimal_required_handler.py tests/test_a_case_create_handler.py tests/test_a_case_duplicate_handler.py tests/test_a_case_invalid_combo_handler.py
python3 -m ruff format handlers/wave_a.py tests/test_a_minimal_required_handler.py tests/test_a_case_create_handler.py tests/test_a_case_duplicate_handler.py tests/test_a_case_invalid_combo_handler.py
python3 -m ruff check handlers/wave_a.py tests/test_a_minimal_required_handler.py tests/test_a_case_create_handler.py tests/test_a_case_duplicate_handler.py tests/test_a_case_invalid_combo_handler.py
pytest tests/test_a_minimal_required_handler.py -q
pytest tests/test_wave_a.py -k TC-A-002 -q
```

## Evidence Path

- `artifacts/A-AUTO-PY-A-MINIMAL-REQUIRED-P1-01/results.jsonl`
- `artifacts/A-AUTO-PY-A-MINIMAL-REQUIRED-P1-01/summary.md`
- `artifacts/A-AUTO-PY-A-MINIMAL-REQUIRED-P1-01/git/diff.patch`
