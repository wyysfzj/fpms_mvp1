# SKEL-COVERAGE-PY-ANNUITY-TASK-ROUTES-01

## Story Shape Classification

- shared_file_density: low
- prereq_dependency_density: medium
- be_fe_coupling: low
- evidence_cost: medium
- chosen_runbook: P0-single-lane-story

## Exact Closure Slice

Add one pytest Skeleton Pack backend route smoke for the annuity task lifecycle route family:

- `POST /annuity/tasks/generate`
- `GET /annuity/tasks`
- `PUT /annuity/tasks/{task_id}/instruction`
- `POST /annuity/tasks/generate-drafts`

The smoke must create or reuse a deterministic GRANTED case through real APIs, generate annuity tasks, list an available task, record a PAY instruction, generate a fee draft, and assert the task projection reflects `draft_generated`.

## Explicit Non-Closure

This task does not test pay-list generation, government payment registration, annuity report exports, terminal-state validation, frontend UI, or backend annuity behavior changes.

## Allowed Files

- `FPMS_Automation_Skeleton_Pack/pytest_python/tests/test_current_annuity_task_routes.py`
- `tasks/automation/SKEL-COVERAGE-PY-ANNUITY-TASK-ROUTES-01.md`
- `artifacts/SKEL-COVERAGE-PY-ANNUITY-TASK-ROUTES-01/**`

## Verification

- `cd FPMS_Automation_Skeleton_Pack/pytest_python && python3 -m ruff check tests/test_current_annuity_task_routes.py`
- `cd FPMS_Automation_Skeleton_Pack/pytest_python && pytest tests/test_current_annuity_task_routes.py -q`
- `python3 FPMS_Automation_Skeleton_Pack/scripts/audit_current_coverage.py`
- `./scripts/task_validate.sh SKEL-COVERAGE-PY-ANNUITY-TASK-ROUTES-01`

## Remaining Follow-up Task IDs

- Additional per-route coverage tasks for remaining commission and grant-fee backend audit gaps.
- Additional canonical real-handler coverage tasks.

## Done Definition

- The route smoke references and exercises all four annuity task lifecycle routes listed above.
- Targeted lint and pytest route smoke pass.
- Coverage audit no longer lists those annuity task routes as rough backend uncovered routes.
- Required evidence and task gate pass.
