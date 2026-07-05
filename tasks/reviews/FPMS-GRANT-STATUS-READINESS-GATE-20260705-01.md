# FPMS-GRANT-STATUS-READINESS-GATE-20260705-01

## Story Shape Classification

- `shared_file_density`: medium
- `prereq_dependency_density`: low
- `be_fe_coupling`: none
- `evidence_cost`: medium
- `chosen_runbook`: `P0-single-lane-story`

## Exact Closure Slice

Unify `GRANTED` readiness checks so grant notice attachment upload and grant-fee status advancement use the same required field rule as case status validation. A case missing publication fields (`pub_no`, `pub_date`) must not advance to `GRANTED` through grant-notice attachment upload.

## Explicit Non-Closure

Do not redesign the full legal status state machine, change case status names, add database migrations, change UI text, or alter grant-fee task state semantics.

## Allowed Files

- `tasks/reviews/FPMS-GRANT-STATUS-READINESS-GATE-20260705-01.md`
- `backend/app/modules/cases/service.py`
- `backend/app/modules/documents/service.py`
- `backend/app/modules/grant_fees/service.py`
- `backend/tests/test_grant_fee_notice_task_creation.py`
- `artifacts/FPMS-GRANT-STATUS-READINESS-GATE-20260705-01/**`

## Verification Commands

- `cd backend && PYTHONPATH=. pytest tests/test_grant_fee_notice_task_creation.py -q`
- `cd backend && python -m ruff check --fix app/modules/cases/service.py app/modules/documents/service.py app/modules/grant_fees/service.py tests/test_grant_fee_notice_task_creation.py`
- `cd backend && python -m ruff format app/modules/cases/service.py app/modules/documents/service.py app/modules/grant_fees/service.py tests/test_grant_fee_notice_task_creation.py`
- `cd backend && python -m ruff check app/modules/cases/service.py app/modules/documents/service.py app/modules/grant_fees/service.py tests/test_grant_fee_notice_task_creation.py`
- `./scripts/task_validate.sh FPMS-GRANT-STATUS-READINESS-GATE-20260705-01`

## Done Definition

- Missing `pub_no` / `pub_date` regression test fails before implementation and passes after implementation.
- Grant-notice attachment upload still advances a fully ready case to `GRANTED`.
- Grant-fee service and document service share the same readiness helper.
- Required evidence files and task gate exist.

## Evidence Path

- `artifacts/FPMS-GRANT-STATUS-READINESS-GATE-20260705-01/**`

## Remaining Follow-Up Task IDs

None
