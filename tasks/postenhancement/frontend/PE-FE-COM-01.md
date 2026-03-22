# PE-FE-COM-01 — Commission frontend follow-up for list stage and settleability visibility.

- Source: `tasks/postenhancement/BATCH5_COMMISSION_CONSULTING_MANIFEST_20260321.md`
- Type: `page + api client`
- Execution mode: Atomic (single-task, single-owner)

## Task Definition

- Goal: close one feasible Batch 5 frontend commission list visibility slice.
- Covered items:
  - `US-COM-02`
  - `FR-COM-02`
- Allowlist:
  - `frontend/src/modules/commission/pages/CommissionList.vue`
  - `frontend/src/api/commission.ts`
  - `frontend/src/api/commission.types.ts`
- Out of scope:
  - settlement batch page
  - report export
  - consulting pages
- Shared ownership:
  - `Yes`
- Verification:
  - `cd frontend && npm run lint`
  - `cd frontend && npm run typecheck`

## Exact Closure Slice

- This task closes exactly:
  - commission list page visibly shows stage completion and settleability-related markers using the current commission contract.

## Explicit Non-Closure Statement

- This task does NOT close:
  - true source tracing beyond the current API contract
  - settlement batch stage-completion UI
  - report aggregation completeness
  - consulting/search linkage

## Remaining Follow-up Task IDs

- `PE-BE-COM-02`
- `PE-FE-COM-02`
- `PE-BE-COM-03`
- `PE-FE-COM-03`

## Done Definition

- [ ] exact closure slice implemented
- [ ] no out-of-scope expansion
- [ ] verification passed
- [ ] artifacts generated
- [ ] task gate passed

## Dirty Baseline Artifacts

- `artifacts/PE-FE-COM-01/baseline_allowlist.diff`
- `artifacts/PE-FE-COM-01/baseline_external_files.txt`

## Execution Checklist

- [ ] Confirm allowlist only
- [ ] Record baseline artifacts before editing
- [ ] Add failing proof first
- [ ] Implement the minimum fix only
- [ ] Run required verification
- [ ] Generate evidence artifacts
- [ ] Run task gate
- [ ] Stop after one closure slice
