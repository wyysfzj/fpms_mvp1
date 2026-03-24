# FRFE04-BE-06 — Harden `POST /gov-payments`

- Source spec: `docs/superpowers/specs/2026-03-23-fee-paylist-govpayment-design.md`
- Type: `backend endpoint`
- Status: `Executable`

## Closure Slice

- Exact closure slice: register one generated/planned `GovPayment` row under an existing pay list with duplicate protection and positive amount rules.
- Explicit non-closure: does not create standalone `GovPayment`, does not create manual rows with nullable `fee_item_id`, and does not implement voucher/invoice fields.
- Remaining follow-up task ids: `FRFE04-BE-07`, `FRFE04-BLOCK-02`

## Dependency

- Must run after `FRFE04-BE-STATE-01` so row-level registration remains compatible with the dedicated `EXPORTED -> PAID` header transition.

## Allowlist

- `backend/app/modules/annuity/api.py`
- `backend/app/modules/annuity/service.py`
- `backend/tests/test_annuity_e2e.py`

## Verification

- `cd backend && ruff check --fix app/modules/annuity/api.py app/modules/annuity/service.py tests/test_annuity_e2e.py`
- `cd backend && ruff format app/modules/annuity/api.py app/modules/annuity/service.py tests/test_annuity_e2e.py`
- `cd backend && ruff check app/modules/annuity/api.py app/modules/annuity/service.py tests/test_annuity_e2e.py`
- `cd backend && pytest -q tests/test_annuity_e2e.py -k gov_payment_register`

## Evidence

- `artifacts/FRFE04-BE-06/results.jsonl`
- `artifacts/FRFE04-BE-06/summary.md`
- `artifacts/FRFE04-BE-06/git/diff.patch`
