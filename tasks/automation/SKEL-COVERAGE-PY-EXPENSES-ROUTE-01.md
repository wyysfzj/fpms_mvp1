# SKEL-COVERAGE-PY-EXPENSES-ROUTE-01

## Story Shape Classification

- shared_file_density: low
- prereq_dependency_density: low
- be_fe_coupling: low
- evidence_cost: medium
- chosen_runbook: P0-single-lane-story

## Exact Closure Slice

Add one pytest Skeleton Pack backend route smoke for the expense create/list route pair:

- `POST /expenses`
- `GET /expenses`

The smoke must create/reuse deterministic case context through real APIs, create one expense row, then assert the list endpoint returns that row.

## Explicit Non-Closure

This task does not implement expense approval/payment workflows, does not test frontend UI, does not change backend expense behavior, and does not cover any other expense or billing endpoint.

## Allowed Files

- `FPMS_Automation_Skeleton_Pack/pytest_python/tests/test_current_expenses_route.py`
- `tasks/automation/SKEL-COVERAGE-PY-EXPENSES-ROUTE-01.md`
- `artifacts/SKEL-COVERAGE-PY-EXPENSES-ROUTE-01/**`

## Verification

- `cd FPMS_Automation_Skeleton_Pack/pytest_python && python3 -m ruff check tests/test_current_expenses_route.py`
- `cd FPMS_Automation_Skeleton_Pack/pytest_python && pytest tests/test_current_expenses_route.py -q`
- `python3 FPMS_Automation_Skeleton_Pack/scripts/audit_current_coverage.py`
- `./scripts/task_validate.sh SKEL-COVERAGE-PY-EXPENSES-ROUTE-01`

## Remaining Follow-up Task IDs

- Additional per-endpoint route coverage tasks for the remaining backend audit gaps.

## Done Definition

- The route smoke references and exercises `POST /expenses` and `GET /expenses`.
- Targeted lint and pytest route smoke pass.
- Coverage audit no longer lists expense create/list routes as rough backend uncovered routes.
- Required evidence and task gate pass.
