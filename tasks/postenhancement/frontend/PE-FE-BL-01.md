# PE-FE-BL-01 — Billing frontend follow-up for manual bill form parity.

- Source: `tasks/postenhancement/BATCH4_BILLING_COLLECTIONS_MANIFEST_20260318.md`
- Type: `page + api client`
- Execution mode: Atomic (single-task, single-owner)

## Task Definition

- Goal: close the first feasible Batch 4 frontend manual-bill slice.
- Covered items:
  - `US-BL-02`
  - `FR-BL-01`
  - `FR-BL-03`
- Allowlist:
  - `frontend/src/modules/billing/pages/BillCreate.vue`
  - `frontend/src/api/billing.ts`
  - `frontend/src/api/billing.types.ts`
- Out of scope:
  - bad debt / dunning pages
  - prepayment / offset pages
  - bill detail/list parity
  - `Batch 5+`
- Shared ownership:
  - `Yes`
- Verification:
  - `cd frontend && npm run lint`
  - `cd frontend && npm run typecheck`

## Exact Closure Slice

- This task closes exactly:
  - manual bill form parity for AR/AP direction and explicit item-row payload mapping to the hardened `/bills/manual` contract.

## Explicit Non-Closure Statement

- This task does NOT close:
  - bad-debt and dunning UI
  - prepayment and offset visibility
  - bill detail/list view redesign

## Remaining Follow-up Task IDs

- `PE-BE-BL-02`
- `PE-FE-BL-02`
- `PE-BE-BL-03`
- `PE-FE-BL-03`

## Done Definition

- [ ] BillCreate manual mode supports AR/AP direction and explicit item-row payload mapping
- [ ] no out-of-scope page redesign
- [ ] verification passed
- [ ] artifacts generated
- [ ] task gate passed

## Dirty Baseline Artifacts

- `artifacts/PE-FE-BL-01/baseline_allowlist.diff`
- `artifacts/PE-FE-BL-01/baseline_external_files.txt`

## Execution Checklist

- [ ] Confirm allowlist only
- [ ] Record baseline artifacts before editing
- [ ] Add failing proof first
- [ ] Implement the minimum fix only
- [ ] Run required verification
- [ ] Generate evidence artifacts
- [ ] Run task gate
- [ ] Stop after one closure slice
