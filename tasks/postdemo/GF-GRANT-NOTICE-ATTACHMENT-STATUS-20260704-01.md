# GF-GRANT-NOTICE-ATTACHMENT-STATUS-20260704-01

## Story Shape Classification

- shared_file_density: medium
- prereq_dependency_density: low
- be_fe_coupling: backend-only
- evidence_cost: medium
- chosen_runbook: P0-single-lane-story

## Exact Closure Slice

Fix the demo bug where uploading the final attachment for an incoming `GRANT_NOTICE` document leaves the case stuck before the granted lifecycle state. When the upload belongs to a grant notice document and the case already has the required publication, grant, and annuity fields, the attachment upload must advance the case from `GRANT_PENDING` to `GRANTED`.

Also restore the ORM registry test prerequisite so the regression test can run after the P1 official-fee carriers introduced an `OfficialFeeChecklist -> PayList` foreign key.

## Explicit Non-Closure

No frontend changes, no new upload UI, no OCR/file parsing, no automatic extraction of grant fields from uploaded files, no grant-fee task workflow redesign, no schema or migration change, no broad status-machine refactor, and no wildcard demo data cleanup.

## Allowed Files

- `tasks/postdemo/GF-GRANT-NOTICE-ATTACHMENT-STATUS-20260704-01.md`
- `backend/app/models/__init__.py`
- `backend/app/modules/documents/service.py`
- `backend/tests/test_grant_fee_notice_task_creation.py`
- `artifacts/GF-GRANT-NOTICE-ATTACHMENT-STATUS-20260704-01/**`

## Verification Commands

```bash
./scripts/evidence_run.sh GF-GRANT-NOTICE-ATTACHMENT-STATUS-20260704-01 test-red /bin/zsh -lc 'cd backend && .venv/bin/python -m pytest -q tests/test_grant_fee_notice_task_creation.py::test_grant_notice_attachment_upload_advances_ready_case_to_granted'
```

```bash
./scripts/evidence_run.sh GF-GRANT-NOTICE-ATTACHMENT-STATUS-20260704-01 lint /bin/zsh -lc 'cd backend && .venv/bin/python -m ruff check app/models/__init__.py app/modules/documents/service.py tests/test_grant_fee_notice_task_creation.py'
```

```bash
./scripts/evidence_run.sh GF-GRANT-NOTICE-ATTACHMENT-STATUS-20260704-01 test /bin/zsh -lc 'cd backend && .venv/bin/python -m pytest -q tests/test_grant_fee_notice_task_creation.py tests/test_grant_fee_state_machine_api.py::test_grant_fee_done_advances_case_to_granted_when_grant_fields_present tests/test_grant_fee_state_machine_api.py::test_grant_fee_done_does_not_advance_case_without_required_grant_fields'
```

```bash
./scripts/task_validate.sh GF-GRANT-NOTICE-ATTACHMENT-STATUS-20260704-01
```

## Done Definition

- A regression test proves uploading an attachment to a ready `GRANT_NOTICE` document advances the linked case to `GRANTED`.
- Existing grant-notice task creation still leaves the case at `GRANT_PENDING` before the final attachment evidence is uploaded.
- Grant-fee `mark_done` behavior remains unchanged.
- Required evidence artifacts exist and task gate passes.

## Remaining Follow-Up Task IDs

- None
