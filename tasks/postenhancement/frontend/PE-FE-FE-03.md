# PE-FE-FE-03 — Fees frontend follow-up for rate config and fee draft parity.

- Source: `tasks/postenhancement/BATCH3_FEES_ANNUITY_MANIFEST_20260317.md`
- Type: `page + api client`
- Execution mode: Atomic (single-task, single-owner)

## Task Definition

- Goal: close the remaining feasible Batch 3 frontend fee-calculation visibility and query parity scope.
- Covered items:
  - `US-FE-02`
  - `FR-FE-03`
  - partial visibility for `US-FE-08`
  - partial visibility for `FR-FE-09`
- Allowlist:
  - `frontend/src/modules/fees/pages/FeeRates.vue`
  - `frontend/src/modules/fees/components/FeeRateForm.vue`
  - `frontend/src/modules/fees/pages/FeeDraftList.vue`
  - `frontend/src/modules/fees/pages/FeeDraftDetail.vue`
  - `frontend/src/api/fees.ts`
  - `frontend/src/api/fees.types.ts`
- Out of scope:
  - annuity pages
  - billing pages
  - case receipt widget
  - route changes
- Acceptance:
  - calc mode, reduction allowance, and effective range are visible and editable where Batch 3 requires
  - fee draft list/detail expose enough total/status context for downstream Batch 3 usage
  - user-facing text remains Simplified Chinese
- Verification:
  - `cd frontend && npm run lint`
  - `cd frontend && npm run typecheck`

## Execution Checklist

- [ ] Confirm allowlist only
- [ ] Implement minimal UI + API mapping changes only
- [ ] Run listed verification commands
- [ ] Generate artifacts evidence
