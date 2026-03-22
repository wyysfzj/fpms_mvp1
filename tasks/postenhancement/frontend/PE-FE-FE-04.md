# PE-FE-FE-04 — Batch 3 frontend follow-up for case receipts and fee overview visibility.

- Source: `tasks/postenhancement/BATCH3_FEES_ANNUITY_MANIFEST_20260317.md`
- Type: `page + api client`
- Execution mode: Atomic (single-task, single-owner)

## Task Definition

- Goal: close the remaining feasible Batch 3 frontend receipt / overview visibility scope.
- Covered items:
  - `US-FE-06`
  - `US-FE-08`
  - `FR-FE-07`
  - `FR-FE-09`
- Allowlist:
  - `frontend/src/modules/cases/components/CaseReceiptsSummary.vue`
  - `frontend/src/modules/fees/pages/FeeDraftList.vue`
  - `frontend/src/modules/fees/pages/FeeDraftDetail.vue`
  - `frontend/src/api/billing.ts`
  - `frontend/src/api/billing.types.ts`
  - `frontend/src/api/fees.ts`
  - `frontend/src/api/fees.types.ts`
- Out of scope:
  - bill create/detail redesign
  - commission pages
  - export / printing
- Acceptance:
  - receipt summary exposes arrears / commissionable / invoice context clearly enough for Batch 3
  - fee overview surfaces receipt + gov-payment-facing information without expanding into Batch 4 workflows
  - user-facing text remains Simplified Chinese
- Verification:
  - `cd frontend && npm run lint`
  - `cd frontend && npm run typecheck`

## Execution Checklist

- [ ] Confirm allowlist only
- [ ] Implement minimal UI + API mapping changes only
- [ ] Run listed verification commands
- [ ] Generate artifacts evidence
