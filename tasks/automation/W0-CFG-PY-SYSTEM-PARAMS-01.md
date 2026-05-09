# W0-CFG-PY-SYSTEM-PARAMS-01

## Story Shape Classification

- shared_file_density: medium
- prereq_dependency_density: medium
- be_fe_coupling: low
- evidence_cost: medium

## chosen_runbook

P0-prereq-heavy-story

## Exact Closure Slice

Close only the pytest Skeleton Pack handler for `TC-W0-CFG-001`: execute the real `/system/params` API flow for creating run-scoped normal and secret parameters, listing them, and asserting metadata plus secret masking.

## Explicit Non-Closure Statement

This task does not implement `TC-W0-CFG-002` bill printing, fee-rate, commission, template, RBAC, Playwright, frontend, backend endpoint, seed migration, or readiness audit handlers.

## Remaining Follow-Up Task IDs

- `tasks/automation/W0-CFG-PY-FEE-RATES-01.md`
- `tasks/automation/W0-CFG-PY-COMMISSION-01.md`
- `tasks/automation/W0-CFG-PY-TEMPLATES-01.md`
- `tasks/automation/W0-CFG-PY-RBAC-SEED-UI-01.md`
- `tasks/automation/W0-CFG-PW-CONFIG-PAGES-01.md`

## Allowed Files

- `tasks/automation/W0-CFG-PY-SYSTEM-PARAMS-01.md`
- `FPMS_Automation_Skeleton_Pack/pytest_python/handlers/wave_w0.py`
- `FPMS_Automation_Skeleton_Pack/pytest_python/tests/test_w0_system_params_handler.py`
- `artifacts/W0-CFG-PY-SYSTEM-PARAMS-01/**`

## Verification Commands

```bash
cd FPMS_Automation_Skeleton_Pack/pytest_python && pytest tests/test_w0_system_params_handler.py -q
cd FPMS_Automation_Skeleton_Pack/pytest_python && pytest tests/test_wave_w0.py -q -k TC-W0-CFG-001
./scripts/task_validate.sh W0-CFG-PY-SYSTEM-PARAMS-01
```

## Evidence Path

- `artifacts/W0-CFG-PY-SYSTEM-PARAMS-01/results.jsonl`
- `artifacts/W0-CFG-PY-SYSTEM-PARAMS-01/summary.md`
- `artifacts/W0-CFG-PY-SYSTEM-PARAMS-01/git/diff.patch`
