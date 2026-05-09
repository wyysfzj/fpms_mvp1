# SKEL-COVERAGE-PY-W0-012-TEMPLATE-LETTERHEAD-01

## Story Shape Classification

- shared_file_density: low
- prereq_dependency_density: low
- be_fe_coupling: low
- evidence_cost: medium
- chosen_runbook: P0-single-lane-story

## Exact Closure Slice

Convert canonical `TC-W0-012` from skeleton to a real pytest handler covering the current implemented template source and letterhead APIs as one documented template-and-letterhead setup flow.

## Explicit Non-Closure

This task does not add template binary upload, template-to-letterhead association schema, document rendering, UI automation, or backend schema changes.

## Allowed Files

- `FPMS_Automation_Skeleton_Pack/pytest_python/handlers/wave_w0.py`
- `FPMS_Automation_Skeleton_Pack/pytest_python/tests/test_w0_template_letterhead_handler.py`
- `tasks/automation/SKEL-COVERAGE-PY-W0-012-TEMPLATE-LETTERHEAD-01.md`
- `artifacts/SKEL-COVERAGE-PY-W0-012-TEMPLATE-LETTERHEAD-01/**`

## Verification Commands

- `cd FPMS_Automation_Skeleton_Pack/pytest_python && python3 -m ruff check handlers/wave_w0.py tests/test_w0_template_letterhead_handler.py`
- `cd FPMS_Automation_Skeleton_Pack/pytest_python && pytest tests/test_w0_template_letterhead_handler.py tests/test_wave_w0.py -q`
- `python3 FPMS_Automation_Skeleton_Pack/scripts/audit_current_coverage.py --json`
- `./scripts/task_validate.sh SKEL-COVERAGE-PY-W0-012-TEMPLATE-LETTERHEAD-01`

## Evidence Path

- `artifacts/SKEL-COVERAGE-PY-W0-012-TEMPLATE-LETTERHEAD-01/**`

## Remaining Follow-Up Task IDs

- Additional canonical real-handler coverage tasks for W0/C/D/E/F/G/G0/H/X waves.

## Done Definition

- `TC-W0-012` is no longer marked with `@skeleton_case`.
- `TC-W0-012` executes the existing template source setup flow.
- `TC-W0-012` executes the existing letterhead setup flow.
- Coverage audit reduces `cases_without_real_handler_count` by one.
- Required evidence and task gate pass.
