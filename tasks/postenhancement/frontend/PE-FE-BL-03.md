# PE-FE-BL-03 — Billing frontend follow-up for prepayment and offset visibility refinement.

- Source: `tasks/postenhancement/BATCH4_BILLING_COLLECTIONS_MANIFEST_20260318.md`
- Type: `page + api client`
- Execution mode: Atomic (single-task, single-owner)

## Task Definition

- Goal: close one feasible Batch 4 frontend prepayment / offset visibility slice.
- Covered items:
  - `US-BL-07`
  - `FR-BL-09`
- Allowlist:
  - `frontend/src/modules/billing/pages/PaymentCreate.vue`
  - `frontend/src/modules/billing/pages/PaymentList.vue`
  - `frontend/src/api/billing.ts`
  - `frontend/src/api/billing.types.ts`
- Out of scope:
  - manual bill create page
  - dunning pages
  - bill print/export
- Shared ownership:
  - `Yes`
- Verification:
  - `cd frontend && npm run lint`
  - `cd frontend && npm run typecheck`

## Exact Closure Slice

- This task closes exactly:
  - one frontend prepayment / offset visibility slice aligned to the selected backend Batch 4 contract change.

## Explicit Non-Closure Statement

- This task does NOT close:
  - manual bill page parity
  - dunning visibility
  - commission-facing indicators

## Remaining Follow-up Task IDs

- `None`

## Done Definition

- [ ] one exact prepayment/offset visibility slice implemented
- [ ] no out-of-scope page redesign
- [ ] verification passed
- [ ] artifacts generated
- [ ] task gate passed

## Dirty Baseline Artifacts

- `artifacts/PE-FE-BL-03/baseline_allowlist.diff`
- `artifacts/PE-FE-BL-03/baseline_external_files.txt`

## Execution Checklist

- [ ] Confirm allowlist only
- [ ] Record baseline artifacts before editing
- [ ] Add failing proof first
- [ ] Implement the minimum fix only
- [ ] Run required verification
- [ ] Generate evidence artifacts
- [ ] Run task gate
- [ ] Stop after one closure slice
