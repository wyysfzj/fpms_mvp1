# PD-P1-BE-BATCH-FILING-FEE-LIMIT-GATE-01 — Align fee-limit tests with batch filing material gate

## Story Shape Classification

- `shared_file_density`: low
- `prereq_dependency_density`: low
- `be_fe_coupling`: none
- `evidence_cost`: medium
- `chosen_runbook`: `P0-single-lane-story`

## Exact Closure Slice

Update the legacy backend batch filing fee-limit tests so their fixtures satisfy the existing final material gate before calling `/api/v1/cases/batch-filing/submit`.

## Explicit Non-Closure

Do not change product behavior, API contracts, frontend code, database models, migrations, material-gate rules, fee-limit service logic, or final QA ledger contents.

## Remaining Follow-Up Task IDs

None.

## Allowed Files

- `backend/tests/test_apply_fee_limit_base_source.py`
- `backend/tests/test_apply_fee_limit_task_fields.py`
- `artifacts/PD-P1-BE-BATCH-FILING-FEE-LIMIT-GATE-01/**`
- `tasks/postdemo/PD-P1-BE-BATCH-FILING-FEE-LIMIT-GATE-01.md`

## Verification Commands

- `cd backend && pytest -q tests/test_apply_fee_limit_base_source.py tests/test_apply_fee_limit_task_fields.py`
- `cd backend && ruff check --fix tests/test_apply_fee_limit_base_source.py tests/test_apply_fee_limit_task_fields.py`
- `cd backend && ruff format tests/test_apply_fee_limit_base_source.py tests/test_apply_fee_limit_task_fields.py`
- `cd backend && ruff check tests/test_apply_fee_limit_base_source.py tests/test_apply_fee_limit_task_fields.py`
- `cd backend && pytest -q`
- `./scripts/task_validate.sh PD-P1-BE-BATCH-FILING-FEE-LIMIT-GATE-01`

## Evidence Path

- `artifacts/PD-P1-BE-BATCH-FILING-FEE-LIMIT-GATE-01/`

## Acceptance

- The three fee-limit failures from the final QA run no longer fail.
- The test fixtures clearly create the minimal filing materials required by the final material gate.
- Backend full pytest returns rc=0.
- No product code is changed.
