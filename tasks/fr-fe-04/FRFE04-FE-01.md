# FRFE04-FE-01 — Fee Management route/menu/API shared setup

- Source spec: `docs/superpowers/specs/2026-03-23-fee-paylist-govpayment-design.md`
- Type: `frontend shared wiring`
- Status: `Executable`

## Closure Slice

- Exact closure slice: add Fee Management-semantic route and menu entry points and extend shared gov-payment API typings only for already-approved backend contracts.
- Explicit non-closure: does not complete any page behavior, detail UI, manual-row UI, or blocked query fields.
- Remaining follow-up task ids: `FRFE04-FE-02`, `FRFE04-FE-03`, `FRFE04-FE-04`, `FRFE04-FE-05`

## Allowlist

- `frontend/src/constants/menu.ts`
- `frontend/src/router/index.ts`
- `frontend/src/api/govPayments.ts`
- `frontend/src/api/govPayments.types.ts`

## Verification

- `npm run lint -- frontend/src/constants/menu.ts frontend/src/router/index.ts frontend/src/api/govPayments.ts frontend/src/api/govPayments.types.ts`
- `npm run typecheck`

## Evidence

- `artifacts/FRFE04-FE-01/results.jsonl`
- `artifacts/FRFE04-FE-01/summary.md`
- `artifacts/FRFE04-FE-01/git/diff.patch`

