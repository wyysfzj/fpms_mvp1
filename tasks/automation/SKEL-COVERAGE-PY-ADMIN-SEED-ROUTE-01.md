# SKEL-COVERAGE-PY-ADMIN-SEED-ROUTE-01

## Story Shape Classification

- shared_file_density: low
- prereq_dependency_density: low
- be_fe_coupling: none
- evidence_cost: low
- chosen_runbook: P0-single-lane-story

## Exact Closure Slice

Add one pytest Skeleton Pack backend route smoke for exactly one endpoint:

- `POST /admin/seed/roles-permissions`

The smoke must authenticate, call the idempotent role/permission seed route through the real API client, and assert `{"status": "ok"}`.

## Explicit Non-Closure

This task does not alter RBAC seed behavior, does not create or edit users directly, does not test role-permission matrix completeness, and does not cover other admin endpoints.

## Allowed Files

- `FPMS_Automation_Skeleton_Pack/pytest_python/tests/test_current_admin_seed_route.py`
- `tasks/automation/SKEL-COVERAGE-PY-ADMIN-SEED-ROUTE-01.md`
- `artifacts/SKEL-COVERAGE-PY-ADMIN-SEED-ROUTE-01/**`

## Verification

- `cd FPMS_Automation_Skeleton_Pack/pytest_python && python3 -m ruff check tests/test_current_admin_seed_route.py`
- `cd FPMS_Automation_Skeleton_Pack/pytest_python && pytest tests/test_current_admin_seed_route.py -q`
- `python3 FPMS_Automation_Skeleton_Pack/scripts/audit_current_coverage.py`
- `./scripts/task_validate.sh SKEL-COVERAGE-PY-ADMIN-SEED-ROUTE-01`

## Remaining Follow-up Task IDs

- Additional per-endpoint route coverage tasks for the remaining backend audit gaps.

## Done Definition

- The route smoke references and exercises `POST /admin/seed/roles-permissions`.
- Targeted lint and pytest route smoke pass.
- Coverage audit no longer lists `POST /admin/seed/roles-permissions` as a rough backend uncovered route.
- Required evidence and task gate pass.
