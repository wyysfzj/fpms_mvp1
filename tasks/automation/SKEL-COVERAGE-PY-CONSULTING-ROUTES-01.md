# SKEL-COVERAGE-PY-CONSULTING-ROUTES-01

## Story Shape Classification

- shared_file_density: low
- prereq_dependency_density: low
- be_fe_coupling: low
- evidence_cost: medium
- chosen_runbook: P0-single-lane-story

## Exact Closure Slice

Add one pytest Skeleton Pack backend route smoke for the consulting case/fee-draft route pair:

- `POST /consulting/cases`
- `POST /consulting/fee-drafts`

The smoke must create or reuse deterministic consulting case context through real APIs, generate one fixed-fee consulting draft, and assert the draft totals and line count.

## Explicit Non-Closure

This task does not implement H-wave canonical handlers, does not test hourly/hybrid modes, does not test frontend UI, does not change backend consulting behavior, and does not cover consulting profitability.

## Allowed Files

- `FPMS_Automation_Skeleton_Pack/pytest_python/tests/test_current_consulting_routes.py`
- `tasks/automation/SKEL-COVERAGE-PY-CONSULTING-ROUTES-01.md`
- `artifacts/SKEL-COVERAGE-PY-CONSULTING-ROUTES-01/**`

## Verification

- `cd FPMS_Automation_Skeleton_Pack/pytest_python && python3 -m ruff check tests/test_current_consulting_routes.py`
- `cd FPMS_Automation_Skeleton_Pack/pytest_python && pytest tests/test_current_consulting_routes.py -q`
- `python3 FPMS_Automation_Skeleton_Pack/scripts/audit_current_coverage.py`
- `./scripts/task_validate.sh SKEL-COVERAGE-PY-CONSULTING-ROUTES-01`

## Remaining Follow-up Task IDs

- Additional H-wave canonical real-handler coverage tasks.
- Additional per-endpoint route coverage tasks for the remaining backend audit gaps.

## Done Definition

- The route smoke references and exercises consulting case and fee-draft routes.
- Targeted lint and pytest route smoke pass.
- Coverage audit no longer lists those consulting routes as rough backend uncovered routes.
- Required evidence and task gate pass.
