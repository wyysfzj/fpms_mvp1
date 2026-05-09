# SKEL-COVERAGE-PY-GRANT-FEE-ROUTES-01

## Story Shape Classification

- shared_file_density: low
- prereq_dependency_density: low
- be_fe_coupling: low
- evidence_cost: medium
- chosen_runbook: P0-single-lane-story

## Exact Closure Slice

Add one pytest Skeleton Pack backend route smoke for the grant-fee task route family:

- `GET /grant-fee-tasks`
- `POST /grant-fee-tasks`
- `GET /grant-fee-tasks/list`
- `GET /grant-fee-tasks/{task_id}/state`
- `PUT /grant-fee-tasks/{task_id}/state`
- `POST /grant-fee-tasks/batch-instruction`
- `POST /grant-fee-tasks/generate-notices`
- `POST /grant-fee-tasks/{task_id}/generate-draft`

The smoke must call the module contract/list routes through the real API and verify task-dependent routes return the expected not-found error envelope for a deterministic missing task id.

## Explicit Non-Closure

This task does not create real grant-fee tasks, does not test happy-path state transitions, does not render grant-fee notice documents, does not generate a real grant-fee draft, does not test frontend UI, and does not change backend grant-fee behavior.

## Allowed Files

- `FPMS_Automation_Skeleton_Pack/pytest_python/tests/test_current_grant_fee_routes.py`
- `tasks/automation/SKEL-COVERAGE-PY-GRANT-FEE-ROUTES-01.md`
- `artifacts/SKEL-COVERAGE-PY-GRANT-FEE-ROUTES-01/**`

## Verification

- `cd FPMS_Automation_Skeleton_Pack/pytest_python && python3 -m ruff check tests/test_current_grant_fee_routes.py`
- `cd FPMS_Automation_Skeleton_Pack/pytest_python && pytest tests/test_current_grant_fee_routes.py -q`
- `python3 FPMS_Automation_Skeleton_Pack/scripts/audit_current_coverage.py`
- `./scripts/task_validate.sh SKEL-COVERAGE-PY-GRANT-FEE-ROUTES-01`

## Remaining Follow-up Task IDs

- Follow-up happy-path grant-fee route coverage task if/when a public API fixture for creating grant-fee tasks exists.
- Additional canonical real-handler coverage tasks.

## Done Definition

- The route smoke references and exercises all grant-fee task routes listed above.
- Targeted lint and pytest route smoke pass.
- Coverage audit no longer lists grant-fee routes as rough backend uncovered routes.
- Required evidence and task gate pass.
