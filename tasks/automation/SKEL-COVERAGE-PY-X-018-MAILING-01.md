# SKEL-COVERAGE-PY-X-018-MAILING-01

## Story Shape Classification

- shared_file_density: low
- prereq_dependency_density: low
- be_fe_coupling: low
- evidence_cost: medium
- chosen_runbook: P0-single-lane-story

## Exact Closure Slice

Convert canonical `TC-X-018` from skeleton to a real pytest handler covering outgoing document mailing batch registration through `/documents/dispatch/mailing/batch-register`.

## Explicit Non-Closure

This task does not implement dispatch sheet generation, envelope printing, attachment permissions, UI mailing interactions, or other document auxiliary flows.

## Allowed Files

- `FPMS_Automation_Skeleton_Pack/pytest_python/handlers/wave_x.py`
- `FPMS_Automation_Skeleton_Pack/pytest_python/tests/test_x_document_mailing_handler.py`
- `FPMS_Automation_Skeleton_Pack/pytest_python/tests/test_x_case_query_handler.py`
- `tasks/automation/SKEL-COVERAGE-PY-X-018-MAILING-01.md`
- `artifacts/SKEL-COVERAGE-PY-X-018-MAILING-01/**`

## Verification Commands

- `cd FPMS_Automation_Skeleton_Pack/pytest_python && python3 -m ruff check handlers/wave_x.py tests/test_x_document_mailing_handler.py tests/test_x_case_query_handler.py`
- `cd FPMS_Automation_Skeleton_Pack/pytest_python && pytest tests/test_x_document_mailing_handler.py tests/test_x_case_query_handler.py -q`
- `python3 FPMS_Automation_Skeleton_Pack/scripts/audit_current_coverage.py --json`
- `./scripts/task_validate.sh SKEL-COVERAGE-PY-X-018-MAILING-01`

## Evidence Path

- `artifacts/SKEL-COVERAGE-PY-X-018-MAILING-01/**`

## Remaining Follow-Up Task IDs

- Additional canonical real-handler coverage tasks for W0/C/D/E/F/G/G0/H/X waves.

## Done Definition

- `TC-X-018` is no longer marked with `@skeleton_case`.
- `TC-X-018` creates or finds an outbound document.
- `TC-X-018` registers `outgoing_reg_no` and `forward_date` through the mailing batch endpoint.
- Coverage audit reduces `cases_without_real_handler_count` by one.
- Required evidence and task gate pass.
