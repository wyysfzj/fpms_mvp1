# FRFE04-FE-04 — Gov-payment registration page hardening

- Source spec: `docs/superpowers/specs/2026-03-23-fee-paylist-govpayment-design.md`
- Type: `frontend page`
- Status: `Executable`

## Closure Slice

- Exact closure slice: harden the generated-row registration page for `POST /gov-payments` using approved backend contracts and Simplified Chinese error/status copy.
- Explicit non-closure: does not implement manual historical row entry or detail-page fetch logic.
- Remaining follow-up task ids: `FRFE04-FE-05`

## Allowlist

- `frontend/src/modules/annuity/pages/GovPaymentCreate.vue`
- `frontend/src/api/govPayments.ts`
- `frontend/src/api/govPayments.types.ts`

## Verification

- `npm run lint -- frontend/src/modules/annuity/pages/GovPaymentCreate.vue frontend/src/api/govPayments.ts frontend/src/api/govPayments.types.ts`
- `npm run typecheck`

## Evidence

- `artifacts/FRFE04-FE-04/results.jsonl`
- `artifacts/FRFE04-FE-04/summary.md`
- `artifacts/FRFE04-FE-04/git/diff.patch`

