# SKEL-COVERAGE-AUDIT-01

## Story Shape Classification

- shared_file_density: medium
- prereq_dependency_density: low
- be_fe_coupling: medium
- evidence_cost: medium
- chosen_runbook: P0-single-lane-story

## Exact Closure Slice

Add a current-implementation coverage audit utility to `FPMS_Automation_Skeleton_Pack` that inspects the real backend routes, frontend routes, canonical testcases, pytest handlers, and Playwright handlers, then exposes explicit coverage/gap counts through asset validation and pytest asset-integrity tests.

## Explicit Non-Closure

This task does not implement missing business-flow handlers, add or change canonical business testcases, change backend/frontend product behavior, or claim all current functionality is fully automated. Gaps discovered by the audit remain explicit follow-up work.

## Allowed Files

- `FPMS_Automation_Skeleton_Pack/scripts/audit_current_coverage.py`
- `FPMS_Automation_Skeleton_Pack/scripts/validate_assets.py`
- `FPMS_Automation_Skeleton_Pack/pytest_python/tests/test_asset_integrity.py`
- `tasks/automation/SKEL-COVERAGE-AUDIT-01.md`
- `artifacts/SKEL-COVERAGE-AUDIT-01/**`

## Verification

- `python3 -m ruff check FPMS_Automation_Skeleton_Pack/scripts/audit_current_coverage.py FPMS_Automation_Skeleton_Pack/scripts/validate_assets.py FPMS_Automation_Skeleton_Pack/pytest_python/tests/test_asset_integrity.py`
- `python3 FPMS_Automation_Skeleton_Pack/scripts/validate_assets.py`
- `cd FPMS_Automation_Skeleton_Pack/pytest_python && pytest tests/test_asset_integrity.py -q`
- `./scripts/task_validate.sh SKEL-COVERAGE-AUDIT-01`

## Remaining Follow-up Task IDs

- `SKEL-COVERAGE-PY-REMAINING-HANDLERS-01`
- `SKEL-COVERAGE-PW-ROUTE-SMOKE-01`
- `SKEL-COVERAGE-BE-ROUTE-GAP-01`

## Done Definition

- The audit script reports current backend/frontend/Skeleton coverage counts.
- Asset validation fails on structural coverage regressions, including canonical cases without any pytest or Playwright handler.
- Pytest asset integrity asserts the audit contract and current minimum real-handler coverage.
- Required evidence and task gate pass.
