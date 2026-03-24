# FRFE04-FE-03 — Pay-list detail page

- Source spec: `docs/superpowers/specs/2026-03-23-fee-paylist-govpayment-design.md`
- Type: `frontend page`
- Status: `Executable`

## Closure Slice

- Exact closure slice: add a detail page that reads one pay list, shows header and rows, and surfaces export / mark-paid / registration entry actions.
- Explicit non-closure: does not implement the manual-row dialog itself, menu wiring, or the dual-table fee overview.
- Remaining follow-up task ids: `FRFE04-FE-04`, `FRFE04-FE-05`

## Allowlist

- `frontend/src/modules/annuity/pages/PayListDetail.vue`
- `frontend/src/router/index.ts`
- `frontend/src/api/govPayments.ts`
- `frontend/src/api/govPayments.types.ts`

## Verification

- `npm run lint -- frontend/src/modules/annuity/pages/PayListDetail.vue frontend/src/router/index.ts frontend/src/api/govPayments.ts frontend/src/api/govPayments.types.ts`
- `npm run typecheck`

## Evidence

- `artifacts/FRFE04-FE-03/results.jsonl`
- `artifacts/FRFE04-FE-03/summary.md`
- `artifacts/FRFE04-FE-03/git/diff.patch`

