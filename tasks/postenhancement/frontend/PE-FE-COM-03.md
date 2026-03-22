# PE-FE-COM-03 — Commission frontend follow-up for report completeness refinement.

- Source: `tasks/postenhancement/BATCH5_COMMISSION_CONSULTING_MANIFEST_20260321.md`
- Type: `page + api client`
- Execution mode: Atomic (single-task, single-owner)

## Task Definition

- Goal: close one feasible Batch 5 frontend report completeness slice.
- Covered items:
  - `FR-COM-07`
- Allowlist:
  - `frontend/src/modules/commission/pages/CommissionSettlement.vue`
  - `frontend/src/api/commission.ts`
  - `frontend/src/api/commission.types.ts`
- Out of scope:
  - commission list page
  - export / print
  - consulting pages
- Shared ownership:
  - `Yes`
- Verification:
  - `cd frontend && npm run lint`
  - `cd frontend && npm run typecheck`

## Exact Closure Slice

- This task closes exactly:
  - one commission settlement report visibility slice using the existing query contract.

## Explicit Non-Closure Statement

- This task does NOT close:
  - export / print
  - settlement batch workflow beyond the selected report slice
  - consulting/search linkage

## Remaining Follow-up Task IDs

- `None`

## Done Definition

- [ ] exact closure slice implemented
- [ ] no out-of-scope expansion
- [ ] verification passed
- [ ] artifacts generated
- [ ] task gate passed

## Dirty Baseline Artifacts

- `artifacts/PE-FE-COM-03/baseline_allowlist.diff`
- `artifacts/PE-FE-COM-03/baseline_external_files.txt`

## Execution Checklist

- [ ] Confirm allowlist only
- [ ] Record baseline artifacts before editing
- [ ] Add failing proof first
- [ ] Implement the minimum fix only
- [ ] Run required verification
- [ ] Generate evidence artifacts
- [ ] Run task gate
- [ ] Stop after one closure slice
