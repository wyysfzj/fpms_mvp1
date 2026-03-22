# PE-BE-BL-02 — Collections backend follow-up for bad-debt and dunning contract refinement.

- Source: `tasks/postenhancement/BATCH4_BILLING_COLLECTIONS_MANIFEST_20260318.md`
- Type: `endpoint`
- Execution mode: Atomic (single-task, single-owner)

## Task Definition

- Goal: close one feasible Batch 4 backend bad-debt / dunning slice.
- Covered items:
  - `US-BL-06`
  - `FR-BL-07`
  - `FR-BL-08`
- Allowlist:
  - `backend/app/modules/collections/api.py`
  - `backend/app/modules/collections/service.py`
  - `backend/app/modules/billing/service.py`
  - `backend/tests/test_collections_e2e.py`
- Out of scope:
  - document generation /催款函
  - prepayment / offset visibility
  - manual bill creation
  - `Batch 5+`
- Shared ownership:
  - `Yes`
- Verification:
  - `ruff check backend/app/modules/collections/api.py backend/app/modules/collections/service.py backend/app/modules/billing/service.py backend/tests/test_collections_e2e.py`
  - `cd backend && pytest -q tests/test_collections_e2e.py -k 'dunning or bad_debt'`

## Exact Closure Slice

- This task closes exactly:
  - one backend dunning/bad-debt read-or-action slice to be fixed during freeze-to-wave execution.

## Explicit Non-Closure Statement

- This task does NOT close:
  - frontend dunning list/detail visibility
  - prepayment allocation or reverse-offset behavior
  - document generation of dunning letters

## Remaining Follow-up Task IDs

- `PE-FE-BL-02`
- `PE-BE-BL-03`
- `PE-FE-BL-03`

## Done Definition

- [ ] one exact dunning/bad-debt closure slice implemented
- [ ] no spillover into document generation or Batch 5
- [ ] verification passed
- [ ] artifacts generated
- [ ] task gate passed

## Dirty Baseline Artifacts

- `artifacts/PE-BE-BL-02/baseline_allowlist.diff`
- `artifacts/PE-BE-BL-02/baseline_external_files.txt`

## Execution Checklist

- [ ] Confirm allowlist only
- [ ] Record baseline artifacts before editing
- [ ] Add failing test or failing proof first
- [ ] Implement the minimum fix only
- [ ] Run required verification
- [ ] Generate evidence artifacts
- [ ] Run task gate
- [ ] Stop after one closure slice
