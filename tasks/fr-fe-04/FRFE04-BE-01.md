# FRFE04-BE-01 — Add `POST /pay-lists` historical header creation

- Source spec: `docs/superpowers/specs/2026-03-23-fee-paylist-govpayment-design.md`
- Type: `backend endpoint`
- Status: `Executable`

## Closure Slice

- Exact closure slice: create one empty historical `PayList` header with current model fields only.
- Explicit non-closure: does not create detail rows, manual items, export, query, detail read, or blocked `SPEC` fields like `Type` and `InvoiceNoFrom/To`.
- Remaining follow-up task ids: `FRFE04-BE-02`, `FRFE04-BE-03`, `FRFE04-BE-04`, `FRFE04-BE-05`, `FRFE04-BE-07`

## Allowlist

- `backend/app/modules/annuity/api.py`
- `backend/app/modules/annuity/service.py`
- `backend/tests/test_annuity_e2e.py`

## Verification

- `cd backend && ruff check --fix app/modules/annuity/api.py app/modules/annuity/service.py tests/test_annuity_e2e.py`
- `cd backend && ruff format app/modules/annuity/api.py app/modules/annuity/service.py tests/test_annuity_e2e.py`
- `cd backend && ruff check app/modules/annuity/api.py app/modules/annuity/service.py tests/test_annuity_e2e.py`
- `cd backend && pytest -q tests/test_annuity_e2e.py -k historical_pay_list_create`

## Evidence

- `artifacts/FRFE04-BE-01/results.jsonl`
- `artifacts/FRFE04-BE-01/summary.md`
- `artifacts/FRFE04-BE-01/git/diff.patch`

