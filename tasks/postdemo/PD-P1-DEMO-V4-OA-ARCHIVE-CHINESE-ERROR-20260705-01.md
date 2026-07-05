# PD-P1-DEMO-V4-OA-ARCHIVE-CHINESE-ERROR-20260705-01

## Story Shape Classification

- shared_file_density: low
- prereq_dependency_density: low
- be_fe_coupling: low
- evidence_cost: low
- chosen_runbook: P0-single-lane-story

## Closure

Translate the official work package archive-blocked API error message to Simplified Chinese so a premature archive check during the P1 V4 demo does not show an English user-facing toast.

## Non-Closure

Do not change archive gate logic, receipt requirements, override policy, frontend behavior, database schema, CPC/OA direct submit, RPA, signature automation, or official payment behavior.

## Allowlist

- `tasks/postdemo/PD-P1-DEMO-V4-OA-ARCHIVE-CHINESE-ERROR-20260705-01.md`
- `backend/app/modules/official_workflows/service.py`
- `backend/tests/test_pd_p1_receipt_archive_api.py`
- `artifacts/PD-P1-DEMO-V4-OA-ARCHIVE-CHINESE-ERROR-20260705-01/**`

## Verification

- `cd backend && .venv/bin/pytest -q tests/test_pd_p1_receipt_archive_api.py`
- task-scoped Ruff for the two backend files
- `./scripts/task_validate.sh PD-P1-DEMO-V4-OA-ARCHIVE-CHINESE-ERROR-20260705-01`

## Done Definition

- A blocked archive response returns Chinese message text for `OFFICIAL_WORK_PACKAGE_ARCHIVE_BLOCKED`.
- Existing successful receipt archive and override tests still pass.
- Evidence exists under `artifacts/PD-P1-DEMO-V4-OA-ARCHIVE-CHINESE-ERROR-20260705-01/**`.

## Follow-Up Task IDs

None.
