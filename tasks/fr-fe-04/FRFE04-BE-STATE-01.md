# FRFE04-BE-STATE-01 — Align pay-list status recompute with `mark-paid`

- Source spec: `docs/superpowers/specs/2026-03-23-fee-paylist-govpayment-design.md`
- Type: `backend service rule`
- Status: `Executable`

## Closure Slice

- Exact closure slice: keep `register_gov_payment` row-level registration behavior, but stop the shared pay-list recompute logic from auto-advancing an `EXPORTED` pay list to `PAID` before the dedicated `POST /pay-lists/{id}/mark-paid` slice runs.
- Explicit non-closure: does not add the `mark-paid` endpoint itself, does not redesign duplicate protection or manual-row behavior, and does not add cancellation or blocked `SPEC` paid metadata fields.
- Remaining follow-up task ids: `FRFE04-BE-05`, `FRFE04-BE-06`, `FRFE04-BLOCK-02`

## Dependency

- Must execute before accepting `FRFE04-BE-05`, because `mark-paid` is otherwise unreachable through supported row-registration behavior.

## Allowlist

- `backend/app/modules/annuity/service.py`
- `backend/tests/test_annuity_e2e.py`

## Verification

- `cd backend && ruff check --fix app/modules/annuity/service.py tests/test_annuity_e2e.py`
- `cd backend && ruff format app/modules/annuity/service.py tests/test_annuity_e2e.py`
- `cd backend && ruff check app/modules/annuity/service.py tests/test_annuity_e2e.py`
- `cd backend && pytest -q tests/test_annuity_e2e.py -k "gov_payment_register or pay_list_mark_paid"`

## Evidence

- `artifacts/FRFE04-BE-STATE-01/results.jsonl`
- `artifacts/FRFE04-BE-STATE-01/summary.md`
- `artifacts/FRFE04-BE-STATE-01/git/diff.patch`
