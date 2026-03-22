# PE-FE-COM-02 — Commission frontend follow-up for settlement completion visibility.

- Source: `tasks/postenhancement/BATCH5_COMMISSION_CONSULTING_MANIFEST_20260321.md`
- Type: `page + api client`
- Execution mode: Atomic (single-task, single-owner)

## Task Definition

- Goal: close one feasible Batch 5 frontend settlement visibility slice.
- Covered items:
  - `US-COM-06`
  - `FR-COM-06`
- Allowlist:
  - `frontend/src/modules/commission/pages/CommissionSettlement.vue`
  - `frontend/src/api/commission.ts`
  - `frontend/src/api/commission.types.ts`
- Out of scope:
  - commission list page
  - report export
  - consulting pages
- Shared ownership:
  - `Yes`
- Verification:
  - `cd frontend && npm run lint`
  - `cd frontend && npm run typecheck`

## Exact Closure Slice

- This task closes exactly:
  - settlement page visibly reflects stage-completion results returned by the current settlement generation/report contract.

## Explicit Non-Closure Statement

- This task does NOT close:
  - report completeness beyond the selected settlement slice
  - consulting/search linkage
  - export / print

## Remaining Follow-up Task IDs

- `PE-BE-COM-03`
- `PE-FE-COM-03`

## Done Definition

- [ ] exact closure slice implemented
- [ ] no out-of-scope expansion
- [ ] verification passed
- [ ] artifacts generated
- [ ] task gate passed

## Dirty Baseline Artifacts

- `artifacts/PE-FE-COM-02/baseline_allowlist.diff`
- `artifacts/PE-FE-COM-02/baseline_external_files.txt`

## Execution Checklist

- [ ] Confirm allowlist only
- [ ] Record baseline artifacts before editing
- [ ] Add failing proof first
- [ ] Implement the minimum fix only
- [ ] Run required verification
- [ ] Generate evidence artifacts
- [ ] Run task gate
- [ ] Stop after one closure slice
