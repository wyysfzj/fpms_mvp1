# FPMS-OFFICIAL-MANIFEST-MULTI-FILE-ROLE-20260705-01

## Story Shape Classification

- `shared_file_density`: low
- `prereq_dependency_density`: low
- `be_fe_coupling`: low
- `evidence_cost`: medium
- `chosen_runbook`: `P0-single-lane-story`

## Exact Closure Slice

Preserve multiple official work package manifest rows for multi-file OA roles, starting with `OA_OTHER_PROOF` and `OA_ADDITIONAL_FILE`, so repeated proof/extra attachments are not overwritten by role-only upsert.

## Explicit Non-Closure

Do not change official notice catalog, attachment role vocabulary, storage paths, OA/CPC direct submit, receipt parsing, or frontend layout.

## Allowed Files

- `tasks/reviews/FPMS-OFFICIAL-MANIFEST-MULTI-FILE-ROLE-20260705-01.md`
- `backend/app/modules/official_workflows/service.py`
- `backend/tests/test_pd_p1_official_work_package_service.py`
- `artifacts/FPMS-OFFICIAL-MANIFEST-MULTI-FILE-ROLE-20260705-01/**`

## Verification Commands

- `cd backend && PYTHONPATH=. pytest tests/test_pd_p1_official_work_package_service.py -q`
- `cd backend && python -m ruff check --fix app/modules/official_workflows/service.py tests/test_pd_p1_official_work_package_service.py`
- `cd backend && python -m ruff format app/modules/official_workflows/service.py tests/test_pd_p1_official_work_package_service.py`
- `cd backend && python -m ruff check app/modules/official_workflows/service.py tests/test_pd_p1_official_work_package_service.py`
- `./scripts/task_validate.sh FPMS-OFFICIAL-MANIFEST-MULTI-FILE-ROLE-20260705-01`

## Done Definition

- Two `OA_OTHER_PROOF` attachments produce two present manifest rows.
- Existing required single-file roles keep one manifest row per role.
- Placeholder rows for missing optional multi-file roles do not block package evaluation once actual attachments exist.
- Required evidence files and task gate exist.

## Evidence Path

- `artifacts/FPMS-OFFICIAL-MANIFEST-MULTI-FILE-ROLE-20260705-01/**`

## Remaining Follow-Up Task IDs

None
