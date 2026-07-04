# PD-P1-GRANT-NOTICE-UPLOAD-LIFECYCLE-20260704-01

## Story Shape Classification

- shared_file_density: medium
- prereq_dependency_density: high
- be_fe_coupling: medium
- evidence_cost: medium

## chosen_runbook

`P0-prereq-heavy-story`

## Closure Slice

Grant notice attachment upload is the file-driven lifecycle step for the demo: when a `GRANT_NOTICE` document receives an attachment and the case has required grant/annuity fields, the case becomes `GRANTED`; the grant-fee task is created or reused; the P1 demo seed and script expose this path.

## Non-Closure

No frontend route redesign, no CPC/OA direct submit, no RPA, no automatic payment, no annuity task generation change, and no broad case status refactor.

## Allowlist

- `backend/app/modules/documents/service.py`
- `backend/tests/test_grant_fee_notice_task_creation.py`
- `FPMS_Automation_Skeleton_Pack/playwright_ts/src/support/pdP1LiveSeed.py`
- `docs/postdemo/postdemo_p1_lifecycle_demo_script_20260704.md`
- `tasks/postdemo/PD-P1-GRANT-NOTICE-UPLOAD-LIFECYCLE-20260704-01.md`
- `artifacts/PD-P1-GRANT-NOTICE-UPLOAD-LIFECYCLE-20260704-01/**`

## Verification

- `cd backend && .venv/bin/python -m pytest tests/test_grant_fee_notice_task_creation.py -q`
- `cd backend && .venv/bin/ruff check app/modules/documents/service.py tests/test_grant_fee_notice_task_creation.py`
- `cd backend && .venv/bin/ruff format --check app/modules/documents/service.py tests/test_grant_fee_notice_task_creation.py`
- `cd FPMS_Automation_Skeleton_Pack/playwright_ts && npm run demo:p1:seed`
- `./scripts/task_validate.sh PD-P1-GRANT-NOTICE-UPLOAD-LIFECYCLE-20260704-01`

## Done Definition

- A failing test first proves that a ready prosecution case with a seeded/imported grant notice document can become `GRANTED` on attachment upload and has exactly one grant-fee task.
- Implementation passes the test without relaxing terminal status protections.
- Demo seed creates a grant notice document fixture and required grant fields without deleting non-demo data.
- Demo script instructs the presenter to upload the grant notice attachment before expecting `已授权`.
- Evidence artifacts are complete.

## Remaining Follow-Up Task IDs

- `PD-P1-CASE-EDIT-GRANT-FIELDS-I18N-20260704-01`
- `PD-P1-WORKFLOW-DEMO-I18N-RECEIPT-20260704-01`
- `PD-P1-LIFECYCLE-DEMO-RERUN-20260704-01`
