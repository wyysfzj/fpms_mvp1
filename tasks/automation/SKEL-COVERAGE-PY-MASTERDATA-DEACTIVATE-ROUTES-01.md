# SKEL-COVERAGE-PY-MASTERDATA-DEACTIVATE-ROUTES-01

## Story Shape Classification

- shared_file_density: low
- prereq_dependency_density: low
- be_fe_coupling: none
- evidence_cost: medium
- chosen_runbook: P0-single-lane-story

## Exact Closure Slice

Add one pytest Skeleton Pack backend route smoke for the masterdata deactivate route family:

- `PUT /applicants/{applicant_id}/deactivate`
- `PUT /countries/{country_id}/deactivate`
- `PUT /departments/{department_id}/deactivate`

The smoke must create or reuse dedicated test records through real APIs, call each deactivate endpoint, and assert each record appears in inactive filtered list results.

## Explicit Non-Closure

This task does not test merge behavior, address/contact behavior, frontend UI, validation errors, or other masterdata endpoints.

## Allowed Files

- `FPMS_Automation_Skeleton_Pack/pytest_python/tests/test_current_masterdata_deactivate_routes.py`
- `tasks/automation/SKEL-COVERAGE-PY-MASTERDATA-DEACTIVATE-ROUTES-01.md`
- `artifacts/SKEL-COVERAGE-PY-MASTERDATA-DEACTIVATE-ROUTES-01/**`

## Verification

- `cd FPMS_Automation_Skeleton_Pack/pytest_python && python3 -m ruff check tests/test_current_masterdata_deactivate_routes.py`
- `cd FPMS_Automation_Skeleton_Pack/pytest_python && pytest tests/test_current_masterdata_deactivate_routes.py -q`
- `python3 FPMS_Automation_Skeleton_Pack/scripts/audit_current_coverage.py`
- `./scripts/task_validate.sh SKEL-COVERAGE-PY-MASTERDATA-DEACTIVATE-ROUTES-01`

## Remaining Follow-up Task IDs

- Additional per-endpoint route coverage tasks for the remaining backend audit gaps.

## Done Definition

- The route smoke references and exercises all three masterdata deactivate routes.
- Targeted lint and pytest route smoke pass.
- Coverage audit no longer lists those deactivate routes as rough backend uncovered routes.
- Required evidence and task gate pass.
