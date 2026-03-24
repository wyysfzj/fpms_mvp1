# FRFE04-BE-07 — Add `POST /pay-lists/{id}/manual-items`

- Source spec: `docs/superpowers/specs/2026-03-23-fee-paylist-govpayment-design.md`
- Type: `backend endpoint`
- Status: `Executable`

## Closure Slice

- Exact closure slice: add one manual/historical `GovPayment` row under an existing pay list and allow nullable `fee_item_id`.
- Explicit non-closure: does not create historical pay-list headers, does not implement standalone `GovPayment`, and does not add structured fee-code/year/invoice/voucher fields.
- Remaining follow-up task ids: `FRFE04-BLOCK-02`, `FRFE04-BLOCK-03`

## Allowlist

- `backend/app/modules/annuity/api.py`
- `backend/app/modules/annuity/service.py`
- `backend/tests/test_annuity_e2e.py`

## Verification

- `cd backend && ruff check --fix app/modules/annuity/api.py app/modules/annuity/service.py tests/test_annuity_e2e.py`
- `cd backend && ruff format app/modules/annuity/api.py app/modules/annuity/service.py tests/test_annuity_e2e.py`
- `cd backend && ruff check app/modules/annuity/api.py app/modules/annuity/service.py tests/test_annuity_e2e.py`
- `cd backend && pytest -q tests/test_annuity_e2e.py -k pay_list_manual_item`

## Evidence

- `artifacts/FRFE04-BE-07/results.jsonl`
- `artifacts/FRFE04-BE-07/summary.md`
- `artifacts/FRFE04-BE-07/git/diff.patch`

