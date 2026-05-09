# W0-CFG-PY-FEE-RATES-01

## Story Shape Classification

- shared_file_density: medium
- prereq_dependency_density: medium
- be_fe_coupling: low
- evidence_cost: medium

## chosen_runbook

P0-prereq-heavy-story

## Exact Closure Slice

Close only the pytest Skeleton Pack handler for `TC-W0-CFG-003`: create the three required APPLY fee-rate configurations from supplemental seed data through the real `/fees/rates` API and verify they are searchable by fee code.

## Explicit Non-Closure Statement

This task does not implement application fee draft generation, missing-rate 409 behavior, calc-mode boundary coverage, commission, template, RBAC, frontend, backend endpoint, or Playwright work.

## Remaining Follow-Up Task IDs

- `tasks/automation/W0-CFG-PY-COMMISSION-01.md`
- `tasks/automation/W0-CFG-PY-TEMPLATES-01.md`
- `tasks/automation/W0-CFG-PY-RBAC-SEED-UI-01.md`

## Allowed Files

- `tasks/automation/W0-CFG-PY-FEE-RATES-01.md`
- `FPMS_Automation_Skeleton_Pack/pytest_python/handlers/wave_w0.py`
- `FPMS_Automation_Skeleton_Pack/pytest_python/tests/test_w0_fee_rate_handler.py`
- `artifacts/W0-CFG-PY-FEE-RATES-01/**`

## Verification Commands

```bash
python3 -m ruff check FPMS_Automation_Skeleton_Pack/pytest_python/handlers/wave_w0.py FPMS_Automation_Skeleton_Pack/pytest_python/tests/test_w0_fee_rate_handler.py
cd FPMS_Automation_Skeleton_Pack/pytest_python && pytest tests/test_w0_fee_rate_handler.py -q
cd FPMS_Automation_Skeleton_Pack/pytest_python && pytest tests/test_wave_w0.py -q -k TC-W0-CFG-003
./scripts/task_validate.sh W0-CFG-PY-FEE-RATES-01
```

## Evidence Path

- `artifacts/W0-CFG-PY-FEE-RATES-01/results.jsonl`
- `artifacts/W0-CFG-PY-FEE-RATES-01/summary.md`
- `artifacts/W0-CFG-PY-FEE-RATES-01/git/diff.patch`
