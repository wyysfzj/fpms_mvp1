# SKEL-COVERAGE-PY-OFFSET-REVERSE-ROUTE-01

## Story Shape Classification

- shared_file_density: low
- prereq_dependency_density: low
- be_fe_coupling: low
- evidence_cost: medium
- chosen_runbook: P0-single-lane-story

## Exact Closure Slice

Add one pytest Skeleton Pack backend route smoke for:

- `POST /offsets/{offset_id}/reverse`

The smoke may create prerequisite client, bill, payment, and offset records through existing real APIs, then must call the reverse endpoint and assert the reversed offset is visible from the real offsets API.

## Explicit Non-Closure

This task does not test offset creation validation, duplicate reverse errors, bad-debt flows, receipt proportional allocation details, payment reporting, frontend UI, or backend billing behavior changes.

## Allowed Files

- `FPMS_Automation_Skeleton_Pack/pytest_python/tests/test_current_offset_reverse_route.py`
- `tasks/automation/SKEL-COVERAGE-PY-OFFSET-REVERSE-ROUTE-01.md`
- `artifacts/SKEL-COVERAGE-PY-OFFSET-REVERSE-ROUTE-01/**`

## Verification

- `cd FPMS_Automation_Skeleton_Pack/pytest_python && python3 -m ruff check tests/test_current_offset_reverse_route.py`
- `cd FPMS_Automation_Skeleton_Pack/pytest_python && pytest tests/test_current_offset_reverse_route.py -q`
- `python3 FPMS_Automation_Skeleton_Pack/scripts/audit_current_coverage.py`
- `./scripts/task_validate.sh SKEL-COVERAGE-PY-OFFSET-REVERSE-ROUTE-01`

## Remaining Follow-up Task IDs

- Additional per-endpoint route coverage tasks for the remaining backend audit gaps.
- Additional canonical real-handler coverage tasks.

## Done Definition

- The route smoke references and exercises `POST /offsets/{offset_id}/reverse`.
- Targeted lint and pytest route smoke pass.
- Coverage audit no longer lists `POST /offsets/{offset_id}/reverse` as a rough backend uncovered route.
- Required evidence and task gate pass.
