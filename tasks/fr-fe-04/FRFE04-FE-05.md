# FRFE04-FE-05 — Manual historical row entry UI

- Source spec: `docs/superpowers/specs/2026-03-23-fee-paylist-govpayment-design.md`
- Type: `frontend component/page capability`
- Status: `Executable`

## Closure Slice

- Exact closure slice: add a manual historical row entry UI under an existing historical pay list, including nullable `fee_item_id` handling.
- Explicit non-closure: does not redesign list/detail IA or expand into case receipts and fee overview.
- Remaining follow-up task ids: `FRFE04-QA-01`

## Allowlist

- `frontend/src/modules/annuity/components/ManualGovPaymentDialog.vue`
- `frontend/src/modules/annuity/pages/PayListDetail.vue`
- `frontend/src/api/govPayments.ts`
- `frontend/src/api/govPayments.types.ts`

## Verification

- `npm run lint -- frontend/src/modules/annuity/components/ManualGovPaymentDialog.vue frontend/src/modules/annuity/pages/PayListDetail.vue frontend/src/api/govPayments.ts frontend/src/api/govPayments.types.ts`
- `npm run typecheck`

## Evidence

- `artifacts/FRFE04-FE-05/results.jsonl`
- `artifacts/FRFE04-FE-05/summary.md`
- `artifacts/FRFE04-FE-05/git/diff.patch`

