# FRFE04-BE-04 — Add `POST /pay-lists/{id}/export`

- Source spec: `docs/superpowers/specs/2026-03-23-fee-paylist-govpayment-design.md`
- Type: `backend endpoint`
- Status: `Executable`

## Closure Slice

- Exact closure slice: generate one Excel export for one pay list and move header state from `DRAFT` to `EXPORTED`.
- Explicit non-closure: does not implement XML/text exports, remote official-client integration, cancellation, or invoice-range schema fields.
- Remaining follow-up task ids: `FRFE04-BE-05`, `FRFE04-BLOCK-04`

## Dependency

- Requires `FRFE04-BE-RBAC-02` first so the export route can use registered `PayList.Export` gating instead of an unseeded permission code.

## Allowlist

- `backend/app/modules/annuity/api.py`
- `backend/app/modules/annuity/service.py`
- `backend/app/modules/annuity/export_excel.py`
- `backend/tests/test_annuity_e2e.py`

## Verification

- `cd backend && ruff check --fix app/modules/annuity/api.py app/modules/annuity/service.py app/modules/annuity/export_excel.py tests/test_annuity_e2e.py`
- `cd backend && ruff format app/modules/annuity/api.py app/modules/annuity/service.py app/modules/annuity/export_excel.py tests/test_annuity_e2e.py`
- `cd backend && ruff check app/modules/annuity/api.py app/modules/annuity/service.py app/modules/annuity/export_excel.py tests/test_annuity_e2e.py`
- `cd backend && pytest -q tests/test_annuity_e2e.py -k pay_list_export`

## Evidence

- `artifacts/FRFE04-BE-04/results.jsonl`
- `artifacts/FRFE04-BE-04/summary.md`
- `artifacts/FRFE04-BE-04/git/diff.patch`
