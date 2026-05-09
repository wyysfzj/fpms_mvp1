# W0-CFG-PY-MASTERDATA-01

## Story Shape Classification

- shared_file_density: high
- prereq_dependency_density: medium
- be_fe_coupling: low
- evidence_cost: medium

## chosen_runbook

P0-prereq-heavy-story

## Exact Closure Slice

Implement only the pytest handler for `TC-W0-CFG-012` in `FPMS_Automation_Skeleton_Pack/pytest_python/handlers/wave_w0.py`.

The handler must create or verify run-scoped master-data records for country, department, client, and applicant via real APIs and assert list/search visibility:

- `DS-CFG-COUNTRY-CN`
- `DS-CFG-DEPT-PATENT`
- `DS-CFG-CLIENT-ACTIVE`
- `DS-CFG-APPLICANT-ENTITY`

## Explicit Non-Closure Statement

This task does not verify inactive master-data exclusion from downstream case/fee/report selectors and does not change backend/frontend master-data behavior.

## Remaining Follow-Up Task IDs

- `tasks/automation/W0-CFG-PY-MASTERDATA-INACTIVE-REFERENCE-01.md`
- `tasks/automation/W0-CFG-QA-CLOSE-01.md`

## Allowed Files

- `tasks/automation/W0-CFG-PY-MASTERDATA-01.md`
- `FPMS_Automation_Skeleton_Pack/pytest_python/handlers/wave_w0.py`
- `FPMS_Automation_Skeleton_Pack/pytest_python/tests/test_w0_masterdata_handler.py`
- `artifacts/W0-CFG-PY-MASTERDATA-01/**`

## Verification Commands

```bash
cd FPMS_Automation_Skeleton_Pack/pytest_python && python3 -m ruff check --fix handlers/wave_w0.py tests/test_w0_masterdata_handler.py
cd FPMS_Automation_Skeleton_Pack/pytest_python && python3 -m ruff format handlers/wave_w0.py tests/test_w0_masterdata_handler.py
cd FPMS_Automation_Skeleton_Pack/pytest_python && python3 -m ruff check handlers/wave_w0.py tests/test_w0_masterdata_handler.py
cd FPMS_Automation_Skeleton_Pack/pytest_python && pytest tests/test_w0_masterdata_handler.py -q
cd FPMS_Automation_Skeleton_Pack/pytest_python && pytest tests/test_wave_w0.py -q -k TC-W0-CFG-012
./scripts/task_validate.sh W0-CFG-PY-MASTERDATA-01
```

## Evidence Path

- `artifacts/W0-CFG-PY-MASTERDATA-01/results.jsonl`
- `artifacts/W0-CFG-PY-MASTERDATA-01/summary.md`
- `artifacts/W0-CFG-PY-MASTERDATA-01/git/diff.patch`
- `artifacts/W0-CFG-PY-MASTERDATA-01/baseline_allowlist.diff`
- `artifacts/W0-CFG-PY-MASTERDATA-01/baseline_external_files.txt`
