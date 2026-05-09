# W0-CFG-PY-BILL-TEMPLATE-PARAM-01

## Story Shape Classification

- shared_file_density: high
- prereq_dependency_density: medium
- be_fe_coupling: low
- evidence_cost: medium

## chosen_runbook

P0-prereq-heavy-story

## Exact Closure Slice

Implement only the pytest handler for `TC-W0-CFG-002` missing-configuration guard in `FPMS_Automation_Skeleton_Pack/pytest_python/handlers/wave_w0.py`.

The handler must verify `GET /system/config-readiness` reports `system_param.bill_template_path` missing, create a minimal manual bill, then assert `GET /bills/{bill_id}/print` returns the business blocker `BILL_TEMPLATE_NOT_CONFIGURED` instead of succeeding silently.

## Explicit Non-Closure Statement

This task does not create a real DOCX template fixture, does not assert successful bill rendering, and does not change backend bill print behavior.

## Remaining Follow-Up Task IDs

- `tasks/automation/W0-CFG-PY-BILL-TEMPLATE-RENDER-FIXTURE-01.md`
- `tasks/automation/W0-CFG-QA-CLOSE-01.md`

## Allowed Files

- `tasks/automation/W0-CFG-PY-BILL-TEMPLATE-PARAM-01.md`
- `FPMS_Automation_Skeleton_Pack/pytest_python/handlers/wave_w0.py`
- `FPMS_Automation_Skeleton_Pack/pytest_python/tests/test_w0_bill_template_param_handler.py`
- `artifacts/W0-CFG-PY-BILL-TEMPLATE-PARAM-01/**`

## Verification Commands

```bash
cd FPMS_Automation_Skeleton_Pack/pytest_python && python3 -m ruff check --fix handlers/wave_w0.py tests/test_w0_bill_template_param_handler.py
cd FPMS_Automation_Skeleton_Pack/pytest_python && python3 -m ruff format handlers/wave_w0.py tests/test_w0_bill_template_param_handler.py
cd FPMS_Automation_Skeleton_Pack/pytest_python && python3 -m ruff check handlers/wave_w0.py tests/test_w0_bill_template_param_handler.py
cd FPMS_Automation_Skeleton_Pack/pytest_python && pytest tests/test_w0_bill_template_param_handler.py -q
cd FPMS_Automation_Skeleton_Pack/pytest_python && pytest tests/test_wave_w0.py -q -k TC-W0-CFG-002
./scripts/task_validate.sh W0-CFG-PY-BILL-TEMPLATE-PARAM-01
```

## Evidence Path

- `artifacts/W0-CFG-PY-BILL-TEMPLATE-PARAM-01/results.jsonl`
- `artifacts/W0-CFG-PY-BILL-TEMPLATE-PARAM-01/summary.md`
- `artifacts/W0-CFG-PY-BILL-TEMPLATE-PARAM-01/git/diff.patch`
- `artifacts/W0-CFG-PY-BILL-TEMPLATE-PARAM-01/baseline_allowlist.diff`
- `artifacts/W0-CFG-PY-BILL-TEMPLATE-PARAM-01/baseline_external_files.txt`
