# A-AUTO-PY-A-COMMISSION-WAITPAY-P1-01

## Story Shape Classification

- shared_file_density: high
- prereq_dependency_density: high
- be_fe_coupling: medium
- evidence_cost: medium
- chosen_runbook: P0-prereq-heavy-story

## Exact Closure Slice

Implement TC-A-024 automation for wait-pay receipt threshold and force-settle override.

## Explicit Non-Closure

Do not implement settlement execution, backend/frontend, or skeleton data changes.

## Remaining Follow-Up Task IDs

- None

## Allowed Files

- tasks/automation/A-AUTO-PY-A-COMMISSION-WAITPAY-P1-01.md
- FPMS_Automation_Skeleton_Pack/pytest_python/handlers/wave_a.py
- FPMS_Automation_Skeleton_Pack/pytest_python/tests/test_a_commission_handler.py
- artifacts/A-AUTO-PY-A-COMMISSION-WAITPAY-P1-01/**

## Verification Commands

```bash
cd FPMS_Automation_Skeleton_Pack/pytest_python
python3 -m ruff check --fix handlers/wave_a.py tests/test_a_commission_handler.py
python3 -m ruff format handlers/wave_a.py tests/test_a_commission_handler.py
python3 -m ruff check handlers/wave_a.py tests/test_a_commission_handler.py
pytest tests/test_a_commission_handler.py -q
pytest tests/test_wave_a.py -k TC-A-024 -q
```

## Evidence Path

- artifacts/A-AUTO-PY-A-COMMISSION-WAITPAY-P1-01/results.jsonl
- artifacts/A-AUTO-PY-A-COMMISSION-WAITPAY-P1-01/summary.md
- artifacts/A-AUTO-PY-A-COMMISSION-WAITPAY-P1-01/git/diff.patch
