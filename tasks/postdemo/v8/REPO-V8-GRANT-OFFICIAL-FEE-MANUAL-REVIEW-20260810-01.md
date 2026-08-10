# REPO-V8-GRANT-OFFICIAL-FEE-MANUAL-REVIEW-20260810-01

Status: IMPLEMENTED / AWAITING INDEPENDENT REVIEW 2026-08-10
Phase: foundation prerequisite for catalog Row120
Risk: PROTECTED
Runbook: P0-prereq-heavy-story

## Exact closure

Implement the approved source-backed manual official-fee review action and its read validator
exactly as frozen in
`docs/product/v8/stories/V8-GRANT-OFFICIAL-FEE-MANUAL-REVIEW-SUCCESSOR-CONTRACT.md`.

## Dependencies

- `V8-GRANT-YEAR-ANNUITY-OBLIGATION-CURRENT-ADOPTION`
- `V8-GRANT-INSTRUCTION-OBLIGATION-ADAPTER-CURRENT-ADOPTION`

## Allowed files

- `backend/app/modules/grant_fees/service.py`
- `backend/app/modules/grant_fees/schemas.py`
- `backend/app/modules/grant_fees/api.py`
- `backend/app/modules/fees/obligation_service.py`
- `backend/tests/test_v8_grant_official_fee_manual_review.py`
- `docs/product/v8/stories/V8-GRANT-OFFICIAL-FEE-MANUAL-REVIEW-SUCCESSOR-CONTRACT.md`
- this task file

## Non-closure

No schema/migration, rate/reduction inference, generic writer change, draft creation, automatic
customer decision, UI, payment, PayList, service fee or unrelated refactor.

## Verification

- RED: `cd backend && python -m pytest -q tests/test_v8_grant_official_fee_manual_review.py`
- GREEN: same exact focused command
- Ruff check on the five allowlisted Python files
- exact-path `git diff --check`
- independent PROTECTED review with P0/P1/P2 all zero

## Done

The exact contract is implemented with targeted RED/GREEN, current scoped checks and independent
zero-finding approval. Adoption must bind the final product commits and exact tree fingerprint.

## Current verification

- RED: focused test file failed `5` tests because the frozen public action did not exist.
- GREEN: focused test file passes `11`; direct grant-year obligation/instruction, generic
  detail/overlay and generic draft regressions pass `197` unique tests.
- Scoped Ruff and exact diff check pass.
- Independent implementation review and adoption remain pending.
