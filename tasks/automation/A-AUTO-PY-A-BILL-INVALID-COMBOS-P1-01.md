# A-AUTO-PY-A-BILL-INVALID-COMBOS-P1-01

## Story Shape Classification

- shared_file_density: high
- prereq_dependency_density: high
- be_fe_coupling: medium
- evidence_cost: medium
- chosen_runbook: P0-prereq-heavy-story

## Exact Closure Slice

Implement TC-A-020 automation for mixed clients, mixed currencies, empty draft, and negative manual AR bill validation.

## Explicit Non-Closure

Do not implement payment offset, commission, backend/frontend, or skeleton data changes.

## Remaining Follow-Up Task IDs

- None

## Allowed Files

- tasks/automation/A-AUTO-PY-A-BILL-INVALID-COMBOS-P1-01.md
- FPMS_Automation_Skeleton_Pack/pytest_python/handlers/wave_a.py
- FPMS_Automation_Skeleton_Pack/pytest_python/tests/test_a_apply_bill_handler.py
- artifacts/A-AUTO-PY-A-BILL-INVALID-COMBOS-P1-01/**

## Verification Commands

```bash
cd FPMS_Automation_Skeleton_Pack/pytest_python
python3 -m ruff check --fix handlers/wave_a.py tests/test_a_apply_bill_handler.py
python3 -m ruff format handlers/wave_a.py tests/test_a_apply_bill_handler.py
python3 -m ruff check handlers/wave_a.py tests/test_a_apply_bill_handler.py
pytest tests/test_a_apply_bill_handler.py -q
pytest tests/test_wave_a.py -k TC-A-020 -q
```

## Evidence Path

- artifacts/A-AUTO-PY-A-BILL-INVALID-COMBOS-P1-01/results.jsonl
- artifacts/A-AUTO-PY-A-BILL-INVALID-COMBOS-P1-01/summary.md
- artifacts/A-AUTO-PY-A-BILL-INVALID-COMBOS-P1-01/git/diff.patch
