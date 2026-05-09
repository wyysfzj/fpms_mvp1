# W0-CFG-PY-TASK-DEADLINE-TEMPLATE-01

## Story Shape Classification

- shared_file_density: high
- prereq_dependency_density: medium
- be_fe_coupling: low
- evidence_cost: medium

## chosen_runbook

P0-prereq-heavy-story

## Exact Closure Slice

Implement only the pytest handler for `TC-W0-CFG-008` in `FPMS_Automation_Skeleton_Pack/pytest_python/handlers/wave_w0.py`.

The handler must create the run-scoped OA reply task template and the linked OA_IN document template through real APIs, then verify persisted deadline metadata:

- `DS-CFG-TASK-OA-REPLY` via `/task-templates`
- `DS-CFG-DOC-OA-IN` via `/doc-templates`

## Explicit Non-Closure Statement

This task does not create a case or document, does not verify automatic task generation from a real incoming document, and does not change backend task-generation logic.

## Remaining Follow-Up Task IDs

- `tasks/automation/W0-CFG-PY-TASK-GENERATION-FLOW-01.md`
- `tasks/automation/W0-CFG-QA-CLOSE-01.md`

## Allowed Files

- `tasks/automation/W0-CFG-PY-TASK-DEADLINE-TEMPLATE-01.md`
- `FPMS_Automation_Skeleton_Pack/pytest_python/handlers/wave_w0.py`
- `FPMS_Automation_Skeleton_Pack/pytest_python/tests/test_w0_task_deadline_template_handler.py`
- `artifacts/W0-CFG-PY-TASK-DEADLINE-TEMPLATE-01/**`

## Verification Commands

```bash
cd FPMS_Automation_Skeleton_Pack/pytest_python && python3 -m ruff check --fix handlers/wave_w0.py tests/test_w0_task_deadline_template_handler.py
cd FPMS_Automation_Skeleton_Pack/pytest_python && python3 -m ruff format handlers/wave_w0.py tests/test_w0_task_deadline_template_handler.py
cd FPMS_Automation_Skeleton_Pack/pytest_python && python3 -m ruff check handlers/wave_w0.py tests/test_w0_task_deadline_template_handler.py
cd FPMS_Automation_Skeleton_Pack/pytest_python && pytest tests/test_w0_task_deadline_template_handler.py -q
cd FPMS_Automation_Skeleton_Pack/pytest_python && pytest tests/test_wave_w0.py -q -k TC-W0-CFG-008
./scripts/task_validate.sh W0-CFG-PY-TASK-DEADLINE-TEMPLATE-01
```

## Evidence Path

- `artifacts/W0-CFG-PY-TASK-DEADLINE-TEMPLATE-01/results.jsonl`
- `artifacts/W0-CFG-PY-TASK-DEADLINE-TEMPLATE-01/summary.md`
- `artifacts/W0-CFG-PY-TASK-DEADLINE-TEMPLATE-01/git/diff.patch`
- `artifacts/W0-CFG-PY-TASK-DEADLINE-TEMPLATE-01/baseline_allowlist.diff`
- `artifacts/W0-CFG-PY-TASK-DEADLINE-TEMPLATE-01/baseline_external_files.txt`
