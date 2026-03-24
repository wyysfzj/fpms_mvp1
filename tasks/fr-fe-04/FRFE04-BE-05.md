# FRFE04-BE-05 — Add `POST /pay-lists/{id}/mark-paid`

- Source spec: `docs/superpowers/specs/2026-03-23-fee-paylist-govpayment-design.md`
- Type: `backend endpoint`
- Status: `Executable`

## Closure Slice

- Exact closure slice: record compatible header paid date and move header state from `EXPORTED` to `PAID`.
- Explicit non-closure: does not skip export state, does not add cancellation, and does not implement blocked `SPEC` paid metadata fields.
- Remaining follow-up task ids: `FRFE04-BLOCK-02`, `FRFE04-BLOCK-05`

## Dependency

- Requires `FRFE04-BE-STATE-01` first so row-level registration no longer auto-skips the dedicated `mark-paid` transition.

## Allowlist

- `backend/app/modules/annuity/api.py`
- `backend/app/modules/annuity/service.py`
- `backend/tests/test_annuity_e2e.py`

## Verification

- `cd backend && ruff check --fix app/modules/annuity/api.py app/modules/annuity/service.py tests/test_annuity_e2e.py`
- `cd backend && ruff format app/modules/annuity/api.py app/modules/annuity/service.py tests/test_annuity_e2e.py`
- `cd backend && ruff check app/modules/annuity/api.py app/modules/annuity/service.py tests/test_annuity_e2e.py`
- `cd backend && pytest -q tests/test_annuity_e2e.py -k pay_list_mark_paid`

## Evidence

- `artifacts/FRFE04-BE-05/results.jsonl`
- `artifacts/FRFE04-BE-05/summary.md`
- `artifacts/FRFE04-BE-05/git/diff.patch`
