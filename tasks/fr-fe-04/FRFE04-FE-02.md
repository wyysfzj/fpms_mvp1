# FRFE04-FE-02 — Pay-list list page

- Source spec: `docs/superpowers/specs/2026-03-23-fee-paylist-govpayment-design.md`
- Type: `frontend page`
- Status: `Executable`

## Closure Slice

- Exact closure slice: make the list page support Phase 3-compatible query, list rendering, export trigger, and historical-header entry trigger under Simplified Chinese Fee Management semantics.
- Explicit non-closure: does not implement detail page, manual-row dialog, or blocked structured filters.
- Remaining follow-up task ids: `FRFE04-FE-03`, `FRFE04-FE-05`

## Allowlist

- `frontend/src/modules/annuity/pages/PayList.vue`
- `frontend/src/api/govPayments.ts`
- `frontend/src/api/govPayments.types.ts`

## Verification

- `npm run lint -- frontend/src/modules/annuity/pages/PayList.vue frontend/src/api/govPayments.ts frontend/src/api/govPayments.types.ts`
- `npm run typecheck`

## Evidence

- `artifacts/FRFE04-FE-02/results.jsonl`
- `artifacts/FRFE04-FE-02/summary.md`
- `artifacts/FRFE04-FE-02/git/diff.patch`

