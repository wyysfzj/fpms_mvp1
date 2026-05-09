# SKEL-COVERAGE-PY-COMMISSION-SETTLEMENT-ROUTES-01

## Story Shape Classification

- shared_file_density: low
- prereq_dependency_density: low
- be_fe_coupling: low
- evidence_cost: medium
- chosen_runbook: P0-single-lane-story

## Exact Closure Slice

Add one pytest Skeleton Pack backend route smoke for the commission settlement/report route family:

- `POST /commission/settlements`
- `POST /commission/settlements/{id}/generate-lines`
- `GET /commission/reports/settlement`
- `GET /commission/reports/settlement/export`

The smoke must create a deterministic settlement batch through the real API, call line generation, query the settlement report, and assert the export endpoint returns an Excel-compatible response.

## Explicit Non-Closure

This task does not create commission earning data, does not test commission rule matching, does not assert non-empty settlement lines, does not test frontend UI, and does not change backend commission behavior.

## Allowed Files

- `FPMS_Automation_Skeleton_Pack/pytest_python/tests/test_current_commission_settlement_routes.py`
- `tasks/automation/SKEL-COVERAGE-PY-COMMISSION-SETTLEMENT-ROUTES-01.md`
- `artifacts/SKEL-COVERAGE-PY-COMMISSION-SETTLEMENT-ROUTES-01/**`

## Verification

- `cd FPMS_Automation_Skeleton_Pack/pytest_python && python3 -m ruff check tests/test_current_commission_settlement_routes.py`
- `cd FPMS_Automation_Skeleton_Pack/pytest_python && pytest tests/test_current_commission_settlement_routes.py -q`
- `python3 FPMS_Automation_Skeleton_Pack/scripts/audit_current_coverage.py`
- `./scripts/task_validate.sh SKEL-COVERAGE-PY-COMMISSION-SETTLEMENT-ROUTES-01`

## Remaining Follow-up Task IDs

- Additional grant-fee route coverage tasks.
- Additional canonical real-handler coverage tasks.

## Done Definition

- The route smoke references and exercises all four commission settlement/report routes listed above.
- Targeted lint and pytest route smoke pass.
- Coverage audit no longer lists those commission settlement/report routes as rough backend uncovered routes.
- Required evidence and task gate pass.
