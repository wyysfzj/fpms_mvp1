# SKEL-COVERAGE-PY-FEE-UNIFIED-QUERY-ROUTE-01

## Story Shape Classification

- shared_file_density: low
- prereq_dependency_density: low
- be_fe_coupling: low
- evidence_cost: medium
- chosen_runbook: P0-single-lane-story

## Exact Closure Slice

Add one pytest Skeleton Pack backend route smoke for exactly one endpoint:

- `GET /fee-unified-query`

The smoke must create/reuse deterministic receipt-side fee data through real APIs, then assert the unified fee query returns the created receipt row.

## Explicit Non-Closure

This task does not mark `TC-X-008` as implemented, does not test payment-side rows, does not test frontend UI, does not change backend billing behavior, and does not cover any other billing endpoint.

## Allowed Files

- `FPMS_Automation_Skeleton_Pack/pytest_python/tests/test_current_fee_unified_query_route.py`
- `tasks/automation/SKEL-COVERAGE-PY-FEE-UNIFIED-QUERY-ROUTE-01.md`
- `artifacts/SKEL-COVERAGE-PY-FEE-UNIFIED-QUERY-ROUTE-01/**`

## Verification

- `cd FPMS_Automation_Skeleton_Pack/pytest_python && python3 -m ruff check tests/test_current_fee_unified_query_route.py`
- `cd FPMS_Automation_Skeleton_Pack/pytest_python && pytest tests/test_current_fee_unified_query_route.py -q`
- `python3 FPMS_Automation_Skeleton_Pack/scripts/audit_current_coverage.py`
- `./scripts/task_validate.sh SKEL-COVERAGE-PY-FEE-UNIFIED-QUERY-ROUTE-01`

## Remaining Follow-up Task IDs

- `SKEL-COVERAGE-PY-X-FEE-REPORT-01`
- Additional per-endpoint route coverage tasks for the remaining backend audit gaps.

## Done Definition

- The route smoke references and exercises `GET /fee-unified-query`.
- Targeted lint and pytest route smoke pass.
- Coverage audit no longer lists `GET /fee-unified-query` as a rough backend uncovered route.
- Required evidence and task gate pass.
