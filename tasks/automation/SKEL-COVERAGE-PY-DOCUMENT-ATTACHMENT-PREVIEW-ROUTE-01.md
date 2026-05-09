# SKEL-COVERAGE-PY-DOCUMENT-ATTACHMENT-PREVIEW-ROUTE-01

## Story Shape Classification

- shared_file_density: low
- prereq_dependency_density: low
- be_fe_coupling: low
- evidence_cost: medium
- chosen_runbook: P0-single-lane-story

## Exact Closure Slice

Add one pytest Skeleton Pack backend route smoke for exactly one endpoint:

- `POST /documents/wizard/attachment-preview`

The smoke must create/reuse deterministic case context and enabled document template metadata through real APIs, then assert the attachment preview returns one candidate for the case row.

## Explicit Non-Closure

This task does not cover wizard batch-create, real attachment rendering, template file resolution, frontend UI, or backend document behavior changes.

## Allowed Files

- `FPMS_Automation_Skeleton_Pack/pytest_python/tests/test_current_document_attachment_preview_route.py`
- `tasks/automation/SKEL-COVERAGE-PY-DOCUMENT-ATTACHMENT-PREVIEW-ROUTE-01.md`
- `artifacts/SKEL-COVERAGE-PY-DOCUMENT-ATTACHMENT-PREVIEW-ROUTE-01/**`

## Verification

- `cd FPMS_Automation_Skeleton_Pack/pytest_python && python3 -m ruff check tests/test_current_document_attachment_preview_route.py`
- `cd FPMS_Automation_Skeleton_Pack/pytest_python && pytest tests/test_current_document_attachment_preview_route.py -q`
- `python3 FPMS_Automation_Skeleton_Pack/scripts/audit_current_coverage.py`
- `./scripts/task_validate.sh SKEL-COVERAGE-PY-DOCUMENT-ATTACHMENT-PREVIEW-ROUTE-01`

## Remaining Follow-up Task IDs

- Additional per-endpoint route coverage tasks for the remaining backend audit gaps.

## Done Definition

- The route smoke references and exercises `POST /documents/wizard/attachment-preview`.
- Targeted lint and pytest route smoke pass.
- Coverage audit no longer lists the attachment preview route as a rough backend uncovered route.
- Required evidence and task gate pass.
