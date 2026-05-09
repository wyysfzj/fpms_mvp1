# SKEL-COVERAGE-PY-W0-003-APPLICANT-01

## Story Shape Classification

- shared_file_density: low
- prereq_dependency_density: low
- be_fe_coupling: low
- evidence_cost: medium
- chosen_runbook: P0-single-lane-story

## Exact Closure Slice

Convert canonical `TC-W0-003` from skeleton to a real pytest handler covering applicant master-data creation and lookup through the existing `/applicants` API.

## Explicit Non-Closure

This task does not implement applicant merge, client address validation, country maintenance, bio-deposit units, UI automation, or backend applicant schema changes.

## Allowed Files

- `FPMS_Automation_Skeleton_Pack/pytest_python/handlers/wave_w0.py`
- `FPMS_Automation_Skeleton_Pack/pytest_python/tests/test_w0_applicant_handler.py`
- `tasks/automation/SKEL-COVERAGE-PY-W0-003-APPLICANT-01.md`
- `artifacts/SKEL-COVERAGE-PY-W0-003-APPLICANT-01/**`

## Verification Commands

- `cd FPMS_Automation_Skeleton_Pack/pytest_python && python3 -m ruff check handlers/wave_w0.py tests/test_w0_applicant_handler.py`
- `cd FPMS_Automation_Skeleton_Pack/pytest_python && pytest tests/test_w0_applicant_handler.py tests/test_wave_w0.py -q`
- `python3 FPMS_Automation_Skeleton_Pack/scripts/audit_current_coverage.py --json`
- `./scripts/task_validate.sh SKEL-COVERAGE-PY-W0-003-APPLICANT-01`

## Evidence Path

- `artifacts/SKEL-COVERAGE-PY-W0-003-APPLICANT-01/**`

## Remaining Follow-Up Task IDs

- Additional canonical real-handler coverage tasks for W0/C/D/E/F/G/G0/H/X waves.

## Done Definition

- `TC-W0-003` is no longer marked with `@skeleton_case`.
- `TC-W0-003` creates entity and individual applicant records through `/applicants`.
- `TC-W0-003` verifies created applicant records through `/applicants` search.
- Coverage audit reduces `cases_without_real_handler_count` by one.
- Required evidence and task gate pass.
