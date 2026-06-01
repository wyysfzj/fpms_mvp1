# PD-P1-FE-FEE-LINKAGE-01 — Fee linkage/checklist UI

## Exact Closure Slice

Implement P1 fee linkage UI that shows related fee drafts, pay-list boundary, fee-reduction interpretation status, cponline official-template readiness, and customer-confirmation blockers.

## Explicit Non-Closure

No official payment. No official Excel generation unless already supported by backend contract. No backend code.

## Remaining Follow-Up Task IDs

- `PD-P1-QA-FULLSCOPE-E2E-01`

## Allowed Files

- `frontend/src/modules/fees/pages/FeeDraftDetail.vue`
- `frontend/src/modules/annuity/pages/PayListDetail.vue`
- `frontend/src/modules/officialWorkflows/components/FeeLinkagePanel.vue`
- `tasks/postdemo/PD-P1-FE-FEE-LINKAGE-01.md`
- `artifacts/PD-P1-FE-FEE-LINKAGE-01/**`

## Verification Commands

- `cd frontend && npm run lint`
- `cd frontend && npm run typecheck`
- `cd frontend && npm run build`
- Browser smoke: fee linkage panel distinguishes internal draft/pay-list from official-template readiness.
- `./scripts/task_validate.sh PD-P1-FE-FEE-LINKAGE-01`

## Evidence Path

- `artifacts/PD-P1-FE-FEE-LINKAGE-01/`

## Acceptance

- UI does not imply `PayList/GovPayment` is already the official upload Excel.
- Fee-rate list source remains blocked/待确认 until readable customer source is available.
