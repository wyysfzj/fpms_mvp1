# FRFE04-BE-03 — Add `GET /pay-lists/{id}`

- Source spec: `docs/superpowers/specs/2026-03-23-fee-paylist-govpayment-design.md`
- Type: `backend endpoint`
- Status: `Executable`

## Closure Slice

- Exact closure slice: return one pay-list header plus associated `GovPayment` rows.
- Explicit non-closure: does not mutate status, export files, create manual rows, or backfill blocked `SPEC` fields.
- Remaining follow-up task ids: `FRFE04-BE-04`, `FRFE04-BE-05`, `FRFE04-BE-07`

## Allowlist

- `backend/app/modules/annuity/api.py`
- `backend/app/modules/annuity/service.py`
- `backend/tests/test_annuity_e2e.py`

## Verification

- `cd backend && ruff check --fix app/modules/annuity/api.py app/modules/annuity/service.py tests/test_annuity_e2e.py`
- `cd backend && ruff format app/modules/annuity/api.py app/modules/annuity/service.py tests/test_annuity_e2e.py`
- `cd backend && ruff check app/modules/annuity/api.py app/modules/annuity/service.py tests/test_annuity_e2e.py`
- `cd backend && pytest -q tests/test_annuity_e2e.py -k pay_list_detail`

## Evidence

- `artifacts/FRFE04-BE-03/results.jsonl`
- `artifacts/FRFE04-BE-03/summary.md`
- `artifacts/FRFE04-BE-03/git/diff.patch`

