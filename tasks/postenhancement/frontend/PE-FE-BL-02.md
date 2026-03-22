# PE-FE-BL-02 — Collections frontend follow-up for dunning visibility refinement.

- Source: `tasks/postenhancement/BATCH4_BILLING_COLLECTIONS_MANIFEST_20260318.md`
- Type: `page + api client`
- Execution mode: Atomic (single-task, single-owner)

## Task Definition

- Goal: close one feasible Batch 4 frontend dunning / bad-debt visibility slice.
- Covered items:
  - `US-BL-06`
  - `FR-BL-07`
  - `FR-BL-08`
- Allowlist:
  - `frontend/src/modules/collections/pages/DunningList.vue`
  - `frontend/src/modules/collections/pages/DunningDetail.vue`
  - `frontend/src/modules/collections/pages/DunningCreate.vue`
  - `frontend/src/api/collections.ts`
  - `frontend/src/api/collections.types.ts`
- Out of scope:
  - prepayment / offset pages
  - manual bill creation page
  - dunning letter generation
  - `Batch 5+`
- Shared ownership:
  - `Yes`
- Verification:
  - `cd frontend && npm run lint`
  - `cd frontend && npm run typecheck`

## Exact Closure Slice

- This task closes exactly:
  - one frontend dunning visibility / filter / state-display slice to match the selected backend dunning/bad-debt contract refinement.

## Explicit Non-Closure Statement

- This task does NOT close:
  - prepayment and offset visibility
  - manual bill create page parity
  - dunning letter rendering/export

## Remaining Follow-up Task IDs

- `PE-BE-BL-03`
- `PE-FE-BL-03`

## Done Definition

- [ ] one exact dunning visibility slice implemented
- [ ] no route or scope spillover
- [ ] verification passed
- [ ] artifacts generated
- [ ] task gate passed

## Dirty Baseline Artifacts

- `artifacts/PE-FE-BL-02/baseline_allowlist.diff`
- `artifacts/PE-FE-BL-02/baseline_external_files.txt`

## Execution Checklist

- [ ] Confirm allowlist only
- [ ] Record baseline artifacts before editing
- [ ] Add failing proof first
- [ ] Implement the minimum fix only
- [ ] Run required verification
- [ ] Generate evidence artifacts
- [ ] Run task gate
- [ ] Stop after one closure slice
