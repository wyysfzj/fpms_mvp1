# SKEL-COVERAGE-PY-DOCUMENT-MAILING-BATCH-ROUTE-01

## Story Shape Classification

- shared_file_density: low
- prereq_dependency_density: low
- be_fe_coupling: low
- evidence_cost: medium
- chosen_runbook: P0-single-lane-story

## Exact Closure Slice

Add one pytest Skeleton Pack backend route smoke for exactly one endpoint:

- `POST /documents/dispatch/mailing/batch-register`

The smoke must create/reuse deterministic case context through real APIs, create one outbound document, register outgoing mailing info for it, and assert the response contains the document with the outgoing registration number.

## Explicit Non-Closure

This task does not cover dispatch sheet creation/detail, attachment preview, envelope preview, frontend UI, or backend mailing behavior changes.

## Allowed Files

- `FPMS_Automation_Skeleton_Pack/pytest_python/tests/test_current_document_mailing_batch_route.py`
- `tasks/automation/SKEL-COVERAGE-PY-DOCUMENT-MAILING-BATCH-ROUTE-01.md`
- `artifacts/SKEL-COVERAGE-PY-DOCUMENT-MAILING-BATCH-ROUTE-01/**`

## Verification

- `cd FPMS_Automation_Skeleton_Pack/pytest_python && python3 -m ruff check tests/test_current_document_mailing_batch_route.py`
- `cd FPMS_Automation_Skeleton_Pack/pytest_python && pytest tests/test_current_document_mailing_batch_route.py -q`
- `python3 FPMS_Automation_Skeleton_Pack/scripts/audit_current_coverage.py`
- `./scripts/task_validate.sh SKEL-COVERAGE-PY-DOCUMENT-MAILING-BATCH-ROUTE-01`

## Remaining Follow-up Task IDs

- `SKEL-COVERAGE-PY-DOCUMENT-WIZARD-ATTACHMENT-PREVIEW-ROUTE-01`
- Additional per-endpoint route coverage tasks for the remaining backend audit gaps.

## Done Definition

- The route smoke references and exercises `POST /documents/dispatch/mailing/batch-register`.
- Targeted lint and pytest route smoke pass.
- Coverage audit no longer lists the mailing batch route as a rough backend uncovered route.
- Required evidence and task gate pass.
