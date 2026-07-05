# FPMS-FEE-RATE-EFFECTIVE-DATE-SELECTION-20260705-01

## Story Shape Classification

- `shared_file_density`: medium
- `prereq_dependency_density`: low
- `be_fe_coupling`: none
- `evidence_cost`: medium
- `chosen_runbook`: `P0-single-lane-story`

## Exact Closure Slice

Make official fee preview, annuity generation, and grant-fee amount resolution select enabled `FeeRate` rows only when `effective_from <= as_of_date <= effective_to`, treating null bounds as open-ended.

## Explicit Non-Closure

Do not change fee amounts, fee seed catalog content, fee trigger rules, PCT/Hague/IC automatic trigger behavior, database schema, payment workflow, or frontend display.

## Allowed Files

- `tasks/reviews/FPMS-FEE-RATE-EFFECTIVE-DATE-SELECTION-20260705-01.md`
- `backend/app/modules/fees/service.py`
- `backend/app/modules/annuity/service.py`
- `backend/app/modules/grant_fees/service.py`
- `backend/tests/test_official_fee_preview_api.py`
- `backend/tests/test_annuity_generate.py`
- `backend/tests/test_grant_fee_notice_task_creation.py`
- `artifacts/FPMS-FEE-RATE-EFFECTIVE-DATE-SELECTION-20260705-01/**`

## Verification Commands

- `cd backend && PYTHONPATH=. pytest tests/test_official_fee_preview_api.py tests/test_annuity_generate.py tests/test_grant_fee_notice_task_creation.py -q`
- `cd backend && python -m ruff check --fix app/modules/fees/service.py app/modules/annuity/service.py app/modules/grant_fees/service.py tests/test_official_fee_preview_api.py tests/test_annuity_generate.py tests/test_grant_fee_notice_task_creation.py`
- `cd backend && python -m ruff format app/modules/fees/service.py app/modules/annuity/service.py app/modules/grant_fees/service.py tests/test_official_fee_preview_api.py tests/test_annuity_generate.py tests/test_grant_fee_notice_task_creation.py`
- `cd backend && python -m ruff check app/modules/fees/service.py app/modules/annuity/service.py app/modules/grant_fees/service.py tests/test_official_fee_preview_api.py tests/test_annuity_generate.py tests/test_grant_fee_notice_task_creation.py`
- `./scripts/task_validate.sh FPMS-FEE-RATE-EFFECTIVE-DATE-SELECTION-20260705-01`

## Done Definition

- Tests demonstrate old/current/future enabled rates and select the current effective rate.
- Official fee preview ignores expired and future rates.
- Annuity fee generation ignores expired and future annuity rates.
- Grant-fee amount resolution ignores expired and future grant/annuity rates.
- Required evidence files and task gate exist.

## Evidence Path

- `artifacts/FPMS-FEE-RATE-EFFECTIVE-DATE-SELECTION-20260705-01/**`

## Remaining Follow-Up Task IDs

None
