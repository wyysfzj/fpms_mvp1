# PE-BE-FE-03 — Fees backend follow-up for calc modes and reduction/discount closure.

- Source: `tasks/postenhancement/BATCH3_FEES_ANNUITY_MANIFEST_20260317.md`
- Type: `service + api`
- Execution mode: Atomic (single-task, single-owner)

## Task Definition

- Goal: close the remaining feasible Batch 3 backend fee-calculation scope.
- Covered items:
  - `US-FE-02`
  - `FR-FE-03`
- Allowlist:
  - `backend/app/modules/fees/api.py`
  - `backend/app/modules/fees/service.py`
  - `backend/app/modules/fees/schemas.py`
  - `backend/tests/test_annuity_e2e.py`
- Out of scope:
  - pay list / gov payment state handling
  - annuity task extraction
  - case receipt / overview queries
  - `Batch 4+`
- Acceptance:
  - `calculate_fee_amount` no longer treats all non-`FIXED` modes as default passthrough
  - covered calc modes are implemented with deterministic rules based on existing `calc_params`
  - reduction / discount behavior is validated and can be overridden manually through existing fee-item editing flow
  - no schema change is introduced
- Verification:
  - `ruff check backend/app/modules/fees/api.py backend/app/modules/fees/service.py backend/app/modules/fees/schemas.py backend/tests/test_annuity_e2e.py`
  - `cd backend && pytest -q tests/test_annuity_e2e.py -k 'calc or reduction or discount or rate'`

## Execution Checklist

- [ ] Confirm allowlist only
- [ ] Add minimal failing backend tests first
- [ ] Implement calc-mode behavior with smallest possible change set
- [ ] Run listed verification commands
- [ ] Generate artifacts evidence
