# W0-CFG-PY-RBAC-CONFIG-ENDPOINTS-01

## Story Shape Classification

- shared_file_density: high
- prereq_dependency_density: medium
- be_fe_coupling: medium
- evidence_cost: medium

## chosen_runbook

P0-prereq-heavy-story

## Exact Closure Slice

Implement only the pytest handler for `TC-W0-CFG-013` API permission coverage in `FPMS_Automation_Skeleton_Pack/pytest_python/handlers/wave_w0.py`.

The handler must verify Admin has the core configuration permissions and verify a non-configuration role is forbidden from representative protected configuration endpoints:

- `/system/config-readiness`
- `/fees/rates`
- `/commission/rules`
- `/task-templates`
- `/doc-templates`
- `/templates`
- `/letterheads`
- `/countries`
- `/departments`

## Explicit Non-Closure Statement

This task does not implement Playwright menu or button visibility checks, does not change backend permissions, and does not test write payload validation for each configuration endpoint.

## Remaining Follow-Up Task IDs

- `tasks/automation/W0-CFG-PW-CONFIG-MENU-MATRIX-01.md`
- `tasks/automation/W0-CFG-QA-CLOSE-01.md`

## Allowed Files

- `tasks/automation/W0-CFG-PY-RBAC-CONFIG-ENDPOINTS-01.md`
- `FPMS_Automation_Skeleton_Pack/pytest_python/handlers/wave_w0.py`
- `FPMS_Automation_Skeleton_Pack/pytest_python/tests/test_w0_permission_handler.py`
- `artifacts/W0-CFG-PY-RBAC-CONFIG-ENDPOINTS-01/**`

## Verification Commands

```bash
cd FPMS_Automation_Skeleton_Pack/pytest_python && python3 -m ruff check --fix handlers/wave_w0.py tests/test_w0_permission_handler.py
cd FPMS_Automation_Skeleton_Pack/pytest_python && python3 -m ruff format handlers/wave_w0.py tests/test_w0_permission_handler.py
cd FPMS_Automation_Skeleton_Pack/pytest_python && python3 -m ruff check handlers/wave_w0.py tests/test_w0_permission_handler.py
cd FPMS_Automation_Skeleton_Pack/pytest_python && pytest tests/test_w0_permission_handler.py -q
cd FPMS_Automation_Skeleton_Pack/pytest_python && pytest tests/test_wave_w0.py -q -k TC-W0-CFG-013
./scripts/task_validate.sh W0-CFG-PY-RBAC-CONFIG-ENDPOINTS-01
```

## Evidence Path

- `artifacts/W0-CFG-PY-RBAC-CONFIG-ENDPOINTS-01/results.jsonl`
- `artifacts/W0-CFG-PY-RBAC-CONFIG-ENDPOINTS-01/summary.md`
- `artifacts/W0-CFG-PY-RBAC-CONFIG-ENDPOINTS-01/git/diff.patch`
- `artifacts/W0-CFG-PY-RBAC-CONFIG-ENDPOINTS-01/baseline_allowlist.diff`
- `artifacts/W0-CFG-PY-RBAC-CONFIG-ENDPOINTS-01/baseline_external_files.txt`
