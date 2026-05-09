# SKEL-COVERAGE-PY-DOCUMENT-DISPATCH-ROUTE-01

## Story Shape Classification

- shared_file_density: low
- prereq_dependency_density: low
- be_fe_coupling: low
- evidence_cost: medium
- chosen_runbook: P0-single-lane-story

## Exact Closure Slice

Add one pytest Skeleton Pack backend route smoke for the document dispatch create/detail route pair:

- `POST /documents/dispatches`
- `GET /documents/dispatches/{dispatch_id}`

The smoke must create/reuse deterministic case context through real APIs, create one outbound document, create a dispatch sheet for that document, then assert the detail endpoint returns the dispatch line.

## Explicit Non-Closure

This task does not cover mailing batch registration, envelope preview, document attachments, frontend UI, or backend dispatch behavior changes.

## Allowed Files

- `FPMS_Automation_Skeleton_Pack/pytest_python/tests/test_current_document_dispatch_route.py`
- `tasks/automation/SKEL-COVERAGE-PY-DOCUMENT-DISPATCH-ROUTE-01.md`
- `artifacts/SKEL-COVERAGE-PY-DOCUMENT-DISPATCH-ROUTE-01/**`

## Verification

- `cd FPMS_Automation_Skeleton_Pack/pytest_python && python3 -m ruff check tests/test_current_document_dispatch_route.py`
- `cd FPMS_Automation_Skeleton_Pack/pytest_python && pytest tests/test_current_document_dispatch_route.py -q`
- `python3 FPMS_Automation_Skeleton_Pack/scripts/audit_current_coverage.py`
- `./scripts/task_validate.sh SKEL-COVERAGE-PY-DOCUMENT-DISPATCH-ROUTE-01`

## Remaining Follow-up Task IDs

- `SKEL-COVERAGE-PY-DOCUMENT-MAILING-BATCH-ROUTE-01`
- Additional per-endpoint route coverage tasks for the remaining backend audit gaps.

## Done Definition

- The route smoke references and exercises document dispatch create/detail routes.
- Targeted lint and pytest route smoke pass.
- Coverage audit no longer lists document dispatch create/detail routes as rough backend uncovered routes.
- Required evidence and task gate pass.
