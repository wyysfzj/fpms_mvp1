# FRFE04-BE-02 — Add `GET /pay-lists`

- Source spec: `docs/superpowers/specs/2026-03-23-fee-paylist-govpayment-design.md`
- Type: `backend endpoint`
- Status: `Executable`

## Closure Slice

- Exact closure slice: return paginated pay-list headers filtered by supported Phase 3 fields only: list number, client, status, planned-pay-date range, currency, and case/app join where feasible.
- Explicit non-closure: does not provide detail rows, export, mark-paid, history-marker filter, type filter, fee-code filter, invoice/voucher filter, or schema changes.
- Remaining follow-up task ids: `FRFE04-BE-03`, `FRFE04-BLOCK-03`

## Dependency

- Requires `FRFE04-BE-RBAC-01` first so the read-only route can use `PayList.Read` instead of write-gated fallback permissions.

## Allowlist

- `backend/app/modules/annuity/api.py`
- `backend/app/modules/annuity/service.py`
- `backend/tests/test_annuity_e2e.py`

## Verification

- `cd backend && ruff check --fix app/modules/annuity/api.py app/modules/annuity/service.py tests/test_annuity_e2e.py`
- `cd backend && ruff format app/modules/annuity/api.py app/modules/annuity/service.py tests/test_annuity_e2e.py`
- `cd backend && ruff check app/modules/annuity/api.py app/modules/annuity/service.py tests/test_annuity_e2e.py`
- `cd backend && pytest -q tests/test_annuity_e2e.py -k pay_list_query`

## Evidence

- `artifacts/FRFE04-BE-02/results.jsonl`
- `artifacts/FRFE04-BE-02/summary.md`
- `artifacts/FRFE04-BE-02/git/diff.patch`
