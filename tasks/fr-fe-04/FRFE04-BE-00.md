# FRFE04-BE-00 — Harden `POST /pay-lists/from-fee-items`

- Source spec: `docs/superpowers/specs/2026-03-23-fee-paylist-govpayment-design.md`
- Type: `backend endpoint`
- Status: `Executable`

## Closure Slice

- Exact closure slice: harden the existing generation endpoint so it closes only the draft-sourced `GOV FeeItem -> PayList + planned GovPayment rows` slice with same-client same-currency validation and duplicate protection.
- Explicit non-closure: does not add historical pay-list creation, query, detail, export, mark-paid, manual-item entry, or schema fields.
- Remaining follow-up task ids: `FRFE04-BE-01`, `FRFE04-BE-02`, `FRFE04-BE-03`, `FRFE04-BE-04`, `FRFE04-BE-05`, `FRFE04-BE-06`, `FRFE04-BE-07`

## Allowlist

- `backend/app/modules/annuity/api.py`
- `backend/app/modules/annuity/service.py`
- `backend/tests/test_annuity_e2e.py`

## Verification

- `cd backend && ruff check --fix app/modules/annuity/api.py app/modules/annuity/service.py tests/test_annuity_e2e.py`
- `cd backend && ruff format app/modules/annuity/api.py app/modules/annuity/service.py tests/test_annuity_e2e.py`
- `cd backend && ruff check app/modules/annuity/api.py app/modules/annuity/service.py tests/test_annuity_e2e.py`
- `cd backend && pytest -q tests/test_annuity_e2e.py -k pay_list_from_fee_items`

## Evidence

- `artifacts/FRFE04-BE-00/results.jsonl`
- `artifacts/FRFE04-BE-00/summary.md`
- `artifacts/FRFE04-BE-00/git/diff.patch`

